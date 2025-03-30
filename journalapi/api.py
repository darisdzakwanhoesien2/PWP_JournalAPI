# journalapi/api.py
from flask import Blueprint
from flask_restful import Api

from journalapi.resources.user import UserRegisterResource, UserLoginResource, UserResource
from journalapi.resources.journal_entry import JournalEntryListResource, JournalEntryResource
from journalapi.resources.comment import CommentCollectionResource, CommentItemResource

# Add your new resource import:
from journalapi.resources.edit_history import EditHistoryResource

api_bp = Blueprint("api", __name__, url_prefix="")  # or "/api"
api = Api(api_bp)

# User endpoints
api.add_resource(UserRegisterResource, "/users/register")
api.add_resource(UserLoginResource, "/users/login")
api.add_resource(UserResource, "/users/<int:user_id>")

# Journal Entry endpoints
api.add_resource(JournalEntryListResource, "/entries/")
api.add_resource(JournalEntryResource, "/entries/<int:entry_id>")

# Comment endpoints
api.add_resource(CommentCollectionResource, "/entries/<int:entry_id>/comments")
api.add_resource(CommentItemResource, "/entries/<int:entry_id>/comments/<int:comment_id>")

# Finally, Edit History route:
api.add_resource(EditHistoryResource, "/entries/<int:entry_id>/history")

