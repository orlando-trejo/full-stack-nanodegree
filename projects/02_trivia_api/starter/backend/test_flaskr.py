import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.user = "postgres"
        self.password = "udacity"
        self.database_path = "postgresql://{}:{}@{}/{}".format(self.user, self.password, 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_all_categories(self):
        res = self.client().get('/categories')
        self.assertEqual(res.status_code, 200)  # Check status code first
    
        data_str = res.data.decode('utf-8')  # Decode from bytes to str if necessary
    
        if data_str:
            try:
                data = json.loads(data_str)
            except json.JSONDecodeError:
                self.fail("Invalid JSON response")
        else:
            self.fail("Response data is empty")
    
        self.assertTrue(data['success'])
        self.assertTrue(len(data['categories']))

    def test_get_all_questions(self):
        res = self.client().get('/questions')
        self.assertEqual(res.status_code, 200)

        data_str = res.data.decode('utf-8')  # Decode from bytes to str if necessary
    
        if data_str:
            try:
                data = json.loads(data_str)
            except json.JSONDecodeError:
                self.fail("Invalid JSON response")
        else:
            self.fail("Response data is empty")
    
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']))
        self.assertIn('questions', data)



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()