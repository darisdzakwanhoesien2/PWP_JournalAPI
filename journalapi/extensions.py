"""Flask JWT extension setup and configuration for user authentication."""

from flask_jwt_extended import JWTManager
from journalapi.models import User

jwt = JWTManager()

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    """Load a user from the JWT identity.

    Args:
        _jwt_header (dict): The JWT header (not used).
        jwt_data (dict): The JWT payload containing the user identity.

    Returns:
        User or None: The User object if found, otherwise None.
    """
    identity = jwt_data["sub"]
    user = User.query.get(int(identity))
    if user is None:
        return None
    return user

@jwt.user_lookup_error_loader
def user_lookup_error(_jwt_header):
    """Handle errors when a user cannot be loaded from the JWT.

    Args:
        _jwt_header (dict): The JWT header (not used).

    Returns:
        tuple: A JSON error response and HTTP status code 403.
    """
    return {"error": "User not found"}, 403