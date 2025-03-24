from journalapi import db
from journalapi.models import Comment

class CommentHandler:

    @staticmethod
    def add_comment(entry_id, user_id, content):
        comment = Comment(journal_entry_id=entry_id, user_id=user_id, content=content)
        db.session.add(comment)
        db.session.commit()
        db.session.refresh(comment)  # Ensures comment remains attached
        return comment.to_dict()

    @staticmethod
    def get_comments(entry_id):
        comments = Comment.query.filter_by(journal_entry_id=entry_id).all()
        return [comment.to_dict() for comment in comments]

    @staticmethod
    def update_comment(comment_id, user_id, content):
        comment = Comment.query.get(comment_id)
        if comment and comment.user_id == user_id:
            comment.content = content
            db.session.commit()
            db.session.refresh(comment)  # Ensures updated data is returned
            return comment.to_dict()
        return None

    @staticmethod
    def delete_comment(comment_id, user_id):
        comment = Comment.query.get(comment_id)
        if comment and comment.user_id == user_id:
            db.session.delete(comment)
            db.session.commit()
            return True
        return False