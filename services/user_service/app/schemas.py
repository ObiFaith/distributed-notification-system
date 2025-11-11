from marshmallow import Schema, fields, validate

# read models
class UserOut(Schema):
    id = fields.Str(required=True)
    email = fields.Email(required=True)
    role = fields.Str(required=True)
    push_tokens = fields.List(fields.Str(), required=True)
    preferences = fields.Dict(required=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

# write models
class UserCreate(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    role = fields.Str(load_default="user", validate=validate.OneOf(["user","admin"]))
    push_tokens = fields.List(fields.Str(), load_default=list)
    preferences = fields.Dict(load_default=dict)

class UserUpdate(Schema):
    role = fields.Str(validate=validate.OneOf(["user","admin"]))
    push_tokens = fields.List(fields.Str())
    preferences = fields.Dict()

class PreferencesUpdate(Schema):
    # free-form dict merge
    __schema__ = True
