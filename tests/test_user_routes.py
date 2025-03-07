import sys
import os
import unittest
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from models import User

class TestUserRoutes(unittest.TestCase):

    def setUp(self):
        """Set up the test client and database."""
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            # Create test user and ensure it's refreshed in session
            hashed_password = generate_password_hash("password123")
            user = User(username="testuser", email="test@example.com", password=hashed_password)
            db.session.add(user)
            db.session.commit()

            db.session.refresh(user)  # ✅ Keeps user attached to session
            self.user_id = user.id
            self.token = create_access_token(identity=self.user_id)

    def tearDown(self):
        """Clean up database after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_user(self):
        """Test retrieving user details."""
        response = self.client.get(f"/users/{self.user_id}", headers={"Authorization": f"Bearer {self.token}"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("username", response.get_json())

    def test_update_user(self):
        """Test updating user details."""
        response = self.client.put(
            f"/users/{self.user_id}",
            json={"username": "updateduser", "email": "updated@example.com"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("User updated successfully", response.get_json()["message"])

    def test_delete_user(self):
        """Test deleting a user."""
        response = self.client.delete(f"/users/{self.user_id}", headers={"Authorization": f"Bearer {self.token}"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("User deleted successfully", response.get_json()["message"])

        # Verify deletion
        response = self.client.get(f"/users/{self.user_id}", headers={"Authorization": f"Bearer {self.token}"})
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()
