"""User API resources for the Journal API."""
from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from journalapi.handlers.user_handler import UserHandler
from journalapi.utils import json_response, generate_token
from schemas import UserRegisterSchema, UserLoginSchema

register_schema = UserRegisterSchema()
login_schema = UserLoginSchema()

class UserRegisterResource(Resource):
    """Handle user registration."""
    def post(self):
        """Register a new user.
        
        Returns:
            Response: JSON response with success message or error.
        """
        try:
            data = register_schema.load(request.get_json())
        except ValidationError as err:
            return json_response({"errors": err.messages}, 422)
        user = UserHandler.register_user(data["username"], data["email"], data["password"])
        if not user:
            return json_response({"error": "Email or username already registered"}, 400)
        return json_response({"message": "User registered successfully"}, 201)

class UserLoginResource(Resource):
    """Handle user login."""
    def post(self):
        """Log in a user and return a JWT token.
        
        Returns:
            Response: JSON response with token or error.
        """
        try:
            data = login_schema.load(request.get_json())
        except ValidationError as err:
            return json_response({"errors": err.messages}, 422)
        user = UserHandler.login_user(data["email"], data["password"])
        if not user:
            return json_response({"error": "Invalid credentials"}, 401)
        token = generate_token(user)
        return json_response({"token": token}, 200)

class UserResource(Resource):
    """Handle individual user operations."""
    @jwt_required()
    def get(self, user_id: int):
        """Retrieve user data by ID.
        
        Args:
            user_id: The ID of the user.
        
        Returns:
            Response: JSON response with user data or error.
        """
        user = UserHandler.get_user(user_id)
        if not user:
            return json_response({"error": "User not found"}, 404)
            
        current_user_id = int(get_jwt_identity())
        print(f"DEBUG: current_user_id={current_user_id}, requested user_id={user_id}")
        if user_id != current_user_id:
            return json_response({"error": "Unauthorized"}, 403)
            
        return json_response(user.to_dict(), 200)

    @jwt_required()
    def put(self, user_id: int):
        """Update user data by ID.
        
        Args:
            user_id: The ID of the user.
        
        Returns:
            Response: JSON response with success message or error.
        """
        user = UserHandler.get_user(user_id)
        if not user:
            return json_response({"error": "User not found"}, 404)
            
        current_user_id = int(get_jwt_identity())
        if user_id != current_user_id:
            return json_response({"error": "Unauthorized"}, 403)
        try:
            data = register_schema.load(request.get_json(), partial=True)
        except ValidationError as err:
            return json_response({"errors": err.messages}, 422)
        user = UserHandler.update_user(
            user_id,
            username=data.get("username"),
            email=data.get("email"),
            password=data.get("password")
        )
        if not user:
            return json_response({"error": "User not found"}, 404)
        return json_response({"message": "User updated successfully"}, 200)

    @jwt_required()
    def delete(self, user_id: int):
        """Delete a user by ID.
        
        Args:
            user_id: The ID of the user.
        
        Returns:
            Response: JSON response with success message or error.
        """
        user = UserHandler.get_user(user_id)
        if not user:
            return json_response({"error": "User not found"}, 404)
            
        current_user_id = int(get_jwt_identity())
        if user_id != current_user_id:
            return json_response({"error": "Unauthorized"}, 403)
        if UserHandler.delete_user(user_id):
            return json_response({"message": "User deleted successfully"}, 200)
        return json_response({"error": "User not found"}, 404)
