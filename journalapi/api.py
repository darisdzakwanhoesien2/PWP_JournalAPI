# PWP_JournalAPI/journalapi/api.py
"""API blueprint and resource definitions for the Journal API."""
from flask import Blueprint
from flask_restful import Api
from journalapi.resources.user import UserRegisterResource, UserLoginResource, UserResource
from journalapi.resources.journal_entry import JournalEntryListResource, JournalEntryResource
from journalapi.resources.comment import CommentCollectionResource, CommentItemResource
from journalapi.resources.edit_history import EditHistoryResource
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__, url_prefix="")
api = Api(api_bp)

# Register resources
api.add_resource(UserRegisterResource, "/users/register")
api.add_resource(UserLoginResource, "/users/login")
api.add_resource(UserResource, "/users/<int:user_id>")
api.add_resource(JournalEntryListResource, "/entries")
api.add_resource(JournalEntryResource, "/entries/<int:entry_id>")
api.add_resource(CommentCollectionResource, "/entries/<int:entry_id>/comments")
api.add_resource(CommentItemResource, "/entries/<int:entry_id>/comments/<int:comment_id>")
api.add_resource(EditHistoryResource, "/entries/<int:entry_id>/history")

logger.info("API blueprint and resources registered")