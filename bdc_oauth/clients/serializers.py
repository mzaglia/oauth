#
# This file is part of OBT OAuth 2.0.
# Copyright (C) 2019-2020 INPE.
#
# OBT OAuth 2.0 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""
formatting the return of the client controllers
"""

from flask_restplus import fields

def get_client_serializer(full=False):
    schema = {
        "_id": fields.String(),
        "user_id": fields.List(fields.String()),
        "client_name": fields.String(),
        "client_uri": fields.String(),
        "redirect_uri": fields.String(),
        "created_at": fields.DateTime(),
        "expired_at": fields.DateTime(),
    }
    if full:
        schema['type_secret'] = fields.String()
        schema['client_secret'] = fields.String()
    return schema


def get_clients_serializer(full=False):
    return {
        'clients': fields.List(fields.Nested(get_client_serializer(full)))
    }


def get_paginate_serializer():
    return {
        'page': fields.Integer(description='Number of this page of results'),
        'pages': fields.Integer(description='Total number of pages of results'),
        'per_page': fields.Integer(description='Number of items per page of results'),
        'total': fields.Integer(description='Total number of results'),
        'items': fields.List(fields.Nested(get_client_serializer()))
    }
