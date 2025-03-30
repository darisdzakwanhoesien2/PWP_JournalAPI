# journalapi/schemas.py
from marshmallow import Schema, fields, validate, ValidationError, EXCLUDE

class UserRegisterSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # or INCLUDE if you prefer
    username = fields.Str(required=True, validate=validate.Length(min=1))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))

class UserLoginSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class JournalEntrySchema(Schema):
    class Meta:
        unknown = EXCLUDE
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    tags = fields.List(fields.Str(), required=True)

class CommentSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    content = fields.Str(required=True, validate=validate.Length(min=1))