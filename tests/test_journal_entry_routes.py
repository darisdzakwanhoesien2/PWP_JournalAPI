import sys
import os
import unittest
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from models import JournalEntry, User

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
            db.session.remove()
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

    def test_get_entries(self):
        token = self.login_user()
        self.client.post("/entries/", json={
            "title": "Test Entry",
            "content": "Testing retrieval",
            "tags": ["test"]
        }, headers={"Authorization": f"Bearer {token}"})

        response = self.client.get("/entries/", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(len(data) > 0)

    def test_update_entry(self):
        token = self.login_user()
        create_response = self.client.post("/entries/", json={
            "title": "Old Title",
            "content": "Old content",
            "tags": ["old"]
        }, headers={"Authorization": f"Bearer {token}"})
        entry_id = create_response.get_json()["entry_id"]

        update_response = self.client.put(f"/entries/{entry_id}", json={
            "title": "Updated Title",
            "content": "Updated content",
            "tags": ["updated"]
        }, headers={"Authorization": f"Bearer {token}"})

        self.assertEqual(update_response.status_code, 200)
        self.assertIn("Updated", update_response.get_json()["message"])

    def test_delete_entry(self):
        token = self.login_user()
        create_response = self.client.post("/entries/", json={
            "title": "Entry to be deleted",
            "content": "Some content",
            "tags": ["delete"]
        }, headers={"Authorization": f"Bearer {token}"})
        entry_id = create_response.get_json()["entry_id"]

        delete_response = self.client.delete(f"/entries/{entry_id}", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(delete_response.status_code, 200)
        self.assertIn("deleted", delete_response.get_json()["message"])

        get_response = self.client.get(f"/entries/{entry_id}", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(get_response.status_code, 404)

if __name__ == "__main__":
    unittest.main()
