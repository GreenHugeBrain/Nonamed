from datetime import datetime
from app import db
from flask_login import UserMixin

# Association table for many-to-many relationship
friends_association = db.Table('friends_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    date_registered = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    password = db.Column(db.String(120), nullable=False)
    friend_of = db.relationship('Friendship', backref='user')
    img = db.Column(db.String, nullable=False)

    def is_friend(self, other_user):
        friendship = Friendship.query.filter_by(
            username=self.username,
            friend_id=other_user.id
        ).first()
        return friendship is not None

class Friendship(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    img = db.Column(db.String, nullable=False)

    def get_friend_username(self):
        friend = User.query.get(self.friend_id)
        return friend.username if friend else None    
        

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_username = db.Column(db.String(150), nullable=False)
    receiver_username = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Message {self.id} from {self.sender_username} to {self.receiver_username}>'

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


