"""
formatting the return of the client controllers
"""

from flask_restplus import fields

def get_client_serializer():
    schema = {
        "_id": fields.String(),
        "user_id": fields.String(),
        "client_name": fields.String(),
        "client_secret": fields.String(),
        "client_uri": fields.String(),
        "redirect_uri": fields.String(),
        "scope": fields.List(fields.String()),
        "created_at": fields.DateTime(),
        "expired_at": fields.DateTime(),
    }
    return schema


def get_clients_serializer():
    return {
        'clients': fields.List(fields.Nested(get_client_serializer()))
    }


def get_paginate_serializer():
    return {
        'page': fields.Integer(description='Number of this page of results'),
        'pages': fields.Integer(description='Total number of pages of results'),
        'per_page': fields.Integer(description='Number of items per page of results'),
        'total': fields.Integer(description='Total number of results'),
        'items': fields.List(fields.Nested(get_client_serializer()))
    }
