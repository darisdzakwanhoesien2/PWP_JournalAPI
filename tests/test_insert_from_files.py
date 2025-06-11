import pytest
import csv
from datetime import datetime, timezone
from insert_from_files import insert_users, insert_journal_entries, insert_edit_history, insert_comments
from journalapi.models import User, JournalEntry, EditHistory, Comment
from werkzeug.security import generate_password_hash

def create_test_csv(tmp_path, filename, data):
    """Create a test CSV file in a temporary directory."""
    file_path = tmp_path / filename
    with open(file_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)
    return file_path

def test_insert_users(app, db_session, tmp_path):
    """Test the insert_users function."""
    # Create test data
    user_data = [
        ["testuser11", "test11@example.com", "password"],
        ["testuser22", "test22@example.com", "password"],
    ]
    file_path = create_test_csv(tmp_path, "users.csv", user_data)

    # Call the insert_users function
    insert_users(file_path)

    # Assert that the users have been inserted into the database
    with app.app_context():
        users = db_session.session.query(User).all()
        print(f"Users in database: {users}")
        assert len(users) == 2
        assert users[0].username == "testuser11"
        assert users[0].email == "test11@example.com"
        assert users[1].username == "testuser22"
        assert users[1].email == "test22@example.com"

def test_insert_journal_entries(app, db_session, tmp_path):
    """Test the insert_journal_entries function."""
    # Create test data
    entry_data = [
        [1, "Test Title 1", "Test Content 1", "tag1, tag2", 0.5, "positive"],
        [2, "Test Title 2", "Test Content 2", "tag3, tag4", -0.5, "negative"],
    ]
    file_path = create_test_csv(tmp_path, "journal_entries.csv", entry_data)

    # Call the insert_journal_entries function
    insert_journal_entries(file_path)

    # Assert that the journal entries have been inserted into the database
    entries = db_session.session.query(JournalEntry).all()
    assert len(entries) == 2
    assert entries[0].title == "Test Title 1"
    assert entries[0].content == "Test Content 1"
    assert entries[1].title == "Test Title 2"
    assert entries[1].content == "Test Content 2"

def test_insert_edit_history(app, db_session, tmp_path):
    """Test the insert_edit_history function."""
    # Create test data
    edit_data = [
        [1, 1, "Previous Content 1", "New Content 1"],
        [2, 2, "Previous Content 2", "New Content 2"],
    ]
    file_path = create_test_csv(tmp_path, "edit_history.csv", edit_data)

    # Call the insert_edit_history function
    insert_edit_history(file_path)

    # Assert that the edit history entries have been inserted into the database
    edits = db_session.session.query(EditHistory).all()
    assert len(edits) == 2
    assert edits[0].previous_content == "Previous Content 1"
    assert edits[0].new_content == "New Content 1"
    assert edits[1].previous_content == "Previous Content 2"
    assert edits[1].new_content == "New Content 2"

def test_insert_comments(app, db_session, tmp_path):
    """Test the insert_comments function."""
    # Create test data
    comment_data = [
        [1, 1, "Test Comment 1"],
        [2, 2, "Test Comment 2"],
    ]
    file_path = create_test_csv(tmp_path, "comments.csv", comment_data)

    # Call the insert_comments function
    insert_comments(file_path)

    # Assert that the comments have been inserted into the database
    comments = db_session.session.query(Comment).all()
    assert len(comments) == 2
    assert comments[0].content == "Test Comment 1"
    assert comments[1].content == "Test Comment 2"
