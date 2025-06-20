## current code
from marshmallow import Schema, fields, validate, ValidationError

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=1))
    email = fields.Email(required=True)
    registered_at = fields.DateTime(dump_only=True)

class EntrySchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    title = fields.Str(required=True, validate=validate.Length(min=1))
    content = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class CommentSchema(Schema):
    id = fields.Int(dump_only=True)
    entry_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    content = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class EditHistorySchema(Schema):
    id = fields.Int(dump_only=True)
    entry_id = fields.Int(required=True)
    edited_at = fields.DateTime(dump_only=True)
    changes = fields.Dict()
