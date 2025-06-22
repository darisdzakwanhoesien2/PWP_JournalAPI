import unittest
from datetime import datetime
from src import models_orm

class ModelsORMTestCase(unittest.TestCase):
    def test_user_to_dict_and_from_dict(self):
        user = models_orm.User(id=1, username='user1', email='user1@example.com', registered_at=datetime.utcnow())
        d = user.to_dict()
        self.assertEqual(d['id'], 1)
        self.assertEqual(d['username'], 'user1')
        self.assertEqual(d['email'], 'user1@example.com')
        self.assertIsNotNone(d['registered_at'])
        user2 = models_orm.User.from_dict(d)
        self.assertEqual(user2.id, 1)
        self.assertEqual(user2.username, 'user1')
        self.assertEqual(user2.email, 'user1@example.com')

    def test_entry_to_dict_and_from_dict(self):
        now = datetime.utcnow()
        entry = models_orm.Entry(id=1, user_id=1, title='Title', content='Content', created_at=now, updated_at=now)
        d = entry.to_dict()
        self.assertEqual(d['id'], 1)
        self.assertEqual(d['user_id'], 1)
        self.assertEqual(d['title'], 'Title')
        self.assertEqual(d['content'], 'Content')
        self.assertIsNotNone(d['created_at'])
        self.assertIsNotNone(d['updated_at'])
        entry2 = models_orm.Entry.from_dict(d)
        self.assertEqual(entry2.id, 1)
        self.assertEqual(entry2.user_id, 1)
        self.assertEqual(entry2.title, 'Title')
        self.assertEqual(entry2.content, 'Content')

    def test_comment_to_dict_and_from_dict(self):
        now = datetime.utcnow()
        comment = models_orm.Comment(id=1, entry_id=1, user_id=1, content='Comment', created_at=now, updated_at=now)
        d = comment.to_dict()
        self.assertEqual(d['id'], 1)
        self.assertEqual(d['entry_id'], 1)
        self.assertEqual(d['user_id'], 1)
        self.assertEqual(d['content'], 'Comment')
        self.assertIsNotNone(d['created_at'])
        self.assertIsNotNone(d['updated_at'])
        comment2 = models_orm.Comment.from_dict(d)
        self.assertEqual(comment2.id, 1)
        self.assertEqual(comment2.entry_id, 1)
        self.assertEqual(comment2.user_id, 1)
        self.assertEqual(comment2.content, 'Comment')

    def test_edit_history_to_dict_and_from_dict(self):
        now = datetime.utcnow()
        edit = models_orm.EditHistory(id=1, entry_id=1, edited_at=now, changes='{"title": {"old": "Old", "new": "New"}}')
        d = edit.to_dict()
        self.assertEqual(d['id'], 1)
        self.assertEqual(d['entry_id'], 1)
        self.assertIsNotNone(d['edited_at'])
        self.assertEqual(d['changes'], '{"title": {"old": "Old", "new": "New"}}')
        edit2 = models_orm.EditHistory.from_dict(d)
        self.assertEqual(edit2.id, 1)
        self.assertEqual(edit2.entry_id, 1)
        self.assertEqual(edit2.changes, '{"title": {"old": "Old", "new": "New"}}')

if __name__ == '__main__':
    unittest.main()
