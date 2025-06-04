"""Tests for database models."""
import json
import pytest
from journalapi.models import User, JournalEntry, Comment, EditHistory
from extensions import db
from werkzeug.security import generate_password_hash

def test_user_model(app, db_session):
    """Test User model functionality."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password=generate_password_hash("password")
        )
        db.session.add(user)
        db.session.commit()
        assert user.check_password("password")
        assert user.to_dict()["username"] == "testuser"
        assert str(user) == "<User testuser>"

def test_journal_entry_model(app, db_session):
    """Test JournalEntry model functionality."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com", password="hashed")
        db.session.add(user)
        db.session.commit()
        entry = JournalEntry(
            user_id=user.id,
            title="Test",
            content="Content",
            tags=json.dumps(["tag1"])
        )
        db.session.add(entry)
        db.session.commit()
        assert entry.to_dict()["tags"] == ["tag1"]
        assert str(entry) == f"<JournalEntry {entry.id}>"

def test_comment_model(app, db_session):
    """Test Comment model functionality."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com", password="hashed")
        db.session.add(user)
        db.session.commit()
        entry = JournalEntry(user_id=user.id, title="Test", content="Content")
        db.session.add(entry)
        db.session.commit()
        comment = Comment(journal_entry_id=entry.id, user_id=user.id, content="Test")
        db.session.add(comment)
        db.session.commit()
        assert comment.to_dict()["content"] == "Test"
        assert str(comment) == f"<Comment {comment.id}>"

def test_edit_history_model(app, db_session):
    """Test EditHistory model functionality."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com", password="hashed")
        db.session.add(user)
        db.session.commit()
        entry = JournalEntry(user_id=user.id, title="Test", content="Content")
        db.session.add(entry)
        db.session.commit()
        history = EditHistory(journal_entry_id=entry.id, old_content="Old")
        db.session.add(history)
        db.session.commit()
        assert history.to_dict()["old_content"] == "Old"
        assert str(history) == f"<EditHistory {history.id}>"