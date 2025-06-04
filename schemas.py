"""Marshmallow schemas for validating API payloads."""
from marshmallow import Schema, fields, validate

class UserRegisterSchema(Schema):
    """Schema for user registration payload."""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))

class UserLoginSchema(Schema):
    """Schema for user login payload."""
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class JournalEntrySchema(Schema):
    """Schema for journal entry payload."""
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    content = fields.Str(required=True, validate=validate.Length(min=1))
    tags = fields.List(fields.Str(), required=False, load_default=[])

class CommentSchema(Schema):
    """Schema for comment payload."""
    content = fields.Str(required=True, validate=validate.Length(min=1, max=500))