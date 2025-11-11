from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError
from ..models import db, User
from ..schemas import UserCreate
from ..utils.response import api_response

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.post("/register")
def register():
    try:
        payload = UserCreate().load(request.get_json(force=True))
    except ValidationError as e:
        return jsonify(api_response(False, None, "validation_error", e.messages)), 400

    if User.query.filter_by(email=payload["email"]).first():
        return jsonify(api_response(False, None, "email_exists", "email_exists")), 409

    u = User(email=payload["email"], role=payload["role"],
             push_tokens=payload.get("push_tokens", []),
             preferences=payload.get("preferences", {}))
    u.set_password(payload["password"])
    db.session.add(u); db.session.commit()

    token = create_access_token(identity=u.id, additional_claims={"role": u.role})
    return jsonify(api_response(True, {"access_token": token, "user_id": u.id}, "created")), 201

@bp.post("/login")
def login():
    body = request.get_json(force=True) or {}
    email = body.get("email"); password = body.get("password")
    if not email or not password:
        return jsonify(api_response(False, None, "missing_credentials", "invalid_request")), 400
    u = User.query.filter_by(email=email).first()
    if not u or not u.check_password(password):
        return jsonify(api_response(False, None, "invalid_credentials", "unauthorized")), 401
    token = create_access_token(identity=u.id, additional_claims={"role": u.role})
    return jsonify(api_response(True, {"access_token": token, "user_id": u.id}))
