from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from services.user_service import UserService

user_bp = Blueprint("users", __name__)

@user_bp.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    user = UserService.register_user(username, email, password)
    if not user:
        return jsonify({"error": "User already exists"}), 400

    return jsonify({"message": "User registered successfully"}), 201

@user_bp.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user = UserService.login_user(email, password)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({"access_token": access_token}), 200

@user_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    user = UserService.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email
    }), 200

@user_bp.route("/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    updated_user = UserService.update_user(
        user_id,
        username=data.get("username"),
        email=data.get("email"),
        password=data.get("password")
    )
    if not updated_user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"message": "User updated successfully"}), 200

@user_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    if not UserService.delete_user(user_id):
        return jsonify({"error": "User not found"}), 404

    return jsonify({"message": "User deleted successfully"}), 200