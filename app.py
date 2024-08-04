from flask import Flask
from ext import db, login_manager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'QDASFIJF89F89234FH89WHG34G89H3489GH'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db.init_app(app)
login_manager.init_app(app)

from routes import *
if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=2018, debug=True)


