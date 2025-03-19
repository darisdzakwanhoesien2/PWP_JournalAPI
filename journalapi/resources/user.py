from flask_restful import Resource, Api
from flask import jsonify, request, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from journalapi.handlers.user_service import UserService
from journalapi.utils import JsonResponse

class UserRegisterResource(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        
        if not username or not email or not password:
            return JsonResponse({"error": "Missing required fields"}, 400)
        
        user = UserService.register_user(username, email, password)
        if not user:
            return JsonResponse({"error": "User already exists"}, 400)  
        
        return JsonResponse({
            "message": "User registered successfully"
        }, 201)

class UserLoginResource(Resource):
    def post(self):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JsonResponse({"error": "Missing email or password"}, 400)

        user = UserService.login_user(email, password)
        if not user:
            return JsonResponse({"error": "Invalid credentials"}, 401)

        access_token = create_access_token(identity=str(user.id))

        return JsonResponse({
            "token": access_token
        }, 200)


class UserResource(Resource):
    @jwt_required()
    def get(self, user_id):
        current_user_id = int(get_jwt_identity())
        if current_user_id != user_id:
            return JsonResponse({"error": "Unauthorized"}, 403)

        user = UserService.get_user(user_id)
        if not user:
            return JsonResponse({"error": "User not found"}, 404)

        return JsonResponse({
            "id": user.id,
            "username": user.username,
            "email": user.email
        }, 200)

    @jwt_required()
    def put(self, user_id):
        current_user_id = int(get_jwt_identity())
        if current_user_id != user_id:
            return JsonResponse({"error": "Unauthorized"}, 403)

        data = request.get_json()
        updated_user = UserService.update_user(
            user_id,
            username=data.get("username"),
            email=data.get("email"),
            password=data.get("password")
        )
        if not updated_user:
            return JsonResponse({"error": "User not found"}, 404)

        return JsonResponse({
            "message": "User updated successfully"
        }, 200)

    @jwt_required()
    def delete(self, user_id):
        current_user_id = int(get_jwt_identity())
        if current_user_id != user_id:
            return JsonResponse({"error": "Unauthorized"}, 403)

        if not UserService.delete_user(user_id):
            return JsonResponse({"error": "User not found"}, 404)

        return JsonResponse({
            "message": "User deleted successfully"
        }, 200)



