# PWP_JournalAPI/journalapi/handlers/comment_handler.py
"""Handler for comment-related operations."""
from extensions import db
from journalapi.models import Comment
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommentHandler:
    """Handles comment creation, retrieval, update, and deletion."""

    @staticmethod
    def add_comment(entry_id: int, user_id: int, content: str) -> dict:
        """Add a comment to a journal entry."""
        try:
            comment = Comment(journal_entry_id=entry_id, user_id=user_id, content=content)
            db.session.add(comment)
            db.session.commit()
            db.session.refresh(comment)
            logger.info(f"Comment added to entry ID {entry_id}")
            return comment.to_dict()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to add comment: {e}")
            raise

    @staticmethod
    def get_comments(entry_id: int) -> list:
        """Retrieve all comments for a journal entry."""
        try:
            comments = Comment.query.filter_by(journal_entry_id=entry_id).all()
            logger.info(f"Retrieved comments for entry ID {entry_id}")
            return [comment.to_dict() for comment in comments]
        except Exception as e:
            logger.error(f"Failed to retrieve comments: {e}")
            raise

    @staticmethod
    def update_comment(comment_id: int, user_id: int, content: str) -> dict:
        """Update a comment if owned by the user."""
        try:
            comment = db.session.get(Comment, comment_id)
            if not comment or comment.user_id != user_id:
                logger.warning(f"Comment ID {comment_id} not found or unauthorized")
                return None
            comment.content = content
            db.session.commit()
            db.session.refresh(comment)
            logger.info(f"Comment ID {comment_id} updated")
            return comment.to_dict()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update comment: {e}")
            raise

    @staticmethod
    def delete_comment(comment_id: int, user_id: int) -> bool:
        """Delete a comment if owned by the user."""
        try:
            comment = db.session.get(Comment, comment_id)
            if not comment or comment.user_id != user_id:
                logger.warning(f"Comment ID {comment_id} not found or unauthorized")
                return False
            db.session.delete(comment)
            db.session.commit()
            logger.info(f"Comment ID {comment_id} deleted")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to delete comment: {e}")
            raise