"""Tests for journal entry API routes."""
import unittest
import json
from journalapi.models import User
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

class TestJournalEntryRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test user and token."""
        self.client = self.client  # Provided by pytest fixture
        with self.app.app_context():
            hashed_password = generate_password_hash("password123")
            user = User(username="testuser", email="test@example.com", password=hashed_password)
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id
            self.token = create_access_token(identity=str(user.id))

    def test_create_entry(self):
        """Test creating a journal entry."""
        response = self.client.post(
            "/api/journal_entries",
            json={
                "title": "Test Entry",
                "content": "Testing journal entry creation",
                "tags": ["test", "journal"]
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("entry_id", data)
        self.entry_id = data["entry_id"]

    def test_get_entries(self):
        """Test retrieving all journal entries."""
        self.client.post(
            "/api/journal_entries",
            json={
                "title": "Test Entry",
                "content": "Testing journal entry creation",
                "tags": ["test"]
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        response = self.client.get(
            "/api/journal_entries",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertGreater(len(data), 0)
        self.assertIn("title", data[0])

    def test_get_entry(self):
        """Test retrieving a single journal entry."""
        create_resp = self.client.post(
            "/api/journal_entries",
            json={
                "title": "Test Entry",
                "content": "Testing journal entry creation",
                "tags": ["test"]
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        entry_id = create_resp.get_json()["entry_id"]
        response = self.client.get(
            f"/api/journal_entries/{entry_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["title"], "Test Entry")

    def test_update_entry(self):
        """Test updating a journal entry."""
        create_resp = self.client.post(
            "/api/journal_entries",
            json={
                "title": "Test Entry",
                "content": "Testing journal entry creation",
                "tags": ["test"]
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        entry_id = create_resp.get_json()["entry_id"]
        response = self.client.put(
            f"/api/journal_entries/{entry_id}",
            json={
                "title": "Updated Entry",
                "content": "Updated content",
                "tags": ["updated"]
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("fully replaced", response.get_json()["message"].lower())

    def test_delete_entry(self):
        """Test deleting a journal entry."""
        create_resp = self.client.post(
            "/api/journal_entries",
            json={
                "title": "Test Entry",
                "content": "Testing journal entry creation",
                "tags": ["test"]
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        entry_id = create_resp.get_json()["entry_id"]
        response = self.client.delete(
            f"/api/journal_entries/{entry_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("deleted", response.get_json()["message"].lower())

    def test_create_entry_invalid_input(self):
        """Test creating a journal entry with invalid input."""
        response = self.client.post(
            "/api/journal_entries",
            json={
                "title": "",
                "content": "",
                "tags": []
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn("errors", data)

if __name__ == "__main__":
    unittest.main()