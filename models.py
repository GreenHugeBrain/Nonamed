from datetime import datetime
from app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    date_registered = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    password = db.Column(db.String(120), nullable=False)
    img = db.Column(db.String, nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    user_image = db.Column(db.String(80), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(), nullable=False)
    image_file = db.Column(db.String(120), nullable=True)
    keywords = db.Column(db.String(200), nullable=True)
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    image = db.Column(db.String(), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)


