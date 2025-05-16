# PWP_JournalAPI/tests/test_user_routes.py
import sys
import os
import unittest
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
from unittest.mock import patch
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
                "email": "test@example.com",
                "password": "password123"
            }
        )
        print("DEBUG [test_register_duplicate_email] response JSON:", response.get_json())
        print("DEBUG [test_register_duplicate_email] status code:", response.status_code)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("email already registered", data["error"].lower())

    def test_register_duplicate_username(self):
        response = self.client.post(
            "/users/register",
            json={
                "username": "testuser",
                "email": "new2@example.com",
                "password": "password123"
            }
        )
        print("DEBUG [test_register_duplicate_username] response JSON:", response.get_json())
        print("DEBUG [test_register_duplicate_username] status code:", response.status_code)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("username already taken", data["error"].lower())

    def test_register_duplicate_username_case_insensitive(self):
        with self.app.app_context():
            user = User(username="conflictuser", email="conflict2@example.com", password=generate_password_hash("password123"))
            db.session.add(user)
            db.session.commit()
            self.assertIsNotNone(User.query.filter_by(username="conflictuser").first())
        response = self.client.post(
            "/users/register",
            json={
                "username": "conflictuser",
                "email": "new4@example.com",
                "password": "password123"
            }
        )
        print("DEBUG [test_register_duplicate_username_case_insensitive] response JSON:", response.get_json())
        print("DEBUG [test_register_duplicate_username_case_insensitive] status code:", response.status_code)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("username already taken", data["error"].lower())

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

    def test_register_server_error(self):
        with patch('journalapi.models.User.__init__', side_effect=Exception("User creation error")):
            response = self.client.post(
                "/users/register",
                json={
                    "username": "servererror",
                    "email": "servererror@example.com",
                    "password": "password123"
                }
            )
        print("DEBUG [test_register_server_error] response JSON:", response.get_json())
        print("DEBUG [test_register_server_error] status code:", response.status_code)
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
        with self.app.app_context():
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

    def test_get_user_not_found(self):
        with self.app.app_context():
            non_existent_id = self.user_id + 999
            token = create_access_token(identity=str(non_existent_id))
        response = self.client.get(
            f"/users/{non_existent_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        print("DEBUG [test_get_user_not_found] response JSON:", response.get_json())
        print("DEBUG [test_get_user_not_found] status code:", response.status_code)
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("not found", data["error"].lower())

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

    def test_update_user_unauthorized(self):
        with self.app.app_context():
            other_token = create_access_token(identity=str(self.user_id + 1))
        response = self.client.put(
            f"/users/{self.user_id}",
            json={"username": "unauthorized", "email": "unauth@example.com"},
            headers={"Authorization": f"Bearer {other_token}"}
        )
        print("DEBUG [test_update_user_unauthorized] response JSON:", response.get_json())
        print("DEBUG [test_update_user_unauthorized] status code:", response.status_code)
        self.assertEqual(response.status_code, 403)
        data = response.get_json()
        self.assertIn("unauthorized", data["error"].lower())

    def test_update_user_invalid_token(self):
        response = self.client.put(
            f"/users/{self.user_id}",
            json={"username": "invalid", "email": "invalid@example.com"},
            headers={"Authorization": "Bearer invalid_token"}
        )
        print("DEBUG [test_update_user_invalid_token] response JSON:", response.get_json())
        print("DEBUG [test_update_user_invalid_token] status code:", response.status_code)
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn("not enough segments", data["msg"].lower())

    def test_update_user_missing_token(self):
        response = self.client.put(
            f"/users/{self.user_id}",
            json={"username": "missing", "email": "missing@example.com"}
        )
        print("DEBUG [test_update_user_missing_token] response JSON:", response.get_json())
        print("DEBUG [test_update_user_missing_token] status code:", response.status_code)
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertIn("missing authorization header", data["msg"].lower())

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

    def test_delete_user_unauthorized(self):
        with self.app.app_context():
            other_token = create_access_token(identity=str(self.user_id + 1))
        response = self.client.delete(
            f"/users/{self.user_id}",
            headers={"Authorization": f"Bearer {other_token}"}
        )
        print("DEBUG [test_delete_user_unauthorized] response JSON:", response.get_json())
        print("DEBUG [test_delete_user_unauthorized] status code:", response.status_code)
        self.assertEqual(response.status_code, 403)
        data = response.get_json()
        self.assertIn("unauthorized", data["error"].lower())

    def test_delete_user_invalid_token(self):
        response = self.client.delete(
            f"/users/{self.user_id}",
            headers={"Authorization": "Bearer invalid_token"}
        )
        print("DEBUG [test_delete_user_invalid_token] response JSON:", response.get_json())
        print("DEBUG [test_delete_user_invalid_token] status code:", response.status_code)
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn("not enough segments", data["msg"].lower())

    def test_delete_user_missing_token(self):
        response = self.client.delete(
            f"/users/{self.user_id}"
        )
        print("DEBUG [test_delete_user_missing_token] response JSON:", response.get_json())
        print("DEBUG [test_delete_user_missing_token] status code:", response.status_code)
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertIn("missing authorization header", data["msg"].lower())

    def test_user_to_dict(self):
        with self.app.app_context():
            user = db.session.get(User, self.user_id)
            user_dict = user.to_dict()
            self.assertEqual(user_dict["username"], "testuser")
            self.assertEqual(user_dict["email"], "test@example.com")
            self.assertEqual(user_dict["id"], self.user_id)

if __name__ == "__main__":
    unittest.main()