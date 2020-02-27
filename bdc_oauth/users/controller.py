#
# This file is part of OBT OAuth 2.0.
# Copyright (C) 2019-2020 INPE.
#
# OBT OAuth 2.0 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import json
from flask import request
from flask_restplus import marshal
from bdc_core.utils.flask import APIResource
from werkzeug.exceptions import (BadRequest, Forbidden, NotFound,
                                 InternalServerError)

from bdc_oauth.auth.decorators import (
    jwt_admin_required, jwt_admin_me_required, jwt_me_required,
    get_userinfo_by_token, jwt_author_required)
from bdc_oauth.users import ns
from bdc_oauth.users.business import UsersBusiness
from bdc_oauth.users.parsers import validate
from bdc_oauth.users.serializers import (get_user_serializer,
                                         get_users_serializer)

api = ns


@api.route('/')
class UsersController(APIResource):

    @jwt_admin_required
    def get(self):
        """
        user list
        """
        users = UsersBusiness.get_all()
        return marshal({"users": users}, get_users_serializer())

    def post(self):
        """
        create new user
        """
        data, status = validate(request.json, 'user_create', validate_password=True)
        if status is False:
            raise BadRequest(json.dumps(data))

        admin = data.get('admin', False)
        # Only admin users can create.
        if admin:
            _, grants, _ = get_userinfo_by_token()

            if 'admin' not in grants:
                raise Forbidden('You need to be an administrator!')

        user = UsersBusiness.create(data, admin=admin)

        if not user:
            raise InternalServerError('Error creating user!')

        return marshal(user, get_user_serializer()), 200


@api.route('/<id>')
class UserController(APIResource):

    @jwt_admin_me_required
    def get(self, id):
        """
        user informations by id
        """
        user = UsersBusiness.get_by_id(id)
        if not user:
            raise NotFound("User not Found!")

        return marshal(user, get_user_serializer())

    @jwt_admin_me_required
    def put(self, id):
        """
        update a user's information
        """
        data, status = validate(request.json, 'user_update')
        if status is False:
            raise BadRequest(json.dumps(data))

        user = UsersBusiness.update(id, data)
        if not user:
            raise InternalServerError('Error updating user!')

        return {
            "message": "User updated!"
        }

    @jwt_me_required
    def delete(self, id):
        """
        apply soft_delete in user (disable)
        """
        status = UsersBusiness.delete(id)
        if not status:
            NotFound("User not Found!")

        return {
            "message": "Deleted user!"
        }


@api.route('/client/<client_id>')
class UsersClientController(APIResource):

    @jwt_author_required
    def get(self, client_id):
        """
        list users authorized (with scope) by app/client
        """
        users = UsersBusiness.get_all_by_client(client_id)
        return marshal({"users": users}, get_users_serializer())


@api.route('/change-password/<id>')
class UserPassController(APIResource):

    @jwt_me_required
    def put(self, id):
        """
        change user password
        """
        data, status = validate(request.json, 'user_change_password', validate_password=True)
        if status is False:
            raise BadRequest(json.dumps(data))

        user = UsersBusiness.change_password(id, data['old_password'], data['password'])
        if not user:
            raise InternalServerError('Error updating user password!')

        return {
            "message": "Password updated!"
        }
