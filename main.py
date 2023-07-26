from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from dotenv import load_dotenv

#load the environmental variables from the .env file
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = "my super secret key"

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
    return render_template("user.html", user_name=name)

#Custome Error Page
#Invalid URL error
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

#Internal server error error
@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500

@app.route("/name", methods=["GET", "POST"])
def name():
    name = None
    form = NamerForm()
    #validate form 
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''

    return render_template("name.html", name=name, form=form)