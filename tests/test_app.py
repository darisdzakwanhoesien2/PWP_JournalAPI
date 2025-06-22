import unittest
from src.app import create_app

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_login_missing_username(self):
        response = self.client.post('/login', json={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('msg', data)
        self.assertEqual(data['msg'], 'Missing username parameter')

    def test_login_success(self):
        response = self.client.post('/login', json={'username': 'testuser'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('access_token', data)

if __name__ == '__main__':
    unittest.main()
