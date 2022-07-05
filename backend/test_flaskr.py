import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from settings import (
    database_name,
    database_username,
    database_password
)


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = database_name
        self.database_username= database_username
        self.database_password = database_password
        # self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        self.database_path = 'postgresql://{}:{}@{}/{}'.format(
            self.database_username, self.database_password,'localhost:5432', self.database_name
            )    

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

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['total'])

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['current_category'])  

    def test_404_category_questions_not_found(self):
        res = self.client().get('/categories/1000/questions')   
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)    

    def test_delete_question(self):
        res = self.client().delete('/questions/6')
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question_id'], 6)
        self.assertEqual(res.status_code, 200)

    def test_422_delete_question_unprocessable(self):
        res = self.client().delete('/questions/250')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)    

    def test_create_question(self):
        new_question = {
            'question': 'What is your hobby',
            'answer': 'Coding',
            'category': 1,
            'difficulty': 3,
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_search_questions(self):
        search_term = {'searchTerm': 'first'}
        res = self.client().post('/questions/search', json=search_term)
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))   



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()