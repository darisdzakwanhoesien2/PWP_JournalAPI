import pytest
from unittest.mock import patch, MagicMock
from journalapi.handlers.comment_handler import CommentHandler
from journalapi.models import Comment
from extensions import db
import logging

class TestCommentHandler:
    """Test cases for CommentHandler."""

    def test_add_comment_success(self):
        """Test successful comment addition."""
        with patch('extensions.db.session.add'), patch('extensions.db.session.commit'):
            result = CommentHandler.add_comment(1, 1, "Test comment")
            assert isinstance(result, dict)
            assert 'content' in result

    def test_add_comment_failure(self):
        """Test comment addition failure."""
        with patch('extensions.db.session.add', side_effect=Exception("DB error")), \
             patch('extensions.db.session.rollback') as mock_rollback:
            with pytest.raises(Exception):
                CommentHandler.add_comment(1, 1, "Test comment")
            mock_rollback.assert_called_once()

    def test_get_comments_success(self):
        """Test successful comment retrieval."""
        mock_comments = [MagicMock(to_dict=lambda: {"content": "test"})]
        with patch('journalapi.models.Comment.query') as mock_query:
            mock_query.filter_by.return_value.all.return_value = mock_comments
            result = CommentHandler.get_comments(1)
            assert len(result) == 1
            assert result[0]['content'] == "test"

    def test_get_comments_failure(self):
        """Test comment retrieval failure."""
        with patch('journalapi.models.Comment.query') as mock_query:
            mock_query.filter_by.side_effect = Exception("DB error")
            with pytest.raises(Exception):
                CommentHandler.get_comments(1)

    def test_update_comment_success(self):
        """Test successful comment update."""
        mock_comment = MagicMock(user_id=1, content="old")
        with patch('extensions.db.session.get', return_value=mock_comment), \
             patch('extensions.db.session.commit'):
            result = CommentHandler.update_comment(1, 1, "new")
            assert mock_comment.content == "new"
            assert result['content'] == "old"  # assuming to_dict returns old state

    def test_update_comment_not_found(self):
        """Test update when comment not found."""
        with patch('extensions.db.session.get', return_value=None):
            result = CommentHandler.update_comment(1, 1, "new")
            assert result is None

    def test_update_comment_unauthorized(self):
        """Test unauthorized comment update."""
        mock_comment = MagicMock(user_id=2)  # different user
        with patch('extensions.db.session.get', return_value=mock_comment):
            result = CommentHandler.update_comment(1, 1, "new")
            assert result is None

    def test_update_comment_failure(self):
        """Test comment update failure."""
        mock_comment = MagicMock(user_id=1)
        with patch('extensions.db.session.get', return_value=mock_comment), \
             patch('extensions.db.session.commit', side_effect=Exception("DB error")), \
             patch('extensions.db.session.rollback') as mock_rollback:
            with pytest.raises(Exception):
                CommentHandler.update_comment(1, 1, "new")
            mock_rollback.assert_called_once()

    def test_delete_comment_success(self):
        """Test successful comment deletion."""
        mock_comment = MagicMock(user_id=1)
        with patch('extensions.db.session.get', return_value=mock_comment), \
             patch('extensions.db.session.delete'), \
             patch('extensions.db.session.commit'):
            result = CommentHandler.delete_comment(1, 1)
            assert result is True

    def test_delete_comment_not_found(self):
        """Test delete when comment not found."""
        with patch('extensions.db.session.get', return_value=None):
            result = CommentHandler.delete_comment(1, 1)
            assert result is False

    def test_delete_comment_unauthorized(self):
        """Test unauthorized comment deletion."""
        mock_comment = MagicMock(user_id=2)  # different user
        with patch('extensions.db.session.get', return_value=mock_comment):
            result = CommentHandler.delete_comment(1, 1)
            assert result is False

    def test_delete_comment_failure(self):
        """Test comment deletion failure."""
        mock_comment = MagicMock(user_id=1)
        with patch('extensions.db.session.get', return_value=mock_comment), \
             patch('extensions.db.session.delete'), \
             patch('extensions.db.session.commit', side_effect=Exception("DB error")), \
             patch('extensions.db.session.rollback') as mock_rollback:
            with pytest.raises(Exception):
                CommentHandler.delete_comment(1, 1)
            mock_rollback.assert_called_once()