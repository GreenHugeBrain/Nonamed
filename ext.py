from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required

db = SQLAlchemy()
login_manager = LoginManager()
