"""Handler for comment management operations."""
from extensions import db
from journalapi.models import Comment, JournalEntry
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommentHandler:
    """Handles comment creation, retrieval, and management."""

    @staticmethod
    def add_comment(entry_id: int, user_id: int, content: str) -> dict:
        """Add a comment to a journal entry."""
        try:
            # Check if journal entry exists
            entry = db.session.get(JournalEntry, entry_id)
            if not entry:
                logger.warning(f"Journal entry {entry_id} not found")
                return None
            comment = Comment(
                journal_entry_id=entry_id,
                user_id=user_id,
                content=content
            )
            db.session.add(comment)
            db.session.commit()
            logger.info(f"Comment added to entry ID {entry_id}")
            return comment.to_dict()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to add comment to entry {entry_id}: {e}")
            raise

    @staticmethod
    def get_comments(entry_id: int) -> list:
        """Retrieve all comments for a journal entry."""
        try:
            # Check if journal entry exists
            entry = db.session.get(JournalEntry, entry_id)
            if not entry:
                logger.warning(f"Journal entry {entry_id} not found")
                return None
            comments = Comment.query.filter_by(journal_entry_id=entry_id).all()
            logger.info(f"Retrieved comments for entry ID {entry_id}")
            return [comment.to_dict() for comment in comments]
        except Exception as e:
            logger.error(f"Failed to retrieve comments for entry {entry_id}: {e}")
            raise

    @staticmethod
    def get_comment(comment_id: int) -> dict:
        """Retrieve a comment by ID."""
        try:
            comment = db.session.get(Comment, comment_id)
            if not comment:
                logger.warning(f"Comment {comment_id} not found")
                return None
            return comment.to_dict()
        except Exception as e:
            logger.error(f"Failed to retrieve comment {comment_id}: {e}")
            raise

    @staticmethod
    def update_comment(comment_id: int, user_id: int, content: str) -> dict:
        """Update a comment's content."""
        try:
            comment = db.session.get(Comment, comment_id)
            if not comment or comment.user_id != user_id:
                logger.warning(f"Comment {comment_id} not found or unauthorized")
                return None
            comment.content = content
            db.session.commit()
            logger.info(f"Comment {comment_id} updated")
            return comment.to_dict()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update comment {comment_id}: {e}")
            raise

    @staticmethod
    def delete_comment(comment_id: int, user_id: int) -> bool:
        """Delete a comment."""
        try:
            comment = db.session.get(Comment, comment_id)
            if not comment or comment.user_id != user_id:
                logger.warning(f"Comment {comment_id} not found or unauthorized")
                return False
            db.session.delete(comment)
            db.session.commit()
            logger.info(f"Comment {comment_id} deleted")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to delete comment {comment_id}: {e}")
            raise