from flask import Blueprint
from flask_restful import Api

from journalapi.resources.user import UserLoginResource, UserRegisterResource, UserResource
from journalapi.resources.journal_entry import JornalEntriesResource, JournalEntryResource
from journalapi.resources.comment import JournalCommentsResource, CommentsResource

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

print("Registering routes...")
api.add_resource(UserRegisterResource, "/user/register/", endpoint="user_register")
api.add_resource(UserLoginResource, "/user/login/", endpoint="user_login")
api.add_resource(UserResource, "/users/<int:user_id>/", endpoint="user")
api.add_resource(JornalEntriesResource, "/entries/", endpoint="entries")
api.add_resource(JournalEntryResource, "/entries/<int:entry_id>", endpoint="entry")
api.add_resource(JournalCommentsResource, "/entries/<int:entry_id>/comments", endpoint="journal_comments")
api.add_resource(CommentsResource, "/comments/<int:comment_id>", endpoint="comments")