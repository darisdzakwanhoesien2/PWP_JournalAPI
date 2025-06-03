"""Tests for user-related API routes."""
import unittest
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
from journalapi.models import User

class TestUserRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test user and token."""
        self.client = self.client  # Provided by pytest fixture
        with self.app.app_context():
            hashed_password = generate_password_hash("password123")
            user = User(username="testuser", email="test@example.com", password=hashed_password)
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id
            self.token = create_access_token(identity=str(user.id))

    def test_get_user(self):
        """Test retrieving user data."""
        response = self.client.get(
            f"/api/users/{self.user_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_get_user] response JSON:", response.get_json())
        print("DEBUG [test_get_user] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("username", data)

    def test_update_user(self):
        """Test updating user data."""
        response = self.client.put(
            f"/api/users/{self.user_id}",
            json={"username": "updateduser", "email": "updated@example.com", "password": "newpassword123"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_update_user] response JSON:", response.get_json())
        print("DEBUG [test_update_user] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("updated", data["message"].lower())

    def test_delete_user(self):
        """Test deleting a user."""
        response = self.client.delete(
            f"/api/users/{self.user_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_delete_user] response JSON:", response.get_json())
        print("DEBUG [test_delete_user] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("deleted successfully", data["message"].lower())

    def test_register_user(self):
        """Test registering a new user."""
        response = self.client.post(
            "/api/users/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "password123"
            }
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("registered", data["message"].lower())

    def test_login_user(self):
        """Test logging in a user."""
        response = self.client.post(
            "/api/users/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("token", data)

if __name__ == "__main__":
    unittest.main()