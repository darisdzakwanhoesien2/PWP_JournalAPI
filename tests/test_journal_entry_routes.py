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
    def test_get_all_entries(self):
        # Create 2 test entries first
        self._create_entry()
        self._create_entry()
        
        response = self.client.get("/entries/",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        self.assertIn("_links", data[0])  # Verify hypermedia

    def test_get_nonexistent_entry(self):
        response = self.client.get("/entries/999",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 404)

    # def test_update_entry_invalid_data(self):
    #     entry = self._create_entry()
    #     response = self.client.put(f"/entries/{entry['entry_id']}",
    #         json={"title": ""},  # Invalid empty title
    #         headers={"Authorization": f"Bearer {self.token}"}
    #     )
    #     self.assertEqual(response.status_code, 422)
    #     self.assertIn("Title cannot be empty", str(response.data))
    
    def test_update_entry_invalid_data(self):
        entry = self._create_entry()
        response = self.client.put(
            f"/entries/{entry['entry_id']}",
            json={"title": "", "content": "Updated content", "tags": ["test"]},  # Empty title now triggers validation
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 422)
        # Check that the error message contains "Title cannot be empty"
        self.assertIn("Title cannot be empty", str(response.get_data(as_text=True)))

    def _create_entry(self):
        response = self.client.post("/entries/", json={
            "title": "Test Entry",
            "content": "Test Content",
            "tags": ["test"]
        }, headers={"Authorization": f"Bearer {self.token}"})
        return response.get_json()
    # In JournalEntryListResource test
    def test_entry_list_hypermedia(self):
        response = self.client.get("/entries/",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        data = response.get_json()
        self.assertIn("_links", data[0])
        self.assertIn("comments", data[0]["_links"])

if __name__ == "__main__":
    unittest.main()
