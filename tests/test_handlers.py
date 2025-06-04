import pytest
from journalapi.models import User, JournalEntry, Comment, EditHistory
from journalapi.handlers.comment_handler import CommentHandler
from journalapi.handlers.journal_entry_handler import JournalEntryHandler
from journalapi.handlers.user_handler import UserHandler
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

def test_add_comment(db, app):
    """Test adding a comment to a journal entry."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(user)
        db.session.commit()
        
        entry = JournalEntry(
            user_id=user.id,
            title="Test Entry",
            content="Content",
            tags=["test"]
        )
        db.session.add(entry)
        db.session.commit()
        
        comment = CommentHandler.add_comment(
            entry_id=entry.id,
            user_id=user.id,
            content="Test comment"
        )
        
        assert comment["id"] is not None
        assert comment["content"] == "Test comment"
        assert comment["journal_entry_id"] == entry.id
        assert comment["user_id"] == user.id

def test_add_comment_invalid_entry(db, app):
    """Test adding comment to non-existent entry."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(user)
        db.session.commit()
        
        with pytest.raises(ValueError, match="Entry not found"):
            CommentHandler.add_comment(
                entry_id=999,
                user_id=user.id,
                content="Test comment"
            )

def test_add_comment_invalid_content(db, app):
    """Test adding comment with empty content."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(user)
        entry = JournalEntry(
            user_id=user.id,
            title="Test Entry",
            content="Content",
            tags=["test"]
        )
        db.session.add(entry)
        db.session.commit()
        
        with pytest.raises(ValueError, match="Content cannot be empty"):
            CommentHandler.add_comment(
                entry_id=entry.id,
                user_id=user.id,
                content=""
            )

def test_get_comments(db, app):
    """Test retrieving comments for a journal entry."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(user)
        entry = JournalEntry(
            user_id=user.id,
            title="Test Entry",
            content="Content",
            tags=["test"]
        )
        db.session.add(entry)
        db.session.commit()
        
        comment = Comment(
            journal_entry_id=entry.id,
            user_id=user.id,
            content="Test comment"
        )
        db.session.add(comment)
        db.session.commit()
        
        comments = CommentHandler.get_comments(entry_id=entry.id)
        
        assert len(comments) == 1
        assert comments[0]["content"] == "Test comment"
        assert comments[0]["journal_entry_id"] == entry.id

def test_update_comment(db, app):
    """Test updating a comment."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(user)
        entry = JournalEntry(
            user_id=user.id,
            title="Test Entry",
            content="Content",
            tags=["test"]
        )
        db.session.add(entry)
        comment = Comment(
            journal_entry_id=entry.id,
            user_id=user.id,
            content="Original"
        )
        db.session.add(comment)
        db.session.commit()
        
        updated = CommentHandler.update_comment(
            comment_id=comment.id,
            user_id=user.id,
            content="Updated"
        )
        
        assert updated is not None
        assert updated["content"] == "Updated"
        assert updated["id"] == comment.id

def test_update_comment_unauthorized(db, app):
    """Test updating a comment not owned."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(user)
        entry = JournalEntry(
            user_id=user.id,
            title="Test Entry",
            content="Content",
            tags=["test"]
        )
        db.session.add(entry)
        comment = Comment(
            journal_entry_id=entry.id,
            user_id=user.id,
            content="Original"
        )
        db.session.add(comment)
        db.session.commit()
        
        result = CommentHandler.update_comment(
            comment_id=comment.id,
            user_id=999,  # Different user
            content="Not allowed"
        )
        
        assert result is None
        # Verify comment wasn't changed
        db_comment = Comment.query.get(comment.id)
        assert db_comment.content == "Original"

def test_update_comment_not_found(db, app):
    """Test updating a non-existent comment."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(user)
        db.session.commit()
        
        result = CommentHandler.update_comment(
            comment_id=999,
            user_id=user.id,
            content="Not found"
        )
        
        assert result is None

def test_delete_comment(db, app):
    """Test deleting a comment."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(user)
        entry = JournalEntry(
            user_id=user.id,
            title="Test Entry",
            content="Content",
            tags=["test"]
        )
        db.session.add(entry)
        comment = Comment(
            journal_entry_id=entry.id,
            user_id=user.id,
            content="Comment"
        )
        db.session.add(comment)
        db.session.commit()
        
        success = CommentHandler.delete_comment(
            comment_id=comment.id,
            user_id=user.id
        )
        
        assert success
        assert Comment.query.get(comment.id) is None

def test_delete_comment_unauthorized(db, app):
    """Test deleting a comment not owned."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(user)
        entry = JournalEntry(
            user_id=user.id,
            title="Test Entry",
            content="Content",
            tags=["test"]
        )
        db.session.add(entry)
        comment = Comment(
            journal_entry_id=entry.id,
            user_id=user.id,
            content="Comment"
        )
        db.session.add(comment)
        db.session.commit()
        
        success = CommentHandler.delete_comment(
            comment_id=comment.id,
            user_id=999  # Different user
        )
        
        assert not success
        assert Comment.query.get(comment.id) is not None

def test_create_entry(db, app):
    """Test creating a journal entry."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(user)
        db.session.commit()
        
        entry = JournalEntryHandler.create_entry(
            user_id=user.id,
            title="Test Entry",
            content="Content",
            tags=["test"]
        )
        
        assert entry["id"] is not None
        assert entry["title"] == "Test Entry"
        assert entry["content"] == "Content"
        assert entry["tags"] == ["test"]
        assert entry["user_id"] == user.id

def test_create_entry_invalid_title(db, app):
    """Test creating an entry with empty title."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(user)
        db.session.commit()
        
        with pytest.raises(ValueError, match="Title cannot be empty"):
            JournalEntryHandler.create_entry(
                user_id=user.id,
                title="",
                content="Content",
                tags=["test"]
            )

def test_get_entries(db, app):
    """Test retrieving entries for a user."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(user)
        entry = JournalEntry(
            user_id=user.id,
            title="Entry",
            content="Content",
            tags=["test"]
        )
        db.session.add(entry)
        db.session.commit()
        
        entries = JournalEntryHandler.get_entries(user_id=user.id)
        
        assert len(entries) == 1
        assert entries[0]["title"] == "Entry"
        assert entries[0]["user_id"] == user.id

def test_get_entry(db, app):
    """Test retrieving a single entry."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(user)
        entry = JournalEntry(
            user_id=user.id,
            title="Entry",
            content="Content",
            tags=["test"]
        )
        db.session.add(entry)
        db.session.commit()
        
        retrieved = JournalEntryHandler.get_entry(
            entry_id=entry.id,
            user_id=user.id
        )
        
        assert retrieved is not None
        assert retrieved["title"] == "Entry"
        assert retrieved["id"] == entry.id

def test_get_entry_not_found(db, app):
    """Test retrieving a non-existent entry."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(user)
        db.session.commit()
        
        retrieved = JournalEntryHandler.get_entry(
            entry_id=999,
            user_id=user.id
        )
        
        assert retrieved is None

def test_update_entry(db, app):
    """Test updating a journal entry."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(user)
        entry = JournalEntry(
            user_id=user.id,
            title="Original",
            content="Original content",
            tags=["original"]
        )
        db.session.add(entry)
        db.session.commit()
        
        updated = JournalEntryHandler.update_entry(
            entry_id=entry.id,
            user_id=user.id,
            title="Updated",
            content="Updated content",
            tags=["updated"]
        )
        
        assert updated is not None
        assert updated["title"] == "Updated"
        assert updated["content"] == "Updated content"
        assert updated["tags"] == ["updated"]
        assert updated == ["user_id"] == user.id
        
        # Verify update in database
        db_entry = JournalEntry.query.get(entry.id)
        assert db_entry.title == "Updated"
        assert db_entry.content == "Updated content"
        assert db_entry.tags == ["updated"]

def test_update_entry_unauthorized(db, app):
    """Test updating an entry not owned."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(user)
        entry = JournalEntry(
            user_id=user.id,
            title="Original",
            content="Original content",
            tags=["original"]
        )
        db.session.add(entry)
        db.session.commit()
        
        updated = JournalEntryHandler.update_entry(
            entry_id=entry.id,
            user_id=999,  # Different user
            title="Not allowed",
            content="Not allowed content",
            tags=["notallowed"]
        )
        
        assert updated is None
        # Verify entry wasn't changed
        db_entry = JournalEntry.query.get(entry.id)
        assert db_entry.title == "Original"
        assert db_entry.content == "Original content"
        assert db_entry.tags == ["original"]

def test_update_entry_not_found(db, app):
    """Test updating a non-existent entry."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(user)
        db.session.commit()
        
        updated = JournalEntryHandler.update_entry(
            entry_id=999,
            user_id=user.id,
            title="Not found",
            content="Not found content",
            tags=["notfound"]
        )
        
        assert updated is None

def test_delete_entry(db, app):
    """Test deleting a journal entry."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(user)
        entry = JournalEntry(
            user_id=user.id,
            title="Entry",
            content="Content",
            tags=["test"]
        )
        db.session.add(entry)
        db.session.commit()
        
        success = JournalEntryHandler.delete_entry(
            entry_id=entry.id,
            user_id=user.id
        )
        
        assert success
        assert JournalEntry.query.get(entry.id) is None

def test_delete_entry_unauthorized(db, app):
    """Test deleting an entry not owned."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(user)
        entry = JournalEntry(
            user_id=user.id,
            title="Entry",
            content="Content",
            tags=["test"]
        )
        db.session.add(entry)
        db.session.commit()
        
        success = JournalEntryHandler.delete_entry(
            entry_id=entry.id,
            user_id=999  # Different user
        )
        
        assert not success
        assert JournalEntry.query.get(entry.id) is not None

def test_register_user(db, app):
    """Test registering a new user."""
    with app.app_context():
        user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpass123"
        }
        user = UserHandler.register_user(**user_data)
        
        assert user is not None
        assert user["username"] == "newuser"
        assert user["email"] == "new@example.com"
        assert check_password_hash(User.query.get(user["id"]).password_hash, "newpass123")

def test_register_user_duplicate_email(db, app):
    """Test registering with a duplicate email."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(user)
        db.session.commit()
        
        user_data = {
            "username": "newuser",
            "email": "test@example.com",
            "password": "newpass123"
        }
        with pytest.raises(ValueError, match="Email already registered"):
            UserHandler.register_user(**user_data)

def test_get_user(db, app):
    """Test retrieving a user."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(user)
        db.session.commit()
        
        retrieved = UserHandler.get_user(user_id=user.id)
        
        assert retrieved is not None
        assert retrieved["username"] == "testuser"
        assert retrieved["email"] == "test@example.com"

def test_update_user(db, app):
    """Test updating a user."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(user)
        db.session.commit()
        
        updated_data = {
            "username": "updateduser",
            "email": "updated@example.com",
            "password": "updatedpass123"
        }
        updated = UserHandler.update_user(user_id=user.id, **updated_data)
        
        assert updated is not None
        assert updated["username"] == "updateduser"
        assert updated["email"] == "updated@example.com"
        assert check_password_hash(User.query.get(user.id).password_hash, "updatedpass123")

def test_delete_user(db, app):
    """Test deleting a user."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(user)
        db.session.commit()
        
        success = UserHandler.delete_user(user_id=user.id)
        
        assert success
        assert User.query.get(user.id) is None