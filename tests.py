from cgi import test
from unittest import TestCase
from server import app
from flask import session
from model import connect_to_db, db, example_data

class FlaskTests(TestCase):

    def setUp(self):
        """ To do before every test. """

        # get the Flask test client
        self.client = app.test_client()
        # show Flask errors that happen during tests
        app.config['TESTING' ] = True
        # set secret key if using sessions
        # app.config['SECRET_KEY'] = 'key'

    def test_login_page(self):
        """ Test login page. """

        result = self.client.get('/')
        self.assertIn(b'Login', result.data)


class FlaskDatabaseTests(TestCase):
    """ Flask tests that use the database. """

    def setUp(self):
        """ To do before every test."""

        # Get the Flask test client
        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

    def tearDown(self):
        """ Do at end of every test. """

        db.session.remove()
        db.drop_all()
        db.engine.dispose()

    def test_login(self):
        """ Test login form. """

        with self.client as c:
            result = c.post('/login', data = {'email': 'one@gmail.com', 'password': 'abc'},
                follow_redirects = True)
            # self.assertEqual(session['user_id'], 'one@gmail.com')
            self.assertIn(b'Welcome', result.data)





if __name__ == "__main__":
    import unittest

    unittest.main()
