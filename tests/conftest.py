"""Pytest fixtures for the Journal API tests."""
import os
import pytest
import sys
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from journalapi import create_app
from journalapi.models import User
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    """Create a Flask app with an in-memory database."""
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })
    with app.app_context():
        from extensions import db
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture
def db_session(app):
    """Provide the SQLAlchemy db session for tests."""
    with app.app_context():
        from extensions import db
        yield db
        db.session.rollback()

@pytest.fixture
def auth_headers(client, app):
    """Create authentication headers for a test user."""
    with app.app_context():
        from extensions import db
        user = User(
            username="testuser",
            email="test@example.com",
            password=generate_password_hash("password123")
        )
        db.session.add(user)
        db.session.commit()
        response = client.post("/api/users/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 200
        token = response.json["token"]
        return {"Authorization": f"Bearer {token}"}