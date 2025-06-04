"""Tests for application initialization."""
import pytest
from journalapi import create_app
from extensions import db

def test_create_app():
    """Test create_app function."""
    app = create_app()
    assert app.config["SECRET_KEY"] == "dev"
    assert "journal.db" in app.config["SQLALCHEMY_DATABASE_URI"]
    assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is False
    with app.app_context():
        assert db.session is not None

def test_create_app_with_test_config():
    """Test create_app with test configuration."""
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret-key"
    }
    app = create_app(test_config)
    assert app.config["TESTING"] is True
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"
    assert app.config["JWT_SECRET_KEY"] == "test-secret-key"