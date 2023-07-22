from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/user/<name>')
def user(name):
    return f"<h1>Hello {name}</h1>"
