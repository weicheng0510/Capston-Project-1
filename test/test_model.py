"""User model tests."""
import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Bookmark, Comment

os.environ['DATABASE_URL'] = "postgresql:///fooddy-test"

from app import app



class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "password")
        uid1 = 1111
        u1.id = uid1

        db.session.commit()

        u1 = User.query.get(uid1)

        self.u1 = u1
        self.uid1 = uid1

        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


    def test_user_model(self):
        """Does basic model work?"""
        u = User(
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no bookmark & no comment
        self.assertEqual(len(u.bookmarks), 0)
        self.assertEqual(len(u.comments), 0)

    ####
    #
    # Bookmark tests
    #
    ####
    def test_user_bookmark(self):
        self.assertEqual(len(self.u1.bookmarks), 0)

        bookmark = Bookmark(
            user_id=self.u1.id,
            recipe_id=123,
            recipe_title='test1'
        )

        self.u1.bookmarks.append(bookmark)
        db.session.commit()

        self.assertEqual(len(self.u1.bookmarks), 1)
        self.assertEqual(self.u1.bookmarks[0].recipe_id, 123)
        self.assertEqual(self.u1.bookmarks[0].user_id, 1111)
        self.assertEqual(self.u1.bookmarks[0].recipe_title, 'test1')

    ####
    #
    # Signup tests
    #
    ####
    def test_valid_signup(self):
        u_test = User.signup("testtesttest", "password")
        uid = 99999
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, "testtesttest")
        self.assertNotEqual(u_test.password, "password")
        # Bcrypt strings should start with $2b$
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        invalid = User.signup(None, "password")
        uid = 123456789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError):
            db.session.commit()

    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError):
            User.signup("testtest", "")
        
        with self.assertRaises(ValueError):
            User.signup("testtest", None)

    ####
    #
    # Authentication tests
    #
    ####
    def test_valid_authentication(self):
        u = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid1)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "badpassword"))



    ####
    #
    # Coomment tests
    #
    ####
    def test_user_bookmark(self):
        self.assertEqual(len(self.u1.comments), 0)

        comment = Comment(
            user_id=self.u1.id,
            recipe_id=123,
            recipe_title='test1',
            text='test123'
        )

        self.u1.comments.append(comment)
        db.session.commit()

        self.assertEqual(len(self.u1.comments), 1)
        self.assertEqual(self.u1.comments[0].recipe_id, 123)
        self.assertEqual(self.u1.comments[0].user_id, 1111)
        self.assertEqual(self.u1.comments[0].recipe_title, 'test1')
        self.assertEqual(self.u1.comments[0].text, 'test123')