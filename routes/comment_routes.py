from flask import Blueprint, request, jsonify
from database import db
from models.comment import Comment
from services.comment_service import CommentService

comment_bp = Blueprint("comments", __name__)

# Add a comment to a journal entry
@comment_bp.route("/entries/<int:entry_id>/comments", methods=["POST"])
def add_comment(entry_id):
    data = request.get_json()
    if not data or "user_id" not in data or "content" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    comment = CommentService.add_comment(entry_id, data["user_id"], data["content"])
    return jsonify({"message": "Comment added successfully", "comment": comment.to_dict()}), 201

# Retrieve all comments for a specific journal entry
@comment_bp.route("/entries/<int:entry_id>/comments", methods=["GET"])
def get_comments(entry_id):
    comments = CommentService.get_comments(entry_id)
    return jsonify([comment.to_dict() for comment in comments]), 200

# Update a specific comment
@comment_bp.route("/comments/<int:comment_id>", methods=["PUT"])
def update_comment(comment_id):
    data = request.get_json()
    if not data or "content" not in data:
        return jsonify({"error": "Missing required content"}), 400

    updated_comment = CommentService.update_comment(comment_id, data["content"])
    if updated_comment:
        return jsonify({"message": "Comment updated", "comment": updated_comment.to_dict()}), 200
    return jsonify({"error": "Comment not found"}), 404

# Delete a specific comment
@comment_bp.route("/comments/<int:comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    if CommentService.delete_comment(comment_id):
        return jsonify({"message": "Comment deleted"}), 200
    return jsonify({"error": "Comment not found"}), 404
