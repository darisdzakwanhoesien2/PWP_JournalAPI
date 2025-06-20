"""Schemas for serializing and deserializing API data."""

from marshmallow import Schema, fields, validate
from marshmallow import ValidationError

class UserSchema(Schema):
    """Schema for User data."""
    username = fields.Str(required=True, validate=validate.Length(min=1))
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))

class EntrySchema(Schema):
    """Schema for Entry data."""
    user_id = fields.Int(required=True)
    title = fields.Str(required=True, validate=validate.Length(min=1))
    content = fields.Str(required=True)

class CommentSchema(Schema):
    """Schema for Comment data."""
    entry_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    content = fields.Str(required=True)

class EditHistorySchema(Schema):
    """Schema for Edit History data."""
    entry_id = fields.Int(required=True)
    edited_at = fields.DateTime()
    changes = fields.Str()
