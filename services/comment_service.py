from extensions import db  # ✅ FIXED: Import db correctly
from model_folder.comment import Comment

class CommentService:

    @staticmethod
    def add_comment(entry_id, user_id, content):
        """Create a new comment and return it as a dictionary."""
        comment = Comment(journal_entry_id=entry_id, user_id=user_id, content=content)
        db.session.add(comment)
        db.session.commit()
        return comment.to_dict()  # ✅ FIXED: Return dict instead of model object

    @staticmethod
    def get_comments(entry_id):
        """Retrieve all comments for a journal entry and return as list of dicts."""
        comments = Comment.query.filter_by(journal_entry_id=entry_id).all()
        return [comment.to_dict() for comment in comments]  # ✅ FIXED: Convert each comment to dict

    @staticmethod
    def update_comment(comment_id, user_id, content):
        """Update a comment and return updated version as dictionary."""
        comment = Comment.query.get(comment_id)
        if comment and comment.user_id == user_id:  # ✅ Ensure user can only edit their own comment
            comment.content = content
            db.session.commit()
            return comment.to_dict()  # ✅ FIXED: Return dict instead of model object
        return None

    @staticmethod
    def delete_comment(comment_id, user_id):
        """Delete a comment if the user owns it."""
        comment = Comment.query.get(comment_id)
        if comment and comment.user_id == user_id:  # ✅ Ensure user can only delete their own comment
            db.session.delete(comment)
            db.session.commit()
            return True
        return False
