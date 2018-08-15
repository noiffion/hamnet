# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import urllib
import urllib.request as url_req
import models
import google.oauth2.credentials
import google_auth_oauthlib.flow
from application import getUserID, createUser
from flask import (request as flask_req, redirect,
                   session as login_session, make_response)


def ggLogin():
    """ Login with a google account """

    # evade Cross-Site Request Forgery
    try:
        if flask_req.args.get('state') != login_session['state']:
            print("Invalid 'state' parameter!")
            return False

        # upgrade the authorization code into a credentials object
        oauth_flow = (google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                      'static/sec/gg_client_secrets.json',
                      scopes=['https://www.googleapis.com/auth/userinfo.email',
                              'https://www.googleapis.com/auth/plus.me'],
                      state=login_session['state']))
        oauth_flow.redirect_uri = "postmessage"
        oauth_flow.fetch_token(code=flask_req.data.decode())
        credentials = oauth_flow.credentials

        # check that the access token is valid
        token_url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?'
                     'access_token={0}'.format(credentials.token))
        token_result = url_req.urlopen(token_url).read().decode()
        token_result = json.loads(token_result)

        # If there was an error in the access token info, abort
        if token_result.get('error'):
            print("Error in accessing the token")
            return False

        # verify that the access token is valid for this app
        with open('static/sec/gg_client_secrets.json', 'r') as gg:
            app = gg.read()
            app_id = json.loads(app)['web']['client_id']
            app_secret = json.loads(app)['web']['client_secret']

        if (token_result['issued_to'] != app_id or
                credentials.client_id != app_id):
            print("Token's user ID doesn't match given user ID.")
            return False

        # verify that the access token is used for the intended user
        userinfo_url = ('https://www.googleapis.com/oauth2/v1/userinfo?'
                        'access_token={0}'.format(credentials.token))
        userinfo_result = url_req.urlopen(userinfo_url).read().decode()
        userinfo_result = json.loads(userinfo_result)
        if token_result['user_id'] != userinfo_result['id']:
            print("Token's client ID does not match app's.")
            return False

    except urllib.error.HTTPerror as e:
        print(e.read())
        print("Failed to connect!")
        return False

    # creating a user profile in the login session
    login_session['access_token'] = credentials.token
    login_session['app_id'] = credentials.client_id
    login_session['email'] = userinfo_result['email']
    login_session['gplus_id'] = userinfo_result['id']
    login_session['provider'] = 'google'
    login_session['picture'] = userinfo_result['picture']
    login_session['username'] = userinfo_result['name']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(userinfo_result["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    return True


def fbLogin():
    """ Login with a Facebook account """

    # evade Cross-Site Request Forgery
    try:
        if flask_req.args.get('state') != login_session['state']:
            print("Invalid 'state' parameter!")
            return False

        access_token = flask_req.data.decode()
        with open('static/sec/fb_client_secrets.json', 'r') as fb:
            app = fb.read()
            app_id = json.loads(app)['web']['app_id']
            app_secret = json.loads(app)['web']['app_secret']

        # use token to get user info from facebook graph API
        oauth_url = ('https://graph.facebook.com/oauth/access_token?'
                     'grant_type=fb_exchange_token&client_id={0}&'
                     'client_secret={1}&fb_exchange_token={2}'
                     .format(app_id, app_secret, access_token))

        verbose_token = url_req.urlopen(oauth_url).read().decode()
        token = json.loads(verbose_token)['access_token']

        userinfo_url = ('https://graph.facebook.com/v2.8/me?access_token={0}'
                        '&fields=name,id,email'.format(token))
        userinfo_result = url_req.urlopen(userinfo_url).read().decode()
        userinfo_result = json.loads(userinfo_result)

        picture_url = ('https://graph.facebook.com/v2.8/me/picture?'
                       'access_token={0}&redirect=0&height=200&width=200'
                       .format(token))
        picture_result = url_req.urlopen(picture_url).read().decode()
        picture_result = json.loads(picture_result)

    except urllib.error.HTTPerror as e:
        print(e.read())
        print("Failed to connect!")
        return False

    # creating a user profile in the login session
    login_session['access_token'] = token
    login_session['app_id'] = app_id
    login_session['email'] = userinfo_result["email"]
    login_session['facebook_id'] = userinfo_result["id"]
    login_session['picture'] = picture_result["data"]["url"]
    login_session['provider'] = 'facebook'
    login_session['username'] = userinfo_result["name"]

    # check if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    return True


def ggLogout():
    """ Logout with a Google account """

    if not login_session.get('access_token'):
        print('Current user has not been connected!')
        return redirect('/login')

    # try accessing the Google API to logout
    try:
        revoke_url = ('https://accounts.google.com/o/oauth2/revoke?token={0}'
                      .format(login_session['access_token']))
        revoke_result = url_req.urlopen(revoke_url)

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    except urllib.error.HTTPError as e:
        print(e.read())
        response = make_response(json.dumps('Failed to revoke token for given'
                                            'user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


def fbLogout():
    """ Logout with a Facebook account """

    if not login_session.get('access_token'):
        print('Current user has not been connected!')
        return redirect('/login')

    # try accessing the Facebook API to logout
    try:
        revoke_url = ('https://graph.facebook.com/{0}/permissions?'
                      'access_token={1}'.format(login_session['facebook_id'],
                                                login_session['access_token']))
        req = url_req.Request(url=revoke_url, method='DELETE')
        rev = url_req.urlopen(req)
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    except urllib.error.HTTPError as e:
        print(e.read())
        response = make_response(json.dumps('Failed to revoke token for given'
                                            'user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response
