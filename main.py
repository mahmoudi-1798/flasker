from flask import Flask, render_template

app = Flask(__name__)

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