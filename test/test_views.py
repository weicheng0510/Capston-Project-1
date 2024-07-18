"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py

import os
from unittest import TestCase
from models import db, connect_db, User, Bookmark, Comment
from bs4 import BeautifulSoup

os.environ['DATABASE_URL'] = "postgresql:///fooddy-test"

from app import app, CURR_USER_KEY

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False

class ViewTestCase(TestCase):

    def setUp(self):
        """Create test client, add sample data."""
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup("testuser", "testuser")
        self.testuser_id = 1111
        self.testuser.id = self.testuser_id
        
        self.u1 = User.signup("abc", "password")
        self.u1_id = 778
        self.u1.id = self.u1_id
        
        db.session.commit()

        self.testcomment = Comment(recipe_id=12345, recipe_title='Hearty Cavolo Nero, Borlotti Bean And Smoked Bacon Soup', user_id=self.testuser_id, text='testing')
        db.session.add(self.testcomment)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_homepage(self):
        """Test homepage"""
        with self.client as c:
            resp = c.get("/")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Picks for you", resp.data)
            self.assertIn(b'Search Recipe', resp.data)

    def test_signup(self):
        """Test user signup"""
        with self.client as c:
            resp = c.post("/signup", data={
                "username": "newuser",
                "password": "newpassword"
            }, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            user = User.query.filter_by(username="newuser").first()
            self.assertIsNotNone(user)
            self.assertIn(b"newuser", resp.data)

    def test_login(self):
        """Test user login"""
        with self.client as c:
            resp = c.post("/login", data={
                "username": "testuser",
                "password": "testuser"
            }, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Hello, testuser!", resp.data)

    def test_logout(self):
        """Test user logout"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get("/logout", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"You have successfully logged out.", resp.data)

    def test_search_recipes(self):
        """Test recipe search functionality"""
        with self.client as c:
            resp = c.get("/search?q=pasta")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Click to see the full recipe.", resp.data)
    
    def test_recipe_detail(self):
        """Test recipe detail page"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            resp = c.get("/recipe/12345")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Hearty Cavolo Nero, Borlotti Bean And Smoked Bacon Soup", resp.data)
            self.assertIn(b'bookmark', resp.data)
            self.assertIn(b'Ingredients for 1 servings', resp.data)
            self.assertIn(b'testing', resp.data)

    def test_add_bookmark(self):
        """Test adding a bookmark"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post("/recipe/12345/bookmark", data={"recipe_title": "Test Recipe"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            bookmark = Bookmark.query.filter_by(user_id=self.testuser_id, recipe_id=12345).first()
            self.assertIsNotNone(bookmark)
            self.assertIn(b'Added to bookmarks', resp.data)

    def test_remove_bookmark(self):
        """Test removing a bookmark"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            # First, add a bookmark to remove
            bookmark = Bookmark(user_id=self.testuser_id, recipe_id=12345, recipe_title="Test Recipe")
            db.session.add(bookmark)
            db.session.commit()

            resp = c.post("/recipe/12345/bookmark", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            bookmark = Bookmark.query.filter_by(user_id=self.testuser_id, recipe_id=12345).first()
            self.assertIsNone(bookmark)
            self.assertIn(b'Remove from bookmarks', resp.data)

    def test_delete_comment(self):
        """Test deleting a comment"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post(f"/comment/{self.testcomment.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            comment = Comment.query.get(self.testcomment.id)
            self.assertIsNone(comment)
            self.assertIn(b'Comment Removed', resp.data)

    def test_edit_comment(self):
        """Test editing a comment"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post(f"/comment/{self.testcomment.id}/edit", data={"text": "Updated Comment"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            updated_comment = Comment.query.get(self.testcomment.id)
            self.assertIsNotNone(updated_comment)
            self.assertEqual(updated_comment.text, "Updated Comment")