from marshmallow import Schema, fields, validate

class TemplateOut(Schema):
    id = fields.Str(required=True)
    code = fields.Str(required=True)
    language = fields.Str(required=True)
    version = fields.Int(required=True)
    subject = fields.Str(allow_none=True)
    body_html = fields.Str(allow_none=True)
    body_text = fields.Str(allow_none=True)
    meta = fields.Dict(required=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

class TemplateCreate(Schema):
    code = fields.Str(required=True)
    language = fields.Str(load_default="en", validate=validate.Length(min=2, max=10))
    subject = fields.Str(allow_none=True, load_default=None)
    body_html = fields.Str(allow_none=True, load_default=None)
    body_text = fields.Str(allow_none=True, load_default=None)
    meta = fields.Dict(load_default=dict)

class TemplateRenderIn(Schema):
    template_code = fields.Str(required=True)
    language = fields.Str(load_default="en")
    version = fields.Raw(load_default="latest")  # "latest" or int
    data = fields.Dict(load_default=dict)
