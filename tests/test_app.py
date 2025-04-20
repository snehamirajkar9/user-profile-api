import unittest
import json
from app import app, db
from app.models import User  # ✅ Fix this line

class UserProfileAPITestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app = app.test_client()

        with app.app_context():
            db.create_all()
            user = User(username='user1', email='user1@example.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_user(self):
        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpassword"
        }
        response = self.app.post('/register', 
                               data=json.dumps(payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        payload = {
            "username": "user1",
            "password": "password"
        }
        response = self.app.post('/login',
                                data=json.dumps(payload),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', json.loads(response.data))

    def test_update_password(self):
        # First login to get token
        login_payload = {
            "username": "user1",
            "password": "password"
        }
        login_response = self.app.post('/login',
                                     data=json.dumps(login_payload),
                                     content_type='application/json')
        token = json.loads(login_response.data)['token']

        # Then update password
        update_payload = {
            "current_password": "password",
            "new_password": "newpassword"
        }
        response = self.app.post('/update_password',
                               data=json.dumps(update_payload),
                               content_type='application/json',
                               headers={'Authorization': token})
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
