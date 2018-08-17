#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3


def insert(yn, function):
    if yn == 'y':
        return function()


db = sqlite3.connect('../hamnet.db')
yellow = '\033[0;33;40m{0}\033[0m'
yn = 'y'


# GENRES
def Genres():
    """ Inserting the four genres into genres table """

    c = db.cursor()

    genres = ['Tragedy', 'Comedy', 'History', 'Romance']
    for genre in genres:
        c.execute("INSERT INTO genres(genre) VALUES('{0}');".format(genre))
    db.commit()
    print(c.execute("SELECT * FROM genres;").fetchall())
    print()

    return genres


# question = '\n\tInserting: {0} - Do you want to proceed? '.format('GENRES')
# yn = input(yellow.format(question))
genres = insert(yn, Genres)


# USERS
def Users():
    """ Inserting the two users """

    c = db.cursor()

    c.execute("INSERT INTO users(username, email, photo)"
              "VALUES('David Kerekes', 'davkedav@gmail.com',"
              "'https://lh3.googleusercontent.com/-XdUIqdMkCWA/AAAAAAAAAAI/AAAAAAAAAAA/4252rscbv5M/photo.jpg');")  # NOQA
    db.commit()

    c.execute("INSERT INTO users(username, email, photo)"
              "VALUES('Billy Rattlelance', 'billyrattle@live.com', NULL);")
    db.commit()

    print(c.execute("SELECT * FROM users;").fetchall())
    print()


# question = '\n\tInserting: {0} - Do you want to proceed? '.format('USERS')
# yn = input(yellow.format(question))
ulist = insert(yn, Users)


# PLAYS
def Plays():
    """ Inserting the dramas into the plays table """

    c = db.cursor()

    with open('playlist', 'r') as f:
        playlist = f.read()
    # print('\n{0}\n'.format(playlist))

    playlist = playlist.split('\n')
    # print('\n{0}\n'.format(playlist))

    plist = []
    for i, play in enumerate(playlist):
        plist.append([i+1])
        list_item = ''
        for char in play:
            if char != ";":
                list_item += char
            else:
                plist[i].append(list_item)
                list_item = ''

    if plist[i] is not None:
        del plist[i]
    # for play in plist:
        # print(play)

    # print("\nChanging drama categories int ids:")
    for play in plist:
        for i, genre in enumerate(genres):
            if play[2] == genre:
                play[2] = (i+1)
    # for play in plist:
        # n print(play)

    # print("\nChanging string dates to int:")
    for play in plist:
        play[3] = int(play[3])
    # for play in plist:
        # print(play)
    # print("\nAnd the playlist is:")
    # print(plist)

    for play in plist:
        if "'" in play[1]:
            play[1] = play[1].replace("'", "`")
    # print("\nAnd the final playlist is:")
    # for play in plist:
        # print(play)

    for play in plist:
        c.execute("INSERT INTO plays(title, genre_id, written_in,"
                  "quote, picpath) "
                  "VALUES('{0}', {1}, {2}, '{3}', '{4}');"
                  .format(play[1], play[2], play[3], play[4], play[5]))
    db.commit()
    print(c.execute("SELECT * FROM plays;").fetchall())
    print()

    return plist


# question = '\n\tInserting: {0} - Do you want to proceed? '.format('PLAYS')
# yn = input(yellow.format(question))
plist = insert(yn, Plays)


# CITIES
def Cities():
    """ Inserting the cities """

    c = db.cursor()

    with open('cities', 'r') as f:
        cities = f.read()
    # print('The cities are: {0}'.format(cities))

    citylist = cities.split('\n')
    if citylist[len(citylist)-1] == '':
        del citylist[len(citylist)-1]
    # print(citylist)

    for city in citylist:
        c.execute("INSERT INTO cities(city_name) "
                  "VALUES('{0}');".format(city))
    db.commit()
    print(c.execute("SELECT * FROM cities;").fetchall())
    print()

    return citylist


# question = '\n\tInserting: {0} - Do you want to proceed? '.format('CITIES')
# yn = input(yellow.format(question))
citylist = insert(yn, Cities)


# REVIEWS
def Reviews():
    """ Inserting the reviews """

    c = db.cursor()

    with open('reviews', 'r') as f:
        reviews = f.read()
    # print(reviews)

    reviewlist = reviews.split('\n')
    if reviewlist[len(reviewlist)-1] == '':
        del reviewlist[len(reviewlist)-1]
    # print(reviewlist)

    rlist = []
    for review in reviewlist:
        row = review.split(';')
        rlist.append(row)
    # for review in rlist:
        # print(review)

    for i, review in enumerate(rlist):
        c.execute("INSERT INTO reviews(review_title, performance_date,"
                  "review_link, user_id) "
                  "VALUES('{0}', '{1}', '{2}', {3});"
                  .format(review[0], review[2], review[3], review[4]))
    db.commit()
    print(c.execute("SELECT * FROM reviews;").fetchall())
    print()

    return rlist


# question = '\n\tInserting: {0} Do you want to proceed? '.format('REVIEWS')
# yn = input(yellow.format(question))
rlist = insert(yn, Reviews)


# THEATRES
def Theatres():
    """ Inserting the theatres """

    c = db.cursor()

    with open('theatres', 'r') as f:
        theatres = f.read()
    # print('The theatres are: {0}'.format(theatres))

    theatrelist = theatres.split('\n')
    if theatrelist[len(theatrelist)-1] == '':
        del theatrelist[len(theatrelist)-1]
    # print(theatrelist)

    tlist = []
    for theatre in theatrelist:
        row = theatre.split(';')
        tlist.append(row)
    # for theatre in tlist:
        # print(theatre)

    for theatre in tlist:
        for i, city in enumerate(citylist):
            if theatre[2] == city:
                theatre[2] = (i+1)

    # for theatre in tlist:
        # print(theatre)

    for theatre in tlist:
        c.execute("INSERT INTO theatres(theatre_name, city_id, address,"
                  "webpage, user_id) VALUES('{0}', {1}, '{2}', '{3}', {4});"
                  .format(theatre[0], theatre[2], theatre[3], theatre[4],
                          theatre[5]))
    db.commit()
    print(c.execute("SELECT * FROM theatres;").fetchall())
    print()

    return tlist


# question = '\n\tInserting: {0} - Do you want to proceed? '.format('THEATRES')
# yn = input(yellow.format(question))
tlist = insert(yn, Theatres)


# PERFORMANCES
def Performances():
    """ Inserting the theatres """

    c = db.cursor()

    plist = []
    play_ids = [26, 32, 29, 24, 20, 20, 20]
    theatre_ids = [1, 7, 8, 9, 10, 11, 12]
    review_ids = [1, 2, 3, 4, 5, 6, 7]

    for i in range(len(rlist)):
        plist.append([(i+1), play_ids[i], theatre_ids[i], review_ids[i], 1])
    plist[i][4] = 2

    # for performance in plist:
    #    print(performance)

    for perf in plist:
        c.execute("INSERT INTO performances(play_id, theatre_id, "
                  "review_id, user_id)"
                  "VALUES({0}, {1}, {2}, {3})"
                  .format(perf[1], perf[2], perf[3], perf[4]))
    db.commit()
    print(c.execute("SELECT * FROM performances;").fetchall())
    print()

    return plist


# question = ('\n\tInserting: {0} - Do you want to proceed? '
#             .format('PERFORMANCES'))
# yn = input(yellow.format(question))
plist = insert(yn, Performances)

db.close()
