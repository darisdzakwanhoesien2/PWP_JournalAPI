# PWP_JournalAPI/tests/test_user_routes.py
import sys
import os
import unittest
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
from unittest.mock import patch
from app import create_app
from extensions import db
from journalapi.models import User  # Added import

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

            self.user_id = user.id
            self.token = create_access_token(identity=str(self.user_id))

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_register_user(self):
        response = self.client.post(
            "/users/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "newpassword123"
            }
        )
        print("DEBUG [test_register_user] response JSON:", response.get_json())
        print("DEBUG [test_register_user] status code:", response.status_code)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("registered successfully", data["message"].lower())

    def test_register_duplicate_email(self):
        response = self.client.post(
            "/users/register",
            json={
                "username": "anotheruser",
                "email": "test@example.com",  # Duplicate email
                "password": "password123"
            }
        )
        print("DEBUG [test_register_duplicate_email] response JSON:", response.get_json())
        print("DEBUG [test_register_duplicate_email] status code:", response.status_code)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("email already registered", data["error"].lower())

    def test_register_invalid_data(self):
        response = self.client.post(
            "/users/register",
            json={
                "username": "",
                "email": "invalid",
                "password": "short"
            }
        )
        print("DEBUG [test_register_invalid_data] response JSON:", response.get_json())
        print("DEBUG [test_register_invalid_data] status code:", response.status_code)
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn("errors", data)

    def test_register_internal_error(self):
        with patch('extensions.db.session.commit', side_effect=Exception("Database error")):
            response = self.client.post(
                "/users/register",
                json={
                    "username": "erroruser",
                    "email": "error@example.com",
                    "password": "password123"
                }
            )
        print("DEBUG [test_register_internal_error] response JSON:", response.get_json())
        print("DEBUG [test_register_internal_error] status code:", response.status_code)
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn("internal server error", data["error"].lower())

    def test_login_user(self):
        response = self.client.post(
            "/users/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        print("DEBUG [test_login_user] response JSON:", response.get_json())
        print("DEBUG [test_login_user] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("token", data)

    def test_login_invalid_credentials(self):
        response = self.client.post(
            "/users/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        )
        print("DEBUG [test_login_invalid_credentials] response JSON:", response.get_json())
        print("DEBUG [test_login_invalid_credentials] status code:", response.status_code)
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertIn("invalid credentials", data["error"].lower())

    def test_get_user(self):
        response = self.client.get(
            f"/users/{self.user_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_get_user] response JSON:", response.get_json())
        print("DEBUG [test_get_user] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("username", data)

    def test_get_user_unauthorized(self):
        with self.app.app_context():  # Add application context
            other_token = create_access_token(identity=str(self.user_id + 1))
        response = self.client.get(
            f"/users/{self.user_id}",
            headers={"Authorization": f"Bearer {other_token}"}
        )
        print("DEBUG [test_get_user_unauthorized] response JSON:", response.get_json())
        print("DEBUG [test_get_user_unauthorized] status code:", response.status_code)
        self.assertEqual(response.status_code, 403)
        data = response.get_json()
        self.assertIn("unauthorized", data["error"].lower())

    def test_update_user(self):
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
        response = self.client.delete(
            f"/users/{self.user_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_delete_user] response JSON:", response.get_json())
        print("DEBUG [test_delete_user] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("deleted successfully", data["message"].lower())

if __name__ == "__main__":
    unittest.main()