"""User API resources for the Journal API."""
from flask_restful import Resource
from flask import request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError
from journalapi.handlers.user_handler import UserHandler
from journalapi.utils import json_response
from schemas import UserRegisterSchema, UserLoginSchema
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

register_schema = UserRegisterSchema()
login_schema = UserLoginSchema()

class UserRegisterResource(Resource):
    def post(self):
        try:
            data = register_schema.load(request.get_json())
            user = UserHandler.register_user(
                username=data["username"],
                email=data["email"],
                password=data["password"]
            )
            if not user:
                return json_response({"error": "Email already registered"}, 400)  # Changed error message
            return json_response(
                {"message": "User registered successfully", "_links": {"self": f"/api/users/{user.id}"}},
                201
            )
        except ValidationError as e:
            logger.error(f"Validation error: {e.messages}")
            return json_response({"error": e.messages}, 422)
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return json_response({"error": "Internal server error"}, 500)

class UserLoginResource(Resource):
    """Handle user login."""

    def post(self):
        """Log in a user and return a JWT token."""
        try:
            data = login_schema.load(request.get_json())
            user = UserHandler.login_user(email=data["email"], password=data["password"])
            if not user:
                logger.warning(f"Invalid login attempt for {data['email']}")
                return json_response({"error": "Invalid credentials"}, 401)
            token = create_access_token(identity=str(user.id))
            logger.info(f"User {data['email']} logged in")
            return json_response(
                {"token": token, "_links": {"self": f"/api/users/{user.id}"}},
                200
            )
        except ValidationError as e:
            logger.error(f"Validation error: {e.messages}")
            return json_response({"error": e.messages}, 422)
        except Exception as e:
            logger.error(f"Login error: {e}")
            return json_response({"error": "Internal server error"}, 500)

class UserResource(Resource):
    """Handle user data retrieval and modification."""

    @jwt_required()
    def get(self, user_id: int):
        """Retrieve a user's data by ID."""
        try:
            current_user_id = int(get_jwt_identity())
            if user_id != current_user_id:
                logger.warning(f"Unauthorized access to user {user_id}")
                return json_response({"error": "Unauthorized"}, 403)
            user = UserHandler.get_user(user_id)
            if not user:
                logger.warning(f"User {user_id} not found")
                return json_response({"error": "User not found"}, 404)
            logger.info(f"Retrieved user {user_id}")
            return json_response(user.to_dict(), 200)
        except ValueError as ve:
            logger.error(f"Invalid user ID format: {ve}")
            return json_response({"error": "Invalid authentication token"}, 401)
        except Exception as e:
            logger.error(f"Error retrieving user {user_id}: {e}")
            return json_response({"error": "Internal server error"}, 500)

    @jwt_required()
    def put(self, user_id: int):
        """Update a user's data by ID."""
        try:
            current_user_id = int(get_jwt_identity())
            if user_id != current_user_id:
                logger.warning(f"Unauthorized update for user {user_id}")
                return json_response({"error": "Unauthorized"}, 403)
            data = register_schema.load(request.get_json(), partial=True)
            user = UserHandler.update_user(
                user_id=user_id,
                username=data.get("username"),
                email=data.get("email"),
                password=data.get("password")
            )
            if not user:
                logger.warning(f"User {user_id} not found")
                return json_response({"error": "User not found"}, 404)
            logger.info(f"Updated user {user_id}")
            return json_response(
                {"message": "User updated successfully", "_links": {"self": f"/api/users/{user.id}"}},
                200
            )
        except ValidationError as e:
            logger.error(f"Validation error: {e.messages}")
            return json_response({"error": e.messages}, 422)
        except ValueError as ve:
            logger.error(f"Invalid user ID format: {ve}")
            return json_response({"error": "Invalid authentication token"}, 401)
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return json_response({"error": "Internal server error"}, 500)

    @jwt_required()
    def delete(self, user_id: int):
        """Delete a user by ID."""
        try:
            current_user_id = int(get_jwt_identity())
            if user_id != current_user_id:
                logger.warning(f"Unauthorized delete for user {user_id}")
                return json_response({"error": "Unauthorized"}, 403)
            success = UserHandler.delete_user(user_id)
            if not success:
                logger.warning(f"User {user_id} not found")
                return json_response({"error": "User not found"}, 404)
            logger.info(f"Deleted user {user_id}")
            return json_response({"message": "User deleted successfully"}, 200)
        except ValueError as ve:
            logger.error(f"Invalid user ID format: {ve}")
            return json_response({"error": "Invalid authentication token"}, 401)
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return json_response({"error": "Internal server error"}, 500)