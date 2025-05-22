"""User-related API resources for the Journal API."""
from flask_restful import Resource
from flask import request, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import ValidationError
import traceback
from extensions import db
from journalapi.models import User
from journalapi.utils import json_response
from schemas import UserRegisterSchema, UserLoginSchema

register_schema = UserRegisterSchema()
login_schema = UserLoginSchema()

class UserRegisterResource(Resource):
    """Handle user registration."""
    def post(self):
        """Register a new user.
        
        Returns:
            tuple: JSON response with success message or error.
        """
        try:
            data = register_schema.load(request.get_json())
            if User.query.filter_by(email=data["email"]).first():
                return json_response({"error": "Email already registered"}, 400)
            if User.query.filter_by(username=data["username"]).first():
                return json_response({"error": "Username already taken"}, 400)
            hashed_password = generate_password_hash(data["password"])
            user = User(username=data["username"], email=data["email"], password=hashed_password)
            db.session.add(user)
            db.session.commit()
            return json_response({"message": "User registered successfully"}, 201)
        except ValidationError as err:
            return json_response({"errors": err.messages}, 422)
        except Exception as e:
            current_app.logger.error("⚠️ Registration failed: %s", e)
            current_app.logger.error(traceback.format_exc())
            return json_response({"error": "Internal server error"}, 500)

class UserLoginResource(Resource):
    """Handle user login."""
    def post(self):
        """Log in a user and return a JWT token.
        
        Returns:
            tuple: JSON response with token or error message.
        """
        try:
            data = login_schema.load(request.get_json())
        except ValidationError as err:
            return json_response({"errors": err.messages}, 422)
        user = User.query.filter_by(email=data["email"]).first()
        if not user or not check_password_hash(user.password, data["password"]):
            return json_response({"error": "Invalid credentials"}, 401)
        token = create_access_token(identity=str(user.id))
        return json_response({"token": token}, 200)

class UserResource(Resource):
    """Handle user data retrieval and modification."""
    @jwt_required()
    def get(self, user_id):
        """Retrieve a user's data by ID.
        
        Args:
            user_id (int): The ID of the user.
        
        Returns:
            tuple: JSON response with user data or error message.
        """
        current_user_id = get_jwt_identity()
        if str(user_id) != current_user_id:
            return json_response({"error": "Unauthorized"}, 403)
        user = User.query.get(user_id)
        if not user:
            return json_response({"error": "User not found"}, 404)
        return json_response({"id": user.id, "username": user.username, "email": user.email}, 200)

    @jwt_required()
    def put(self, user_id):
        """Update a user's data by ID.
        
        Args:
            user_id (int): The ID of the user.
        
        Returns:
            tuple: JSON response with success message or error.
        """
        current_user_id = get_jwt_identity()
        if str(user_id) != current_user_id:
            return json_response({"error": "Unauthorized"}, 403)
        user = User.query.get(user_id)
        if not user:
            return json_response({"error": "User not found"}, 404)
        data = request.get_json() or {}
        if "username" in data:
            user.username = data["username"]
        if "email" in data:
            user.email = data["email"]
        if "password" in data:
            user.password = generate_password_hash(data["password"])
        db.session.commit()
        return json_response({"message": "User updated successfully"}, 200)

    @jwt_required()
    def delete(self, user_id):
        """Delete a user by ID.
        
        Args:
            user_id (int): The ID of the user.
        
        Returns:
            tuple: JSON response with success message or error.
        """
        current_user_id = get_jwt_identity()
        if str(user_id) != current_user_id:
            return json_response({"error": "Unauthorized"}, 403)
        user = User.query.get(user_id)
        if not user:
            return json_response({"error": "User not found"}, 404)
        db.session.delete(user)
        db.session.commit()
        return json_response({"message": "User deleted successfully"}, 200)

# # PWP_JournalAPI/resources/user.py
# from flask_restful import Resource
# from flask import request, current_app
# from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
# from werkzeug.security import generate_password_hash, check_password_hash
# from marshmallow import ValidationError
# import traceback
# from extensions import db
# from journalapi.models import User
# from journalapi.utils import JsonResponse

# try:
#     from schemas import UserRegisterSchema, UserLoginSchema
# except ImportError:
#     from ...schemas import UserRegisterSchema, UserLoginSchema

# register_schema = UserRegisterSchema()
# login_schema = UserLoginSchema()

# class UserRegisterResource(Resource):
#     def post(self):
#         try:
#             data = register_schema.load(request.get_json())
#             if User.query.filter_by(email=data["email"]).first():
#                 return JsonResponse({"error": "Email already registered"}, 400)
#             if User.query.filter_by(username=data["username"]).first():
#                 return JsonResponse({"error": "Username already taken"}, 400)
#             hashed_password = generate_password_hash(data["password"])
#             user = User(username=data["username"], email=data["email"], password=hashed_password)
#             db.session.add(user)
#             db.session.commit()
#             return JsonResponse({"message": "User registered successfully"}, 201)
#         except ValidationError as err:
#             return JsonResponse({"errors": err.messages}, 422)
#         except Exception as e:
#             current_app.logger.error("⚠️ Registration failed: %s", e)
#             current_app.logger.error(traceback.format_exc())
#             return JsonResponse({"error": "Internal server error"}, 500)

# class UserLoginResource(Resource):
#     def post(self):
#         try:
#             data = login_schema.load(request.get_json())
#         except ValidationError as err:
#             return JsonResponse({"errors": err.messages}, 422)
#         user = User.query.filter_by(email=data["email"]).first()
#         if not user or not check_password_hash(user.password, data["password"]):
#             return JsonResponse({"error": "Invalid credentials"}, 401)
#         token = create_access_token(identity=str(user.id))
#         return JsonResponse({"token": token}, 200)

# class UserResource(Resource):
#     @jwt_required()
#     def get(self, user_id):
#         current_user_id = get_jwt_identity()
#         if str(user_id) != current_user_id:
#             return JsonResponse({"error": "Unauthorized"}, 403)
#         user = User.query.get(user_id)
#         if not user:
#             return JsonResponse({"error": "User not found"}, 404)
#         return JsonResponse({"id": user.id, "username": user.username, "email": user.email}, 200)

#     @jwt_required()
#     def put(self, user_id):
#         current_user_id = get_jwt_identity()
#         if str(user_id) != current_user_id:
#             return JsonResponse({"error": "Unauthorized"}, 403)
#         user = User.query.get(user_id)
#         if not user:
#             return JsonResponse({"error": "User not found"}, 404)
#         data = request.get_json() or {}
#         if "username" in data:
#             user.username = data["username"]
#         if "email" in data:
#             user.email = data["email"]
#         if "password" in data:
#             user.password = generate_password_hash(data["password"])
#         db.session.commit()
#         return JsonResponse({"message": "User updated successfully"}, 200)

#     @jwt_required()
#     def delete(self, user_id):
#         current_user_id = get_jwt_identity()
#         if str(user_id) != current_user_id:
#             return JsonResponse({"error": "Unauthorized"}, 403)
#         user = User.query.get(user_id)
#         if not user:
#             return JsonResponse({"error": "User not found"}, 404)
#         db.session.delete(user)
#         db.session.commit()
#         return JsonResponse({"message": "User deleted successfully"}, 200)
