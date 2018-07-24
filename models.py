# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import create_engine

import random, string
from passlib.context import CryptContext
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, 
                         BadSignature, SignatureExpired)  # /home/Adat/edu/MOOC/Udacity/4__BackEnd/FSF/17/5pale


Base = declarative_base()

pwd_context = CryptContext(schemes=['pbkdf2_sha256', 'des_crypt'],
                           deprecated='auto')
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))

class Genres(Base):
    __tablename__ = 'genres'
    id = Column(Integer, primary_key = True)
    genre = Column(String(20))

    @property
    def serialize(self):
        return {'id': self.id,
                'genre': self.genre}


class Plays(Base):
    __tablename__ = 'plays'
    id = Column(Integer, primary_key = True)
    title = Column(String(50), nullable = False)
    genres = relationship(Genres)
    genre_id = Column(Integer, ForeignKey('genres.id'))
    written_in = Column(Integer)
    plot = Column(String(250), nullable = False)

    @property
    def serialize(self):
        return {'id': self.id,
                'title': self.title,
                'genre_id': self.genre_id,
                'written_in': self.written_in,
                'plot': self.plot}

        
class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True)
    username = Column(String(60), nullable = False)
    email = Column(String(50), nullable = False)
    photo = Column(String(50))
    password_hash = Column(String(64))
        
    def hash_password(self, password):
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(secret_key, expires_in = expiration)
        return s.dumps({'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            #Valid Token, but expired
            return None
        except BadSignature:
            #Invalid Token
            return None
        user_id = data['id']
        return user_id

    @property
    def serialize(self):
        return {'id': self.id,
                'username': self.username,
                'email': self.email,
                'photo': self.photo}


class Dramalist(Base):
    __tablename__ = 'dramalist'
    id = Column(Integer, primary_key = True)
    plays = relationship(Plays)
    play_id = Column(Integer, ForeignKey('plays.id'))
    in_theatre = Column(String(100), nullable = False)
    when = Column(Date)
    users = relationship(Users)
    user_id = Column(Integer, ForeignKey('users.id'))

    @property
    def serialize(self):
        return {'id': self.id,
                'play_id': self.play_id,
                'in_theatre': self.in_theatre,
                'when': self.when,
                'user_id': self.user_id}


engine = create_engine('sqlite:///hamnet.db')
 
Base.metadata.create_all(engine)

