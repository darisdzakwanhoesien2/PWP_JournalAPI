"""Tests for comment-related API routes."""
import pytest
from journalapi.models import User, JournalEntry, Comment
from werkzeug.security import generate_password_hash

def test_add_comment(client, auth_headers: dict, app, db_session):
    """Test adding a comment to a journal entry."""
    with app.app_context():
        user = db_session.session.query(User).first()
        entry = JournalEntry(user_id=user.id, title="Test Entry", content="Content")
        db_session.session.add(entry)
        db_session.session.commit()
        # Valid comment
        response = client.post(
            f"/api/journal_entries/{entry.id}/comments",
            json={"content": "This is a test comment."},
            headers=auth_headers
        )
        assert response.status_code == 201
        assert "comment_id" in response.json
        comment = db_session.session.query(Comment).get(response.json["comment_id"])
        assert comment.content == "This is a test comment."
        # Invalid comment (empty content)
        response = client.post(
            f"/api/journal_entries/{entry.id}/comments",
            json={"content": ""},
            headers=auth_headers
        )
        assert response.status_code == 422
        assert "errors" in response.json
        # Non-existent entry
        response = client.post(
            f"/api/journal_entries/{entry.id + 1}/comments",
            json={"content": "Invalid entry"},
            headers=auth_headers
        )
        assert response.status_code == 404

def test_get_comments(client, auth_headers: dict, app, db_session):
    """Test retrieving comments for a journal entry."""
    with app.app_context():
        user = db_session.session.query(User).first()
        entry = JournalEntry(user_id=user.id, title="Test Entry", content="Content")
        db_session.session.add(entry)
        db_session.session.commit()
        comment = Comment(journal_entry_id=entry.id, user_id=user.id, content="Test comment")
        db_session.session.add(comment)
        db_session.session.commit()
        # Valid retrieval
        response = client.get(
            f"/api/journal_entries/{entry.id}/comments",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]["content"] == "Test comment"
        assert "_links" in response.json[0]
        # Non-existent entry
        response = client.get(
            f"/api/journal_entries/{entry.id + 1}/comments",
            headers=auth_headers
        )
        assert response.status_code == 404
        # Empty comments
        new_entry = JournalEntry(user_id=user.id, title="Empty Entry", content="No comments")
        db_session.session.add(new_entry)
        db_session.session.commit()
        response = client.get(
            f"/api/journal_entries/{new_entry.id}/comments",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json == []

def test_update_comment(client, auth_headers: dict, app, db_session):
    """Test updating a comment."""
    with app.app_context():
        user = db_session.session.query(User).first()
        entry = JournalEntry(user_id=user.id, title="Test Entry", content="Content")
        db_session.session.add(entry)
        db_session.session.commit()
        comment = Comment(journal_entry_id=entry.id, user_id=user.id, content="Original")
        db_session.session.add(comment)
        db_session.session.commit()
        # Valid update
        response = client.put(
            f"/api/journal_entries/{entry.id}/comments/{comment.id}",
            json={"content": "Updated Comment"},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "fully replaced" in response.json["message"].lower()
        updated_comment = db_session.session.query(Comment).get(comment.id)
        assert updated_comment.content == "Updated Comment"
        # Invalid update (empty content)
        response = client.put(
            f"/api/journal_entries/{entry.id}/comments/{comment.id}",
            json={"content": ""},
            headers=auth_headers
        )
        assert response.status_code == 422
        # Non-existent comment
        response = client.put(
            f"/api/journal_entries/{entry.id}/comments/{comment.id + 1}",
            json={"content": "Invalid"},
            headers=auth_headers
        )
        assert response.status_code == 404
        # Unauthorized update
        other_user = User(
            username="otheruser",
            email="other@example.com",
            password=generate_password_hash("password123")
        )
        db_session.session.add(other_user)
        db_session.session.commit()
        other_token = client.post("/api/users/login", json={
            "email": "other@example.com",
            "password": "password123"
        }).json["token"]
        response = client.put(
            f"/api/journal_entries/{entry.id}/comments/{comment.id}",
            json={"content": "Unauthorized"},
            headers={"Authorization": f"Bearer {other_token}"}
        )
        assert response.status_code == 404

def test_delete_comment(client, auth_headers: dict, app, db_session):
    """Test deleting a comment."""
    with app.app_context():
        user = db_session.session.query(User).first()
        entry = JournalEntry(user_id=user.id, title="Test Entry", content="Content")
        db_session.session.add(entry)
        db_session.session.commit()
        comment = Comment(journal_entry_id=entry.id, user_id=user.id, content="To delete")
        db_session.session.add(comment)
        db_session.session.commit()
        # Valid deletion
        response = client.delete(
            f"/api/journal_entries/{entry.id}/comments/{comment.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "deleted" in response.json["message"].lower()
        assert db_session.session.query(Comment).get(comment.id) is None
        # Non-existent comment
        response = client.delete(
            f"/api/journal_entries/{entry.id}/comments/{comment.id + 1}",
            headers=auth_headers
        )
        assert response.status_code == 404
        # Unauthorized deletion
        other_user = User(
            username="otheruser",
            email="other@example.com",
            password=generate_password_hash("password123")
        )
        db_session.session.add(other_user)
        db_session.session.commit()
        other_token = client.post("/api/users/login", json={
            "email": "other@example.com",
            "password": "password123"
        }).json["token"]
        other_comment = Comment(journal_entry_id=entry.id, user_id=user.id, content="Other")
        db_session.session.add(other_comment)
        db_session.session.commit()
        response = client.delete(
            f"/api/journal_entries/{entry.id}/comments/{other_comment.id}",
            headers={"Authorization": f"Bearer {other_token}"}
        )
        assert response.status_code == 404