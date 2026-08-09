import unittest
from app import create_app
from models import db
from models.user import User

class AuthTestCase(unittest.TestCase):
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

    def test_registration_and_login(self):
        # Register User
        res = self.client.post('/register', data={
            'name': 'Test Engineer',
            'email': 'engineer@test.com',
            'password': 'Password123',
            'confirm_password': 'Password123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            user = User.query.filter_by(email='engineer@test.com').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.name, 'Test Engineer')

        # Login User
        res_login = self.client.post('/login', data={
            'email': 'engineer@test.com',
            'password': 'Password123'
        }, follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b'Welcome back', res_login.data)

        # Logout User
        res_logout = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(res_logout.status_code, 200)

if __name__ == '__main__':
    unittest.main()
