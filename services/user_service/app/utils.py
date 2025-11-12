import re
import html

def sanitize_string(value):
    """Sanitize string input to prevent XSS attacks"""
    if not isinstance(value, str):
        return value
    
    # Remove HTML tags
    value = re.sub(r'<[^>]*>', '', value)
    
    # Escape special characters
    value = html.escape(value)
    
    return value.strip()

def sanitize_dict(data):
    """Recursively sanitize dictionary values"""
    if isinstance(data, dict):
        return {key: sanitize_dict(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_dict(item) for item in data]
    elif isinstance(data, str):
        return sanitize_string(data)
    else:
        return data

def validate_uuid(uuid_string):
    """Validate UUID format"""
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(uuid_string))

def get_pagination_meta(page, limit, total):
    """Generate pagination metadata"""
    total_pages = (total + limit - 1) // limit if total > 0 else 0
    return {
        'total': total,
        'limit': limit,
        'page': page,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_previous': page > 1
    }

def format_response(success=True, data=None, error=None, message='', meta=None):
    """Format API response according to task requirements"""
    response = {
        'success': success,
        'message': message
    }
    if data is not None:
        response['data'] = data
    if error is not None:
        response['error'] = error
    if meta is not None:
        response['meta'] = meta
    return response