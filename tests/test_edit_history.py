"""Tests for edit history API routes."""
import unittest
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
from journalapi.models import User, JournalEntry, EditHistory

class TestEditHistoryRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test user, entry, and token."""
        self.client = self.client  # Provided by pytest fixture
        with self.app.app_context():
            hashed_password = generate_password_hash("password123")
            user = User(username="testuser", email="test@example.com", password=hashed_password)
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id
            self.token = create_access_token(identity=str(user.id))

            entry = JournalEntry(
                user_id=self.user_id,
                title="Test Entry",
                content="Some test content"
            )
            db.session.add(entry)
            db.session.commit()
            self.entry_id = entry.id

            edit = EditHistory(
                journal_entry_id=self.entry_id,
                old_content="Original content"
            )
            db.session.add(edit)
            db.session.commit()

    def test_get_edit_history(self):
        """Test retrieving edit history for a journal entry."""
        response = self.client.get(
            f"/api/journal_entries/{self.entry_id}/history",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertGreater(len(data), 0)
        self.assertIn("old_content", data[0])

if __name__ == "__main__":
    unittest.main()