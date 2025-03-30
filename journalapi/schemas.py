from marshmallow import Schema, fields, validate, ValidationError

class UserRegisterSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=1))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class JournalEntrySchema(Schema):
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    tags = fields.List(fields.Str(), required=True)

class CommentSchema(Schema):
    content = fields.Str(required=True, validate=validate.Length(min=1))
