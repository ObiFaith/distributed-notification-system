"""
Validation schemas for template service
"""

def validate_template_data(data):
    """Validate template creation data"""
    errors = {}
    
    if not data.get('code'):
        errors['code'] = 'Template code is required'
    
    if not data.get('name'):
        errors['name'] = 'Template name is required'
    
    if not data.get('notification_type'):
        errors['notification_type'] = 'Notification type is required'
    elif data['notification_type'] not in ['email', 'push', 'sms']:
        errors['notification_type'] = 'Invalid notification type'
    
    if not data.get('body'):
        errors['body'] = 'Template body is required'
    
    return errors