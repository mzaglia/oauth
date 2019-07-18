"""
validation of user controllers schemas
"""

from cerberus import Validator

def user_base():
    return {
        'name': {"type": "string", "empty": False, "required": True},
        'email': {"type": "string", "empty": False, "required": True},
        'institution': {"type": "string", "empty": True, "required": False},
        'occupation': {"type": "string", "empty": True, "required": False}
    }

def user_password():
    return {
        'password': {"type": "string", "empty": False, "required": True},
        'confirm_password': {"type": "string", "empty": False, "required": True}
    }

def user_change_password():
    return dict(user_password(), **{
        'old_password': {"type": "string", "empty": False, "required": True},
    })

def user_create():
    return dict(user_base(), **user_password())

def user_update():
    return user_base()


def validate(data, type_schema, validate_password=False):
    schema = eval('{}()'.format(type_schema))
    
    v = Validator(schema)
    if not v.validate(data):
        return v.errors, False
        
    if validate_password and data['password'] != data['confirm_password']:
        return {
            'message': 'Password and password confirm must be the same!'
        }, False
    return data, True