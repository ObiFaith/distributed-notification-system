from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import func
from jinja2 import Template as JinjaTemplate
from ..models import db, Template
from ..schemas import TemplateOut, TemplateCreate, TemplateRenderIn
from ..utils.response import api_response
from ..utils.pagination import paginate

bp = Blueprint("templates", __name__, url_prefix="/")

# List templates with filters + pagination
@bp.get("/templates")
def list_templates():
    code = request.args.get("code")
    language = request.args.get("language")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))

    q = Template.query
    if code:
        q = q.filter(Template.code == code)
    if language:
        q = q.filter(Template.language == language)

    q = q.order_by(Template.code.asc(), Template.language.asc(), Template.version.desc())
    items, meta = paginate(q, page, limit)
    data = TemplateOut(many=True).dump(items)
    return jsonify(api_response(True, data, meta=meta))

# Get specific template (latest or version) by code + optional lang/version
@bp.get("/templates/<code>")
def get_template(code: str):
    lang = request.args.get("lang", "en")
    version = request.args.get("version", "latest")

    q = Template.query.filter_by(code=code, language=lang)
    if version == "latest":
        tpl = q.order_by(Template.version.desc()).first()
    else:
        try:
            version_int = int(version)
        except ValueError:
            return jsonify(api_response(False, None, "validation_error", "version_must_be_int_or_latest")), 400
        tpl = q.filter_by(version=version_int).first()

    if not tpl:
        return jsonify(api_response(False, None, "not_found", "template_not_found")), 404

    return jsonify(api_response(True, TemplateOut().dump(tpl)))

# Create a new template version (auto-increments per code+language)
@bp.post("/templates")
def create_template():
    try:
        payload = TemplateCreate().load(request.get_json(force=True))
    except ValidationError as e:
        return jsonify(api_response(False, None, "validation_error", e.messages)), 400

    code = payload["code"]
    lang = payload["language"]

    latest_version = db.session.query(func.max(Template.version))\
        .filter_by(code=code, language=lang).scalar() or 0

    tpl = Template(
        code=code, language=lang, version=latest_version + 1,
        subject=payload.get("subject"),
        body_html=payload.get("body_html"),
        body_text=payload.get("body_text"),
        meta=payload.get("meta", {})
    )
    db.session.add(tpl)
    db.session.commit()

    return jsonify(api_response(True, {
        "code": tpl.code, "language": tpl.language, "version": tpl.version, "id": tpl.id
    }, "created")), 201

# Render a template by code/lang/version with variables (variable substitution)
@bp.post("/templates/render")
def render_template_preview():
    try:
        payload = TemplateRenderIn().load(request.get_json(force=True))
    except ValidationError as e:
        return jsonify(api_response(False, None, "validation_error", e.messages)), 400

    code = payload["template_code"]
    lang = payload.get("language", "en")
    version = payload.get("version", "latest")
    data = payload.get("data", {})

    q = Template.query.filter_by(code=code, language=lang)
    if version == "latest":
        tpl = q.order_by(Template.version.desc()).first()
    else:
        try:
            version_int = int(version)
        except ValueError:
            return jsonify(api_response(False, None, "validation_error", "version_must_be_int_or_latest")), 400
        tpl = q.filter_by(version=version_int).first()

    if not tpl:
        return jsonify(api_response(False, None, "not_found", "template_not_found")), 404

    rendered = {
        "subject": JinjaTemplate(tpl.subject or "").render(**data),
        "html": JinjaTemplate(tpl.body_html or "").render(**data),
        "text": JinjaTemplate(tpl.body_text or "").render(**data)
    }
    return jsonify(api_response(True, rendered))

# List all versions for a given code + language
@bp.get("/templates/<code>/versions")
def list_versions(code: str):
    lang = request.args.get("lang", "en")
    q = Template.query.filter_by(code=code, language=lang).order_by(Template.version.desc())
    items = q.all()
    if not items:
        return jsonify(api_response(False, None, "not_found", "template_not_found")), 404
    data = TemplateOut(many=True).dump(items)
    meta = {
        "total": len(items), "limit": len(items), "page": 1,
        "total_pages": 1, "has_next": False, "has_previous": False
    }
    return jsonify(api_response(True, data, meta=meta))
