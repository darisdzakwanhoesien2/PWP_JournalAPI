"""Tests for API resource endpoints."""
import json
import pytest
from journalapi.models import User, JournalEntry, Comment, EditHistory
from werkzeug.security import generate_password_hash

def test_user_endpoints(client, auth_headers: dict, app, db_session):
    """Test user-related endpoints."""
    with app.app_context():
        # Register
        response = client.post("/api/users/register", json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123"
        })
        assert response.status_code == 201
        assert "registered" in response.json["message"].lower()
        # Login
        response = client.post("/api/users/login", json={
            "email": "newuser@example.com",
            "password": "password123"
        })
        assert response.status_code == 200
        assert "token" in response.json
        new_token = response.json["token"]
        # Get user
        user = db_session.session.query(User).filter_by(email="newuser@example.com").first()
        response = client.get(f"/api/users/{user.id}", headers={"Authorization": f"Bearer {new_token}"})
        assert response.status_code == 200
        assert response.json["username"] == "newuser"
        # Invalid get (non-existent user)
        response = client.get(f"/api/users/{user.id + 1}", headers={"Authorization": f"Bearer {new_token}"})
        assert response.status_code == 404
        # Update user
        response = client.put(f"/api/users/{user.id}", json={
            "username": "updateduser",
            "email": "updated@example.com",
            "password": "newpassword123"
        }, headers={"Authorization": f"Bearer {new_token}"})
        assert response.status_code == 200
        assert "updated" in response.json["message"].lower()
        # Invalid update (short password)
        response = client.put(f"/api/users/{user.id}", json={
            "password": "short"
        }, headers={"Authorization": f"Bearer {new_token}"})
        assert response.status_code == 422
        # Delete user
        response = client.delete(f"/api/users/{user.id}", headers={"Authorization": f"Bearer {new_token}"})
        assert response.status_code == 200
        assert "deleted" in response.json["message"].lower()
        # Unauthorized access
        other_user = User(
            username="otheruser",
            email="other@example.com",
            password=generate_password_hash("password123")
        )
        db_session.session.add(other_user)
        db_session.session.commit()
        # Ensure other_user.id is different from user.id
        if other_user.id == user.id:
            other_user.id += 1
            db_session.session.commit()
        other_token = client.post("/api/users/login", json={
            "email": "other@example.com",
            "password": "password123"
        }).json["token"]
        response = client.get(f"/api/users/{other_user.id}", headers={"Authorization": f"Bearer {new_token}"})
        print(f"DEBUG: Unauthorized access test - requested user_id={other_user.id}, token belongs to user_id={user.id}, response status={response.status_code}")
        assert response.status_code == 403
        response = client.get(f"/api/users/{other_user.id}", headers={"Authorization": f"Bearer {other_token}"})
        assert response.status_code == 200

def test_journal_entry_endpoints(client, auth_headers: dict, app, db_session):
    """Test journal entry endpoints."""
    with app.app_context():
        user = db_session.session.query(User).first()
        # Create entry
        response = client.post("/api/journal_entries", json={
            "title": "Test Entry",
            "content": "Content",
            "tags": ["test"]
        }, headers=auth_headers)
        assert response.status_code == 201
        assert "entry_id" in response.json
        entry_id = response.json["entry_id"]
        # Invalid create (empty title)
        response = client.post("/api/journal_entries", json={
            "title": "",
            "content": "Invalid"
        }, headers=auth_headers)
        assert response.status_code == 422
        # Get entries
        response = client.get("/api/journal_entries", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json) > 0
        assert response.json[0]["title"] == "Test Entry"
        # Get entry
        response = client.get(f"/api/journal_entries/{entry_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json["title"] == "Test Entry"
        # Invalid get (non-existent entry)
        response = client.get(f"/api/journal_entries/{entry_id + 1}", headers=auth_headers)
        assert response.status_code == 404
        # Update entry
        response = client.put(f"/api/journal_entries/{entry_id}", json={
            "title": "Updated Entry",
            "content": "Updated Content",
            "tags": ["updated"]
        }, headers=auth_headers)
        assert response.status_code == 200
        assert "updated" in response.json["message"].lower()
        # Invalid update (empty title)
        response = client.put(f"/api/journal_entries/{entry_id}", json={
            "title": "",
            "content": "Invalid"
        }, headers=auth_headers)
        assert response.status_code == 422
        # Delete entry
        response = client.delete(f"/api/journal_entries/{entry_id}", headers=auth_headers)
        assert response.status_code == 200
        assert "deleted" in response.json["message"].lower()
        # Unauthorized access
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
        other_entry = JournalEntry(user_id=user.id, title="Other Entry", content="Other")
        db_session.session.add(other_entry)
        db_session.session.commit()
        response = client.get(f"/api/journal_entries/{other_entry.id}", headers={"Authorization": f"Bearer {other_token}"})
        assert response.status_code == 403

def test_comment_endpoints(client, auth_headers: dict, app, db_session):
    """Test comment endpoints."""
    with app.app_context():
        user = db_session.session.query(User).first()
        entry = JournalEntry(user_id=user.id, title="Test Entry", content="Content")
        db_session.session.add(entry)
        db_session.session.commit()
        # Add comment
        response = client.post(f"/api/journal_entries/{entry.id}/comments", json={
            "content": "Test comment"
        }, headers=auth_headers)
        assert response.status_code == 201
        assert "comment_id" in response.json
        comment_id = response.json["comment_id"]
        # Invalid add (empty content)
        response = client.post(f"/api/journal_entries/{entry.id}/comments", json={
            "content": ""
        }, headers=auth_headers)
        assert response.status_code == 422
        # Get comments
        response = client.get(f"/api/journal_entries/{entry.id}/comments", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json) > 0
        assert response.json[0]["content"] == "Test comment"
        # Invalid get (non-existent entry)
        response = client.get(f"/api/journal_entries/{entry.id + 1}/comments", headers=auth_headers)
        assert response.status_code == 404
        # Update comment
        response = client.put(f"/api/journal_entries/{entry.id}/comments/{comment_id}", json={
            "content": "Updated comment"
        }, headers=auth_headers)
        assert response.status_code == 200
        assert "fully replaced" in response.json["message"].lower()
        # Invalid update (empty content)
        response = client.put(f"/api/journal_entries/{entry.id}/comments/{comment_id}", json={
            "content": ""
        }, headers=auth_headers)
        assert response.status_code == 422
        # Delete comment
        response = client.delete(f"/api/journal_entries/{entry.id}/comments/{comment_id}", headers=auth_headers)
        assert response.status_code == 200
        assert "deleted" in response.json["message"].lower()
        # Unauthorized comment update
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
        response = client.put(f"/api/journal_entries/{entry.id}/comments/{other_comment.id}", json={
            "content": "Unauthorized"
        }, headers={"Authorization": f"Bearer {other_token}"})
        assert response.status_code == 404

def test_edit_history_endpoint(client, auth_headers: dict, app, db_session):
    """Test edit history endpoint."""
    with app.app_context():
        user = db_session.session.query(User).first()
        entry = JournalEntry(user_id=user.id, title="Test Entry", content="Content")
        db_session.session.add(entry)
        db_session.session.commit()
        history = EditHistory(journal_entry_id=entry.id, old_content="Old Content")
        db_session.session.add(history)
        db_session.session.commit()
        # Valid retrieval
        response = client.get(f"/api/journal_entries/{entry.id}/history", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 1
        assert response.json[0]["old_content"] == "Old Content"
        # Non-existent entry
        response = client.get(f"/api/journal_entries/{entry.id + 1}/history", headers=auth_headers)
        assert response.status_code == 404
        # Unauthorized access
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
        response = client.get(f"/api/journal_entries/{entry.id}/history", headers={"Authorization": f"Bearer {other_token}"})
        assert response.status_code == 403
