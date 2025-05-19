# tests/test_journal_entry_routes.py
import unittest
import json
from app import create_app
from extensions import db
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
from journalapi.models import User

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
        self.assertEqual(len(data["entries"]), 0)
        self.assertIn("_links", data)
        links = data["_links"]
        self.assertEqual(links["self"]["href"], "/entries")
        self.assertEqual(links["create"]["href"], "/entries")

    def test_get_entries_multiple(self):
        self.client.post(
            "/entries/",
            json={
                "title": "Entry 1",
                "content": "Content 1",
                "tags": ["tag1"]
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.client.post(
            "/entries/",
            json={
                "title": "Entry 2",
                "content": "Content 2",
                "tags": ["tag2"]
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        response = self.client.get(
            "/entries/",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_get_entries_multiple] response JSON:", response.get_json())
        print("DEBUG [test_get_entries_multiple] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data["entries"]), 2)
        self.assertEqual(data["entries"][0]["title"], "Entry 1")
        self.assertEqual(data["entries"][1]["title"], "Entry 2")
        self.assertIn("_links", data)
        links = data["_links"]
        self.assertEqual(links["self"]["href"], "/entries")
        self.assertEqual(links["create"]["href"], "/entries")
        for entry in data["entries"]:
            entry_links = entry["_links"]
            self.assertEqual(entry_links["self"]["href"], f"/entries/{entry['id']}")
            self.assertEqual(entry_links["edit"]["href"], f"/entries/{entry['id']}")
            self.assertEqual(entry_links["delete"]["href"], f"/entries/{entry['id']}")
            self.assertEqual(entry_links["comments"]["href"], f"/entries/{entry['id']}/comments")
            self.assertEqual(entry_links["history"]["href"], f"/entries/{entry['id']}/history")

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
        self.assertIn("_links", data)
        links = data["_links"]
        self.assertEqual(links["self"]["href"], f"/entries/{self.entry_id}")
        self.assertEqual(links["edit"]["href"], f"/entries/{self.entry_id}")
        self.assertEqual(links["delete"]["href"], f"/entries/{self.entry_id}")
        self.assertEqual(links["comments"]["href"], f"/entries/{self.entry_id}/comments")
        self.assertEqual(links["history"]["href"], f"/entries/{self.entry_id}/history")

    def test_get_entry(self):
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
        links = data["_links"]
        self.assertEqual(links["self"]["href"], f"/entries/{entry_id}")
        self.assertEqual(links["edit"]["href"], f"/entries/{entry_id}")
        self.assertEqual(links["delete"]["href"], f"/entries/{entry_id}")
        self.assertEqual(links["comments"]["href"], f"/entries/{entry_id}/comments")
        self.assertEqual(links["history"]["href"], f"/entries/{entry_id}/history")

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
        self.assertIn("message", data)
        self.assertIn("_links", data)
        links = data["_links"]
        self.assertEqual(links["self"]["href"], f"/entries/{entry_id}")
        self.assertEqual(links["edit"]["href"], f"/entries/{entry_id}")
        self.assertEqual(links["delete"]["href"], f"/entries/{entry_id}")
        self.assertEqual(links["comments"]["href"], f"/entries/{entry_id}/comments")
        self.assertEqual(links["history"]["href"], f"/entries/{entry_id}/history")

    def test_update_entry_invalid_data(self):
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

        response = self.client.put(
            f"/entries/{entry_id}",
            json={
                "title": None,
                "content": "",
                "tags": [123, None, "valid"]
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_update_entry_invalid_data] response JSON:", response.get_json())
        print("DEBUG [test_update_entry_invalid_data] status code:", response.status_code)
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn("errors", data)

    def test_update_entry_invalid_tags(self):
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

        response = self.client.put(
            f"/entries/{entry_id}",
            json={
                "title": "Valid Title",
                "content": "Valid Content",
                "tags": [None, "", 123]
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_update_entry_invalid_tags] response JSON:", response.get_json())
        print("DEBUG [test_update_entry_invalid_tags] status code:", response.status_code)
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn("errors", data)

    def test_delete_entry(self):
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

        response = self.client.delete(
            f"/entries/{entry_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_delete_entry] response JSON:", response.get_json())
        print("DEBUG [test_delete_entry] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("message", data)
        self.assertIn("_links", data)
        links = data["_links"]
        self.assertEqual(links["self"]["href"], "/entries")
        self.assertEqual(links["create"]["href"], "/entries")

    def test_delete_entry_unauthorized(self):
        with self.app.app_context():
            hashed_password = generate_password_hash("password123")
            other_user = User(username="otheruser", email="other@example.com", password=hashed_password)
            db.session.add(other_user)
            db.session.commit()
            other_token = create_access_token(identity=str(other_user.id))

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

        response = self.client.delete(
            f"/entries/{entry_id}",
            headers={"Authorization": f"Bearer {other_token}"}
        )
        print("DEBUG [test_delete_entry_unauthorized] response JSON:", response.get_json())
        print("DEBUG [test_delete_entry_unauthorized] status code:", response.status_code)
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("error", data)

    def test_delete_entry_unauthorized_non_existent(self):
        with self.app.app_context():
            hashed_password = generate_password_hash("password123")
            other_user = User(username="otheruser2", email="other2@example.com", password=hashed_password)
            db.session.add(other_user)
            db.session.commit()
            other_token = create_access_token(identity=str(other_user.id))
        response = self.client.delete(
            "/entries/999",
            headers={"Authorization": f"Bearer {other_token}"}
        )
        print("DEBUG [test_delete_entry_unauthorized_non_existent] response JSON:", response.get_json())
        print("DEBUG [test_delete_entry_unauthorized_non_existent] status code:", response.status_code)
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("error", data)

    def test_delete_entry_unauthorized_valid_entry(self):
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

        with self.app.app_context():
            hashed_password = generate_password_hash("password123")
            other_user = User(username="otheruser3", email="other3@example.com", password=hashed_password)
            db.session.add(other_user)
            db.session.commit()
            other_token = create_access_token(identity=str(other_user.id))

        response = self.client.delete(
            f"/entries/{entry_id}",
            headers={"Authorization": f"Bearer {other_token}"}
        )
        print("DEBUG [test_delete_entry_unauthorized_valid_entry] response JSON:", response.get_json())
        print("DEBUG [test_delete_entry_unauthorized_valid_entry] status code:", response.status_code)
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("error", data)

    def test_delete_entry_unauthorized_existing_entry(self):
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

        with self.app.app_context():
            hashed_password = generate_password_hash("password123")
            other_user = User(username="otheruser4", email="other4@example.com", password=hashed_password)
            db.session.add(other_user)
            db.session.commit()
            other_token = create_access_token(identity=str(other_user.id))

        response = self.client.delete(
            f"/entries/{entry_id}",
            headers={"Authorization": f"Bearer {other_token}"}
        )
        print("DEBUG [test_delete_entry_unauthorized_existing_entry] response JSON:", response.get_json())
        print("DEBUG [test_delete_entry_unauthorized_existing_entry] status code:", response.status_code)
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("error", data)

if __name__ == "__main__":
    unittest.main()