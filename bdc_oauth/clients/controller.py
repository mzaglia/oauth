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
from werkzeug.exceptions import InternalServerError, BadRequest, NotFound
from bdc_core.utils.flask import APIResource

from bdc_oauth.auth.decorators import jwt_required, jwt_admin_required, \
    jwt_author_required, jwt_admin_author_required, jwt_me_required
from bdc_oauth.clients import ns
from bdc_oauth.clients.business import ClientsBusiness
from bdc_oauth.clients.validators import validate
from bdc_oauth.clients.serializers import get_client_serializer, \
    get_clients_serializer

api = ns


@api.route('/')
class ClientsController(APIResource):

    @jwt_required
    def get(self):
        """
        list clients that are not expired
        """
        clients = ClientsBusiness.get_all()
        return marshal({"clients": clients}, get_clients_serializer())

    @jwt_admin_required
    def post(self):
        user_id = request.id

        """
        create new client
        """
        data, status = validate(request.json, 'client_create')
        if status is False:
            raise BadRequest(json.dumps(data))

        client = ClientsBusiness.create(user_id, data)
        if not client:
            raise InternalServerError('Error creating client!')

        return marshal(client, get_client_serializer()), 201


@api.route('/<client_id>')
class ClientController(APIResource):

    @jwt_author_required
    def get(self, client_id):
        """
        list information from an active app/client
        """
        client = ClientsBusiness.get_by_id(client_id)
        if not client:
            raise NotFound("Client not Found!")

        return marshal(client, get_client_serializer(True)), 200

    @jwt_author_required
    def put(self, client_id):
        """
        update client
        """
        data, status = validate(request.json, 'client_base')
        if status is False:
            raise BadRequest(json.dumps(data))

        client = ClientsBusiness.update(client_id, data)
        if not client:
            raise InternalServerError('Error updating client!')

        return {
            "message": "Updated Client!"
        }

    @jwt_author_required
    def delete(self, client_id):
        """
        delete client
        """
        status = ClientsBusiness.delete(client_id)
        if not status:
            raise NotFound("Client not Found!")

        return {
            "message": "Deleted client!"
        }


@api.route('/<id>/status/<action>')
class ClientStatusController(APIResource):

    @jwt_admin_author_required
    def put(self, id, action):
        """
        enable or disable a client
        """

        if action.lower() not in ['enable', 'disable']:
            raise BadRequest('Action not found. Set "enable or disable"!')

        data = {}
        if action == 'enable':
            data, status = validate(request.json, 'date_expiration')
            if status is False:
                raise BadRequest(json.dumps(data))

        status = ClientsBusiness.update_date_expiration(
            id, action, data.get('expired_at', None))
        if not status:
            raise NotFound("Client not Found!")

        return {
            "message": "Updated client!"
        }


@api.route('/users/<id>')
class AdminClientsController(APIResource):

    @jwt_me_required
    def get(self, id):
        """
        list clients by a user (if the user is an admin of the app)
        """
        clients = ClientsBusiness.list_by_userid(id)
        return marshal({"clients": clients}, get_clients_serializer(True))


@api.route('/<client_id>/author/<user_id>')
class AdminAuthorsClientsController(APIResource):

    @jwt_author_required
    def post(self, client_id, user_id):
        """
        add new author in client/application
        """
        _ = ClientsBusiness.add_author(client_id, user_id)
        return {
            "message": "Updated client!"
        }

    @jwt_author_required
    def delete(self, client_id, user_id):
        """
        remove author in client/application
        """
        _ = ClientsBusiness.delete_author(client_id, user_id)
        return {
            "message": "Updated client!"
        }

