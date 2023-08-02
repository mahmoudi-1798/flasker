from flask import Flask, render_template, flash, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

from dotenv import load_dotenv

#load the environmental variables from the .env file
load_dotenv()

app = Flask(__name__)
# sqlite database
#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

# Mysql database
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://kourosh:password@localhost/users"
app.config["SECRET_KEY"] = "my super secret key"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    age = db.Column(db.Integer)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, email, age):
        self.name = name
        self.email = email
        self.age = age

class UserForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    age = IntegerField("Age")
    submit = SubmitField("Submit")

#Form class, inherited from FlaskForm
class NamerForm(FlaskForm):
    name = StringField("Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

#Home page
@app.route('/')
def index():
    return render_template("index.html")

# User page
@app.route('/user/<name>')
def user(name):
    return render_template("user.html", name=name)

#Custome Error Page
#Invalid URL error
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

#Internal server error error
@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500

# Form page 
@app.route("/name", methods=["GET", "POST"])
def name():
    name = None
    form = NamerForm()
    #validate form 
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully.") #To show a message at top after submiting and entering
    return render_template("name.html", name=name, form=form)

@app.route("/user/add", methods=["GET", "POST"])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, email=form.email.data, age=form.age.data)
            db.session.add(user)
            db.session.commit()
            #flash("Form Submitted Successfully.") #To show a message at top after submiting and entering
            return redirect("/list")
        else:
            flash("User with this email exsist.") 
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.age.data = 0
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", form=form, name=name, our_users=our_users)

@app.route("/list")
def users_list():
    form = UserForm()
    our_users = Users.query.order_by(Users.date_added)
    flash("Form Submitted Successfully.") #To show a message at top after submiting and entering
    return render_template("users_list.html", form=form, our_users=our_users)

@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        name_to_update.age = request.form["age"]
        try:
            db.session.commit()
            flash("User information updated successfully.")
            return render_template("update.html", form=form, name_to_update=name_to_update, id=id)
        except:
            db.session.commit()
            flash("Something went wrong.Try again later.")
            return render_template("update.html", form=form, name_to_update=name_to_update, id=id)
    else:
        return render_template("update.html", form=form, name_to_update=name_to_update, id=id)

@app.route("/delete/<int:id>")
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Succussfully.")

        our_users = Users.query.order_by(Users.date_added)
        return render_template("users_list.html", form=form, name=name, our_users=our_users)
    except:
        flash("Something went wrong.Try again.")
        return render_template("users_list.html", form=form, name=name, our_users=our_users)
