import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin


app = Flask(__name__)

class Config(object):
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    SESSION_TYPE="sqlalchemy"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FACEBOOK_OAUTH_CLIENT_ID = os.environ.get("FACEBOOK_OAUTH_CLIENT_ID")
    FACEBOOK_OAUTH_CLIENT_SECRET = os.environ.get("FACEBOOK_OAUTH_CLIENT_SECRET")
    APPLICATTION_NAME="hamnet"

app.config.from_object(Config)
db = SQLAlchemy(app)



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True)


class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(User)


class Genres(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(10), nullable=False)


class Plays(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    genres = db.relationship(Genres)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))
    written_in = db.Column(db.Integer)
    quote = db.Column(db.String(200))
    picpath = db.Column(db.String(100))


class Reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review_title = db.Column(db.String(100), nullable=False)
    performance_date = db.Column(db.Date)
    review_link = db.Column(db.String(500))
    user = db.relationship(User)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Cities(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(30))


class Theatres(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    theatre_name = db.Column(db.String(40), nullable=False)
    city = db.relationship(Cities)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))
    address = db.Column(db.String(300))
    webpage = db.Column(db.String(500))
    user = db.relationship(User)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Performances(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plays = db.relationship(Plays)
    play_id = db.Column(db.Integer, db.ForeignKey('plays.id'))
    theatres = db.relationship(Theatres)
    theatre_id = db.Column(db.Integer, db.ForeignKey('theatres.id'))
    reviews = db.relationship(Reviews)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'))
    user = db.relationship(User)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# setup login manager
login_manager = LoginManager()
login_manager.login_view = "facebook.login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
