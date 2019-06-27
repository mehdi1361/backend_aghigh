def announcements_schema():
    return {
        'title': {
            'type': 'string',
            'required': True,
            'empty': False
        },
        'description': {
            'type': 'string',
            'required': True,
            'empty': False
        },
        'receivers': {
            'type': 'list',
            'required': True,
            'empty': False
        }
    }


def update_announcements_schema():
    return {
        'title': {
            'type': 'string',
            'required': True,
            'empty': False
        },
        'description': {
            'type': 'string',
            'required': True,
            'empty': False
        }
    }
