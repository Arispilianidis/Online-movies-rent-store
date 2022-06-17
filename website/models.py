from enum import unique
from . import db
from flask_login import UserMixin
from datetime import datetime

# Many to many relationship
user_movie = db.Table('user_movie',
    db.Column('user_model_id',db.Integer,db.ForeignKey('user_model.id'), primary_key=True),
    db.Column('movie_model_id',db.Integer,db.ForeignKey('movie_model.id'),primary_key=True),
    db.Column('rent_date', db.DateTime(timezone=True), default=datetime.now()),
    db.Column('return_date', db.DateTime(timezone=True))
    )

class MovieModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False, unique=True)
    info = db.Column(db.String(1000))
    category = db.Column(db.String(50))
    
    def __repr__(self):
        return f"'Movie': '{self.title}'"

class UserModel(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(150))
    lname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    movies = db.relationship('MovieModel', secondary = user_movie, backref = 'buyers')

    def __repr__(self):
        return f" {self.fname} {self.lname}"

    

