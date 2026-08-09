import unittest
from app import create_app
from models import db
from models.user import User
from models.job_role import JobRole
from services.fallback_evaluator import FallbackEvaluator

class InterviewTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_fallback_evaluator(self):
        q_text = "Explain how Flask application routes and request context work."
        ans_text = "Flask uses decorators like @app.route to map URLs to view functions. It manages context using thread-local request and application objects, allowing clean access to request headers, arguments, and session data."
        
        eval_res = FallbackEvaluator.evaluate_answer(q_text, ans_text, target_skill="Flask")
        
        self.assertGreaterEqual(eval_res["overall_score"], 60.0)
        self.assertIn("relevance_score", eval_res)
        self.assertTrue(eval_res["is_demo_mode"])

    def test_interview_creation_flow(self):
        # Register User
        self.client.post('/register', data={
            'name': 'Candidate',
            'email': 'candidate@test.com',
            'password': 'Password123',
            'confirm_password': 'Password123'
        })
        self.client.post('/login', data={'email': 'candidate@test.com', 'password': 'Password123'})

        # Start Interview
        res = self.client.post('/start-interview', data={'role_id': 1}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

if __name__ == '__main__':
    unittest.main()
