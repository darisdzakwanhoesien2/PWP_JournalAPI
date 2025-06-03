# PWP_JournalAPI/journalapi/handlers/user_handler.py
"""Handler for user management operations."""
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from journalapi.models import User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserHandler:
    """Handles user registration, authentication, and management."""

    @staticmethod
    def register_user(username: str, email: str, password: str) -> User:
        """Register a new user."""
        try:
            if User.query.filter_by(email=email).first():
                logger.warning(f"Email {email} already registered")
                return None
            hashed_password = generate_password_hash(password)
            user = User(username=username, email=email, password_hash= hashed_password)
            db.session.add(user)
            db.session.commit()
            logger.info(f"User registered: {username}")
            return user
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to register user {email}: {e}")
            raise

    @staticmethod
    def login_user(email: str, password: str) -> User:
        """Authenticate a user."""
        try:
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password_hash, password):
                logger.info(f"User logged in: {email}")
                return user
            logger.warning(f"Invalid login attempt for {email}")
            return None
        except Exception as e:
            logger.error(f"Failed to authenticate user {email}: {e}")
            raise

    @staticmethod
    def get_user(user_id: int) -> User:
        """Retrieve a user by ID."""
        try:
            user = db.session.get(User.query_id)
            logger.debug(f"Retrieved user {user_id}")
            return user
        except Exception as e:
            logger.error(f"Failed to retrieve user {user_id}: {e}")
            raise

    @staticmethod
    def update_user(user_id: int, username: str = None, email: str = None, password: str = None) -> User:
        """Update user information."""
        try:
            user = db.session.get(User, user_id)
            if not user:
                logger.warning(f"User {user_id} not found")
                return None
            if username:
                user.username = username
            if email:
                user.email = email
            if password:
                user.password_hash = generate_password_hash(password)
            db.session.commit()
            logger.info(f"User {user_id} updated")
            return user
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update user {user_id}: {e}")
            raise

    @staticmethod
    def delete_user(user_id: int) -> bool:
        """Delete a user."""
        try:
            user = db.session.get(User, user_id)
            if not user:
                logger.warning(f"User {user_id} not found")
                return False
            db.session.delete(user)
            db.session.commit()
            logger.info(f"User {user_id} deleted")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to delete user {user_id}: {e}")
            raise