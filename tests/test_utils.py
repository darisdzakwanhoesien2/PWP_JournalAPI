# PWP_JournalAPI/tests/test_utils.py
import unittest
from journalapi.utils import JsonResponse, detect_resource_type, generate_links
from flask import Response

class TestUtils(unittest.TestCase):
    def test_json_response_with_entry(self):
        data = {"id": 1, "title": "Test Entry", "content": "Content"}
        response = JsonResponse(data, 200)
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        response_data = response.get_json()
        self.assertIn("_links", response_data)
        self.assertEqual(response_data["_links"]["self"]["href"], "/entries/1")

    def test_json_response_with_user(self):
        data = {"id": 1, "username": "testuser", "email": "test@example.com"}
        response = JsonResponse(data, 200)
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn("_links", response_data)
        self.assertEqual(response_data["_links"]["self"]["href"], "/users/1")

    def test_json_response_with_comment(self):
        data = {"id": 1, "journal_entry_id": 1, "content": "Test comment"}
        response = JsonResponse(data, 200)
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn("_links", response_data)
        self.assertEqual(response_data["_links"]["self"]["href"], "/entries/1/comments/1")

    def test_detect_resource_type_entry(self):
        data = {"title": "Test Entry"}
        self.assertEqual(detect_resource_type(data), "entry")

    def test_detect_resource_type_user(self):
        data = {"email": "test@example.com"}
        self.assertEqual(detect_resource_type(data), "user")

    def test_detect_resource_type_comment(self):
        data = {"content": "Test", "journal_entry_id": 1}
        self.assertEqual(detect_resource_type(data), "comment")

    def test_detect_resource_type_none(self):
        data = {"unknown": "value"}
        self.assertIsNone(detect_resource_type(data))

    def test_generate_links_entry(self):
        links = generate_links("entry", 1)
        self.assertEqual(links["self"]["href"], "/entries/1")
        self.assertEqual(links["comments"]["href"], "/entries/1/comments")
        self.assertEqual(links["history"]["href"], "/entries/1/history")

    def test_generate_links_user(self):
        links = generate_links("user", 1)
        self.assertEqual(links["self"]["href"], "/users/1")
        self.assertEqual(links["edit"]["href"], "/users/1")

    def test_generate_links_comment(self):
        links = generate_links("comment", 1)
        self.assertEqual(links["self"]["href"], "/entries/1/comments/1")

    def test_generate_links_unknown(self):
        links = generate_links("unknown", 1)
        self.assertEqual(links, {})

if __name__ == "__main__":
    unittest.main()