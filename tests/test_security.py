import unittest
from app import create_app

class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

    def test_protected_routes(self):
        routes = [
            ("GET", "/users/1"),
            ("POST", "/entries/"),
            ("PUT", "/entries/1"),
            ("DELETE", "/entries/1")
        ]
        
        for method, path in routes:
            response = getattr(self.client, method.lower())(path)
            self.assertEqual(response.status_code, 401)