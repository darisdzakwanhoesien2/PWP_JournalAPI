import sys
import os
import unittest
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

# Ensure the project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from models import User, Comment, JournalEntry

class TestCommentRoutes(unittest.TestCase):

    def setUp(self):
        """Set up the test client and database."""
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.client = self.app.test_client()

        with self.app.app_context():  # ✅ FIX: Push app context before DB operations
            db.create_all()

            # Create test user
            hashed_password = generate_password_hash("password123")
            user = User(username="testuser", email="test@example.com", password=hashed_password)
            db.session.add(user)
            db.session.commit()

            # Create test journal entry
            journal_entry = JournalEntry(
                user_id=user.id,
                title="Test Journal Entry",
                content="This is a test journal entry."
            )
            db.session.add(journal_entry)
            db.session.commit()

            self.user_id = user.id
            self.entry_id = journal_entry.id
            self.token = create_access_token(identity=self.user_id)

    def tearDown(self):
        """Clean up database after each test."""
        with self.app.app_context():  # ✅ FIX: Ensure app context before DB cleanup
            db.session.remove()
            db.drop_all()

    def test_add_comment(self):
        """Test adding a comment to a journal entry."""
        response = self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": "This is a test comment."},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("Comment added successfully", response.get_json()["message"])

    def test_get_comments(self):
        """Test retrieving comments for a journal entry."""
        # First, create a comment
        self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": "This is a test comment."},
            headers={"Authorization": f"Bearer {self.token}"}
        )

        # Now retrieve comments
        response = self.client.get(
            f"/entries/{self.entry_id}/comments",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(len(data) > 0)
        self.assertIn("This is a test comment.", data[0]["content"])

    def test_update_comment(self):
        """Test updating a comment."""
        # First, create a comment
        create_response = self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": "Original Comment"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        comment_id = create_response.get_json()["comment"]["id"]

        # Now update the comment
        update_response = self.client.put(
            f"/comments/{comment_id}",
            json={"content": "Updated Comment"},
            headers={"Authorization": f"Bearer {self.token}"}
        )

        self.assertEqual(update_response.status_code, 200)
        self.assertIn("Comment updated", update_response.get_json()["message"])

    def test_delete_comment(self):
        """Test deleting a comment."""
        # First, create a comment
        create_response = self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": "Comment to be deleted"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        comment_id = create_response.get_json()["comment"]["id"]

        # Now delete the comment
        delete_response = self.client.delete(
            f"/comments/{comment_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        self.assertEqual(delete_response.status_code, 200)
        self.assertIn("Comment deleted", delete_response.get_json()["message"])

        # Verify deletion
        get_response = self.client.get(
            f"/entries/{self.entry_id}/comments",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        data = get_response.get_json()
        self.assertFalse(any(comment["id"] == comment_id for comment in data))

if __name__ == "__main__":
    unittest.main()
