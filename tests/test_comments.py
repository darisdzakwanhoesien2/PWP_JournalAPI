# tests/test_comments.py
import unittest
import json
from app import create_app
from extensions import db
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
from journalapi.models import User, JournalEntry, Comment

class TestComments(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            hashed_password = generate_password_hash("password123")
            user = User(username="testuser", email="test@example.com", password=hashed_password)
            db.session.add(user)
            db.session.commit()  # Commit user first
            entry = JournalEntry(
                user_id=user.id,
                title="Test Entry",
                content="Test Content",
                tags=json.dumps(["test"]),
                sentiment_score=0.75,
                sentiment_tag=json.dumps(["positive"])
            )
            db.session.add(entry)
            db.session.commit()
            self.user_id = user.id
            self.entry_id = entry.id
            self.token = create_access_token(identity=str(self.user_id))

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_comments_empty(self):
        response = self.client.get(
            f"/entries/{self.entry_id}/comments",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_get_comments_empty] response JSON:", response.get_json())
        print("DEBUG [test_get_comments_empty] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data["comments"]), 0)
        self.assertIn("_links", data)
        links = data["_links"]
        self.assertEqual(links["self"]["href"], f"/entries/{self.entry_id}/comments")
        self.assertEqual(links["entry"]["href"], f"/entries/{self.entry_id}")

    def test_create_comment(self):
        response = self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": "Test Comment"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_create_comment] response JSON:", response.get_json())
        print("DEBUG [test_create_comment] status code:", response.status_code)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("comment_id", data)
        comment_id = data["comment_id"]
        self.assertIn("_links", data)
        links = data["_links"]
        self.assertEqual(links["self"]["href"], f"/entries/{self.entry_id}/comments/{comment_id}")
        self.assertEqual(links["edit"]["href"], f"/entries/{self.entry_id}/comments/{comment_id}")
        self.assertEqual(links["delete"]["href"], f"/entries/{self.entry_id}/comments/{comment_id}")
        self.assertEqual(links["entry"]["href"], f"/entries/{self.entry_id}")

    def test_get_comments(self):
        create_response = self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": "Test Comment"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(create_response.status_code, 201)
        comment_id = create_response.get_json()["comment_id"]

        response = self.client.get(
            f"/entries/{self.entry_id}/comments",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_get_comments] response JSON:", response.get_json())
        print("DEBUG [test_get_comments] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data["comments"]), 1)
        comment = data["comments"][0]
        self.assertEqual(comment["content"], "Test Comment")
        self.assertIn("_links", comment)
        links = comment["_links"]
        self.assertEqual(links["self"]["href"], f"/entries/{self.entry_id}/comments/{comment_id}")
        self.assertEqual(links["edit"]["href"], f"/entries/{self.entry_id}/comments/{comment_id}")
        self.assertEqual(links["delete"]["href"], f"/entries/{self.entry_id}/comments/{comment_id}")
        self.assertEqual(links["entry"]["href"], f"/entries/{self.entry_id}")
        self.assertIn("_links", data)
        top_links = data["_links"]
        self.assertEqual(top_links["self"]["href"], f"/entries/{self.entry_id}/comments")
        self.assertEqual(top_links["entry"]["href"], f"/entries/{self.entry_id}")

    def test_update_comment(self):
        create_response = self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": "Original Comment"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(create_response.status_code, 201)
        comment_id = create_response.get_json()["comment_id"]

        response = self.client.put(
            f"/entries/{self.entry_id}/comments/{comment_id}",
            json={"content": "Updated Comment"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_update_comment] response JSON:", response.get_json())
        print("DEBUG [test_update_comment] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("message", data)
        self.assertIn("_links", data)
        links = data["_links"]
        self.assertEqual(links["self"]["href"], f"/entries/{self.entry_id}/comments/{comment_id}")
        self.assertEqual(links["edit"]["href"], f"/entries/{self.entry_id}/comments/{comment_id}")
        self.assertEqual(links["delete"]["href"], f"/entries/{self.entry_id}/comments/{comment_id}")
        self.assertEqual(links["entry"]["href"], f"/entries/{self.entry_id}")

    def test_update_comment_invalid_data(self):
        create_response = self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": "Original Comment"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(create_response.status_code, 201)
        comment_id = create_response.get_json()["comment_id"]

        response = self.client.put(
            f"/entries/{self.entry_id}/comments/{comment_id}",
            json={"content": ""},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_update_comment_invalid_data] response JSON:", response.get_json())
        print("DEBUG [test_update_comment_invalid_data] status code:", response.status_code)
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn("errors", data)

    def test_delete_comment(self):
        create_response = self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": "Test Comment"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(create_response.status_code, 201)
        comment_id = create_response.get_json()["comment_id"]

        response = self.client.delete(
            f"/entries/{self.entry_id}/comments/{comment_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("DEBUG [test_delete_comment] response JSON:", response.get_json())
        print("DEBUG [test_delete_comment] status code:", response.status_code)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("message", data)
        self.assertIn("_links", data)
        links = data["_links"]
        self.assertEqual(links["self"]["href"], f"/entries/{self.entry_id}/comments")
        self.assertEqual(links["entry"]["href"], f"/entries/{self.entry_id}")

    def test_delete_comment_unauthorized(self):
        create_response = self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": "Test Comment"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(create_response.status_code, 201)
        comment_id = create_response.get_json()["comment_id"]

        with self.app.app_context():
            hashed_password = generate_password_hash("password123")
            other_user = User(username="otheruser", email="other@example.com", password=hashed_password)
            db.session.add(other_user)
            db.session.commit()
            other_token = create_access_token(identity=str(other_user.id))

        response = self.client.delete(
            f"/entries/{self.entry_id}/comments/{comment_id}",
            headers={"Authorization": f"Bearer {other_token}"}
        )
        print("DEBUG [test_delete_comment_unauthorized] response JSON:", response.get_json())
        print("DEBUG [test_delete_comment_unauthorized] status code:", response.status_code)
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("error", data)

    def test_comment_to_dict(self):
        create_response = self.client.post(
            f"/entries/{self.entry_id}/comments",
            json={"content": "Test Comment"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(create_response.status_code, 201)
        comment_id = create_response.get_json()["comment_id"]

        with self.app.app_context():
            comment = db.session.get(Comment, comment_id)
            comment_dict = comment.to_dict()
            self.assertEqual(comment_dict["content"], "Test Comment")
            self.assertEqual(comment_dict["journal_entry_id"], self.entry_id)
            self.assertEqual(comment_dict["user_id"], self.user_id)
if __name__ == "__main__":
    unittest.main()