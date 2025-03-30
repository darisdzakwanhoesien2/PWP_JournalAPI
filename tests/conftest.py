import sys
import os
import flask

# Add the root directory to sys.path so imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app
from extensions import db  # Assuming you defined db in extensions.py
from journalapi.models import User, JournalEntry, Comment

@pytest.fixture(scope="module")
def test_client():
    """Creates a Flask test client and sets up the in-memory test database."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    
    with app.app_context():
        db.init_app(app)
        db.create_all()
        yield app.test_client()
        db.drop_all()
