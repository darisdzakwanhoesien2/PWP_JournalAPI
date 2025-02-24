import sys
import os
import unittest

# Add the project root directory to sys.path so Python can find app.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app  # Import the factory function
from extensions import db
from models import User

class TestUserRoutes(unittest.TestCase):

    def setUp(self):
        """Set up the test client and database."""
        self.app = create_app()  # Call create_app() instead of importing app
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Use an in-memory database for tests
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up the database after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_user(self):
        """Test user registration."""
        response = self.client.post("/users/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn("User registered successfully", response.get_json()["message"])

    def test_login_user(self):
        """Test user login."""
        # First, register a user
        self.client.post("/users/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        })

        # Now, try to log in
        response = self.client.post("/users/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.get_json())  # Ensure token is returned

    def test_get_user(self):
        """Test retrieving user details."""
        with self.app.app_context():
            user = User(username="testuser", email="test@example.com", password="hashedpassword")
            db.session.add(user)
            db.session.commit()

        response = self.client.get(f"/users/{user.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["username"], "testuser")

    def test_update_user(self):
        """Test updating user details."""
        with self.app.app_context():
            user = User(username="testuser", email="test@example.com", password="hashedpassword")
            db.session.add(user)
            db.session.commit()

        response = self.client.put(f"/users/{user.id}", json={
            "username": "updateduser",
            "email": "updated@example.com"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["username"], "updateduser")

    def test_delete_user(self):
        """Test deleting a user."""
        with self.app.app_context():
            user = User(username="testuser", email="test@example.com", password="hashedpassword")
            db.session.add(user)
            db.session.commit()

        response = self.client.delete(f"/users/{user.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("User deleted successfully", response.get_json()["message"])

if __name__ == "__main__":
    unittest.main()
