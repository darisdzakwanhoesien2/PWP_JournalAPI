# PWP_JournalAPI/journalapi/utils.py
"""Utility functions for the Journal API."""
import json
from datetime import datetime, timedelta
import jwt
from werkzeug.security import check_password_hash
from journalapi.models import User

def json_response(data, status_code=200):
    """Create a JSON response with the given data and status code.
    
    Args:
        data: The data to serialize as JSON.
        status_code (int): HTTP status code (default: 200).
    
    Returns:
        tuple: Flask response tuple (json, status, headers).
    """
    return json.dumps(data), status_code, {"Content-Type": "application/json"}

def authenticate_user(username, password):
    """Authenticate a user with the given credentials.
    
    Args:
        username (str): The user's username.
        password (str): The user's password.
    
    Returns:
        User: The authenticated user object, or None if authentication fails.
    """
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return user
    return None

def generate_token(user):
    """Generate a JWT token for the given user.
    
    Args:
        user: The user object to generate a token for.
    
    Returns:
        str: The generated JWT token.
    """
    payload = {
        "user_id": user.id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, "secret_key", algorithm="HS256")

# import json
# from flask import Response

# def JsonResponse(body, status=200, mimetype="application/json"):
#     if isinstance(body, dict) and "_links" not in body:
#         if "id" in body:
#             resource_type = detect_resource_type(body)
#             body["_links"] = generate_links(resource_type, body["id"])
#     return Response(json.dumps(body), status=status, mimetype=mimetype)

# def detect_resource_type(data):
#     if "title" in data:
#         return "entry"
#     elif "email" in data:
#         return "user"
#     elif "content" in data and "journal_entry_id" in data:
#         return "comment"
#     return None

# def generate_links(resource_type, id_):
#     if resource_type == "entry":
#         return {
#             "self": {"href": f"/entries/{id_}"},
#             "edit": {"href": f"/entries/{id_}"},
#             "delete": {"href": f"/entries/{id_}"},
#             "comments": {"href": f"/entries/{id_}/comments"},
#             "history": {"href": f"/entries/{id_}/history"}
#         }
#     elif resource_type == "user":
#         return {
#             "self": {"href": f"/users/{id_}"},
#             "edit": {"href": f"/users/{id_}"},
#             "delete": {"href": f"/users/{id_}"}
#         }
#     elif resource_type == "comment":
#         return {
#             "self": {"href": f"/entries/{id_}/comments/{id_}"},
#             "edit": {"href": f"/entries/{id_}/comments/{id_}"},
#             "delete": {"href": f"/entries/{id_}/comments/{id_}"}
#         }
#     return {}
