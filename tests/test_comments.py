# PWP_JournalAPI/tests/test_comments.py

import sys
import os
import unittest
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from journalapi.models import User, Comment, JournalEntry

class TestCommentRoutes(unittest.TestCase):
    def setUp(self):
        """
        Creates a fresh in-memory DB, adds a test user & entry,
        and logs that user in with create_access_token(...).
        """
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

            self.user_id = user.id
            # IMPORTANT: use str(...) for the identity
            self.token = create_access_token(identity=str(user.id))

            # Create a test journal entry
            entry = JournalEntry(
                user_id=self.user_id,
                title="Test Entry",
                content="Some test content"
            )
            db.session.add(entry)
            db.session.commit()
            self.entry_id = entry.id

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_add_comment(self):
        response = self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": "This is a test comment."},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_add_comment] response JSON:", response.get_json())
        print("DEBUG [test_add_comment] status code:", response.status_code)

        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("comment_id", data)

    def test_get_comments(self):
        # create a comment
        create_resp = self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": "This is a test comment."},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(create_resp.status_code, 201)

        response = self.client.get(
            f"/entries/{self.entry_id}/comments",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_get_comments] response JSON:", response.get_json())
        print("DEBUG [test_get_comments] status code:", response.status_code)

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertGreater(len(data), 0)
        self.assertIn("content", data[0])

    def test_update_comment(self):
        create_resp = self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": "Original Comment"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(create_resp.status_code, 201)
        comment_id = create_resp.get_json()["comment_id"]

        update_resp = self.client.put(
            f"/entries/{self.entry_id}/comments/{comment_id}",
            json={"content": "Updated Comment"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_update_comment] response JSON:", update_resp.get_json())
        print("DEBUG [test_update_comment] status code:", update_resp.status_code)

        self.assertEqual(update_resp.status_code, 200)
        self.assertIn("fully replaced", update_resp.get_json()["message"].lower())

    def test_delete_comment(self):
        create_resp = self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": "Comment to be deleted"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(create_resp.status_code, 201)
        comment_id = create_resp.get_json()["comment_id"]

        delete_resp = self.client.delete(
            f"/entries/{self.entry_id}/comments/{comment_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_delete_comment] response JSON:", delete_resp.get_json())
        print("DEBUG [test_delete_comment] status code:", delete_resp.status_code)

        self.assertEqual(delete_resp.status_code, 200)
        self.assertIn("deleted", delete_resp.get_json()["message"].lower())

        # verify gone
        get_resp = self.client.get(
            f"/entries/{self.entry_id}/comments",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(get_resp.status_code, 200)
        data = get_resp.get_json()
        self.assertFalse(any(c["id"] == comment_id for c in data))

if __name__ == "__main__":
    unittest.main()

