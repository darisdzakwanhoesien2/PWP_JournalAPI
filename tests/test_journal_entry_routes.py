import sys
import os

# Add the parent directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from app import app, db
from models import User
from models import JournalEntry

class TestJournalEntryRoutes(unittest.TestCase):

    def setUp(self):
        """Set up the test client and database."""
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            # Create a test user
            user = User(username="testuser", email="test@example.com", password="password123")
            db.session.add(user)
            db.session.commit()

    def tearDown(self):
        """Clean up the database after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_entry(self):
        """Test creating a journal entry."""
        # Log in the test user
        login_response = self.app.post("/users/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        access_token = login_response.get_json()["access_token"]

        # Create a journal entry
        response = self.app.post("/entries/", json={
            "title": "Test Entry",
            "content": "This is a test entry.",
            "tags": ["test", "journal"]
        }, headers={"Authorization": f"Bearer {access_token}"})
        self.assertEqual(response.status_code, 201)
        self.assertIn("Entry created successfully", response.get_json()["message"])

    def test_get_entries(self):
        """Test retrieving all journal entries."""
        # Log in the test user
        login_response = self.app.post("/users/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        access_token = login_response.get_json()["access_token"]

        # Create a journal entry
        self.app.post("/entries/", json={
            "title": "Test Entry",
            "content": "This is a test entry.",
            "tags": ["test", "journal"]
        }, headers={"Authorization": f"Bearer {access_token}"})

        # Retrieve all entries
        response = self.app.get("/entries/", headers={"Authorization": f"Bearer {access_token}"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)

    def test_update_entry(self):
        """Test updating a journal entry."""
        # Log in the test user
        login_response = self.app.post("/users/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        access_token = login_response.get_json()["access_token"]

        # Create a journal entry
        self.app.post("/entries/", json={
            "title": "Test Entry",
            "content": "This is a test entry.",
            "tags": ["test", "journal"]
        }, headers={"Authorization": f"Bearer {access_token}"})

        # Update the entry
        response = self.app.put("/entries/1", json={
            "title": "Updated Entry",
            "content": "This is an updated entry."
        }, headers={"Authorization": f"Bearer {access_token}"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Entry updated successfully", response.get_json()["message"])

    def test_delete_entry(self):
        """Test deleting a journal entry."""
        # Log in the test user
        login_response = self.app.post("/users/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        access_token = login_response.get_json()["access_token"]

        # Create a journal entry
        self.app.post("/entries/", json={
            "title": "Test Entry",
            "content": "This is a test entry.",
            "tags": ["test", "journal"]
        }, headers={"Authorization": f"Bearer {access_token}"})

        # Delete the entry
        response = self.app.delete("/entries/1", headers={"Authorization": f"Bearer {access_token}"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Entry deleted successfully", response.get_json()["message"])

if __name__ == "__main__":
    unittest.main()