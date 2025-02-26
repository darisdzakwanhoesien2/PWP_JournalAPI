import sys
import os

# Add the parent directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, db
from models import User, JournalEntry, EditHistory, Comment

@pytest.fixture(scope="module")
def test_client():
    """Creates a Flask test client and sets up the database."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()
