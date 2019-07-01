#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3


db = sqlite3.connect('../hamnet.db')


def deleteTable(table):
    c = db.cursor()
    c.execute("DELETE FROM '{0}';".format(table))
    db.commit()


tables = ['genres', 'plays', 'user',  'cities', 'flask_dance_oauth',
          'reviews', 'theatres', 'performances']

yellow = '\033[0;33;40m{0}\033[0m'
yn = input(yellow.format("\nDo you want to delete the 9 tables? (y/n) "))
if yn.lower() == 'y':
    print("\nDeleting the contents of \nthe following table(s): ")
    for table in tables:
        print("\t\t\t {0}".format(table))
        deleteTable(table)
else:
    print("Goodbye!")

print()
db.close()
