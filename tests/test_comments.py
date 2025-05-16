# PWP_JournalAPI/tests/test_comments.py
import sys
import os
import unittest
from datetime import datetime, timezone  # Added import
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
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

    def test_comment_to_dict(self):
        with self.app.app_context():
            comment = Comment(
                journal_entry_id=self.entry_id,
                user_id=self.user_id,
                content="Test comment",
                timestamp=datetime.now(timezone.utc)
            )
            db.session.add(comment)
            db.session.commit()
            comment_dict = comment.to_dict()
            self.assertEqual(comment_dict["content"], "Test comment")
            self.assertIn("timestamp", comment_dict)

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

    def test_add_comment_invalid_data(self):
        response = self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": ""},  # Invalid: empty content
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_add_comment_invalid_data] response JSON:", response.get_json())
        print("DEBUG [test_add_comment_invalid_data] status code:", response.status_code)
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn("errors", data)

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

    def test_update_comment_unauthorized(self):
        # Create a second user
        with self.app.app_context():
            hashed_password = generate_password_hash("password123")
            other_user = User(username="otheruser", email="other@example.com", password=hashed_password)
            db.session.add(other_user)
            db.session.commit()
            other_token = create_access_token(identity=str(other_user.id))

        # Create a comment with the first user
        create_resp = self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": "Original Comment"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(create_resp.status_code, 201)
        comment_id = create_resp.get_json()["comment_id"]

        # Try to update with the second user's token
        update_resp = self.client.put(
            f"/entries/{self.entry_id}/comments/{comment_id}",
            json={"content": "Unauthorized Update"},
            headers={"Authorization": f"Bearer {other_token}"}
        )
        print("DEBUG [test_update_comment_unauthorized] response JSON:", update_resp.get_json())
        print("DEBUG [test_update_comment_unauthorized] status code:", update_resp.status_code)
        self.assertEqual(update_resp.status_code, 404)
        data = update_resp.get_json()
        self.assertIn("error", data)

    def test_update_comment_invalid_entry_id(self):
        # Create a comment
        create_resp = self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": "Test comment"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(create_resp.status_code, 201)
        comment_id = create_resp.get_json()["comment_id"]

        # Try to update with invalid entry_id
        response = self.client.put(
            f"/entries/999/comments/{comment_id}",
            json={"content": "Updated comment"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_update_comment_invalid_entry_id] response JSON:", response.get_json())
        print("DEBUG [test_update_comment_invalid_entry_id] status code:", response.status_code)
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("error", data)

    def test_update_comment_invalid_data(self):
        create_resp = self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": "Original Comment"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(create_resp.status_code, 201)
        comment_id = create_resp.get_json()["comment_id"]

        response = self.client.put(
            f"/entries/{self.entry_id}/comments/{comment_id}",
            json={"content": ""},  # Invalid: empty content
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_update_comment_invalid_data] response JSON:", response.get_json())
        print("DEBUG [test_update_comment_invalid_data] status code:", response.status_code)
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn("errors", data)

    def test_delete_comment_unauthorized(self):
        # Create a second user
        with self.app.app_context():
            hashed_password = generate_password_hash("password123")
            other_user = User(username="otheruser", email="other@example.com", password=hashed_password)
            db.session.add(other_user)
            db.session.commit()
            other_token = create_access_token(identity=str(other_user.id))

        # Create a comment with the first user
        create_resp = self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": "Comment to delete"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(create_resp.status_code, 201)
        comment_id = create_resp.get_json()["comment_id"]

        # Try to delete with the second user's token
        delete_resp = self.client.delete(
            f"/entries/{self.entry_id}/comments/{comment_id}",
            headers={"Authorization": f"Bearer {other_token}"}
        )
        print("DEBUG [test_delete_comment_unauthorized] response JSON:", delete_resp.get_json())
        print("DEBUG [test_delete_comment_unauthorized] status code:", delete_resp.status_code)
        self.assertEqual(delete_resp.status_code, 404)
        data = delete_resp.get_json()
        self.assertIn("error", data)

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