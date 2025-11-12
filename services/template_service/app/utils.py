def get_pagination_meta(page, limit, total):
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