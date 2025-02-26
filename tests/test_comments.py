import sys
import os

# Add the parent directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from models.comment import Comment

class TestCommentRoutes(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_add_comment(self):
        response = self.app.post("/entries/1/comments", json={
            "user_id": 1,
            "content": "This is a test comment"
        })
        self.assertEqual(response.status_code, 201)

    def test_get_comments(self):
        response = self.app.get("/entries/1/comments")
        self.assertEqual(response.status_code, 200)

    def test_update_comment(self):
        self.app.post("/entries/1/comments", json={"user_id": 1, "content": "Test"})
        response = self.app.put("/comments/1", json={"content": "Updated test comment"})
        self.assertEqual(response.status_code, 200)

    def test_delete_comment(self):
        self.app.post("/entries/1/comments", json={"user_id": 1, "content": "Test"})
        response = self.app.delete("/comments/1")
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
