## The plays of Shakespeare

  These pages contain all the plays of Shakespeare (36 dramas published in the First Folio in 1623)
and three more works of the poet. The focus of the webpage is to list the (mainly) theatrical 
renditions of the plays: their dates of performance, their reviews and the venues where they were 
presented. The information about the performances (theatres, reviews, the details of the 39 plays, 
and all the related data is stored in a database (hamnet.db - an sqlite3 database containing 9 
tables.) The Flask web framework is used for rendering the pages in Python. Javascript is used a few
times on the client side. Linux (Lubuntu 18.04) was the system of development and Chromium is the 
development browser.


#### Program files and required software 

  The database schema is created by the models.py file: its output is the above mentioned 
hamnet.db sqlite3 database. The initial content of the database can be generated by running 
the insert_DB.py program, and it can be deleted by running the delete_DB.py file, this way
the database can be erased and the initial db can be set up with running these two programs. 
Both of these are in the DB folder.

  The login procedure is coded in the authoriz.py file, this module is imported in the main
application.py file. The html templates needed (with the embedded Javascript code) are in 
the templates folder. If the JS code needed to work with variables received from Flask they
could not be called from an outside js file. Every python file (application.py, models.py, 
authoriz.py, insert_DB.py, delete_DB.py) is PEP8 compliant (tested by pycodestyle).
Although SQLAlchemy is used, the somewhat more complex SQL queries were written in 'native' SQL
and can be found in three text files in the 'DB/Queries' folder. 

  The following programs needed to be installed to run the server (application.py) file and
browse the pages:
 - Python 3
 - SQLite 3

with pip3:
 - Flask (1.0.2)
 - google-auth (1.5.0) and google-auth-oauthlib (0.2.0)
 - SQLAlchemy (1.2.9)
 - urllib (1.23)

 
#### Running and using the webpage

  To run the server application one needs to run the application.py file with Python 3.
```
$ python3 application.py
```

  Then after typing the 'localhost:8000' in the address bar of the browser the webpage will be up 
and running. After navigating to the genre tablinks one can select a drama and clicking on the 
title take the user to the page dedicated to the performances of that play.

On initial setup the following plays have performance entries: Macbeth and Othello, 
Midsummer Night's Dream, III Richard, The Tempest. Macbeth has three from two different users.

If the user is not logged in the details of the performnaces are shown (without being able to edit 
the entries). If the user is logged in just the entries created by the user are shown and become
editable: a new one can be added, or existing ones can be deleted or edited. 
This process makes it sure that a user cannot delete or edit an entry that was not created by 
him/her. 

On the performances edit pages there is a link which takes the user to a page where the theatres
can be edited or deleted or new ones added. Every modification attempt requires authorization: 
without logging in a user cannot edit the entries meaning they cannot be modified by anyone other 
than the maker of the entry. Every update or addition will only take place after correctly filling
out the forms, and clicking on the submit button at the bottom of the form.

The login requires a valid Google or Facebook account (with these two I believe nearly 100% of the
users are covered). The status of the user (logged in or out is displayed in the footer on the 
main page and in the header on the 'inner' pages - the login links are right next to the status
info.

  The pages are intended to be responsive and tested on devices with screen sizes ranging from 
300px width to 1,500px.


#### License
MIT License (see attached LICENSE file)
