from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, PasswordField, BooleanField,TextAreaField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

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
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    password_hash = db.Column(db.String(128))

    @property 
    def password(self):
        raise AttributeError("Password is not a readable attribute!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, name, email, password_hash):
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

class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")


class UserForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo("password_hash2", message="Passwords doesn't match.")])
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

#Form class, inherited from FlaskForm
class NamerForm(FlaskForm):
    name = StringField("Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

class PasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
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
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256") # we hash the password before send it to db
            user = Users(name=form.name.data, email=form.email.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
            #flash("Form Submitted Successfully.") #To show a message at top after submiting and entering
            return redirect("/list")
        else:
            flash("User with this email exsist.") 
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.password_hash.data = ''

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

@app.route("/login", methods=["GET", "POST"])
def login():
    email = None
    password = None
    entered_pw = None
    passed = None

    form = PasswordForm()
    #validate form 
    if form.validate_on_submit(): 
        email = form.email.data
        password = form.password.data
        form.email.data = ''
        form.password.data = ''

        entered_pw = Users.query.filter_by(email=email).first()

        passed = check_password_hash(entered_pw.password_hash, password)
        if passed == True:
            flash("Login Successfully.")
            return redirect("/user/{}".format(email)) 

    return render_template("login.html", email=name, password=password, form=form)

@app.route("/add-post", methods=["GET", "POST"])
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)

        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''

        db.session.add(post)
        db.session.commit()

        flash("Blog Posted Successfully.")

    return render_template("add_post.html", form=form)

@app.route("/posts", methods=["GET", "POST"])
def posts():
    posts = Posts.query.order_by(Posts.date_posted)

    return render_template("posts.html", posts=posts)

@app.route("/posts/<int:id>")
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html", post=post)

@app.route("/posts/edit/<int:id>", methods=["GET", "POST"])
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data
        post.content = form.content.data
        post.slug = form.slug.data

        db.session.add(post)
        db.session.commit()
        flash("Post has been Updated.")
        return redirect(url_for("post", id=post.id))
    form.title.data = post.title
    form.author.data = post.author
    form.content.data = post.content
    form.slug.data = post.slug

    return render_template("edit_post.html", form=form)

@app.route("/posts/delete/<int:id>")
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
     
    try:
        db.session.delete(post_to_delete)
        db.session.commit()

        flash("Post has been deleted.")
        posts = Posts.query.order_by(Posts.date_posted)

        return render_template("posts.html", posts=posts)
    except:
        flash("There was a problem. Try again later.")

        posts = Posts.query.order_by(Posts.date_posted)

        return render_template("posts.html", posts=posts)