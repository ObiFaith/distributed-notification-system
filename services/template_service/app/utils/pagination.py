from math import ceil

def paginate(query, page: int, limit: int):
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    total_pages = ceil(total / limit) if limit else 1
    meta = {
        "total": total,
        "limit": limit,
        "page": page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1
    }
    return items, meta
