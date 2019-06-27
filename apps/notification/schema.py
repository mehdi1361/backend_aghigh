def add_token_schema():
    return {
        'token': {
            'type': 'string',
            'required': True,
            'empty': False
        },
        'device': {
            'type': 'string',
            'allowed': ['mobile', 'web'],
            'required': True,
            'empty': False
        }
    }
