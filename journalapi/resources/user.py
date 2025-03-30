# journalapi/resources/user.py
# journalapi/resources/user.py

from flask_restful import Resource
from flask import request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import ValidationError

from extensions import db
from journalapi.models import User
from journalapi.utils import JsonResponse
from schemas import UserRegisterSchema, UserLoginSchema

register_schema = UserRegisterSchema()
login_schema = UserLoginSchema()

class UserRegisterResource(Resource):
    def post(self):
        """
        Registers a new user with a unique email. 
        Marshmallow validates required fields (username, email, password).
        Returns 201 on success, or 422 if validation fails.
        """
        try:
            data = register_schema.load(request.get_json())
        except ValidationError as err:
            return JsonResponse({"errors": err.messages}, 422)

        if User.query.filter_by(email=data["email"]).first():
            return JsonResponse({"error": "User already exists"}, 400)

        hashed_password = generate_password_hash(data["password"])
        user = User(
            username=data["username"], 
            email=data["email"], 
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()

        return JsonResponse({"message": "User registered successfully"}, 201)


class UserLoginResource(Resource):
    def post(self):
        """
        Logs in an existing user by email + password. 
        Returns a JWT token on success, or 401 if invalid creds.
        """
        try:
            data = login_schema.load(request.get_json())
        except ValidationError as err:
            return JsonResponse({"errors": err.messages}, 422)

        user = User.query.filter_by(email=data["email"]).first()
        if not user or not check_password_hash(user.password, data["password"]):
            return JsonResponse({"error": "Invalid credentials"}, 401)

        # IMPORTANT: Convert user.id to string for newer Flask-JWT-Extended versions
        token = create_access_token(identity=str(user.id))
        return JsonResponse({"token": token}, 200)


class UserResource(Resource):
    @jwt_required()
    def get(self, user_id):
        """
        Retrieves user details if the token belongs to the same user.
        """
        current_user_id = get_jwt_identity()
        # current_user_id is a string; convert or compare as str
        if str(user_id) != current_user_id:
            return JsonResponse({"error": "Unauthorized"}, 403)

        user = User.query.get(user_id)
        if not user:
            return JsonResponse({"error": "User not found"}, 404)

        return JsonResponse({
            "id": user.id,
            "username": user.username,
            "email": user.email
        }, 200)

    @jwt_required()
    def put(self, user_id):
        """
        Updates a user record if the token belongs to the same user.
        Only updates fields present in the request body.
        """
        current_user_id = get_jwt_identity()
        if str(user_id) != current_user_id:
            return JsonResponse({"error": "Unauthorized"}, 403)

        user = User.query.get(user_id)
        if not user:
            return JsonResponse({"error": "User not found"}, 404)

        data = request.get_json() or {}
        if "username" in data:
            user.username = data["username"]
        if "email" in data:
            user.email = data["email"]
        if "password" in data:
            user.password = generate_password_hash(data["password"])

        db.session.commit()
        return JsonResponse({"message": "User updated successfully"}, 200)

    @jwt_required()
    def delete(self, user_id):
        """
        Deletes a user record if the token belongs to the same user.
        """
        current_user_id = get_jwt_identity()
        if str(user_id) != current_user_id:
            return JsonResponse({"error": "Unauthorized"}, 403)

        user = User.query.get(user_id)
        if not user:
            return JsonResponse({"error": "User not found"}, 404)

        db.session.delete(user)
        db.session.commit()
        return JsonResponse({"message": "User deleted successfully"}, 200)
