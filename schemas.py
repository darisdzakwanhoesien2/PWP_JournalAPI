"""Marshmallow schemas for the Journal API."""
from marshmallow import Schema, fields, validate

class CommentSchema(Schema):
    """Schema for validating comment data."""
    content = fields.Str(required=True, validate=validate.Length(min=1))

class JournalEntrySchema(Schema):
    """Schema for validating journal entry data."""
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    content = fields.Str(required=True, validate=validate.Length(min=1))
    tags = fields.List(fields.Str(), missing=[])

class UserRegisterSchema(Schema):
    """Schema for validating user registration data."""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6), load_only=True)

class UserLoginSchema(Schema):
    """Schema for validating user login data."""
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)

# # schemas.py
# from marshmallow import Schema, fields, validate, EXCLUDE

# class UserRegisterSchema(Schema):
#     class Meta:
#         unknown = EXCLUDE
#     username = fields.Str(required=True, validate=validate.Length(min=1))
#     email = fields.Email(required=True)
#     password = fields.Str(required=True, validate=validate.Length(min=6))

# class UserLoginSchema(Schema):
#     class Meta:
#         unknown = EXCLUDE
#     email = fields.Email(required=True)
#     password = fields.Str(required=True)

# class JournalEntrySchema(Schema):
#     class Meta:
#         unknown = EXCLUDE
#     title = fields.Str(required=True)
#     content = fields.Str(required=True)
#     tags = fields.List(fields.Str(), required=True)

# class CommentSchema(Schema):
#     class Meta:
#         unknown = EXCLUDE
#     content = fields.Str(required=True, validate=validate.Length(min=1))