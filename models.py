"""SQLAlchemy models for Fooddy"""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

bcrypt = Bcrypt()
db = SQLAlchemy()



def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)



class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.Text, nullable = False, unique = True)
    password = db.Column(db.Text, nullable = False)

    bookmarks = db.relationship('Bookmark')
    comments = db.relationship('Comment')

    @classmethod
    def signup(cls, username, password):
        """Sign up user. Hashes password and adds user to system."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        user = User(username = username, password = hashed_pwd)
        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Find user with username and password and return user object. If not return False."""

        user = cls.query.filter_by(username = username).first()
        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        return False
    


class Bookmark(db.Model):
    """Mapping user bookmark"""

    __tablename__ = 'bookmarks'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete = 'cascade'))
    recipe_id = db.Column(db.Integer, nullable = False)
    recipe_title = db.Column(db.Text, nullable = False)

    user = db.relationship('User')



class Comment(db.Model):
    """Comments message for recipe."""

    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    recipe_id = db.Column(db.Integer, nullable = False)
    recipe_title = db.Column(db.Text, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete = 'cascade'))
    text = db.Column(db.String(500), nullable = False)
    timestamp = db.Column(db.DateTime, nullable = False, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User')