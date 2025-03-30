from flask_restful import Resource
from flask import request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import ValidationError

from ..models import User
from .. import db
from ..utils import JsonResponse
from ..schemas import UserRegisterSchema, UserLoginSchema

register_schema = UserRegisterSchema()
login_schema = UserLoginSchema()

class UserRegisterResource(Resource):
    def post(self):
        try:
            data = register_schema.load(request.get_json())
        except ValidationError as err:
            return JsonResponse({"errors": err.messages}, 400)

        if User.query.filter_by(email=data["email"]).first():
            return JsonResponse({"error": "User already exists"}, 400)

        user = User(
            username=data["username"],
            email=data["email"],
            password=generate_password_hash(data["password"])
        )
        db.session.add(user)
        db.session.commit()

        return JsonResponse({"message": "User registered successfully"}, 201)

class UserLoginResource(Resource):
    def post(self):
        try:
            data = login_schema.load(request.get_json())
        except ValidationError as err:
            return JsonResponse({"errors": err.messages}, 400)

        user = User.query.filter_by(email=data["email"]).first()
        if not user or not check_password_hash(user.password, data["password"]):
            return JsonResponse({"error": "Invalid credentials"}, 401)

        return JsonResponse({"token": create_access_token(identity=user.id)}, 200)

class UserResource(Resource):
    @jwt_required()
    def get(self, user_id):
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return JsonResponse({"error": "Unauthorized"}, 403)

        user = db.session.get(User, user_id)
        if not user:
            return JsonResponse({"error": "User not found"}, 404)

        return JsonResponse({
            "id": user.id,
            "username": user.username,
            "email": user.email
        }, 200)

    @jwt_required()
    def put(self, user_id):
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return JsonResponse({"error": "Unauthorized"}, 403)

        data = request.get_json()
        user = db.session.get(User, user_id)
        if not user:
            return JsonResponse({"error": "User not found"}, 404)

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
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return JsonResponse({"error": "Unauthorized"}, 403)

        user = db.session.get(User, user_id)
        if not user:
            return JsonResponse({"error": "User not found"}, 404)

        db.session.delete(user)
        db.session.commit()
        return JsonResponse({"message": "User deleted successfully"}, 200)
