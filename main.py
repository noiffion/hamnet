import os
import json
import random
import string
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, login_user, current_user, logout_user
from models import db, login_manager, app
from oauth import blueprint
from models import (Genres, Plays, User, Reviews, OAuth, Cities, Theatres, 
                    Performances, db, login_manager, app)
from flask import (Flask, render_template, redirect, jsonify, url_for, flash,
                   request as flask_req, session as login_session)

app.register_blueprint(blueprint, url_prefix="/login")
login_manager.init_app(app)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out")
    return redirect(url_for("home"))


@app.route("/login/facebook/authorized")
def authorized():
    current_uri = login_session.get('current_uri')
    print("\nauthorized current_uri: ", current_uri, "\n")
    return redirect(url_for(current_uri))


def loggedIn():
    if current_user.is_authenticated:
        flash("You are logged in as: {0}".format(current_user.name))
        return True
    else:
        flash("You are not logged in.")
        return False


def dateTr(date, result):
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

    login_session['current_uri'] = url_for('home')

    playlist = []
    for i in range(4):
        playlist.append(Plays.query.filter_by(genre_id=i+1)
                .order_by(Plays.title).all())
    loggedIn()
    return render_template('oeuvre.html', playlist=playlist)


@app.route('/play/<int:play_id>/')
def showPlayPerf(play_id):

    # to avoid error if play_id is bigger than 39 in the uri
    if play_id >= 40:
        return redirect('/')

    # redirect to editable page if logged-in
    if loggedIn():
        return redirect(url_for('modifyPlayPerf', play_id=play_id))

    # remembering the uri to be able to redirect back here after sign in
    login_session['current_uri'] = url_for('showPlayPerf', play_id=play_id)

    play = Plays.query.filter_by(id=play_id).first()

    # putting the result of a multiple JOIN SQL query into a list of lists
    with open('./shaky/DB/Queries/query_1.txt', 'r') as f:
        query = f.read()
    perfs = db.engine.execute(query.format(play_id))
    performances = []
    for perf in perfs:
        performances.append([perf.review_link, perf.review_title, perf.webpage,
                             perf.theatre_name, perf.city_name,
                             perf.performance_date, perf.username])
    changeMonth(performances)

    return render_template('pp_show.html', play=play, perfs=performances)


@app.route('/play/<int:play_id>/modify/', methods=['GET', 'POST'])
def modifyPlayPerf(play_id):

    # to avoid error if play_id is bigger than 39 in the uri
    if play_id >= 40:
        return redirect('/')

    # redirect to non-editable page if not logged-in
    if not loggedIn():
        return redirect(url_for('showPlayPerf', play_id=play_id))

    # remembering the uri to be able to redirect back here after sign in
    login_session['current_uri'] = url_for('modifyPlayPerf', play_id=play_id)

    play = Plays.query.filter_by(id=play_id).first()

    # putting the result of a multiple JOIN SQL query into a list of lists
    with open('./shaky/DB/Queries/query_2.txt', 'r') as f:
        query = f.read()
    perfs = db.engine.execute(query.format(play_id, current_user.id))
    performances = []
    for perf in perfs:
        performances.append(
          [
           perf.review_link, perf.review_title, 
           perf.webpage, perf.theatre_name, 
           perf.city_name, perf.performance_date, 
           perf.username, perf.review_id, 
           perf.id, perf.user_id
          ]
        )
    changeMonth(performances)

    if flask_req.method == 'POST':
        print("\nflask_req.form: {0}\n".format(flask_req.form))

        # evading unauthorized deleting
        if int(flask_req.form['user_id']) != current_user.id:
            return redirect(url_for('home'))

        perf_id = flask_req.form['perfID']
        rev_id = flask_req.form['perf_reviewID']
        print(perf_id, rev_id)

        del_performance = Performances.query.filter_by(id=perf_id).first()
        del_review = Reviews.query.filter_by(id=rev_id).first()
        print(del_performance, del_review)
        db.session.delete(del_performance)
        db.session.delete(del_review)
        db.session.commit()
        return redirect(url_for('modifyPlayPerf', play_id=play_id))

    return render_template('pp_modify.html', play=play, perfs=performances)


@app.route('/play/<int:play_id>/add/', methods=['GET', 'POST'])
def addPerf(play_id):

    # to avoid error if play_id is bigger than 39 in the uri
    if play_id >= 40:
        return redirect('/')

    # redirect to non-editable page if not logged-in
    if not loggedIn():
        return redirect(url_for('showPlayPerf', play_id=play_id))

    login_session['current_uri'] = url_for('addPerf', play_id=play_id)

    play = Plays.query.filter_by(id=play_id).first()
    theatres = Theatres.query.order_by(Theatres.theatre_name).all()

    # on submitting the form create the new entries in the database
    if flask_req.method == 'POST':

        # creating a new Review entry in the DB
        p_date = flask_req.form['p_date']
        newReview = Reviews(review_title=flask_req.form['review_title'],
                            performance_date=dateTr(p_date, 'y-m-d'),
                            review_link=flask_req.form['review_link'],
                            user_id=current_user.id)
        db.session.add(newReview)
        db.session.commit()

        # creating a new Performance entry in the DB
        newPerformance = Performances(play_id=play_id,
                                      theatre_id=flask_req.form['theatre'],
                                      review_id=newReview.id,
                                      user_id=current_user.id)
        db.session.add(newPerformance)
        db.session.commit()
        return redirect(url_for('modifyPlayPerf', play_id=play_id))

    return render_template('form_perform.html', play=play, theatres=theatres)


@app.route('/play/<int:play_id>/edit/<int:perf_id>/', methods=['GET', 'POST'])
def editPerf(play_id, perf_id):

    # to avoid error if play_id is bigger than 39 in the uri
    if play_id >= 40:
        return redirect('/')

    # redirect to non-editable page if not logged-in
    if not loggedIn():
        return redirect(url_for('showPlayPerf', play_id=play_id))

    # creating the necessary data objects from the database
    play = Plays.query.filter_by(id=play_id).first()
    theatres = Theatres.query.order_by(Theatres.theatre_name).all()
    performance = Performances.query.filter_by(id=perf_id).first()
    review = Reviews.query.filter_by(id=performance.review_id).first()
    # change the date format from 'YYYY-MM-DD' to 'DD-MM-YYYY'
    p_date = str(review.performance_date)
    p_date = dateTr(p_date, 'd-m-y')

    # evading unauthorized editing
    if performance.user_id != current_user.id:
        return redirect(url_for('home'))

    login_session['current_uri'] = url_for('editPerf', play_id=play_id, perf_id=perf_id)

    # on submitting the form update the information in the database
    if flask_req.method == 'POST':
        p_date = flask_req.form['p_date']
        performance.theatre_id = flask_req.form['theatre']
        review.review_title = flask_req.form['review_title']
        review.performance_date = dateTr(p_date, 'y-m-d')
        review.review_link = flask_req.form['review_link']
        db.session.commit()
        return redirect(url_for('modifyPlayPerf', play_id=play_id))

    return render_template('form_editPerform.html', play=play, review=review,
                           theatres=theatres,  perf=performance, p_date=p_date)


@app.route('/theatres/<int:play_id>/', methods=['GET', 'POST'])
def theatres(play_id):

    # to avoid error if play_id is bigger than 39 in the uri
    if play_id >= 40:
        return redirect('/')

    # redirect to non-editable page if not logged-in
    if not loggedIn():
        return redirect('/')

    # reading and executing an sql join of theatres and cities table
    with open('./shaky/DB/Queries/query_3.txt', 'r') as f:
        query = f.read()
    theatres = []
    tres = db.engine.execute(query.format(current_user.id))
    for theatre in tres:
        theatres.append([theatre.id, theatre.theatre_name, theatre.city_id,
                         theatre.city_name, theatre.address, theatre.webpage])

    # creating necessary variables for the form_theatres.html js script
    len_theatres = len(theatres)
    play = Plays.query.filter_by(id=play_id).first()
    cities = Cities.query.order_by(Cities.city_name).all()
    len_cities = len(cities)
    theatres_index_lst = []
    for i in range(len_theatres):
        theatres_index_lst.append(theatres[i][0])

    # reading and executing the form data
    if flask_req.method == 'POST':
        if flask_req.form['theatre_id'] == 1:  # cannot remove Globe theatre
            return redirect(url_for('theatres', play_id=play_id))

        # creating a new theatre
        elif flask_req.form['theatre_id'] == 'new':
            print(flask_req.form)
            new_theatre = Theatres(theatre_name=flask_req.form['theatre_name'],
                                   city_id=flask_req.form['city'],
                                   address=flask_req.form['address'],
                                   webpage=flask_req.form['webpage'])
            db.session.add(new_theatre)
            db.session.commit()
            return redirect(url_for('addPerf', play_id=play_id))

        # deleting a theatre
        elif flask_req.form.get('theatre_name') is None:
            t_id = flask_req.form['theatre_id']
            del_theatre = Theatres.query.filter_by(id=t_id).first()
            db.session.delete(del_theatre)
            db.session.commit()
            return redirect(url_for('addPerf', play_id=play_id))

        # updating a theatre
        else:
            t_id = flask_req.form['theatre_id']
            edit_theatre = Theatres.query.filter_by(id=t_id).first()
            edit_theatre.theatre_name = flask_req.form['theatre_name']
            edit_theatre.city_id = flask_req.form['city']
            edit_theatre.address = flask_req.form['address']
            edit_theatre.webpage = flask_req.form['webpage']
            db.session.commit()
            return redirect(url_for('addPerf', play_id=play_id))

    return render_template('form_theatres.html', theatres=theatres,
                           len_theatres=len_theatres, play=play,
                           cities=cities, len_cities=len_cities,
                           tindex=theatres_index_lst)




# JSON API to retrieve information about all of the plays
@app.route('/api/plays/JSON/')
def playsJSON():
    plays = Plays.query.order_by(Plays.title).all()
    return jsonify(plays_of_Shakespeare=[p.serialize for p in plays])


# JSON API to retrieve information about all of the theatres
@app.route('/api/theatres/JSON/')
def theatresJSON():
    ths = Theatres.query.order_by(Theatres.theatre_name).all()
    return jsonify(theatres=[t.serialize for t in ths])


# JSON API to retrieve information about performances of a given play
@app.route('/api/play/<int:play_id>/performance/JSON/')
def performancesJSON(play_id):
    prfs = Performances.query.filter_by(play_id=play_id).all()
    return jsonify(performance=[p.serialize for p in prfs])
