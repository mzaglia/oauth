#
# This file is part of OBT OAuth 2.0.
# Copyright (C) 2019-2020 INPE.
#
# OBT OAuth 2.0 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""
validation of auth controllers schemas
"""

from cerberus import Validator

def login():
    return {
        'username': {"type": "string", "empty": False, "required": True},
        'password': {"type": "string", "empty": False, "required": True}
    }

def validate(data, type_schema):
    schema = eval('{}()'.format(type_schema))
    
    v = Validator(schema)
    if not v.validate(data):
        return v.errors, False
    return data, True
