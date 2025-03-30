from flask import Blueprint
from flask_restful import Api
from .resources.user import UserRegisterResource, UserLoginResource, UserResource
from .resources.journal_entry import JournalEntryResource, JournalEntryListResource
from .resources.comment import CommentCollectionResource, CommentItemResource

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

api.add_resource(UserRegisterResource, "/users/register")
api.add_resource(UserLoginResource, "/users/login")
api.add_resource(UserResource, "/users/<int:user_id>")

api.add_resource(JournalEntryListResource, "/entries")
api.add_resource(JournalEntryResource, "/entries/<int:entry_id>")

api.add_resource(CommentCollectionResource, "/entries/<int:entry_id>/comments")
api.add_resource(CommentItemResource, "/entries/<int:entry_id>/comments/<int:comment_id>")
