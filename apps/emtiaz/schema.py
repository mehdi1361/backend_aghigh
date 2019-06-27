def activity_param_add_schema():
    return {
        'id': {
            'type': 'integer',
            'required': True,
            'empty': False
        },
        'value': {
            'type': 'integer',
            'required': True,
            'empty': False,
            'min': 0,
            'max': 5
        }
    }
