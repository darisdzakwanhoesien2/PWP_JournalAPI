import unittest
import json
from src.app import create_app

class UsersTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.testing = True
        # Clear users data before tests
        from src.data_store import save_users
        save_users([])
        # Register a user and get token for protected endpoints
        self.client.post('/users/register', json={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword'
        })
        login_resp = self.client.post('/login', json={'username': 'testuser'})
        self.token = login_resp.get_json()['access_token']
        self.auth_header = {'Authorization': f'Bearer {self.token}'}

    def test_register_user(self):
        response = self.client.post('/users/register', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword'
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['username'], 'newuser')
        self.assertEqual(data['email'], 'newuser@example.com')

    def test_register_missing_fields(self):
        response = self.client.post('/users/register', json={
            'username': 'useronly'
        })
        self.assertEqual(response.status_code, 400)

    def test_register_duplicate_username(self):
        response = self.client.post('/users/register', json={
            'username': 'testuser',
            'email': 'other@example.com'
        })
        self.assertEqual(response.status_code, 400)

    def test_register_duplicate_email(self):
        response = self.client.post('/users/register', json={
            'username': 'otheruser',
            'email': 'testuser@example.com'
        })
        self.assertEqual(response.status_code, 400)

    def test_get_users_unauthorized(self):
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 401)

    def test_get_users_authorized(self):
        response = self.client.get('/users', headers=self.auth_header)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('items', data)

    def test_update_user(self):
        # Get user id
        users_resp = self.client.get('/users', headers=self.auth_header)
        user_id = users_resp.get_json()['items'][0]['id']
        response = self.client.put(f'/users/{user_id}', json={
            'email': 'updated@example.com'
        }, headers=self.auth_header)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['email'], 'updated@example.com')

    def test_delete_user(self):
        # Register a user to delete
        reg_resp = self.client.post('/users/register', json={
            'username': 'tobedeleted',
            'email': 'tobedeleted@example.com',
            'password': 'testpassword'
        })
        user_id = reg_resp.get_json()['id']
        login_resp = self.client.post('/login', json={'username': 'tobedeleted'})
        token = login_resp.get_json()['access_token']
        auth_header = {'Authorization': f'Bearer {token}'}
        response = self.client.delete(f'/users/{user_id}', headers=auth_header)
        self.assertEqual(response.status_code, 204)

if __name__ == '__main__':
    unittest.main()
