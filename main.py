from websforms import LoginForm, PostForm, UserForm, NamerForm, PasswordForm, SearchForm
from models import *
from werkzeug.utils import secure_filename
import uuid as uuid
import os

#Home page
@app.route('/')
def index():
    return render_template("index.html")

#Custome Error Page
#Invalid URL error
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

#Internal server error error
@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500

#Sign-in
@app.route("/user/add", methods=["GET", "POST"])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256") # we hash the password before send it to db
            user = Users(username=form.username.data ,name=form.name.data, email=form.email.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
            #flash("Form Submitted Successfully.") #To show a message at top after submiting and entering
            return redirect("/login")
        else:
            flash("User with this email exsist.") 
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.password_hash.data = ''

    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", form=form, name=name, our_users=our_users)

#List of Users
@app.route("/list")
def users_list():
    form = UserForm()
    our_users = Users.query.order_by(Users.date_added)
    flash("Form Submitted Successfully.") #To show a message at top after submiting and entering
    return render_template("users_list.html", form=form, our_users=our_users)

#Update User
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form["name"]
        name_to_update.username = request.form["username"]
        name_to_update.email = request.form["email"]
        name_to_update.about = request.form["about"]
        
        if request.files["profile_pic"]:
            name_to_update.profile_pic = request.files["profile_pic"]

            pic_filename = secure_filename(name_to_update.profile_pic.filename)
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            #save pic to images
            name_to_update.profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'],pic_name))
            name_to_update.profile_pic = pic_name
            try:
                db.session.commit()
                flash("User information updated successfully.")
                return redirect(url_for("dashboard"))
                #return render_template("update.html", form=form, name_to_update=name_to_update, id=id)
            except:
                db.session.commit()
                flash("Something went wrong.Try again later.")
                return render_template("update.html", form=form, name_to_update=name_to_update, id=id)
        else:
            db.session.commit()
            flash("User information updated successfully.")
            return redirect(url_for("dashboard"))

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

@app.route("/delete_pic/<int:id>")
def delete_pic(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()

    try:
        db.session.delete(user_to_delete.profile_pic)
        db.session.commit()
        flash("Profile Picture Deleted Succussfully.")

        return render_template("dashboard.html") 
    except:
        flash("Something went wrong.Try again.")
        return render_template("dashboard.html") 

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                return redirect(url_for("dashboard"))
            else:
                flash("Password is wrong. Try again.")
        else:
            flash("Username is wrong. Try again.")
    form.username.data = ''

    return render_template("login.html", form=form) 

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You has been logged out.")
    return redirect(url_for("login"))

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    form = LoginForm()
    flash("Logged in Successfully.")
    return render_template("dashboard.html") 

@app.route("/add-post", methods=["GET", "POST"])
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data, content=form.content.data, poster_id=poster, slug=form.slug.data)

        form.title.data = ''
        form.content.data = ''
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
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    id = current_user.id

    if id == post.poster.id or current_user.username == "admin":
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            post.slug = form.slug.data

            db.session.add(post)
            db.session.commit()
            flash("Post has been Updated.")
            return redirect(url_for("post", id=post.id))
        form.title.data = post.title
        form.content.data = post.content
        form.slug.data = post.slug

        return render_template("edit_post.html", form=form)
    else:
        flash("You are not authorized to edit this post.")
        posts = Posts.query.order_by(Posts.date_posted)

        return render_template("posts.html", posts=posts)

@app.route("/posts/delete/<int:id>")
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id

    if id == post_to_delete.poster.id or current_user.username == "admin":
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
    else:
        flash("You are not authorized to delete this post.")
        posts = Posts.query.order_by(Posts.date_posted)

        return render_template("posts.html", posts=posts)

@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

@app.route("/search", methods=['POST'])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        post.searched = form.searched.data

        posts = posts.filter(
            or_(
                Posts.content.like('%' + post.searched + '%'),
                Posts.author.like('%' + post.searched + '%'),
                Posts.title.like('%' + post.searched + '%')
            )
        )
        posts = posts.order_by(Posts.title).all()
        

        return render_template("search.html", form=form, searched=post.searched, posts=posts)

@app.route("/admin")
@login_required
def admin():
    return render_template("admin.html")