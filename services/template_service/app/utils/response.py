from typing import Any, Optional, Dict

def api_response(success: bool, data: Optional[Any] = None,
                 message: str = "ok", error: Optional[str] = None,
                 meta: Optional[Dict] = None):
    default_meta = meta or {
        "total": (1 if data is not None and not isinstance(data, list) else (len(data) if isinstance(data, list) else 0)),
        "limit": 0, "page": 0, "total_pages": 0,
        "has_next": False, "has_previous": False
    }
    return {
        "success": success,
        "data": data,
        "error": error,
        "message": message,
        "meta": default_meta
    }
