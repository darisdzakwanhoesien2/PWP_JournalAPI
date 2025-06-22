import unittest
import json
from src.app import create_app

class EntriesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        self.app.testing = True
        # Clear entries, comments, and edit history data before tests
        from src.data_store import save_entries, save_comments, save_edit_history, save_users, load_users
        save_entries([])
        save_comments([])
        save_edit_history([])
        save_users([])
        # Register a user and get token for protected endpoints
        self.client.post('/users/register', json={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword'
        })
        users = load_users()
        self.user_id = users[0]['id'] if users else None
        login_resp = self.client.post('/login', json={'username': 'testuser'})
        self.token = login_resp.get_json()['access_token']
        self.auth_header = {'Authorization': f'Bearer {self.token}'}

    def tearDown(self):
        self.app_context.pop()

    def test_create_entry(self):
        response = self.client.post('/entries', json={
            'user_id': self.user_id,
            'title': 'Test Entry',
            'content': 'This is a test entry.'
        }, headers=self.auth_header)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['title'], 'Test Entry')
        self.assertEqual(data['content'], 'This is a test entry.')
        self.assertEqual(data['user_id'], 1)

    def test_get_entries(self):
        # Create an entry first
        self.test_create_entry()
        response = self.client.get('/entries', headers=self.auth_header)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('items', data)
        self.assertGreaterEqual(len(data['items']), 1)

    def test_get_entry(self):
        self.test_create_entry()
        response = self.client.get('/entries/1', headers=self.auth_header)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['id'], 1)

    def test_update_entry(self):
        self.test_create_entry()
        response = self.client.put('/entries/1', json={
            'title': 'Updated Title',
            'content': 'Updated content.'
        }, headers=self.auth_header)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['title'], 'Updated Title')
        self.assertEqual(data['content'], 'Updated content.')

    def test_delete_entry(self):
        self.test_create_entry()
        response = self.client.delete('/entries/1', headers=self.auth_header)
        self.assertEqual(response.status_code, 204)
        # Verify deletion
        response = self.client.get('/entries/1', headers=self.auth_header)
        self.assertEqual(response.status_code, 404)

    def _add_comment(self):
        self.test_create_entry()
        response = self.client.post('/entries/1/comments', json={
            'user_id': self.user_id,
            'content': 'This is a comment.'
        }, headers=self.auth_header)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['content'], 'This is a comment.')
        self.assertEqual(data['entry_id'], 1)
        # Debug print comments data after creation
        from src.data_store import load_comments
        comments = load_comments()
        print(f"Comments after creation: {comments}")
        return data['id']

    def test_add_comment(self):
        self._add_comment()

    def test_get_comments(self):
        self._add_comment()
        response = self.client.get('/entries/1/comments', headers=self.auth_header)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('items', data)
        self.assertGreaterEqual(len(data['items']), 1)

    def test_update_comment(self):
        comment_id = self._add_comment()
        print(f"Updating comment with id: {comment_id}")
        print(f"Update comment request URL: /entries/comments/{comment_id}")
        print(f"Update comment request headers: {self.auth_header}")
        response = self.client.put(f'/entries/comments/{comment_id}', json={
            'content': 'Updated comment.'
        }, headers=self.auth_header)
        print(f"Update comment response status: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['content'], 'Updated comment.')

    def test_delete_comment(self):
        comment_id = self._add_comment()
        print(f"Deleting comment with id: {comment_id}")
        print(f"Delete comment request URL: /entries/comments/{comment_id}")
        print(f"Delete comment request headers: {self.auth_header}")
        response = self.client.delete(f'/entries/comments/{comment_id}', headers=self.auth_header)
        print(f"Delete comment response status: {response.status_code}")
        self.assertEqual(response.status_code, 204)
        # Verify deletion
        response = self.client.get(f'/entries/comments/{comment_id}', headers=self.auth_header)
        self.assertEqual(response.status_code, 404)

    def test_get_edit_history_empty(self):
        self.test_create_entry()
        response = self.client.get('/entries/1/edit_history', headers=self.auth_header)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('items', data)
        self.assertEqual(len(data['items']), 0)

    def test_edit_history_on_update(self):
        self.test_create_entry()
        # Update entry to create edit history
        self.client.put('/entries/1', json={
            'title': 'Edited Title',
            'content': 'Edited content.'
        }, headers=self.auth_header)
        response = self.client.get('/entries/1/edit_history', headers=self.auth_header)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertGreaterEqual(len(data['items']), 1)

    def test_get_edit_history_item(self):
        self.test_edit_history_on_update()
        response = self.client.get('/entries/1/edit_history/1', headers=self.auth_header)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['id'], 1)

    def test_create_entry_missing_data(self):
        response = self.client.post('/entries', json={}, headers=self.auth_header)
        self.assertEqual(response.status_code, 400)

    def test_update_entry_missing_data(self):
        self.test_create_entry()
        response = self.client.put('/entries/1', json={}, headers=self.auth_header)
        self.assertEqual(response.status_code, 400)  # should return 400 for empty update data

    def test_update_entry_nonexistent(self):
        response = self.client.put('/entries/9999', json={
            'title': 'Nonexistent',
            'content': 'Nonexistent content'
        }, headers=self.auth_header)
        self.assertEqual(response.status_code, 404)

    def test_delete_entry_nonexistent(self):
        response = self.client.delete('/entries/9999', headers=self.auth_header)
        self.assertEqual(response.status_code, 404)

    def test_add_comment_missing_data(self):
        self.test_create_entry()
        response = self.client.post('/entries/1/comments', json={}, headers=self.auth_header)
        self.assertEqual(response.status_code, 400)

    def test_update_comment_missing_data(self):
        comment_id = self._add_comment()
        response = self.client.put(f'/entries/comments/{comment_id}', json={}, headers=self.auth_header)
        self.assertEqual(response.status_code, 400)

    def test_update_comment_nonexistent(self):
        response = self.client.put('/entries/comments/9999', json={
            'content': 'Nonexistent comment'
        }, headers=self.auth_header)
        self.assertEqual(response.status_code, 404)

    def test_delete_comment_nonexistent(self):
        response = self.client.delete('/entries/comments/9999', headers=self.auth_header)
        self.assertEqual(response.status_code, 404)

    def test_get_edit_history_item_nonexistent(self):
        self.test_create_entry()
        response = self.client.get('/entries/1/edit_history/9999', headers=self.auth_header)
        self.assertEqual(response.status_code, 404)

    def test_get_entries_empty(self):
        # Clear entries and test get_entries returns empty list
        from src.data_store import save_entries
        save_entries([])
        response = self.client.get('/entries', headers=self.auth_header)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('items', data)
        self.assertEqual(len(data['items']), 0)

    def test_create_entry_invalid_data(self):
        # Missing required fields
        response = self.client.post('/entries', json={'user_id': None}, headers=self.auth_header)
        self.assertEqual(response.status_code, 400)

    def test_get_entry_not_found(self):
        response = self.client.get('/entries/9999', headers=self.auth_header)
        self.assertEqual(response.status_code, 404)

    def test_update_entry_no_changes(self):
        self.test_create_entry()
        response = self.client.put('/entries/1', json={'title': 'Test', 'content': 'Content'}, headers=self.auth_header)
        self.assertEqual(response.status_code, 200)

    def test_delete_entry_not_found(self):
        response = self.client.delete('/entries/9999', headers=self.auth_header)
        self.assertEqual(response.status_code, 404)

    def test_get_entries_by_user_no_entries(self):
        response = self.client.get('/entries/user/9999', headers=self.auth_header)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('items', data)
        self.assertEqual(len(data['items']), 0)

    def test_add_comment_invalid_data(self):
        self.test_create_entry()
        response = self.client.post('/entries/1/comments', json={'user_id': None}, headers=self.auth_header)
        self.assertEqual(response.status_code, 400)

    def test_get_comment_not_found(self):
        response = self.client.get('/entries/comments/9999', headers=self.auth_header)
        self.assertEqual(response.status_code, 404)

    def test_update_comment_no_content(self):
        comment_id = self._add_comment()
        response = self.client.put(f'/entries/comments/{comment_id}', json={'content': 'Comment'}, headers=self.auth_header)
        self.assertEqual(response.status_code, 200)

    def test_delete_comment_not_found(self):
        response = self.client.delete('/entries/comments/9999', headers=self.auth_header)
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
