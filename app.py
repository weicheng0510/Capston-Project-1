import os
from flask import Flask, render_template, request, flash, redirect, session, g
from models import db, connect_db, User, Bookmark, Comment
from forms import UserForm, CommentForm
from sqlalchemy.exc import IntegrityError
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('SUPABASE_DB_URL', 'postgresql:///fooddy_db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY',"key")

connect_db(app)

CURR_USER_KEY = "curr_user"
API_KEY = os.environ.get('API_KEY')

with app.app_context():
    db.create_all()

##############################################################################
# Homepage and error pages

@app.route('/')
def homepage():
    res = requests.get('https://api.spoonacular.com/recipes/random', params={'apiKey':API_KEY, 'number':4})
    data = res.json()
    return render_template('home.html', recipes = data)


@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404


##############################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]



@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.
    Create new user and add to DB. Redirect to home page.
    If form not valid, present form.
    If already has a user with that username: flash message and re-present form.
    """
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
            )
            db.session.commit()

        except IntegrityError as e:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)
    

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = UserForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("You have successfully logged out.", 'success')
    return redirect("/login")


##############################################################################
# Recipes


@app.route('/search')
def search_recipes():
    """show search recipes"""
    q = request.args.get('q')
    page = request.args.get('page',1, type=int)
    offset = (page - 1) * 10
    res = requests.get('https://api.spoonacular.com/recipes/complexSearch', params={'apiKey':API_KEY, 'query':q, 'offset':offset, 'number':10})
    data = res.json()
    results = data['results']
    total_pages = (data['totalResults'] + 9) // 10 
    return render_template('/recipes/recipes.html', recipes = results, q = q, page = page, total_pages = total_pages)


@app.route('/recipe/<int:id>', methods=['GET', 'POST'])
def recipe_detail(id):
    """show recipe detail and handle comment posting"""

    res = requests.get(f'https://api.spoonacular.com/recipes/{id}/information', params={'apiKey': API_KEY})
    data = res.json()

    form = CommentForm()

    if form.validate_on_submit() and g.user:
        text = form.text.data
        recipe_title = data['title']
        new_comment = Comment(recipe_id=id, recipe_title=recipe_title, user_id=g.user.id, text=text)
        db.session.add(new_comment)
        db.session.commit()
        flash("Comment added.", "success")
        return redirect(f'/recipe/{id}')

    comments = Comment.query.filter_by(recipe_id=id).order_by(Comment.timestamp.desc()).all()

    if g.user:
        bookmarks = [bookmark.recipe_id for bookmark in g.user.bookmarks]
        return render_template('/recipes/recipe_detail.html', recipe=data, bookmarks=bookmarks, comments=comments, form=form)
    
    return render_template('/recipes/recipe_detail.html', recipe=data, comments=comments, form=form)


@app.route('/recipe/<int:id>/bookmark', methods = ['POST'])
def recipe_bookmark(id):
    """bookmark or remove bookmark"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/login")
    
    bookmark = Bookmark.query.filter_by(user_id = g.user.id, recipe_id = id).first()
    
    if bookmark:
        db.session.delete(bookmark)
        db.session.commit()
        flash('Remove from bookmarks', 'success')
    else:
        recipe_title = request.form.get('recipe_title')
        new_bookmark = Bookmark(user_id = g.user.id, recipe_id = id, recipe_title = recipe_title)
        db.session.add(new_bookmark)
        db.session.commit()
        flash('Added to bookmarks', 'success')

    return redirect(f'/recipe/{id}')


@app.route('/bookmark/<int:id>/delete', methods = ['POST'])
def bookmark_remove(id):
    """remove bookmark"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/login")
    
    bookmark = Bookmark.query.get_or_404(id)
    db.session.delete(bookmark)
    db.session.commit()
    flash('Remove from bookmarks', 'success')

    return redirect(f'/user/{g.user.id}')



##############################################################################
# user profile

@app.route('/user/<int:id>')
def show_profile(id):
    """profile page with user post comments and list of bookmark recipe"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/login")
    
    bookmarks = g.user.bookmarks
    comments = g.user.comments

    return render_template('/users/user.html', bookmarks = bookmarks, comments = comments, user = g.user)


@app.route('/user/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")

##############################################################################
# comment


@app.route('/comment/<int:id>/delete', methods=['POST'])
def delete_comment(id):
    """remove comment"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/login")

    comment = Comment.query.get_or_404(id)
    if comment.user_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    db.session.delete(comment)
    db.session.commit()
    flash('Comment Removed', 'success')
    return redirect(f'/user/{g.user.id}')

@app.route('/comment/<int:id>/edit', methods=['GET','POST'])
def edit_comment(id):
    """edit comment"""
    
    comment = Comment.query.get_or_404(id)
    form = CommentForm(obj=comment)
    recipe_id = comment.recipe_id
    
    res = requests.get(f'https://api.spoonacular.com/recipes/{recipe_id}/information', params={'apiKey': API_KEY})
    data = res.json()

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/login")
    
    if comment.user_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    if form.validate_on_submit():
        comment.text = form.text.data
        db.session.commit()
        return redirect(f'/user/{g.user.id}')
    
    
    return render_template('/users/comment_edit.html', recipe=data, form=form, comment = comment)

