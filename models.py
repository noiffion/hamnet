# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()


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

