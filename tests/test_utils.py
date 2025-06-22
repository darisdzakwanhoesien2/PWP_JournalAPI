import unittest
from src.routes_users import _build_user_response
from src import utils
from src.models_orm import User

class UtilsTestCase(unittest.TestCase):
    def test_build_user_response(self):
        user = User(id=1, username='testuser', email='test@example.com')
        response = _build_user_response(user)
        self.assertIn('_links', response)
        self.assertEqual(response['id'], 1)
        self.assertEqual(response['username'], 'testuser')
        self.assertEqual(response['email'], 'test@example.com')

    def test_user_links(self):
        links = utils.user_links(1)
        self.assertIn('self', links)
        self.assertIn('entries', links)

    def test_users_collection_links(self):
        links = utils.users_collection_links()
        self.assertIn('self', links)

from src.routes_entries import _build_entry_response, _build_comment_response, _build_edit_history_response
from src.models_orm import Entry, Comment, EditHistory

class UtilsTestCase(unittest.TestCase):
    def test_build_user_response(self):
        user = User(id=1, username='testuser', email='test@example.com')
        response = _build_user_response(user)
        self.assertIn('_links', response)
        self.assertEqual(response['id'], 1)
        self.assertEqual(response['username'], 'testuser')
        self.assertEqual(response['email'], 'test@example.com')

    def test_user_links(self):
        links = utils.user_links(1)
        self.assertIn('self', links)
        self.assertIn('entries', links)

    def test_users_collection_links(self):
        links = utils.users_collection_links()
        self.assertIn('self', links)

    def test_build_entry_response(self):
        entry = Entry(id=1, user_id=1, title='Test', content='Content')
        response = _build_entry_response(entry)
        self.assertIn('_links', response)
        self.assertEqual(response['id'], 1)
        self.assertEqual(response['title'], 'Test')

    def test_build_comment_response(self):
        comment = Comment(id=1, entry_id=1, user_id=1, content='Comment')
        response = _build_comment_response(comment, entry_id=1)
        self.assertIn('_links', response)
        self.assertEqual(response['id'], 1)
        self.assertEqual(response['content'], 'Comment')

    def test_build_edit_history_response(self):
        edit = EditHistory(id=1, entry_id=1, changes={'title': {'old': 'Old', 'new': 'New'}})
        response = _build_edit_history_response(edit, entry_id=1)
        self.assertIn('_links', response)
        self.assertEqual(response['id'], 1)
        self.assertIn('title', response['changes'])

if __name__ == '__main__':
    unittest.main()
