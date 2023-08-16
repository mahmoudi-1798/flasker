from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from flask_ckeditor import CKEditor

#load the environmental variables from the .env file
#from dotenv import load_dotenv
#load_dotenv()

app = Flask(__name__)

ckeditor = CKEditor(app)

# Mysql database
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://kourosh:password@localhost/users"
app.config["SECRET_KEY"] = "my super secret key"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    password_hash = db.Column(db.String(128))

    posts = db.relationship("Posts", backref="poster")

    @property 
    def password(self):
        raise AttributeError("Password is not a readable attribute!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self,username, name, email, password_hash):
        self.username = username
        self.name = name
        self.email = email
        self.password_hash = password_hash

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    poster_id = db.Column(db.Integer, db.ForeignKey("users.id"))
