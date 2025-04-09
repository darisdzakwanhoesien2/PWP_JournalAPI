# PWP_JournalAPI/tests/test_journal_entry_routes.py

import unittest
import json
from app import create_app
from extensions import db

class TestJournalEntryRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            # Create and log in a user
            self.client.post("/users/register", json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123"
            })
            response = self.client.post("/users/login", json={
                "email": "test@example.com",
                "password": "password123"
            })
            data = json.loads(response.data)
            self.token = data["token"]

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_entry(self):
        response = self.client.post("/entries/", json={
            "title": "Test Entry",
            "content": "Testing journal entry creation",
            "tags": ["test", "journal"]
        }, headers={"Authorization": f"Bearer {self.token}"})
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn("entry_id", data)

if __name__ == "__main__":
    unittest.main()
