def field_change_status_schema():
    return {
        'id': {
            'type': 'integer',
            'required': True,
            'empty': False
        },
        'status': {
            'type': 'boolean',
            'required': True,
            'empty': False
        },
        'comment': {
            'type': 'string',
            'required': True,
            'empty': True
        }
    }


def additional_fields_add_schema():
    return {
        'id': {
            'type': 'integer',
            'required': True,
            'empty': False
        },
        'value': {
            'type': 'string',
            'required': True,
            'empty': True
        }
    }
