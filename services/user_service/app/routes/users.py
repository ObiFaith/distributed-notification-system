from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity
from ..models import db, User
from ..schemas import UserOut, UserCreate, UserUpdate
from ..utils.response import api_response
from ..utils.pagination import paginate
from ..utils.security import require_auth, require_role

bp = Blueprint("users", __name__, url_prefix="/")

@bp.get("/users")
@require_auth(optional=True)
def list_users():
    # admin-only listing; normal users get just themselves if authenticated
    claims_role = (getattr(get_jwt_identity, "__call__", lambda: None)() and "user")  # avoid error when optional
    role = None
    try:
        from flask_jwt_extended import get_jwt
        role = get_jwt().get("role")
    except Exception:
        pass

    q = User.query
    if role != "admin":
        uid = None
        try:
            from flask_jwt_extended import get_jwt_identity
            uid = get_jwt_identity()
        except Exception:
            uid = None
        if uid:
            q = q.filter(User.id == uid)
        else:
            return jsonify(api_response(False, None, "forbidden", "forbidden")), 403

    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    items, meta = paginate(q.order_by(User.created_at.desc()), page, limit)
    data = UserOut(many=True).dump(items)
    return jsonify(api_response(True, data, meta=meta))

@bp.post("/users")
@require_role("admin")
def create_user():
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
    return jsonify(api_response(True, UserOut().dump(u), "created")), 201

@bp.get("/users/<user_id>")
@require_auth(optional=True)
def get_user(user_id):
    u = User.query.get(user_id)
    if not u:
        return jsonify(api_response(False, None, "not_found", "user_not_found")), 404

    # permission: self or admin
    role = None
    try:
        from flask_jwt_extended import get_jwt
        role = get_jwt().get("role")
        uid = get_jwt_identity()
    except Exception:
        role, uid = None, None

    if role != "admin" and uid != u.id:
        return jsonify(api_response(False, None, "forbidden", "forbidden")), 403

    return jsonify(api_response(True, UserOut().dump(u)))

@bp.patch("/users/<user_id>")
@require_role("admin")
def update_user(user_id):
    u = User.query.get(user_id)
    if not u:
        return jsonify(api_response(False, None, "not_found", "user_not_found")), 404
    try:
        payload = UserUpdate().load(request.get_json(force=True))
    except ValidationError as e:
        return jsonify(api_response(False, None, "validation_error", e.messages)), 400

    if "role" in payload: u.role = payload["role"]
    if "push_tokens" in payload: u.push_tokens = payload["push_tokens"]
    if "preferences" in payload: u.preferences = payload["preferences"]
    db.session.commit()
    return jsonify(api_response(True, UserOut().dump(u)))

@bp.patch("/users/<user_id>/preferences")
@require_auth()
def update_preferences(user_id):
    u = User.query.get(user_id)
    if not u:
        return jsonify(api_response(False, None, "not_found", "user_not_found")), 404
    uid = get_jwt_identity()
    role = None
    from flask_jwt_extended import get_jwt
    role = get_jwt().get("role")
    if role != "admin" and uid != u.id:
        return jsonify(api_response(False, None, "forbidden", "forbidden")), 403

    body = request.get_json(force=True) or {}
    u.preferences = {**(u.preferences or {}), **body}
    db.session.commit()
    return jsonify(api_response(True, {"id": u.id, "preferences": u.preferences}))

@bp.delete("/users/<user_id>")
@require_role("admin")
def delete_user(user_id):
    u = User.query.get(user_id)
    if not u:
        return jsonify(api_response(False, None, "not_found", "user_not_found")), 404
    db.session.delete(u); db.session.commit()
    return jsonify(api_response(True, {"id": user_id}, "deleted"))
