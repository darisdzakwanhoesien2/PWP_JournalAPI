# PWP_JournalAPI/journalapi/resources/user.py
"""User API resources for the Journal API."""
from flask_restful import Resource
from flask import request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from marshmallow import ValidationError
from extensions import db
from journalapi.models import User
from journalapi.utils import json_response
from schemas import UserRegisterSchema, UserLoginSchema
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

register_schema = UserRegisterSchema()
login_schema = UserLoginSchema()

class UserRegisterResource(Resource):
    """Handle user registration."""

    def post(self):
        """Register a new user.

        Returns:
            JSON response with success message or error.
        """
        try:
            data = register_schema.load(request.get_json())
            if User.query.filter_by(email=data["email"]).first():
                logger.warning(f"Email {data['email']} already registered")
                return json_response({"error": "Email already registered"}, 400)
            if User.query.filter_by(username=data["username"]).first():
                logger.warning(f"Username {data['username']} already taken")
                return json_response({"error": "Username already taken"}, 400)
            user = User(
                username=data["username"],
                email=data["email"],
                password_hash=generate_password_hash(data["password"])
            )
            db.session.add(user)
            db.session.commit()
            logger.info(f"User registered: {data['username']}")
            return json_response(
                {"message": "User registered successfully", "_links": {"self": f"/api/users/{user.id}"}},
                201
            )
        except ValidationError as e:
            logger.error(f"Validation error: {e.messages}")
            return json_response({"error": e.messages}, 422)
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {e}")
            return json_response({"error": "Internal server error"}, 500)

class UserLoginResource(Resource):
    """Handle user login."""

    def post(self):
        """Log in a user and return a JWT token.

        Returns:
            JSON response with JWT token or error.
        """
        try:
            data = login_schema.load(request.get_json())
            user = User.query.filter_by(email=data["email"]).first()
            if not user or not user.check_password(data["password"]):
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
        """Retrieve a user's data by ID.

        Args:
            user_id (int): ID of the user.

        Returns:
            JSON response with user data or error.
        """
        try:
            current_user_id = int(get_jwt_identity())
            if user_id != current_user_id:
                logger.warning(f"Unauthorized access to user {user_id}")
                return json_response({"error": "Unauthorized"}, 403)
            user = db.session.get(User, user_id)
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
        """Update a user's data by ID.

        Args:
            user_id (int): ID of the user.

        Returns:
            JSON response with success message or error.
        """
        try:
            current_user_id = int(get_jwt_identity())
            if user_id != current_user_id:
                logger.warning(f"Unauthorized update for user {user_id}")
                return json_response({"error": "Unauthorized"}, 403)
            user = db.session.get(User, user_id)
            if not user:
                logger.warning(f"User {user_id} not found")
                return json_response({"error": "User not found"}, 404)
            data = register_schema.load(request.get_json(), partial=True)
            # Check for duplicate username/email
            if "username" in data and data["username"] != user.username:
                if User.query.filter_by(username=data["username"]).first():
                    logger.warning(f"Username {data['username']} already taken")
                    return json_response({"error": "Username already taken"}, 400)
                user.username = data["username"]
            if "email" in data and data["email"] != user.email:
                if User.query.filter_by(email=data["email"]).first():
                    logger.warning(f"Email {data['email']} already registered")
                    return json_response({"error": "Email already registered"}, 400)
                user.email = data["email"]
            if "password" in data:
                user.password_hash = generate_password_hash(data["password"])
            db.session.commit()
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
            db.session.rollback()
            logger.error(f"Error updating user {user_id}: {e}")
            return json_response({"error": "Internal server error"}, 500)

    @jwt_required()
    def delete(self, user_id: int):
        """Delete a user by ID.

        Args:
            user_id (int): ID of the user.

        Returns:
            JSON response with success message or error.
        """
        try:
            current_user_id = int(get_jwt_identity())
            if user_id != current_user_id:
                logger.warning(f"Unauthorized delete for user {user_id}")
                return json_response({"error": "Unauthorized"}, 403)
            user = db.session.get(User, user_id)
            if not user:
                logger.warning(f"User {user_id} not found")
                return json_response({"error": "User not found"}, 404)
            db.session.delete(user)
            db.session.commit()
            logger.info(f"Deleted user {user_id}")
            return json_response({"message": "User deleted successfully"}, 200)
        except ValueError as ve:
            logger.error(f"Invalid user ID format: {ve}")
            return json_response({"error": "Invalid authentication token"}, 401)
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting user {user_id}: {e}")
            return json_response({"error": "Internal server error"}, 500)