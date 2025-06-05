"""Utility functions for the Journal API."""
import json
from typing import Any, Union
from flask import Response
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from journalapi.models import User

def json_response(data: Any, status_code: int = 200) -> Response:
    """Create a JSON response with the given data and status code.
    
    Args:
        data: The data to serialize as JSON (dict, list, or str).
        status_code: HTTP status code (default: 200).
    
    Returns:
        Response: Flask Response object with JSON content.
    """
    return Response(
        response=json.dumps(data),
        status=status_code,
        mimetype="application/json"
    )

def authenticate_user(username: str, password: str) -> Union[User, None]:
    """Authenticate a user with the given credentials.
    
    Args:
        username: The user's username.
        password: The user's password.
    
    Returns:
        User: The authenticated user object, or None if authentication fails.
    """
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return user
    return None

def generate_token(user: User) -> str:
    """Generate a JWT token for the given user.
    
    Args:
        user: The user object to generate a token for.
    
    Returns:
        str: The generated JWT token.
    """
    return create_access_token(identity=str(user.id))
