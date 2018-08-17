#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import auth
import json
import random
import string
import datetime
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker, scoped_session
from models import (Base, Genres, Plays, Users, Reviews,
                    Cities, Theatres, Performances)
from flask import (Flask, render_template, redirect, jsonify, url_for, flash,
                   request as flask_req, session as login_session)


app = Flask(__name__)

APPLICATION_NAME = "Shake-speare"

engine = create_engine('sqlite:///hamnet.db')
Base.metadata.bind = engine
session = scoped_session(sessionmaker(
          autocommit=False, autoflush=True, bind=engine))


def createUser(login_session):
    """Creates a user in the database"""
    newUser = Users(username=login_session['username'],
                    email=login_session['email'],
                    photo=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(Users).filter_by(email=login_session['email']).one()
    session.close()
    return user.id


def getUserInfo(user_id):
    user = session.query(Users).filter_by(id=user_id).one()
    session.close()
    return user


def getUserID(email):
    try:
        user = session.query(Users).filter_by(email=email).one()
        session.close()
        return user.id
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def loggedIn(user_id):
    """ Check if user is logged in, it displays a message in the
       footer or the header accordingly """
    if user_id:
        flash("You are logged in as: {0}".format(login_session['username']))
        return True
    else:
        flash("You are not logged in.")
        return False


def dateTr(date, result):
    """ Transform the date into a reversed format based on the 'result'
        parameter (ie. 'DD-MM-YYYY' format to 'YYYY-MM-DD' and vice versa) """

    if result.lower() == 'y-m-d':
        pDate = date
        pDateYear = int(pDate[-4:])  # Year is the last four characters

        for i, p in enumerate(pDate[:-5]):  # Month is after the first '-'
            if p == '-':
                pDateMonth = int(pDate[:-5][(i+1):])
                break

        for i, p in enumerate(pDate[:-5]):  # Day is before the first '-'
            if p == '-':
                pDateDay = int(pDate[:-5][:i])
                break

        pDate = datetime.date(pDateYear, pDateMonth, pDateDay)
        return pDate

    elif result.lower() == 'd-m-y':
        pDate = date
        pDateYear = pDate[:4]  # Year is the first four characters

        for i, p in enumerate(pDate[5:]):
            if p == '-':
                pDateMonth = pDate[5:][:i]  # Month before the second '-'
                break

        for i, p in enumerate(pDate[5:]):
            if p == '-':
                pDateDay = pDate[5:][(i+1):]  # Day is after the 2nd '-'
                break

        pDate = "{0}-{1}-{2}".format(pDateDay, pDateMonth, pDateYear)
        return pDate

    else:
        return False


def changeMonth(performances):
    """ Changing int month value (1-12) to string month value (Jan-Dec) """
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for perf in performances:
        try:
            for i, month in enumerate(months):
                if int(perf[5][5:7]) == (i+1):
                    perf[5] = str(perf[5][:4]) + month + str(perf[5][8:])
        except ValueError:
            continue


@app.route('/')
def home():
    """Displays the main page"""

    login_session['current_uri'] = url_for('home')
    print(login_session)

    playlist = []
    for i in range(4):
        playlist.append(session.query(Plays).filter_by(genre_id=i+1)
                                            .order_by(asc(Plays.title)).all())
    loggedIn(login_session.get('user_id'))
    session.close()
    return render_template('oeuvre.html', playlist=playlist)


@app.route('/login')
def showLogin():
    """Displays the login page"""

    print(login_session)

    if login_session.get('provider') and login_session.get('user_id'):
        return redirect(login_session['current_uri'])

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(33))
    login_session['state'] = state
    uri = login_session['current_uri']
    return render_template('login.html', STATE=state, URI=uri)


@app.route('/login/<provider>', methods=['POST'])
def login(provider):
    """Login based on authorization server"""

    # after login welcome message with picture
    with open('./templates/loginWelcome.txt', 'r') as f:
        html_output = f.read()

    if provider == 'google':
        if auth.ggLogin():
            return html_output.format(login_session['username'],
                                      login_session['picture'])
        else:
            return redirect('/')

    elif provider == 'facebook':
        if auth.fbLogin():
            return html_output.format(login_session['username'],
                                      login_session['picture'])
        else:
            return redirect('/')


@app.route('/play/<int:play_id>/')
def showPlayPerf(play_id):
    """Displays the performances of the given play"""

    # to avoid error if play_id is bigger than 39 in the uri
    if play_id >= 40:
        return redirect('/')

    # redirect to editable page if logged-in
    if loggedIn(login_session.get('user_id')):
        session.close()
        return redirect(url_for('modifyPlayPerf', play_id=play_id))

    # remembering the uri to be able to redirect back here after sign in
    login_session['current_uri'] = url_for('showPlayPerf', play_id=play_id)
    print(login_session)

    play = session.query(Plays).filter_by(id=play_id).one()

    # putting the result of a multiple JOIN SQL query into a list of lists
    with open('./DB/Queries/query_1.txt', 'r') as f:
        query = f.read()
    perfs = engine.execute(query.format(play_id))
    performances = []
    for perf in perfs:
        performances.append([perf.review_link, perf.review_title, perf.webpage,
                             perf.theatre_name, perf.city_name,
                             perf.performance_date, perf.username])
    changeMonth(performances)

    session.close()
    return render_template('pp_show.html', play=play, perfs=performances)


@app.route('/play/<int:play_id>/modify/', methods=['GET', 'POST'])
def modifyPlayPerf(play_id):
    """Like showPlayPerf but if user is logged in the perfs can be edited"""

    # to avoid error if play_id is bigger than 39 in the uri
    if play_id >= 40:
        return redirect('/')

    # redirect to non-editable page if not logged-in
    if not loggedIn(login_session.get('user_id')):
        session.close()
        return redirect(url_for('showPlayPerf', play_id=play_id))

    # remembering the uri to be able to redirect back here after sign in
    login_session['current_uri'] = url_for('modifyPlayPerf', play_id=play_id)
    print(login_session)

    play = session.query(Plays).filter_by(id=play_id).one()

    # putting the result of a multiple JOIN SQL query into a list of lists
    with open('./DB/Queries/query_2.txt', 'r') as f:
        query = f.read()
    perfs = engine.execute(query.format(play_id, login_session['user_id']))
    performances = []
    for perf in perfs:
        performances.append([perf.review_link, perf.review_title, perf.webpage,
                             perf.theatre_name, perf.city_name,
                             perf.performance_date, perf.username,
                             perf.review_id, perf.id, perf.user_id])
    changeMonth(performances)

    if flask_req.method == 'POST':
        print("\nflask_req.form: {0}\n".format(flask_req.form))

        # evading unauthorized deleting
        if flask_req.form['user_id'] != login_session['user_id']:
            return redirect(url_for('home'))

        del_performance = (session.query(Performances)
                           .filter_by(id=flask_req.form['perfID']).one())
        del_review = (session.query(Reviews)
                      .filter_by(id=flask_req.form['perf_reviewID']).one())
        session.delete(del_performance)
        session.delete(del_review)
        session.commit()
        session.close()
        return redirect(url_for('modifyPlayPerf', play_id=play_id))

    session.close()
    return render_template('pp_modify.html', play=play, perfs=performances)


@app.route('/play/<int:play_id>/add/', methods=['GET', 'POST'])
def addPerf(play_id):
    """ Add a performance to a play """

    # to avoid error if play_id is bigger than 39 in the uri
    if play_id >= 40:
        return redirect('/')

    # redirect to non-editable page if not logged-in
    if not loggedIn(login_session.get('user_id')):
        session.close()
        return redirect(url_for('showPlayPerf', play_id=play_id))

    login_session['current_uri'] = url_for('addPerf', play_id=play_id)

    play = session.query(Plays).filter_by(id=play_id).one()
    theatres = (session.query(Theatres)
                .order_by(asc(Theatres.theatre_name)).all())

    # on submitting the form create the new entries in the database
    if flask_req.method == 'POST':

        # creating a new Review entry in the DB
        p_date = flask_req.form['p_date']
        newReview = Reviews(review_title=flask_req.form['review_title'],
                            performance_date=dateTr(p_date, 'y-m-d'),
                            review_link=flask_req.form['review_link'],
                            user_id=login_session['user_id'])
        session.add(newReview)
        session.commit()

        # creating a new Performance entry in the DB
        newPerformance = Performances(play_id=play_id,
                                      theatre_id=flask_req.form['theatre'],
                                      review_id=newReview.id,
                                      user_id=login_session['user_id'])
        session.add(newPerformance)
        session.commit()
        session.close()
        return redirect(url_for('modifyPlayPerf', play_id=play_id))

    session.close()
    return render_template('form_perform.html', play=play, theatres=theatres)


@app.route('/play/<int:play_id>/edit/<int:perf_id>/', methods=['GET', 'POST'])
def editPerf(play_id, perf_id):
    """ Edit a performance of a play """

    # to avoid error if play_id is bigger than 39 in the uri
    if play_id >= 40:
        return redirect('/')

    # redirect to non-editable page if not logged-in
    if not loggedIn(login_session.get('user_id')):
        session.close()
        return redirect(url_for('showPlayPerf', play_id=play_id))

    # creating the necessary data objects from the database
    play = session.query(Plays).filter_by(id=play_id).one()
    theatres = (session.query(Theatres)
                .order_by(asc(Theatres.theatre_name)).all())
    performance = session.query(Performances).filter_by(id=perf_id).one()
    review = session.query(Reviews).filter_by(id=performance.review_id).one()
    # change the date format from 'YYYY-MM-DD' to 'DD-MM-YYYY'
    p_date = str(review.performance_date)
    p_date = dateTr(p_date, 'd-m-y')

    # evading unauthorized editing
    if performance.user_id != login_session['user_id']:
        return redirect(url_for('home'))

    login_session['current_uri'] = (url_for('editPerf',
                                    play_id=play_id, perf_id=perf_id))

    # on submitting the form update the information in the database
    if flask_req.method == 'POST':
        p_date = flask_req.form['p_date']
        performance.theatre_id = flask_req.form['theatre']
        review.review_title = flask_req.form['review_title']
        review.performance_date = dateTr(p_date, 'y-m-d')
        review.review_link = flask_req.form['review_link']
        session.commit()
        session.close()
        return redirect(url_for('modifyPlayPerf', play_id=play_id))

    session.close()
    return render_template('form_editPerform.html', play=play, review=review,
                           theatres=theatres,  perf=performance, p_date=p_date)


@app.route('/theatres/<int:play_id>/', methods=['GET', 'POST'])
def theatres(play_id):
    """ Add, edit, remove theatres to/from the database"""

    # to avoid error if play_id is bigger than 39 in the uri
    if play_id >= 40:
        return redirect('/')

    # redirect to non-editable page if not logged-in
    if not loggedIn(login_session.get('user_id')):
        session.close()
        return redirect('/')

    # reading and executing an sql join of theatres and cities table
    with open('./DB/Queries/query_3.txt', 'r') as f:
        query = f.read()
    theatres = []
    tres = engine.execute(query.format(login_session['user_id']))
    for theatre in tres:
        theatres.append([theatre.id, theatre.theatre_name, theatre.city_id,
                         theatre.city_name, theatre.address, theatre.webpage])

    # creating necessary variables for the form_theatres.html js script
    len_theatres = len(theatres)
    play = session.query(Plays).filter_by(id=play_id).one()
    cities = session.query(Cities).order_by(asc(Cities.city_name)).all()
    len_cities = len(cities)
    theatres_index_lst = []
    for i in range(len_theatres):
        theatres_index_lst.append(theatres[i][0])

    # reading and executing the form data
    if flask_req.method == 'POST':
        if flask_req.form['theatre_id'] == 1:  # cannot remove Globe theatre
            session.close()
            return redirect(url_for('theatres', play_id=play_id))

        # creating a new theatre
        elif flask_req.form['theatre_id'] == 'new':
            print(flask_req.form)
            new_theatre = Theatres(theatre_name=flask_req.form['theatre_name'],
                                   city_id=flask_req.form['city'],
                                   address=flask_req.form['address'],
                                   webpage=flask_req.form['webpage'])
            session.add(new_theatre)
            session.commit()
            session.close()
            return redirect(url_for('addPerf', play_id=play_id))

        # deleting a theatre
        elif flask_req.form.get('theatre_name') is None:
            del_theatre = (session.query(Theatres)
                           .filter_by(id=flask_req.form['theatre_id']).one())
            session.delete(del_theatre)
            session.commit()
            session.close()
            return redirect(url_for('addPerf', play_id=play_id))

        # updating a theatre
        else:
            edit_theatre = (session.query(Theatres)
                            .filter_by(id=flask_req.form['theatre_id']).one())
            edit_theatre.theatre_name = flask_req.form['theatre_name']
            edit_theatre.city_id = flask_req.form['city']
            edit_theatre.address = flask_req.form['address']
            edit_theatre.webpage = flask_req.form['webpage']
            session.commit()
            session.close()
            return redirect(url_for('addPerf', play_id=play_id))

    session.close()
    return render_template('form_theatres.html', theatres=theatres,
                           len_theatres=len_theatres, play=play,
                           cities=cities, len_cities=len_cities,
                           tindex=theatres_index_lst)


@app.route('/logout')
def logout():
    """ Logout based on authorization server """

    print(login_session)

    if login_session.get('provider'):

        if login_session['provider'] == 'google':
            auth.ggLogout()  # auth module ggLogout func
            del login_session['gplus_id']

        elif login_session['provider'] == 'facebook':
            auth.fbLogout()  # auth module fbLogout func
            del login_session['facebook_id']

        del login_session['access_token']
        del login_session['app_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']

        return redirect(login_session['current_uri'])

    else:
        return redirect('/')


# JSON API to retrieve information about all of the plays
@app.route('/plays/JSON/')
def playsJSON():
    plays = session.query(Plays).order_by(asc(Plays.title)).all()
    return jsonify(plays_of_Shakespeare=[p.serialize for p in plays])


# JSON API to retrieve information about all of the theatres
@app.route('/theatres/JSON/')
def theatresJSON():
    ths = session.query(Theatres).order_by(asc(Theatres.theatre_name)).all()
    return jsonify(theatres=[t.serialize for t in ths])


# JSON API to retrieve information about performances of a given play
@app.route('/play/<int:play_id>/performance/JSON/')
def performancesJSON(play_id):
    prfs = session.query(Performances).filter_by(play_id=play_id).all()
    return jsonify(performance=[p.serialize for p in prfs])


if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
