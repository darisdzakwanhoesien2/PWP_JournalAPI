from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.journal_entry_service import JournalEntryService
import json

journal_entry_bp = Blueprint("entries", __name__)

@journal_entry_bp.route("/", methods=["POST"])
@jwt_required()
def create_entry():
    user_id = get_jwt_identity()
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")
    tags = data.get("tags", [])

    if not title or not content:
        return jsonify({"error": "Missing required fields"}), 400

    entry = JournalEntryService.create_entry(user_id, title, content, tags)
    return jsonify({"message": "Entry created successfully", "entry": entry.to_dict()}), 201

@journal_entry_bp.route("/", methods=["GET"])
@jwt_required()
def get_entries():
    user_id = get_jwt_identity()
    entries = JournalEntryService.get_entries(user_id)
    return jsonify([entry.to_dict() for entry in entries]), 200

@journal_entry_bp.route("/<int:entry_id>", methods=["GET"])
@jwt_required()
def get_entry(entry_id):
    user_id = get_jwt_identity()
    entry = JournalEntryService.get_entry(entry_id)
    if not entry or entry.user_id != user_id:
        return jsonify({"error": "Entry not found"}), 404

    return jsonify(entry.to_dict()), 200

@journal_entry_bp.route("/<int:entry_id>", methods=["PUT"])
@jwt_required()
def update_entry(entry_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    updated_entry = JournalEntryService.update_entry(
        entry_id,
        title=data.get("title"),
        content=data.get("content"),
        tags=data.get("tags")
    )
    if not updated_entry or updated_entry.user_id != user_id:
        return jsonify({"error": "Entry not found"}), 404

    return jsonify({"message": "Entry updated successfully", "entry": updated_entry.to_dict()}), 200

@journal_entry_bp.route("/<int:entry_id>", methods=["DELETE"])
@jwt_required()
def delete_entry(entry_id):
    user_id = get_jwt_identity()
    if not JournalEntryService.delete_entry(entry_id):
        return jsonify({"error": "Entry not found"}), 404

    return jsonify({"message": "Entry deleted successfully"}), 200