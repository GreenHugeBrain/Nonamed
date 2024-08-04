from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired

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
    title = StringField('სათაური')
    content = TextAreaField('კონტენტი')
    user_image = FileField('Image (Optional)', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    image = FileField('ფოტო', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    keywords = StringField('საკვანძო სიტყვები')
    submit = SubmitField('დამატება')

class CommentForm(FlaskForm):
    post_id = IntegerField('Post ID', validators=[DataRequired()])
    comment = TextAreaField('კომენტარი', validators=[DataRequired()])    
    image = FileField('Image') 
    submit = SubmitField('კომენტარის დამატება')

