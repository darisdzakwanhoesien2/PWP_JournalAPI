from flask_jwt_extended import JWTManager
from journalapi.models import User

jwt = JWTManager()

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    user = User.query.get(int(identity))
    if user is None:
        return None
    return user

@jwt.user_lookup_error_loader
def user_lookup_error(_jwt_header, jwt_data):
    return {"error": "User not found"}, 403
