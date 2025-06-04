# tests/test_handlers.py
"""Tests for handler classes."""
import pytest
from journalapi.handlers.comment_handler import CommentHandler
from journalapi.handlers.user_handler import UserHandler
from journalapi.handlers.journal_entry_handler import JournalEntryHandler
from journalapi.models import User, JournalEntry, Comment
from werkzeug.security import generate_password_hash
from extensions import db

def test_comment_handler(app, db_session):
    """Test CommentHandler methods."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com", password="hashed")
        db.session.add(user)
        db.session.commit()
        entry = JournalEntry(user_id=user.id, title="Test", content="Content")
        db.session.add(entry)
        db.session.commit()
        # Test add_comment
        comment = CommentHandler.add_comment(entry.id, user.id, "Test comment")
        assert comment["content"] == "Test comment"
        # Test get_comments
        comments = CommentHandler.get_comments(entry.id)
        assert len(comments) == 1
        # Test update_comment
        updated = CommentHandler.update_comment(comment["id"], user.id, "Updated")
        assert updated["content"] == "Updated"
        # Test unauthorized update
        assert CommentHandler.update_comment(comment["id"], user.id + 1, "Unauthorized") is None
        # Test delete_comment
        assert CommentHandler.delete_comment(comment["id"], user.id) is True
        assert CommentHandler.delete_comment(comment["id"], user.id) is False

def test_user_handler(app, db_session):
    """Test UserHandler methods."""
    with app.app_context():
        # Test register_user
        user = UserHandler.register_user("testuser", "test@example.com", "password")
        assert user.username == "testuser"
        assert UserHandler.register_user("testuser", "test@example.com", "password") is None
        # Test login_user
        assert UserHandler.login_user("test@example.com", "password") is not None
        assert UserHandler.login_user("test@example.com", "wrong") is None
        # Test get_user
        assert UserHandler.get_user(user.id).email == "test@example.com"
        assert UserHandler.get_user(user.id + 1) is None
        # Test update_user
        updated = UserHandler.update_user(user.id, username="newuser", email="new@example.com")
        assert updated.username == "newuser"
        assert UserHandler.update_user(user.id + 1, username="invalid") is None
        # Test delete_user
        assert UserHandler.delete_user(user.id) is True
        assert UserHandler.delete_user(user.id) is False

def test_journal_entry_handler(app, db_session):
    """Test JournalEntryHandler methods."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com", password="hashed")
        db.session.add(user)
        db.session.commit()
        # Test create_entry
        result = JournalEntryHandler.create_entry(user.id, "Test", "Content", ["tag1"])
        entry_id = result["entry_id"]
        assert JournalEntry.query.get(entry_id).title == "Test"
        # Test get_entries
        entries = JournalEntryHandler.get_entries(user.id)
        assert len(entries) == 1
        # Test get_entry
        entry = JournalEntryHandler.get_entry(entry_id)
        assert entry["title"] == "Test"
        assert JournalEntryHandler.get_entry(entry_id + 1) is None
        # Test update_entry
        updated = JournalEntryHandler.update_entry(entry_id, title="Updated", tags=["tag2"])
        assert updated["title"] == "Updated"
        assert JournalEntryHandler.update_entry(entry_id + 1, title="Invalid") is None
        # Test delete_entry
        assert JournalEntryHandler.delete_entry(entry_id) is True
        assert JournalEntryHandler.delete_entry(entry_id) is False