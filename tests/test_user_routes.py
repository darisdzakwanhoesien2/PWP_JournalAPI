# PWP_JournalAPI/tests/test_user_routes.py

import sys
import os
import unittest
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from journalapi.models import User

class TestUserRoutes(unittest.TestCase):
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

            self.user_id = user.id  # integer
            # create token as string
            self.token = create_access_token(identity=str(self.user_id))

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_get_user(self):
        # 200 if user matches token
        response = self.client.get(
            f"/users/{self.user_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_get_user] response JSON:", response.get_json())
        print("DEBUG [test_get_user] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("username", data)

    def test_update_user(self):
        # 200 if user matches token
        response = self.client.put(
            f"/users/{self.user_id}",
            json={"username": "updateduser", "email": "updated@example.com", "password": "newpassword123"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_update_user] response JSON:", response.get_json())
        print("DEBUG [test_update_user] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("updated", data["message"].lower())

    def test_delete_user(self):
        # 200 if user matches token
        response = self.client.delete(
            f"/users/{self.user_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_delete_user] response JSON:", response.get_json())
        print("DEBUG [test_delete_user] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("deleted successfully", data["message"].lower())
        
    def test_get_other_user(self):
        # Should return 403 Forbidden
        response = self.client.get(
            f"/users/{self.user_id + 1}",  # Different user ID
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 403)

    def test_register_existing_email(self):
        response = self.client.post("/users/register", json={
            "username": "newuser",
            "email": "test@example.com",  # Already exists
            "password": "password123"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("already exists", response.get_json()["error"])

    def test_invalid_login(self):
        response = self.client.post("/users/login", json={
            "email": "wrong@example.com",
            "password": "invalid"
        })
        self.assertEqual(response.status_code, 401)
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
