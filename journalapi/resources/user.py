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
        username, email, password = data.get("username"), data.get("email"), data.get("password")
        if not username or not email or not password:
            return JsonResponse({"error": "Missing fields"}, 400)
        if User.query.filter_by(email=email).first():
            return JsonResponse({"error": "User already exists"}, 400)
        user = User(username=username, email=email, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        return JsonResponse({"message": "User registered"}, 201)

class UserLoginResource(Resource):
    def post(self):
        data = request.get_json()
        email, password = data.get("email"), data.get("password")
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return JsonResponse({"error": "Invalid credentials"}, 401)
        return JsonResponse({"token": create_access_token(identity=user.id)}, 200)

class UserResource(Resource):
    @jwt_required()
    def get(self, user_id):
        current_id = get_jwt_identity()
        if current_id != user_id:
            return JsonResponse({"error": "Unauthorized"}, 403)
        user = User.query.get(user_id)
        if not user:
            return JsonResponse({"error": "User not found"}, 404)
        return JsonResponse({"id": user.id, "username": user.username, "email": user.email}, 200)