import sys
import os
import unittest
from werkzeug.security import generate_password_hash

# Ensure the project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from model_folder import JournalEntry, User

class TestJournalEntryRoutes(unittest.TestCase):

    def setUp(self):
        """Set up the test client and database."""
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            # Hash the password before saving
            hashed_password = generate_password_hash("password123")
            user = User(username="testuser", email="test@example.com", password=hashed_password)

            db.session.add(user)
            db.session.commit()

    def tearDown(self):
        """Clean up database after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login_user(self):
        """Logs in the test user and retrieves the JWT token."""
        response = self.client.post("/users/login", json={
            "email": "test@example.com",
            "password": "password123"
        })

        print("Login Response:", response.get_json())  # Debugging

        self.assertEqual(response.status_code, 200, f"Login failed: {response.get_json()}")

        return response.get_json().get("token")  # Use .get() to avoid KeyError


    def test_create_entry(self):
        """Test creating a journal entry with authentication."""
        token = self.login_user()

        response = self.client.post("/entries/", json={
            "user_id": 1,
            "title": "Test Entry",
            "content": "Testing journal entry creation",
            "tags": ["test", "journal"],
            "sentiment_score": 0.8,
            "sentiment_tag": ["positive"]
        }, headers={"Authorization": f"Bearer {token}"})

        self.assertEqual(response.status_code, 201)
        self.assertIn("Entry created successfully", response.get_json()["message"]) #self.assertIn("Journal entry created", response.get_json()["message"])

    def test_get_entries(self):
        """Test retrieving all journal entries."""
        token = self.login_user()

        # Create an entry first
        self.client.post("/entries/", json={
            "user_id": 1,
            "title": "Test Entry",
            "content": "Testing retrieval",
            "tags": ["test"],
            "sentiment_score": 0.9,
            "sentiment_tag": ["joy"]
        }, headers={"Authorization": f"Bearer {token}"})

        # Now retrieve entries
        response = self.client.get("/entries/", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(len(data) > 0)
        self.assertIn("Test Entry", data[0]["title"])

    def test_update_entry(self):
        """Test updating an existing journal entry."""
        token = self.login_user()

        # First, create an entry
        create_response = self.client.post("/entries/", json={
            "user_id": 1,
            "title": "Old Title",
            "content": "Old content",
            "tags": ["old"],
            "sentiment_score": 0.5,
            "sentiment_tag": ["neutral"]
        }, headers={"Authorization": f"Bearer {token}"})

        entry_id = create_response.get_json()["entry_id"]

        # Now update the entry
        update_response = self.client.put(f"/entries/{entry_id}", json={
            "title": "Updated Title",
            "content": "Updated content",
            "tags": ["updated"],
            "sentiment_score": 0.9,
            "sentiment_tag": ["positive"]
        }, headers={"Authorization": f"Bearer {token}"})

        self.assertEqual(update_response.status_code, 200)
        self.assertIn("Entry updated successfully", update_response.get_json()["message"])

        # Verify the update
        get_response = self.client.get(f"/entries/{entry_id}", headers={"Authorization": f"Bearer {token}"})
        updated_data = get_response.get_json()
        self.assertEqual(updated_data["title"], "Updated Title")
        self.assertEqual(updated_data["content"], "Updated content")

    def test_delete_entry(self):
        """Test deleting a journal entry."""
        token = self.login_user()

        # First, create an entry
        create_response = self.client.post("/entries/", json={
            "user_id": 1,
            "title": "Entry to be deleted",
            "content": "Some content",
            "tags": ["delete"],
            "sentiment_score": 0.7,
            "sentiment_tag": ["neutral"]
        }, headers={"Authorization": f"Bearer {token}"})

        entry_id = create_response.get_json()["entry_id"]

        # Now delete the entry
        delete_response = self.client.delete(f"/entries/{entry_id}", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(delete_response.status_code, 200)
        self.assertIn("Entry deleted successfully", delete_response.get_json()["message"]) # self.assertIn("Journal entry deleted", delete_response.get_json()["message"])

        # Verify that the entry no longer exists
        get_response = self.client.get(f"/entries/{entry_id}", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(get_response.status_code, 404)

if __name__ == "__main__":
    unittest.main()