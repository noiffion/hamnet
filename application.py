# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import httplib2, json, requests, random, string  # httplib2 should be checked out
from flask import (Flask, render_template, request, redirect, jsonify, url_for,
        flash, session as login_session, make_response)
from sqlalchemy import create_engine, asc 
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, Genres, Plays, Users, Dramalist
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError


app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())\
        ['web']['client_id']  # json should be obtained from google
APPLICATION_NAME =  # "Placeholder"

engine = create_engine('sqlite:///hamnet.db')
Base.metadata.bind = engine
session = scoped_session(sessionmaker(autocommit=False, 
                                      autoflush=False, 
                                      bind=engine))

