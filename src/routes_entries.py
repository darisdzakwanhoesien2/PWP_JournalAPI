from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from src.data_store import load_entries, save_entries, load_comments, save_comments, load_edit_history, save_edit_history, get_next_id
from src.models_orm import Entry, Comment, EditHistory
from src.utils import entry_links, entries_collection_links, comment_links, comments_collection_links, edit_history_links, edit_history_collection_links
from src.schemas import EntrySchema, CommentSchema, EditHistorySchema
from src.cache import cache

"""Module for entry-related API routes."""

entries_bp = Blueprint('entries', __name__)
entry_schema = EntrySchema()
comment_schema = CommentSchema()
edit_history_schema = EditHistorySchema()

def _build_entry_response(entry):
    """
    Helper function to build entry response dictionary with links.
    """
    entry_dict = entry.to_dict()
    entry_dict['_links'] = entry_links(entry.id, entry.user_id)
    return entry_dict

def _build_comment_response(comment, entry_id):
    """
    Helper function to build comment response dictionary with links.
    """
    comment_dict = comment.to_dict()
    comment_dict['_links'] = comment_links(comment.id, entry_id=entry_id)
    return comment_dict

def _build_edit_history_response(edit, entry_id):
    """
    Helper function to build edit history response dictionary with links.
    """
    edit_dict = edit.to_dict()
    edit_dict['_links'] = edit_history_links(entry_id, edit.id)
    return edit_dict

@entries_bp.route('', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300)
def get_entries():
    """
    Retrieve a list of all entries.
    """
    entries_data = load_entries()
    entries = [Entry.from_dict(e) for e in entries_data]
    result = []
    for entry in entries:
        entry_dict = entry.to_dict()
        entry_dict['_links'] = entry_links(entry.id, entry.user_id)
        result.append(entry_dict)
    response = {
        'items': result,
        '_links': entries_collection_links()
    }
    return jsonify(response), 200

@entries_bp.route('', methods=['POST'])
@jwt_required()
def create_entry():
    """
    Create a new entry.
    """
    json_data = request.get_json()
    if not json_data:
        abort(400, description='No input data provided')
    try:
        data = entry_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    entries_data = load_entries()
    new_id = get_next_id(entries_data)
    entry = Entry(id=new_id, user_id=data['user_id'], title=data['title'], content=data['content'])
    entries_data.append(entry.to_dict())
    save_entries(entries_data)
    entry_dict = entry.to_dict()
    entry_dict['_links'] = entry_links(entry.id, entry.user_id)
    return jsonify(entry_dict), 201

@entries_bp.route('/<int:entry_id>', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300)
def get_entry(entry_id):
    """
    Retrieve an entry by ID.
    """
    entries_data = load_entries()
    entry_data = next((e for e in entries_data if e['id'] == entry_id), None)
    if not entry_data:
        abort(404, description='Entry not found')
    entry = Entry.from_dict(entry_data)
    entry_dict = entry.to_dict()
    entry_dict['_links'] = entry_links(entry.id, entry.user_id)
    return jsonify(entry_dict), 200

@entries_bp.route('/<int:entry_id>', methods=['PUT'])
@jwt_required()
def update_entry(entry_id):
    """
    Update an entry's information.
    """
    json_data = request.get_json()
    if not json_data:
        abort(400, description='No input data provided')
    try:
        data = entry_schema.load(json_data, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400
    entries_data = load_entries()
    entry_index = next((i for i, e in enumerate(entries_data) if e['id'] == entry_id), None)
    if entry_index is None:
        abort(404, description='Entry not found')
    # Save old entry for edit history
    old_entry = entries_data[entry_index].copy()
    # Update fields if present
    if 'title' in data:
        entries_data[entry_index]['title'] = data['title']
    if 'content' in data:
        entries_data[entry_index]['content'] = data['content']
    entries_data[entry_index]['updated_at'] = data.get('updated_at') or old_entry.get('updated_at')
    save_entries(entries_data)
    # Add to edit history
    edit_history_data = load_edit_history()
    new_edit_id = get_next_id(edit_history_data)
    changes = {}
    for field in ['title', 'content']:
        if field in data and data[field] != old_entry.get(field):
            changes[field] = {'old': old_entry.get(field), 'new': data[field]}
    if changes:
        edit_history = EditHistory(id=new_edit_id, entry_id=entry_id, changes=changes)
        edit_history_data.append(edit_history.to_dict())
        save_edit_history(edit_history_data)
    entry = Entry.from_dict(entries_data[entry_index])
    entry_dict = entry.to_dict()
    entry_dict['_links'] = entry_links(entry.id, entry.user_id)
    return jsonify(entry_dict), 200

@entries_bp.route('/<int:entry_id>', methods=['DELETE'])
@jwt_required()
def delete_entry(entry_id):
    """
    Delete an entry by ID.
    """
    entries_data = load_entries()
    entry_index = next((i for i, e in enumerate(entries_data) if e['id'] == entry_id), None)
    if entry_index is None:
        abort(404, description='Entry not found')
    entries_data.pop(entry_index)
    save_entries(entries_data)
    return '', 204

@entries_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300)
def get_entries_by_user(user_id):
    """
    Retrieve entries by user ID.
    """
    entries_data = load_entries()
    user_entries = [Entry.from_dict(e) for e in entries_data if e['user_id'] == user_id]
    result = []
    for entry in user_entries:
        entry_dict = entry.to_dict()
        entry_dict['_links'] = entry_links(entry.id, entry.user_id)
        result.append(entry_dict)
    response = {
        'items': result,
        '_links': entries_collection_links(user_id=user_id)
    }
    return jsonify(response), 200

@entries_bp.route('/<int:entry_id>/comments', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300)
def get_comments(entry_id):
    """
    Retrieve comments for an entry.
    """
    comments_data = load_comments()
    entry_comments = [Comment.from_dict(c) for c in comments_data if c['entry_id'] == entry_id]
    result = []
    for comment in entry_comments:
        comment_dict = comment.to_dict()
        comment_dict['_links'] = comment_links(comment.id, entry_id=entry_id)
        result.append(comment_dict)
    response = {
        'items': result,
        '_links': comments_collection_links(entry_id=entry_id)
    }
    return jsonify(response), 200

@entries_bp.route('/<int:entry_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(entry_id):
    """
    Add a comment to an entry.
    """
    import logging
    json_data = request.get_json()
    if not json_data:
        abort(400, description='No input data provided')
    # Inject entry_id from URL into json_data before validation
    json_data['entry_id'] = entry_id
    try:
        data = comment_schema.load(json_data)
    except ValidationError as err:
        logging.error("Validation error in add_comment: %s", err.messages)
        return jsonify(err.messages), 400
    comments_data = load_comments()
    new_id = get_next_id(comments_data)
    comment = Comment(id=new_id, entry_id=entry_id, user_id=data['user_id'], content=data['content'])
    comments_data.append(comment.to_dict())
    save_comments(comments_data)
    logging.info("Comment added: %s", comment.to_dict())
    comment_dict = comment.to_dict()
    comment_dict['_links'] = comment_links(comment.id, entry_id=entry_id)
    return jsonify(comment_dict), 201

@entries_bp.route('/comments/<int:comment_id>', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300)
def get_comment(comment_id):
    """
    Retrieve a comment by ID.
    """
    comments_data = load_comments()
    comment_data = next((c for c in comments_data if c['id'] == comment_id), None)
    if not comment_data:
        abort(404, description='Comment not found')
    comment = Comment.from_dict(comment_data)
    comment_dict = comment.to_dict()
    comment_dict['_links'] = comment_links(comment.id, entry_id=comment.entry_id)
    return jsonify(comment_dict), 200

@entries_bp.route('/comments/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    """
    Update a comment by ID.
    """
    import logging
    logging.info("Request headers: %s", dict(request.headers))
    logging.info("Request json: %s", request.get_json())
    json_data = request.get_json()
    if not json_data:
        abort(400, description='No input data provided')
    try:
        data = comment_schema.load(json_data, partial=True)
    except ValidationError as err:
        logging.error("Validation error in update_comment: %s", err.messages)
        return jsonify(err.messages), 400
    comments_data = load_comments()
    logging.info("Updating comment with id %s (type %s), current comments IDs: %s", comment_id, type(comment_id), [c['id'] for c in comments_data])
    comment_index = next((i for i, c in enumerate(comments_data) if c['id'] == comment_id), None)
    if comment_index is None:
        logging.error("Comment with id %s not found for update", comment_id)
        abort(404, description='Comment not found')
    comments_data[comment_index]['content'] = data['content']
    comments_data[comment_index]['updated_at'] = data.get('updated_at') or comments_data[comment_index].get('updated_at')
    save_comments(comments_data)
    comment = Comment.from_dict(comments_data[comment_index])
    comment_dict = comment.to_dict()
    comment_dict['_links'] = comment_links(comment.id, entry_id=comment.entry_id)
    return jsonify(comment_dict), 200

@entries_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """
    Delete a comment by ID.
    """
    import logging
    logging.info("Request headers: %s", dict(request.headers))
    comments_data = load_comments()
    logging.info("Deleting comment with id %s (type %s), current comments IDs: %s", comment_id, type(comment_id), [c['id'] for c in comments_data])
    comment_index = next((i for i, c in enumerate(comments_data) if c['id'] == comment_id), None)
    if comment_index is None:
        logging.error("Comment with id %s not found for deletion", comment_id)
        abort(404, description='Comment not found')
    comments_data.pop(comment_index)
    save_comments(comments_data)
    return '', 204

@entries_bp.route('/<int:entry_id>/edit_history', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300)
def get_edit_history(entry_id):
    """
    Retrieve edit history for an entry.
    """
    edit_history_data = load_edit_history()
    entry_edit_history = [EditHistory.from_dict(e) for e in edit_history_data if e['entry_id'] == entry_id]
    result = []
    for edit in entry_edit_history:
        edit_dict = edit.to_dict()
        edit_dict['_links'] = edit_history_links(entry_id, edit.id)
        result.append(edit_dict)
    response = {
        'items': result,
        '_links': edit_history_collection_links(entry_id)
    }
    return jsonify(response), 200

@entries_bp.route('/<int:entry_id>/edit_history/<int:edit_id>', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300)
def get_edit_history_item(entry_id, edit_id):
    """
    Retrieve a specific edit history item by ID.
    """
    edit_history_data = load_edit_history()
    edit_data = next((e for e in edit_history_data if e['entry_id'] == entry_id and e['id'] == edit_id), None)
    if not edit_data:
        abort(404, description='Edit history item not found')
    edit = EditHistory.from_dict(edit_data)
    edit_dict = edit.to_dict()
    edit_dict['_links'] = edit_history_links(entry_id, edit_id)
    return jsonify(edit_dict), 200
