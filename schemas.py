"""Marshmallow schemas for the Journal API."""
from marshmallow import Schema, fields, validates, ValidationError

class CommentSchema(Schema):
    content = fields.Str(required=True)

    @validates("content")
    def validate_content(self, value):
        if len(value) < 1:
            raise ValidationError("Shorter than minimum length 1.")

class JournalEntrySchema(Schema):
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    tags = fields.List(fields.Str, required=False, missing=[])

class UserRegisterSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda s: len(s) >= 6)

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)