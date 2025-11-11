from flask import request, jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from functools import wraps

def require_auth(optional=False):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request(optional=optional)
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def require_role(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") not in roles:
                return jsonify({"success": False, "data": None,
                                "error": "forbidden", "message": "forbidden",
                                "meta": {"total":0,"limit":0,"page":0,"total_pages":0,
                                         "has_next":False,"has_previous":False}}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
