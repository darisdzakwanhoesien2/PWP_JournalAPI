import unittest
from app import create_app
from extensions import db
from journalapi.models import User, JournalEntry, Comment

class TestModels(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def test_user_deletion_cascade(self):
        # Create user with entry and comment
        user = User(username="test", email="test@test.com", password="pass")
        entry = JournalEntry(user_id=user.id, title="Test", content="Content")
        comment = Comment(journal_entry_id=entry.id, user_id=user.id, content="Comment")
        
        with self.app.app_context():
            db.session.add_all([user, entry, comment])
            db.session.commit()
            db.session.delete(user)
            db.session.commit()

            self.assertEqual(JournalEntry.query.count(), 0)
            self.assertEqual(Comment.query.count(), 0)