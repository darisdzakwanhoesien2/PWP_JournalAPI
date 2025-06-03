"""Tests for comment-related API routes."""
import unittest
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
from journalapi.models import User, Comment, JournalEntry

class TestCommentRoutes(unittest.TestCase):
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

    def test_add_comment(self):
        """Test adding a comment to a journal entry."""
        response = self.client.post(
            f"/api/journal_entries/{self.entry_id}/comments",
            json={"content": "This is a test comment."},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_add_comment] response JSON:", response.get_json())
        print("DEBUG [test_add_comment] status code:", response.status_code)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("comment_id", data)

    def test_get_comments(self):
        """Test retrieving comments for a journal entry."""
        self.client.post(
            f"/api/journal_entries/{self.entry_id}/comments",
            json={"content": "This is a test comment."},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        response = self.client.get(
            f"/api/journal_entries/{self.entry_id}/comments",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_get_comments] response JSON:", response.get_json())
        print("DEBUG [test_get_comments] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertGreater(len(data), 0)
        self.assertIn("content", data[0])

    def test_update_comment(self):
        """Test updating a comment."""
        create_resp = self.client.post(
            f"/api/journal_entries/{self.entry_id}/comments",
            json={"content": "Original Comment"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        comment_id = create_resp.get_json()["comment_id"]
        update_resp = self.client.put(
            f"/api/journal_entries/{self.entry_id}/comments/{comment_id}",
            json={"content": "Updated Comment"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_update_comment] response JSON:", update_resp.get_json())
        print("DEBUG [test_update_comment] status code:", update_resp.status_code)
        self.assertEqual(update_resp.status_code, 200)
        self.assertIn("fully replaced", update_resp.get_json()["message"].lower())

    def test_delete_comment(self):
        """Test deleting a comment."""
        create_resp = self.client.post(
            f"/api/journal_entries/{self.entry_id}/comments",
            json={"content": "Comment to be deleted"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        comment_id = create_resp.get_json()["comment_id"]
        delete_resp = self.client.delete(
            f"/api/journal_entries/{self.entry_id}/comments/{comment_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_delete_comment] response JSON:", delete_resp.get_json())
        print("DEBUG [test_delete_comment] status code:", delete_resp.status_code)
        self.assertEqual(delete_resp.status_code, 200)
        self.assertIn("deleted", delete_resp.get_json()["message"].lower())
        get_resp = self.client.get(
            f"/api/journal_entries/{self.entry_id}/comments",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        data = get_resp.get_json()
        self.assertFalse(any(c["id"] == comment_id for c in data))

    def test_add_comment_invalid_input(self):
        """Test adding a comment with invalid input."""
        response = self.client.post(
            f"/api/journal_entries/{self.entry_id}/comments",
            json={"content": ""},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn("errors", data)

if __name__ == "__main__":
    unittest.main()