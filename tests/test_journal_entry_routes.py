# tests/test_journal_entry_routes.py
import sys
import os
import unittest
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from journalapi.models import JournalEntry, User

class TestJournalEntryRoutes(unittest.TestCase):

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

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def login_user(self):
        response = self.client.post("/users/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        print("Login Response:", response.get_json())
        self.assertEqual(response.status_code, 200)
        return response.get_json().get("token")

    def test_create_entry(self):
        token = self.login_user()
        response = self.client.post("/entries/", json={
            "title": "Test Entry",
            "content": "Testing journal entry creation",
            "tags": ["test", "journal"]
        }, headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(response.status_code, 201)
        self.assertIn("entry_id", response.get_json())

    # ... similarly fix other tests ...
