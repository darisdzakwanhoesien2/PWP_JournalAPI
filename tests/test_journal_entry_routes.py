"""Tests for journal entry-related API routes."""
import json
import pytest
from journalapi.models import User, JournalEntry
from werkzeug.security import generate_password_hash

def test_create_entry(client, auth_headers: dict, app, db_session):
    """Test creating a journal entry."""
    with app.app_context():
        # Valid entry
        response = client.post(
            "/api/journal_entries",
            json={
                "title": "Test Entry",
                "content": "Testing journal entry creation",
                "tags": ["test", "journal"]
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        assert "entry_id" in response.json
        entry = db_session.session.query(JournalEntry).get(response.json["entry_id"])
        assert entry.title == "Test Entry"
        assert entry.to_dict()["tags"] == ["test", "journal"]
        # Invalid entry (empty title/content)
        response = client.post(
            "/api/journal_entries",
            json={"title": "", "content": ""},
            headers=auth_headers
        )
        assert response.status_code == 422
        assert "errors" in response.json

def test_get_entries(client, auth_headers: dict, app, db_session):
    """Test retrieving all journal entries."""
    with app.app_context():
        user = db_session.session.query(User).first()
        entry = JournalEntry(user_id=user.id, title="Test Entry", content="Content", tags=json.dumps(["test"]))
        db_session.session.add(entry)
        db_session.session.commit()
        # Valid retrieval
        response = client.get("/api/journal_entries", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]["title"] == "Test Entry"
        # No entries
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
        response = client.get("/api/journal_entries", headers={"Authorization": f"Bearer {other_token}"})
        assert response.status_code == 200
        assert response.json == []

def test_get_entry(client, auth_headers: dict, app, db_session):
    """Test retrieving a single journal entry."""
    with app.app_context():
        user = db_session.session.query(User).first()
        entry = JournalEntry(user_id=user.id, title="Test Entry", content="Content")
        db_session.session.add(entry)
        db_session.session.commit()
        # Valid retrieval
        response = client.get(f"/api/journal_entries/{entry.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json["title"] == "Test Entry"
        # Non-existent entry
        response = client.get(f"/api/journal_entries/{entry.id + 1}", headers=auth_headers)
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
        response = client.get(f"/api/journal_entries/{entry.id}", headers={"Authorization": f"Bearer {other_token}"})
        assert response.status_code == 403

def test_update_entry(client, auth_headers: dict, app, db_session):
    """Test updating a journal entry."""
    with app.app_context():
        user = db_session.session.query(User).first()
        entry = JournalEntry(user_id=user.id, title="Test Entry", content="Content")
        db_session.session.add(entry)
        db_session.session.commit()
        # Valid update
        response = client.put(
            f"/api/journal_entries/{entry.id}",
            json={
                "title": "Updated Entry",
                "content": "Updated Content",
                "tags": ["updated"]
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "updated" in response.json["message"].lower()
        updated_entry = db_session.session.query(JournalEntry).get(entry.id)
        assert updated_entry.title == "Updated Entry"
        # Invalid update (empty title)
        response = client.put(
            f"/api/journal_entries/{entry.id}",
            json={"title": "", "content": "Invalid"},
            headers=auth_headers
        )
        assert response.status_code == 422
        # Non-existent entry
        response = client.put(
            f"/api/journal_entries/{entry.id + 1}",
            json={"title": "Invalid", "content": "Invalid"},
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
            f"/api/journal_entries/{entry.id}",
            json={"title": "Unauthorized", "content": "Unauthorized"},
            headers={"Authorization": f"Bearer {other_token}"}
        )
        assert response.status_code == 403

def test_delete_entry(client, auth_headers: dict, app, db_session):
    """Test deleting a journal entry."""
    with app.app_context():
        user = db_session.session.query(User).first()
        entry = JournalEntry(user_id=user.id, title="Test Entry", content="Content")
        db_session.session.add(entry)
        db_session.session.commit()
        # Valid deletion
        response = client.delete(f"/api/journal_entries/{entry.id}", headers=auth_headers)
        assert response.status_code == 200
        assert "deleted" in response.json["message"].lower()
        assert db_session.session.query(JournalEntry).get(entry.id) is None
        # Non-existent entry
        response = client.delete(f"/api/journal_entries/{entry.id + 1}", headers=auth_headers)
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
        other_entry = JournalEntry(user_id=user.id, title="Other Entry", content="Other")
        db_session.session.add(other_entry)
        db_session.session.commit()
        response = client.delete(
            f"/api/journal_entries/{other_entry.id}",
            headers={"Authorization": f"Bearer {other_token}"}
        )
        assert response.status_code == 403