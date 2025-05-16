# tests/test_edit_history.py
import unittest
import json
from app import create_app
from extensions import db
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
from journalapi.models import User, JournalEntry, EditHistory
from datetime import datetime, timezone

class TestEditHistory(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            hashed_password = generate_password_hash("password123")
            user = User(username="testuser", email="test@example.com", password=hashed_password)
            db.session.add(user)
            db.session.commit()
            entry = JournalEntry(
                user_id=user.id,
                title="Test Entry",
                content="Test Content",
                tags=json.dumps(["test"]),
                sentiment_score=0.75,
                sentiment_tag=json.dumps(["positive"])
            )
            db.session.add(entry)
            db.session.commit()
            self.user_id = user.id
            self.entry_id = entry.id
            self.token = create_access_token(identity=str(self.user_id))

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_edit_history_empty(self):
        response = self.client.get(
            f"/entries/{self.entry_id}/history",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_get_edit_history_empty] response JSON:", response.get_json())
        print("DEBUG [test_get_edit_history_empty] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data["edits"]), 0)
        self.assertIn("_links", data)
        links = data["_links"]
        self.assertEqual(links["self"]["href"], f"/entries/{self.entry_id}/history")
        self.assertEqual(links["entry"]["href"], f"/entries/{self.entry_id}")

    def test_get_edit_history(self):
        with self.app.app_context():
            edit = EditHistory(
                journal_entry_id=self.entry_id,
                user_id=self.user_id,
                edited_at=datetime.now(timezone.utc),
                previous_content="Old Content",
                new_content="New Content"
            )
            db.session.add(edit)
            db.session.commit()
            self.edit_id = edit.id

        response = self.client.get(
            f"/entries/{self.entry_id}/history",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_get_edit_history] response JSON:", response.get_json())
        print("DEBUG [test_get_edit_history] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data["edits"]), 1)
        edit = data["edits"][0]
        self.assertEqual(edit["journal_entry_id"], self.entry_id)
        self.assertEqual(edit["user_id"], self.user_id)
        self.assertEqual(edit["previous_content"], "Old Content")
        self.assertEqual(edit["new_content"], "New Content")
        self.assertIn("_links", edit)
        links = edit["_links"]
        self.assertEqual(links["self"]["href"], f"/entries/{self.entry_id}/history/{self.edit_id}")
        self.assertEqual(links["entry"]["href"], f"/entries/{self.entry_id}")
        self.assertIn("_links", data)
        top_links = data["_links"]
        self.assertEqual(top_links["self"]["href"], f"/entries/{self.entry_id}/history")
        self.assertEqual(top_links["entry"]["href"], f"/entries/{self.entry_id}")

    def test_edit_history_to_dict(self):
        with self.app.app_context():
            edit = EditHistory(
                journal_entry_id=self.entry_id,
                user_id=self.user_id,
                edited_at=datetime.now(timezone.utc),
                previous_content="Old Content",
                new_content="New Content"
            )
            db.session.add(edit)
            db.session.commit()
            edit_id = edit.id
            edit_dict = edit.to_dict()
            self.assertEqual(edit_dict["journal_entry_id"], self.entry_id)
            self.assertEqual(edit_dict["user_id"], self.user_id)
            self.assertEqual(edit_dict["previous_content"], "Old Content")
            self.assertEqual(edit_dict["new_content"], "New Content")
            self.assertEqual(edit_dict["id"], edit_id)

if __name__ == "__main__":
    unittest.main()