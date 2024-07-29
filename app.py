from flask import Flask, render_template, redirect, request, flash
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
    img = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    user_image = FileField('Image (Optional)', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    image = FileField('Image (Optional)', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    keywords = StringField('Keywords (Comma-separated)')
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
    img = db.Column(db.String, nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    user_image = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(), nullable=False)
    image_file = db.Column(db.String(120), nullable=True)
    keywords = db.Column(db.String(200), nullable=True)  # New column for keywords
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
    user = None
    if current_user.is_authenticated:
        user = User.query.filter_by(username=current_user.username).first()

    if comment_form.validate_on_submit():
        if current_user.is_authenticated:
            new_comment = Comment(username=current_user.username, content=comment_form.comment.data, post_id=comment_form.post_id.data)
            db.session.add(new_comment)
            db.session.commit()
            return redirect("/")
        else:
            flash("You must be logged in to post a comment.", "warning")

    user_is_true = any(post.username == current_user.username for post in posts) if current_user.is_authenticated else False

    return render_template("index.html", posts=posts, comment_form=comment_form, user=user, UserTrue=user_is_true)

@app.route("/add_post", methods=["POST", "GET"])
@login_required
def add_post():
    user = User.query.filter_by(username=current_user.username).first()
    form = PostForm()

    if form.validate_on_submit():
        print('Form is valid')
        image_file = None
        if form.image.data:
            image_file = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], image_file))
        
        new_post = Post(
            username=current_user.username,
            title=form.title.data,
            content=form.content.data,
            image_file=image_file,
            user_image=current_user.img,
            keywords=form.keywords.data
        )
        db.session.add(new_post)
        db.session.commit()
        flash('Post added successfully!', 'success')
        return redirect("/")
    else:
        flash('Form errors: ' + str(form.errors), 'error')
    return render_template("addpost.html", form=form, user=user)

@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        image_file = secure_filename(form.img.data.filename) if form.img.data else 'default.jpg'
        if form.img.data:
            form.img.data.save(os.path.join(app.config['UPLOAD_FOLDER'], image_file))

        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, img=image_file)
        db.session.add(new_user)
        db.session.commit()
        flash("User registered successfully!", "success")
        return redirect('/login')
    return render_template("register.html", form=form)

@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect('/')
        else:
            flash("Invalid username or password", "danger")
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect('/')

@app.route("/edit_post/<int:id>", methods=["POST", "GET"])
@login_required
def edit_post(id):
    form = PostForm()
    post = Post.query.get_or_404(id)
    
    if request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
        form.keywords.data = post.keywords 

    if form.validate_on_submit():
        print('1231312312')
        post.title = form.title.data
        post.content = form.content.data
        post.keywords = form.keywords.data  # Update keywords
        
        # Handle the new image if it's provided
        if form.image.data:
            # Delete the old image if it exists
            if post.image_file and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], post.image_file)):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post.image_file))
                
            # Save the new image
            image_file = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], image_file))
            post.image_file = image_file

        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect("/")

    return render_template('edit_post.html', form=form, post=post)

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=2018, debug=True)
