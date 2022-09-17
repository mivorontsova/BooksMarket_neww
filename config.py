from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'xf3g82g27f9cdv443ui480nw'
login = LoginManager(app)
login.login_view = 'login'
app.config['SECRET_KEY'] = 'xf3g82g27f9cdv443ui480nw'
MAX_CONTENT_LENGTH = 1024 * 1024
generate_password_hash = generate_password_hash
check_password_hash = check_password_hash


