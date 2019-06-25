from cerberus import Validator

def to_date(s):
    return datetime.strptime(s, '%Y-%m-%d') if s else None

def client_base():
    return {
        'name': {"type": "string", "empty": False, "required": True},
        'uri': {"type": "string", "empty": False, "required": True},
        'scope': {"type": "list", "empty": False, "required": True},
        'redirect_uri': {"type": "string", "empty": False, "required": True}
    }

def client_create():
    return dict(client_base(), **{
        'expired_at': {"type": "date", "coerce": to_date, "required": False, "empty": True}
    })


def validate(data, type_schema):
    schema = eval('{}()'.format(type_schema))
    
    v = Validator(schema)
    if not v.validate(data):
        return v.errors, False
    return data, True