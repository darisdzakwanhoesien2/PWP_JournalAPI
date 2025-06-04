"""Tests for user-related API routes."""
import pytest
from journalapi.models import User
from werkzeug.security import generate_password_hash

def test_register_user(client, app, db_session):
    """Test registering a new user."""
    with app.app_context():
        # Valid registration
        response = client.post("/api/users/register", json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123"
        })
        assert response.status_code == 201
        assert "registered" in response.json["message"].lower()
        user = db_session.session.query(User).filter_by(email="newuser@example.com").first()
        assert user.username == "newuser"
        # Duplicate email
        response = client.post("/api/users/register", json={
            "username": "anotheruser",
            "email": "newuser@example.com",
            "password": "password123"
        })
        assert response.status_code == 400
        # Invalid input (short password)
        response = client.post("/api/users/register", json={
            "username": "invalid",
            "email": "invalid@example.com",
            "password": "short"
        })
        assert response.status_code == 422

def test_login_user(client, app, db_session):
    """Test logging in a user."""
    with app.app_context():
        # Setup test user
        user = User(
            username="testuser",
            email="test@example.com",
            password=generate_password_hash("password123")
        )
        db_session.session.add(user)
        db_session.session.commit()
        # Valid login
        response = client.post("/api/users/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 200
        assert "token" in response.json
        # Invalid password
        response = client.post("/api/users/login", json={
            "email": "test@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        # Non-existent user
        response = client.post("/api/users/login", json={
            "email": "nonexistent@example.com",
            "password": "password123"
        })
        assert response.status_code == 401
        # Invalid input (missing email)
        response = client.post("/api/users/login", json={
            "password": "password123"
        })
        assert response.status_code == 422

def test_get_user(client, auth_headers: dict, app, db_session):
    """Test retrieving user data."""
    with app.app_context():
        user = db_session.session.query(User).first()
        # Valid retrieval
        response = client.get(f"/api/users/{user.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json["username"] == "testuser"
        # Non-existent user
        response = client.get(f"/api/users/{user.id + 1}", headers=auth_headers)
        assert response.status_code == 404
        # Unauthorized access
        other_user = User(
            username="otheruser",
            email="other@example.com",
            password=generate_password_hash("password123")
        )
        db_session.session.add(other_user)
        db_session.session.commit()
        response = client.get(f"/api/users/{other_user.id}", headers=auth_headers)
        assert response.status_code == 403

def test_update_user(client, auth_headers: dict, app, db_session):
    """Test updating user data."""
    with app.app_context():
        user = db_session.session.query(User).first()
        # Valid update
        response = client.put(
            f"/api/users/{user.id}",
            json={
                "username": "updateduser",
                "email": "updated@example.com",
                "password": "newpassword123"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "updated" in response.json["message"].lower()
        updated_user = db_session.session.query(User).get(user.id)
        assert updated_user.username == "updateduser"
        assert updated_user.check_password("newpassword123")
        # Invalid update (short password)
        response = client.put(
            f"/api/users/{user.id}",
            json={"password": "short"},
            headers=auth_headers
        )
        assert response.status_code == 422
        # Non-existent user
        response = client.put(
            f"/api/users/{user.id + 1}",
            json={"username": "invalid"},
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
        response = client.put(
            f"/api/users/{other_user.id}",
            json={"username": "unauthorized"},
            headers=auth_headers
        )
        assert response.status_code == 403

def test_delete_user(client, auth_headers: dict, app, db_session):
    """Test deleting a user."""
    with app.app_context():
        user = db_session.session.query(User).first()
        # Valid deletion
        response = client.delete(f"/api/users/{user.id}", headers=auth_headers)
        assert response.status_code == 200
        assert "deleted successfully" in response.json["message"].lower()
        assert db_session.session.query(User).get(user.id) is None
        # Non-existent user
        response = client.delete(f"/api/users/{user.id + 1}", headers=auth_headers)
        assert response.status_code == 404
        # Unauthorized deletion
        other_user = User(
            username="otheruser",
            email="other@example.com",
            password=generate_password_hash("password123")
        )
        db_session.session.add(other_user)
        db_session.session.commit()
        response = client.delete(f"/api/users/{other_user.id}", headers=auth_headers)
        assert response.status_code == 403