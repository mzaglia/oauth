"""
validation of client controllers schemas
"""

from datetime import datetime
from cerberus import Validator

def to_date(s):
    return datetime.strptime(s, '%Y-%m-%d') if s else None

def valide_scope(list_scope):
    for scope in list_scope:
        if scope not in ['read']:
            return None
    return list_scope

def client_base():
    return {
        'client_name': {"type": "string", "empty": False, "required": True},
        'client_uri': {"type": "string", "empty": False, "required": True},
        'redirect_uri': {"type": "string", "empty": False, "required": True}
    }

def date_expiration():
    return {
        'expired_at': {"type": "date", "coerce": to_date, "required": False, "empty": True}
    }

def client_create():
    return dict(client_base(), **date_expiration(), **{
        'scope': {"type": "list", "coerce": valide_scope, "empty": False, "required": True}
    })
    

def validate(data, type_schema):
    schema = eval('{}()'.format(type_schema))
    
    v = Validator(schema)
    if not v.validate(data):
        return v.errors, False
    return data, True