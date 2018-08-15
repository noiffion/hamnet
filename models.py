# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, ForeignKey

Base = declarative_base()


class Genres(Base):
    __tablename__ = 'genres'
    id = Column(Integer, primary_key=True)
    genre = Column(String(10), nullable=False)

    @property
    def serialize(self):
        return {'id': self.id,
                'genre': self.genre}


class Plays(Base):
    __tablename__ = 'plays'
    id = Column(Integer, primary_key=True)
    title = Column(String(30), nullable=False)
    genres = relationship(Genres)
    genre_id = Column(Integer, ForeignKey('genres.id'))
    written_in = Column(Integer)
    quote = Column(String(200))
    picpath = Column(String(100))

    @property
    def serialize(self):
        return {'id': self.id,
                'title': self.title,
                'genre': self.genres.genre,
                'genre_id': self.genre_id,
                'written_in': self.written_in,
                'quote': self.quote}


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(60), nullable=False)
    email = Column(String(50), nullable=False)
    photo = Column(String(500))

    @property
    def serialize(self):
        return {'id': self.id,
                'username': self.username,
                'email': self.email,
                'photo': self.photo}


class Reviews(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    review_title = Column(String(100), nullable=False)
    performance_date = Column(Date)
    review_link = Column(String(500))
    users = relationship(Users)
    user_id = Column(Integer, ForeignKey('users.id'))

    @property
    def serialize(self):
        return {'id': self.id,
                'review_title': self.review_title,
                'performance_date': self.performance_date,
                'review_link': self.review_link,
                'user_id': self.user_id}


class Cities(Base):
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True)
    city_name = Column(String(30))

    @property
    def serialize(self):
        return {'id': self.id,
                'city_name': self.city_name}


class Theatres(Base):
    __tablename__ = 'theatres'
    id = Column(Integer, primary_key=True)
    theatre_name = Column(String(40), nullable=False)
    city = relationship(Cities)
    city_id = Column(Integer, ForeignKey('cities.id'))
    address = Column(String(300))
    webpage = Column(String(500))
    users = relationship(Users)
    user_id = Column(Integer, ForeignKey('users.id'))

    @property
    def serialize(self):
        return {'id': self.id,
                'theatre_name': self.theatre_name,
                'city': self.city.city_name,
                'city_id': self.city_id,
                'address': self.address,
                'webpage': self.webpage}


class Performances(Base):
    __tablename__ = 'performances'
    id = Column(Integer, primary_key=True)
    plays = relationship(Plays)
    play_id = Column(Integer, ForeignKey('plays.id'))
    theatres = relationship(Theatres)
    theatre_id = Column(Integer, ForeignKey('theatres.id'))
    reviews = relationship(Reviews)
    review_id = Column(Integer, ForeignKey('reviews.id'))
    users = relationship(Users)
    user_id = Column(Integer, ForeignKey('users.id'))

    @property
    def serialize(self):
        return {'id': self.id,
                'play_id': self.play_id,
                'play_title': self.plays.title,
                'theatre_id': self.theatre_id,
                'theatre': self.theatres.theatre_name,
                'review_id': self.review_id,
                'review': self.reviews.review_title,
                'user_id': self.user_id,
                'entry_made_by': self.users.username}


engine = create_engine('sqlite:///hamnet.db')

Base.metadata.create_all(engine)
