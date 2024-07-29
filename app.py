from flask import Flask, render_template, redirect, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user, UserMixin, login_required, logout_user
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'QDASFIJF89F89234FH89WHG34G89H3489GH'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()])
    image = FileField('Image (Optional)', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    submit = SubmitField('Submit')

class CommentForm(FlaskForm):
    post_id = IntegerField('Post ID', validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[DataRequired()])    
    submit = SubmitField('Submit Comment')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(), nullable=False)
    image_file = db.Column(db.String(120), nullable=True)  # New column for image file path
    comments = db.relationship('Comment', backref='post', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/", methods=["GET", "POST"])
def home():
    posts = Post.query.all()[::-1]
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        new_comment = Comment(username=current_user.username, content=comment_form.comment.data, post_id=comment_form.post_id.data)
        db.session.add(new_comment)
        db.session.commit()
        return redirect("/")
    return render_template("index.html", posts=posts, comment_form=comment_form)

@app.route("/add_post", methods=["POST", "GET"])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        image_file = None
        if form.image.data:
            image_file = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], image_file))
        
        new_post = Post(username=current_user.username, title=form.title.data, content=form.content.data, image_file=image_file)
        db.session.add(new_post)
        db.session.commit()
        return redirect("/")
    return render_template("addpost.html", form=form)

@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return "User registered successfully!"
    return render_template("register.html", form=form)

@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect('/')
        else:
            return "Invalid username or password"
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    with app.app_context():
        db.create_all()
    app.run(debug=True)
