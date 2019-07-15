import os
import json
from flask import request
from flask_restplus import marshal
from werkzeug.exceptions import InternalServerError, BadRequest, NotFound
from bdc_core.utils.flask import APIResource

from bdc_oauth.clients import ns
from bdc_oauth.clients.business import ClientsBusiness
from bdc_oauth.clients.parsers import validate
from bdc_oauth.clients.serializers import get_client_serializer, get_clients_serializer
# from bdc_oauth.utils.decorators import jwt_required

api = ns

@api.route('/')
class ClientsController(APIResource):

    # @jwt_required
    def get(self):
        """
        Endpoint responsável listar os clientes que não estão expirados
        """
        clients = ClientsBusiness.get_all()
        return marshal({"clients": clients}, get_clients_serializer())
    
    # @jwt_required
    def post(self):
        # TODO: get to token
        user_id = '5d1a1cc632a61a2718cd709a'

        """
        Endpoint responsável criar um novo cliente
        """
        data, status = validate(request.json, 'client_create')
        if status is False:
            raise BadRequest(json.dumps(data))

        client = ClientsBusiness.create(user_id, data)
        if not client:
            raise InternalServerError('Error creating client!')

        return marshal(client, get_client_serializer())



@api.route('/<id>')
class ClientController(APIResource):

    # @jwt_required
    def get(self, id): 
        """
        Endpoint responsável listar infos de um cliente que não está expirado
        """
        client = ClientsBusiness.get_by_id(id)
        if not client:
            raise NotFound("Client not Found!")
        
        return marshal(client, get_client_serializer()), 200

    # @jwt_required
    def put(self, id):
        """
        Endpoint responsável atualizar um cliente
        """
        data, status = validate(request.json, 'client_base')
        if status is False:
            raise BadRequest(json.dumps(data))

        client = ClientsBusiness.update(id, data)
        if not client:
            raise InternalServerError('Error updating client!')

        return {
            "message": "Updated Client!"
        }

    # @jwt_required
    def delete(self, id):
        """
        Endpoint responsável por deletar um cliente
        """
        status = ClientsBusiness.delete(id)
        if not status:
            raise NotFound("Client not Found!")
        
        return {
            "message": "Deleted client!"
        }


@api.route('/<id>/status/<action>')
class ClientStatusController(APIResource):

    def put(self, id, action):
        if action.lower() not in ['enable', 'disable']:
            raise BadRequest('Action not found. Set "enable or disable"!')

        data = {}
        if action == 'enable':
            data, status = validate(request.json, 'date_expiration')
            if status is False:
                raise BadRequest(json.dumps(data))

        """
        Endpoint responsável por desativar ou ativar um Cliente
        """
        status = ClientsBusiness.update_date_expiration(id, action, data.get('expired_at', None))
        if not status:
            raise NotFound("Client not Found!")
        
        return {
            "message": "Updated client!"
        }


@api.route('/<user_id>')
class AdminClientsController(APIResource):

    # @jwt_required
    def get(self, user_id):
        """
        Endpoint responsável listar os clientes criado por um usuário e que não estão expirados
        """
        clients = ClientsBusiness.list_by_userid(user_id)
        return marshal({"clients": clients}, get_clients_serializer())


@api.route('/<id>/new-secret')
class ClientCredentialsController(APIResource):

    # @jwt_required
    def put(self, id):
        """
        Endpoint responsável por gerar uma nova secret para um client
        """
        secret = ClientsBusiness.generate_new_secret(id)
        if not secret:
            raise InternalServerError('Error generate secret!')

        return {
            "new_secret": secret
        }