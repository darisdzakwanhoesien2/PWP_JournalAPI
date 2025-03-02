from flask import Blueprint, request, jsonify
from extensions import db  # ✅ FIXED: Import db correctly
from model_folder.comment import Comment
from services.comment_service import CommentService
from flask_jwt_extended import jwt_required, get_jwt_identity

comment_bp = Blueprint("comments", __name__)

# Add a comment to a journal entry
@comment_bp.route("/entries/<int:entry_id>/comments", methods=["POST"])
@jwt_required()
def add_comment(entry_id):
    data = request.get_json()
    current_user_id = get_jwt_identity()

    if not data or "content" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    comment = CommentService.add_comment(entry_id, current_user_id, data["content"])
    return jsonify({"message": "Comment added successfully", "comment": comment}), 201  # ✅ FIXED: Return dictionary

# Retrieve all comments for a specific journal entry
@comment_bp.route("/entries/<int:entry_id>/comments", methods=["GET"])
@jwt_required()
def get_comments(entry_id):
    comments = CommentService.get_comments(entry_id)
    return jsonify(comments), 200  # ✅ FIXED: Ensure a list of dictionaries is returned

# Update a specific comment
@comment_bp.route("/comments/<int:comment_id>", methods=["PUT"])
@jwt_required()
def update_comment(comment_id):
    data = request.get_json()
    current_user_id = get_jwt_identity()

    if not data or "content" not in data:
        return jsonify({"error": "Missing required content"}), 400

    updated_comment = CommentService.update_comment(comment_id, current_user_id, data["content"])
    if updated_comment:
        return jsonify({"message": "Comment updated", "comment": updated_comment}), 200  # ✅ FIXED: Return dict
    return jsonify({"error": "Comment not found or unauthorized"}), 404  # ✅ Improved error handling

# Delete a specific comment
@comment_bp.route("/comments/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(comment_id):
    current_user_id = get_jwt_identity()

    if CommentService.delete_comment(comment_id, current_user_id):
        return jsonify({"message": "Comment deleted"}), 200  # ✅ FIXED: Consistent response
    return jsonify({"error": "Comment not found or unauthorized"}), 404  # ✅ Improved error handling