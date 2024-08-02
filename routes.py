from flask import render_template, redirect, request, flash, url_for
from app import app, db
from models import User, Post, Comment
from forms import RegisterForm, LoginForm, PostForm, CommentForm
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from ext import login_manager
from PIL import Image
import os

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
            new_comment = Comment(username=current_user.username, content=comment_form.comment.data, post_id=comment_form.post_id.data, image=current_user.img)
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
        image_file = None
        if form.image.data:
            image_file = secure_filename(form.image.data.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file)
            form.image.data.save(file_path)
            image = Image.open(file_path)
            image = image.convert('RGB')
            webp_filename = f"{os.path.splitext(image_file)[0]}.webp"
            webp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], webp_filename)
            image.save(webp_file_path, 'webp', optimize=True, quality=10)
            image_file = webp_filename

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
        image_file = 'default.jpg'
        
        if form.img.data:
            image_file = secure_filename(form.img.data.filename)
            original_file_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file)
            form.img.data.save(original_file_path)
            
            # Convert the image to WebP format
            with Image.open(original_file_path) as image:
                image = image.convert('RGB')
                webp_filename = f"{os.path.splitext(image_file)[0]}.webp"
                webp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], webp_filename)
                image.save(webp_file_path, 'webp', optimize=True, quality=10)
                
                # Optionally, remove the original image file if not needed
                os.remove(original_file_path)
                
                image_file = webp_filename

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
        # Populate form fields with existing post data
        form.title.data = post.title
        form.content.data = post.content
        form.keywords.data = post.keywords

    if form.validate_on_submit():
        # Update fields only if new data is provided
        if form.title.data:
            post.title = form.title.data
        
        if form.content.data:
            post.content = form.content.data
        
        if form.keywords.data:
            post.keywords = form.keywords.data
        
        # Handle the image update
        if form.image.data:
            # Delete the old image if it exists
            if post.image_file:
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], post.image_file)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
                    
            # Save the new image
            image_file = secure_filename(form.image.data.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file)
            form.image.data.save(file_path)
            image = Image.open(file_path)
            image = image.convert('RGB')
            webp_filename = f"{os.path.splitext(image_file)[0]}.webp"
            webp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], webp_filename)
            image.save(webp_file_path, 'webp', optimize=True, quality=10)
            post.image_file = webp_filename

        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect('/')
    
    return render_template('edit_post.html', form=form, post=post)


@app.route('/profile/<username>')
@login_required
def profile(username):
    comment_form = CommentForm()
    user = User.query.filter_by(username=username).first()  # Get the user by username
    if user is None:
        flash('User not found.', 'danger')
        return redirect(url_for('home'))
    posts = Post.query.filter_by(username=user.username).all()
    return render_template('profile.html', user=user, posts=posts, comment_form=comment_form)






@app.route("/delete_post/<int:id>", methods=["POST"])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if post.username == current_user.username:
        if post.image_file:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], post.image_file)
            if os.path.exists(image_path):
                os.remove(image_path)
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted successfully!", "success")
    else:
        flash("You are not authorized to delete this post.", "danger")
    return redirect('/')


@app.route('/search/<string:name>', methods=['GET', 'POST'])
def search(name):
    comment_form = CommentForm()
    posts = Post.query.filter(Post.keywords.ilike(f"%{name}%")).all()

    return render_template('search_results.html', posts=posts, comment_form=comment_form)

@app.route("/post/<int:post_id>")
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)


