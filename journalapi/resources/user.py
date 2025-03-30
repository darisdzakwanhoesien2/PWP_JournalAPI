from flask_restful import Resource
from flask import request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User
from .. import db
from ..utils import JsonResponse

class UserRegisterResource(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            return JsonResponse({"error": "Missing required fields"}, 400)

        if User.query.filter_by(email=email).first():
            return JsonResponse({"error": "User already exists"}, 400)

        hashed_password = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        return JsonResponse({"message": "User registered successfully"}, 201)

class UserLoginResource(Resource):
    def post(self):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JsonResponse({"error": "Missing email or password"}, 400)

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return JsonResponse({"error": "Invalid credentials"}, 401)

        token = create_access_token(identity=user.id)
        return JsonResponse({"token": token}, 200)

class UserResource(Resource):
    @jwt_required()
    def get(self, user_id):
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return JsonResponse({"error": "Unauthorized"}, 403)

        user = db.session.get(User, user_id)
        if not user:
            return JsonResponse({"error": "User not found"}, 404)

        return JsonResponse({"id": user.id, "username": user.username, "email": user.email}, 200)

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