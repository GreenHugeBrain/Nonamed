from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import Flask, render_template, redirect, request, flash, url_for
from app import app, db
from models import User, Post, Comment, Friendship, Message
from forms import RegisterForm, LoginForm, PostForm, CommentForm
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from ext import login_manager
from PIL import Image
import os

socketio = SocketIO(app, cors_allowed_origins="*")


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


@app.route('/add_friend/<username>', methods=['POST'])
@login_required
def add_friend(username):
    comment_form = CommentForm()
    user_to_add = User.query.filter_by(username=username).first()
    is_friend = False
    
    if user_to_add is None:
        flash('User not found.', 'danger')
        return redirect(url_for('home'))
    
    # Check if the current user is already friends with the user_to_add
    if current_user.is_friend(user_to_add):
        flash('You are already friends with this user.', 'info')
        return redirect(url_for('profile', username=username))
    
    # Add the current user as a friend to the user_to_add
    new_friend_for_user_to_add = Friendship(username=user_to_add.username, friend_id=current_user.id, img=user_to_add.img)
    db.session.add(new_friend_for_user_to_add)
    
    # Add the user_to_add as a friend to the current user
    new_friend_for_current_user = Friendship(username=current_user.username, friend_id=user_to_add.id, img=current_user.img)
    db.session.add(new_friend_for_current_user)
    
    db.session.commit()
    is_friend = True
    posts = Post.query.filter_by(username=user_to_add.username).all()
    
    return render_template('profile.html', user=user_to_add, posts=posts, comment_form=comment_form, is_friend=is_friend)




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


@app.route('/chat/<username>', methods=['GET', 'POST'])
@login_required
def chat_with_user(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('home'))

    if request.method == "POST":
        content = request.form.get('message')
        if content:
            new_message = Message(
                sender_username=current_user.username,
                receiver_username=username,
                content=content
            )
            db.session.add(new_message)
            db.session.commit()
            emit('new_message', {'sender': current_user.username, 'content': content}, room=username)
            return redirect(url_for('chat_with_user', username=username))

    messages = Message.query.filter(
        ((Message.sender_username == current_user.username) & (Message.receiver_username == username)) |
        ((Message.sender_username == username) & (Message.receiver_username == current_user.username))
    ).order_by(Message.timestamp.asc()).all()

    return render_template('chat_with_user.html', user=user, messages=messages)

@app.route('/chats')
@login_required
def chats():
    friends = Friendship.query.filter_by(username=current_user.username).all()
    recent_chats = []

    for friend in friends:
        recent_message = Message.query.filter(
            ((Message.sender_username == current_user.username) & (Message.receiver_username == friend.get_friend_username())) |
            ((Message.sender_username == friend.get_friend_username()) & (Message.receiver_username == current_user.username))
        ).order_by(Message.timestamp.desc()).first()
        recent_chats.append((friend.get_friend_username(), recent_message))

    return render_template('chats.html', recent_chats=recent_chats)


@socketio.on('connect')
def handle_connect():
    join_room(current_user.username)

@socketio.on('disconnect')
def handle_disconnect():
    leave_room(current_user.username)

@socketio.on('send_message')
def handle_send_message(data):
    receiver = data['receiver']
    content = data['content']
    new_message = Message(
        sender_username=current_user.username,
        receiver_username=receiver,
        content=content
    )
    db.session.add(new_message)
    db.session.commit()
    emit('new_message', {'sender': current_user.username, 'content': content}, room=receiver)