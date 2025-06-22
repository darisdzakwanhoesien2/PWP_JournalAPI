import unittest
from src import models

class ModelsTestCase(unittest.TestCase):
    def test_user_to_dict_and_from_dict(self):
        user = models.User(id=1, username='user1', email='user1@example.com')
        d = user.to_dict()
        self.assertEqual(d['id'], 1)
        self.assertEqual(d['username'], 'user1')
        self.assertEqual(d['email'], 'user1@example.com')
        user2 = models.User.from_dict(d)
        self.assertEqual(user2.id, 1)
        self.assertEqual(user2.username, 'user1')
        self.assertEqual(user2.email, 'user1@example.com')

    def test_entry_to_dict_and_from_dict(self):
        entry = models.Entry(id=1, user_id=1, title='Title', content='Content')
        d = entry.to_dict()
        self.assertEqual(d['id'], 1)
        self.assertEqual(d['user_id'], 1)
        self.assertEqual(d['title'], 'Title')
        self.assertEqual(d['content'], 'Content')
        entry2 = models.Entry.from_dict(d)
        self.assertEqual(entry2.id, 1)
        self.assertEqual(entry2.user_id, 1)
        self.assertEqual(entry2.title, 'Title')
        self.assertEqual(entry2.content, 'Content')

    def test_comment_to_dict_and_from_dict(self):
        comment = models.Comment(id=1, entry_id=1, user_id=1, content='Comment')
        d = comment.to_dict()
        self.assertEqual(d['id'], 1)
        self.assertEqual(d['entry_id'], 1)
        self.assertEqual(d['user_id'], 1)
        self.assertEqual(d['content'], 'Comment')
        comment2 = models.Comment.from_dict(d)
        self.assertEqual(comment2.id, 1)
        self.assertEqual(comment2.entry_id, 1)
        self.assertEqual(comment2.user_id, 1)
        self.assertEqual(comment2.content, 'Comment')

    def test_edit_history_to_dict_and_from_dict(self):
        changes = {'title': {'old': 'Old', 'new': 'New'}}
        edit = models.EditHistory(id=1, entry_id=1, changes=changes)
        d = edit.to_dict()
        self.assertEqual(d['id'], 1)
        self.assertEqual(d['entry_id'], 1)
        self.assertEqual(d['changes'], changes)
        edit2 = models.EditHistory.from_dict(d)
        self.assertEqual(edit2.id, 1)
        self.assertEqual(edit2.entry_id, 1)
        self.assertEqual(edit2.changes, changes)

if __name__ == '__main__':
    unittest.main()
