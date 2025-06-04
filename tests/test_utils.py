# tests/test_utils.py
"""Tests for utility functions."""
import pytest
from journalapi.utils import json_response, authenticate_user, generate_token
from journalapi.models import User
from werkzeug.security import generate_password_hash
from extensions import db

def test_json_response():
    """Test json_response function."""
    response = json_response({"message": "test"}, 200)
    assert response.status_code == 200
    assert response.json == {"message": "test"}

def test_authenticate_user(app, db_session):
    """Test authenticate_user function."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password=generate_password_hash("password")
        )
        db.session.add(user)
        db.session.commit()
        assert authenticate_user("testuser", "password") is not None
        assert authenticate_user("testuser", "wrong") is None
        assert authenticate_user("nonexistent", "password") is None

def test_generate_token(app, db_session):
    """Test generate_token function."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com", password="hashed")
        db.session.add(user)
        db.session.commit()
        token = generate_token(user)
        assert isinstance(token, str)
        assert len(token) > 0