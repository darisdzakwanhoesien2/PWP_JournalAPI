import sys
import os
import unittest
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from models import User, Comment, JournalEntry

class TestCommentRoutes(unittest.TestCase):

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
            db.session.refresh(user)

            self.user_id = user.id
            self.token = create_access_token(identity=self.user_id)

            journal_entry = JournalEntry(user_id=user.id, title="Test Journal Entry", content="Test content", tags="[]")
            db.session.add(journal_entry)
            db.session.commit()
            db.session.refresh(journal_entry)
            self.entry_id = journal_entry.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_comment(self):
        response = self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": "This is a test comment."},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("comment_id", response.get_json())

    def test_get_comments(self):
        self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": "This is a test comment."},
            headers={"Authorization": f"Bearer {self.token}"}
        )

        response = self.client.get(
            f"/entries/{self.entry_id}/comments",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(len(data) > 0)
        self.assertIn("content", data[0])

    def test_update_comment(self):
        create_response = self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": "Original Comment"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        comment_id = create_response.get_json()["comment_id"]

        update_response = self.client.put(
            f"/entries/{self.entry_id}/comments/{comment_id}",
            json={"content": "Updated Comment"},
            headers={"Authorization": f"Bearer {self.token}"}
        )

        self.assertEqual(update_response.status_code, 200)
        self.assertIn("Updated", update_response.get_json()["message"])

    def test_delete_comment(self):
        create_response = self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": "Comment to be deleted"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        comment_id = create_response.get_json()["comment_id"]

        delete_response = self.client.delete(
            f"/entries/{self.entry_id}/comments/{comment_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        self.assertEqual(delete_response.status_code, 200)
        self.assertIn("deleted", delete_response.get_json()["message"])

        get_response = self.client.get(
            f"/entries/{self.entry_id}/comments",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        data = get_response.get_json()
        self.assertFalse(any(comment["id"] == comment_id for comment in data))

if __name__ == "__main__":
    unittest.main()
