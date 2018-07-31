# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import urllib.request
import models
import google.oauth2.credentials
import google_auth_oauthlib.flow
from application import getUserID, createUser
from flask import (request as flask_request, redirect,
                   session as login_session, make_response)


def ggLogin():

    try:
        """ Evade Cross-Site Request Forgery. """
        if flask_request.args.get('state') != login_session['state']:
            print("Invalid 'state' parameter!")
            return False

        """ Upgrade the authorization code into a credentials object. """
        oauth_flow = (google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                      'SEC/gg_client_secrets.json',
                      scopes=['https://www.googleapis.com/auth/userinfo.email',
                              'https://www.googleapis.com/auth/plus.me'],
                      state=login_session['state']))
        oauth_flow.redirect_uri = "postmessage"
        oauth_flow.fetch_token(code=flask_request.data.decode())
        credentials = oauth_flow.credentials

        """ Check that the access token is valid. """
        token_url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?'
                     'access_token={0}'.format(credentials.token))
        token_result = urllib.request.urlopen(token_url).read().decode()
        token_result = json.loads(token_result)

        """ If there was an error in the access token info, abort. """
        if token_result.get('error'):
            print("Error in accessing the token")
            return False

        """ Verify that the access token is valid for this app. """
        with open('SEC/gg_client_secrets.json', 'r') as gg:
            app = gg.read()
            app_id = json.loads(app)['web']['client_id']
            app_secret = json.loads(app)['web']['client_secret']

        if (token_result['issued_to'] != app_id or
                credentials.client_id != app_id):
            print("Token's user ID doesn't match given user ID.")
            return False

        """ Verify that the access token is used for the intended user. """
        userinfo_url = ('https://www.googleapis.com/oauth2/v1/userinfo?'
                        'access_token={0}'.format(credentials.token))
        userinfo_result = urllib.request.urlopen(userinfo_url).read().decode()
        userinfo_result = json.loads(userinfo_result)
        if token_result['user_id'] != userinfo_result['id']:
            print("Token's client ID does not match app's.")
            return False

    except urllib.error.HTTPerror as e:
        print(e.read())
        print("Failed to connect!")
        return False

    login_session['access_token'] = credentials.token
    login_session['app_id'] = credentials.client_id
    login_session['email'] = userinfo_result['email']
    login_session['gplus_id'] = userinfo_result['id']
    login_session['provider'] = 'google'
    login_session['picture'] = userinfo_result['picture']
    login_session['username'] = userinfo_result['name']

    """ See see if user exists, if it doesn't make a new one. """
    user_id = getUserID(userinfo_result["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    return True


def fbLogin():

    try:
        """ Evade Cross-Site Request Forgery. """
        if flask_request.args.get('state') != login_session['state']:
            print("Invalid 'state' parameter!")
            return False

        access_token = flask_request.data.decode()
        with open('SEC/fb_client_secrets.json', 'r') as fb:
            app = fb.read()
            app_id = json.loads(app)['web']['app_id']
            app_secret = json.loads(app)['web']['app_secret']

        """ Use token to get user info from facebook graph API. """
        oauth_url = ('https://graph.facebook.com/oauth/access_token?'
                     'grant_type=fb_exchange_token&client_id={0}&'
                     'client_secret={1}&fb_exchange_token={2}'
                     .format(app_id, app_secret, access_token))

        verbose_token = urllib.request.urlopen(oauth_url).read().decode()
        token = json.loads(verbose_token)['access_token']

        userinfo_url = ('https://graph.facebook.com/v2.8/me?access_token={0}'
                        '&fields=name,id,email'.format(token))
        userinfo_result = urllib.request.urlopen(userinfo_url).read().decode()
        userinfo_result = json.loads(userinfo_result)

        picture_url = ('https://graph.facebook.com/v2.8/me/picture?'
                       'access_token={0}&redirect=0&height=200&width=200'
                       .format(token))
        picture_result = urllib.request.urlopen(picture_url).read().decode()
        picture_result = json.loads(picture_result)

    except urllib.error.HTTPerror as e:
        print(e.read())
        print("Failed to connect!")
        return False

    login_session['access_token'] = token
    login_session['app_id'] = app_id
    login_session['email'] = userinfo_result["email"]
    login_session['facebook_id'] = userinfo_result["id"]
    login_session['picture'] = picture_result["data"]["url"]
    login_session['provider'] = 'facebook'
    login_session['username'] = userinfo_result["name"]

    """ Check if user exists. """
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    return True


def ggLogout():
    if not login_session.get('access_token'):
        print('Current user has not been connected!')
        return redirect('/login')

    try:
        revoke_url = ('https://accounts.google.com/o/oauth2/revoke?token={0}'
                      .format(login_session['access_token']))
        revoke_result = urllib.request.urlopen(revoke_url)

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
    if not login_session.get('access_token'):
        print('Current user has not been connected!')
        return redirect('/login')

    try:
        revoke_url = ('https://graph.facebook.com/{0}/permissions?'
                      'access_token={1}'.format(login_session['facebook_id'],
                                                login_session['access_token']))
        req = urllib.request.Request(url=revoke_url, method='DELETE')
        rev = urllib.request.urlopen(req)
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    except urllib.error.HTTPError as e:
        print(e.read())
        response = make_response(json.dumps('Failed to revoke token for given'
                                            'user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response
