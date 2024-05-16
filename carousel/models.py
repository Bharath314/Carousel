from flask_sqlalchemy import SQLAlchemy
from flask import current_app 
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    display_picture = db.Column(
        db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(40), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.display_picture}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow())
    image_file = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.caption}', '{self.image_file}, '{self.date_posted}')"


class Followers(db.Model):
    followed_id = db.Column(db.Integer, primary_key=True, nullable=False)
    follower_id = db.Column(db.Integer, primary_key=True, nullable=False)



    # current_user = carousel_user()
