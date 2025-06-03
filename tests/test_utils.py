"""Tests for utility functions."""
import unittest
from werkzeug.security import generate_password_hash
from journalapi.models import User
from journalapi.utils import authenticate_user, generate_token, json_response

class TestUtils(unittest.TestCase):
    def setUp(self):
        """Set up test user."""
        self.client = self.client  # Provided by pytest fixture
        with self.app.app_context():
            hashed_password = generate_password_hash("password123")
            user = User(username="testuser", email="test@example.com", password=hashed_password)
            db.session.add(user)
            db.session.commit()
            self.user = user

    def test_json_response(self):
        """Test creating a JSON response."""
        data = {"test": "value"}
        response, status, headers = json_response(data, 200)
        self.assertEqual(status, 200)
        self.assertIn("application/json", headers["Content-Type"])
        self.assertEqual(json.loads(response), data)

    def test_authenticate_user(self):
        """Test authenticating a user."""
        with self.app.app_context():
            user = authenticate_user("testuser", "password123")
            self.assertEqual(user.id, self.user.id)
            user = authenticate_user("testuser", "wrongpass")
            self.assertIsNone(user)

    def test_generate_token(self):
        """Test generating a JWT token."""
        with self.app.app_context():
            token = generate_token(self.user)
            decoded = jwt.decode(token, "secret_key", algorithms=["HS256"])
            self.assertEqual(decoded["user_id"], self.user.id)

if __name__ == "__main__":
    unittest.main()