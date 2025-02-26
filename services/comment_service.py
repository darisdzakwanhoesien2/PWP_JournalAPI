from database import db
from models.comment import Comment

class CommentService:

    @staticmethod
    def add_comment(entry_id, user_id, content):
        comment = Comment(journal_entry_id=entry_id, user_id=user_id, content=content)
        db.session.add(comment)
        db.session.commit()
        return comment

    @staticmethod
    def get_comments(entry_id):
        return Comment.query.filter_by(journal_entry_id=entry_id).all()

    @staticmethod
    def update_comment(comment_id, content):
        comment = Comment.query.get(comment_id)
        if comment:
            comment.content = content
            db.session.commit()
            return comment
        return None

    @staticmethod
    def delete_comment(comment_id):
        comment = Comment.query.get(comment_id)
        if comment:
            db.session.delete(comment)
            db.session.commit()
            return True
        return False
