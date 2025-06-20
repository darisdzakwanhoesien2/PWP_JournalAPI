## current code
from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from src.data_store import load_users, save_users, get_next_id
from src.models_orm import User
from src.utils import user_links, users_collection_links
from src.schemas import UserSchema
from src.cache import cache

"""
User-related API routes module.
"""

users_bp = Blueprint('users', __name__)
user_schema = UserSchema()

def _build_user_response(user):
    """
    Helper function to build user response dictionary with links.
    """
    user_dict = user.to_dict()
    user_dict['_links'] = user_links(user.id)
    return user_dict

@users_bp.route('', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300)
def get_users():
    """
    Retrieve a list of all users.
    """
    users_data = load_users()
    users = [User.from_dict(u) for u in users_data]
    result = [_build_user_response(user) for user in users]
    response = {
        'items': result,
        '_links': users_collection_links()
    }
    return jsonify(response), 200

@users_bp.route('/register', methods=['POST'])
def register_user():
    """
    Register a new user.
    """
    json_data = request.get_json()
    if not json_data:
        abort(400, description='No input data provided')
    try:
        data = user_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    users_data = load_users()
    # Check for duplicate username or email
    for u in users_data:
        if u['username'] == data['username']:
            abort(400, description='Username already exists')
        if u['email'] == data['email']:
            abort(400, description='Email already exists')
    new_id = get_next_id(users_data)
    user = User(id=new_id, username=data['username'], email=data['email'])
    users_data.append(user.to_dict())
    save_users(users_data)
    user_dict = _build_user_response(user)
    return jsonify(user_dict), 201

@users_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300)
def get_user(id):
    """
    Retrieve a user by ID.
    """
    users_data = load_users()
    user_data = next((u for u in users_data if u['id'] == id), None)
    if not user_data:
        abort(404, description='User not found')
    user = User.from_dict(user_data)
    user_dict = _build_user_response(user)
    return jsonify(user_dict), 200

@users_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    """
    Update a user's information.
    """
    json_data = request.get_json()
    if not json_data:
        abort(400, description='No input data provided')
    try:
        data = user_schema.load(json_data, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400
    users_data = load_users()
    user_index = next((i for i, u in enumerate(users_data) if u['id'] == id), None)
    if user_index is None:
        abort(404, description='User not found')
    # Update fields if present
    if 'username' in data:
        # Check for duplicate username
        for u in users_data:
            if u['username'] == data['username'] and u['id'] != id:
                abort(400, description='Username already exists')
        users_data[user_index]['username'] = data['username']
    if 'email' in data:
        # Check for duplicate email
        for u in users_data:
            if u['email'] == data['email'] and u['id'] != id:
                abort(400, description='Email already exists')
        users_data[user_index]['email'] = data['email']
    save_users(users_data)
    user = User.from_dict(users_data[user_index])
    user_dict = _build_user_response(user)
    return jsonify(user_dict), 200

@users_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    """
    Delete a user by ID.
    """
    users_data = load_users()
    user_index = next((i for i, u in enumerate(users_data) if u['id'] == id), None)
    if user_index is None:
        abort(404, description='User not found')
    users_data.pop(user_index)
    save_users(users_data)
    return '', 204
