import pytest
from journalapi import create_app
from extensions import db as _db
import os
import tempfile
import json

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'test-secret-key'
    })

    with app.app_context():
        _db.create_all()

    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def db(app):
    """Database fixture."""
    with app.app_context():
        yield _db
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
def auth_headers(client):
    """Fixture to get authentication headers."""
    # Register a test user
    response = client.post('/api/users/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'  # Make sure password meets requirements
    })
    assert response.status_code == 201, f"Registration failed: {response.get_data(as_text=True)}"
    
    # Login to get token
    response = client.post('/api/users/login', json={
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    assert response.status_code == 200, f"Login failed: {response.get_data(as_text=True)}"
    
    # Get the token from JSON response
    response_data = response.get_json()
    token = response_data['token']
    
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }