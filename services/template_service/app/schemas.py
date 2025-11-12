def validate_template_data(data: dict) -> dict:
    errors = {}
    if not isinstance(data.get('variables', []), list):
        errors['variables'] = 'Variables must be a list'
    ...
    return errors