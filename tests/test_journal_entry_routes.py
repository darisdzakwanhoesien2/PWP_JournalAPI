# PWP_JournalAPI/tests/test_journal_entry_routes.py
import unittest
import json
from app import create_app
from extensions import db
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
from journalapi.models import User  # Added import

class TestJournalEntryRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            # Create test user
            hashed_password = generate_password_hash("password123")
            user = User(username="testuser", email="test@example.com", password=hashed_password)
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id
            self.token = create_access_token(identity=str(self.user_id))

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_entries_empty(self):
        response = self.client.get(
            "/entries/",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_get_entries_empty] response JSON:", response.get_json())
        print("DEBUG [test_get_entries_empty] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_create_entry(self):
        response = self.client.post(
            "/entries/",
            json={
                "title": "Test Entry",
                "content": "Testing journal entry creation",
                "tags": ["test", "journal"]
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_create_entry] response JSON:", response.get_json())
        print("DEBUG [test_create_entry] status code:", response.status_code)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("entry_id", data)
        self.entry_id = data["entry_id"]

    def test_get_entry(self):
        # First, create an entry
        create_response = self.client.post(
            "/entries/",
            json={
                "title": "Test Entry",
                "content": "Testing journal entry creation",
                "tags": ["test", "journal"]
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(create_response.status_code, 201)
        entry_id = create_response.get_json()["entry_id"]

        # Test GET
        response = self.client.get(
            f"/entries/{entry_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_get_entry] response JSON:", response.get_json())
        print("DEBUG [test_get_entry] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["title"], "Test Entry")
        self.assertIn("_links", data)

    def test_get_entry_not_found(self):
        response = self.client.get(
            "/entries/999",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_get_entry_not_found] response JSON:", response.get_json())
        print("DEBUG [test_get_entry_not_found] status code:", response.status_code)
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("error", data)

    def test_update_entry(self):
        # First, create an entry
        create_response = self.client.post(
            "/entries/",
            json={
                "title": "Test Entry",
                "content": "Testing journal entry creation",
                "tags": ["test", "journal"]
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(create_response.status_code, 201)
        entry_id = create_response.get_json()["entry_id"]

        # Test PUT
        response = self.client.put(
            f"/entries/{entry_id}",
            json={
                "title": "Updated Entry",
                "content": "Updated content",
                "tags": ["updated", "journal"]
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_update_entry] response JSON:", response.get_json())
        print("DEBUG [test_update_entry] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("fully replaced", data["message"].lower())

    def test_update_entry_invalid_data(self):
        # First, create an entry
        create_response = self.client.post(
            "/entries/",
            json={
                "title": "Test Entry",
                "content": "Testing journal entry creation",
                "tags": ["test", "journal"]
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(create_response.status_code, 201)
        entry_id = create_response.get_json()["entry_id"]

        # Test PUT with invalid data
        response = self.client.put(
            f"/entries/{entry_id}",
            json={
                "title": "",  # Invalid: empty title
                "content": "Updated content",
                "tags": ["updated", "journal"]
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_update_entry_invalid_data] response JSON:", response.get_json())
        print("DEBUG [test_update_entry_invalid_data] status code:", response.status_code)
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn("errors", data)

    def test_delete_entry(self):
        # First, create an entry
        create_response = self.client.post(
            "/entries/",
            json={
                "title": "Test Entry",
                "content": "Testing journal entry creation",
                "tags": ["test", "journal"]
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(create_response.status_code, 201)
        entry_id = create_response.get_json()["entry_id"]

        # Test DELETE
        response = self.client.delete(
            f"/entries/{entry_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_delete_entry] response JSON:", response.get_json())
        print("DEBUG [test_delete_entry] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("deleted successfully", data["message"].lower())

if __name__ == "__main__":
    unittest.main()