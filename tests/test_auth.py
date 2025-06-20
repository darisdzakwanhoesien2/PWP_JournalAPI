## current code
import unittest
import json
from src.app import create_app

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.testing = True

    def test_login_success(self):
        response = self.client.post('/login', json={'username': 'testuser'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('access_token', data)

    def test_login_missing_username(self):
        response = self.client.post('/login', json={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('msg', data)

if __name__ == '__main__':
    unittest.main()
