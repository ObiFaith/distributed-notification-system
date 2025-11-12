"""
Validation schemas for user service
"""

def validate_user_data(data):
    """Validate user creation data"""
    errors = {}
    
    if not data.get('name'):
        errors['name'] = 'Name is required'
    elif len(data['name']) < 2:
        errors['name'] = 'Name must be at least 2 characters'
    
    if not data.get('email'):
        errors['email'] = 'Email is required'
    elif '@' not in data.get('email', ''):
        errors['email'] = 'Invalid email format'
    
    if not data.get('password'):
        errors['password'] = 'Password is required'
    elif len(data['password']) < 6:
        errors['password'] = 'Password must be at least 6 characters'
    
    return errors


def validate_login_data(data):
    """Validate login data"""
    errors = {}
    
    if not data.get('email'):
        errors['email'] = 'Email is required'
    
    if not data.get('password'):
        errors['password'] = 'Password is required'
    
    return errors