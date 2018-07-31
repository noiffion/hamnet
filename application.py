# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request, json, requests, random, string, authoriz, os
from flask import (Flask, render_template, request, redirect, jsonify, url_for,
                   flash, session as login_session, make_response)
from sqlalchemy import create_engine, asc 
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, Genres, Plays, Users, Dramalist


app = Flask(__name__)

# APPLICATION_NAME =  "Shake-speare"

engine = create_engine('sqlite:///hamnet.db')
Base.metadata.bind = engine
session = scoped_session(sessionmaker(
          autocommit=False, autoflush=False, bind=engine))


def createUser(login_session):
    newUser = Users(username=login_session['username'], 
                    email=login_session['email'],
                    photo=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(Users).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(Users).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(Users).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/')
@app.route('/playlist')
def playList():
    # print(login_session)
    playlist = session.query(Plays).order_by(asc(Plays.title))
    if login_session.get('user_id'):
        return render_template('playlist_view.html', playlist=playlist)
    else:
        return render_template('playlist_edit.html', playlist=playlist)


@app.route('/login')
def showLogin():
    if login_session.get('provider') and login_session.get('user_id'):
        return redirect('/')

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(33))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


""" Login based on authorization server: """
@app.route('/login/<provider>', methods = ['POST'])
def login(provider):

    html_output = ('<h1>Welcome, {0}!</h1><img src="{1}" style="width: '
                   '300px; height: 300px; border-radius: 150px;'
                   '-webkit-border-radius: 150px; -moz-border-radius: '
                   '150px;">')

    if provider == 'google':
        if authoriz.ggLogin() == True:
            return html_output.format(login_session['username'], 
                                      login_session['picture'])
        else:
            return redirect('/')
            
    elif provider == 'facebook':
        if authoriz.fbLogin() == True:
            return html_output.format(login_session['username'], 
                                      login_session['picture'])
        else:
            return redirect('/')
 

""" Logout based on authorization server: """
@app.route('/logout')
def logout():
    if login_session.get('provider'):

        if login_session['provider'] == 'google':
            authoriz.ggLogout()
            del login_session['gplus_id']

        elif login_session['provider'] == 'facebook':
            authoriz.fbLogout()
            del login_session['facebook_id']

        del login_session['access_token']
        del login_session['app_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']

        return redirect('/')

    else:
        return redirect('/')


if __name__ == '__main__':
    """ When running locally, disable OAuthlib's HTTPs verification. """
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)

