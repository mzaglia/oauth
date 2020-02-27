#
# This file is part of OBT OAuth 2.0.
# Copyright (C) 2019-2020 INPE.
#
# OBT OAuth 2.0 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""
formatting the return of the user controllers
"""

from flask_restplus import fields

def get_user_serializer(use_password=False):
    schema = {
        "_id": fields.String(),
        "name": fields.String(),
        "email": fields.String(),
        "institution": fields.String(),
        "occupation": fields.String(),
        "created_at": fields.DateTime(),
        "clients_authorized": fields.List(fields.Nested({
            "id": fields.String(),
            "scope": fields.String()
        }))
    }
    if use_password:
        schema["credential"] = fields.Nested({
            "username": fields.String(),
            "password": fields.String(),
            "grants": fields.List(fields.String())
        })
    else:
        schema["credential"] = fields.Nested({
            "username": fields.String(),
            "grants": fields.List(fields.String())
        })
    return schema


def get_users_serializer():
    return {
        'users': fields.List(fields.Nested(get_user_serializer()))
    }


def get_paginate_serializer():
    return {
        'page': fields.Integer(description='Number of this page of results'),
        'pages': fields.Integer(description='Total number of pages of results'),
        'per_page': fields.Integer(description='Number of items per page of results'),
        'total': fields.Integer(description='Total number of results'),
        'items': fields.List(fields.Nested(get_user_serializer()))
    }
