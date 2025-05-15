# PWP_JournalAPI/tests/test_edit_history.py
import sys
import os
import unittest
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from journalapi.models import User, JournalEntry, EditHistory

class TestEditHistoryRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
        })
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            # Create test user
            hashed_password = generate_password_hash("password123")
            user = User(username="testuser", email="test@example.com", password=hashed_password)
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id
            self.token = create_access_token(identity=str(self.user_id))

            # Create test journal entry
            entry = JournalEntry(
                user_id=self.user_id,
                title="Test Entry",
                content="Initial content"
            )
            db.session.add(entry)
            db.session.commit()
            self.entry_id = entry.id

            # Create test edit history
            edit = EditHistory(
                journal_entry_id=self.entry_id,
                user_id=self.user_id,
                previous_content="Initial content",
                new_content="Updated content"
            )
            db.session.add(edit)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_get_edit_history(self):
        response = self.client.get(
            f"/entries/{self.entry_id}/history",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_get_edit_history] response JSON:", response.get_json())
        print("DEBUG [test_get_edit_history] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertGreater(len(data), 0)
        self.assertIn("previous_content", data[0])
        self.assertIn("new_content", data[0])

    def test_get_edit_history_no_entries(self):
        # Create a new entry with no edit history
        with self.app.app_context():
            new_entry = JournalEntry(
                user_id=self.user_id,
                title="Empty Entry",
                content="No edits"
            )
            db.session.add(new_entry)
            db.session.commit()
            new_entry_id = new_entry.id

        response = self.client.get(
            f"/entries/{new_entry_id}/history",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_get_edit_history_no_entries] response JSON:", response.get_json())
        print("DEBUG [test_get_edit_history_no_entries] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 0)

if __name__ == "__main__":
    unittest.main()