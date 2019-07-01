import os
from flask import request
from flask_restplus import Resource, marshal

from bdc_oauth.clients import ns
from bdc_oauth.clients.business import ClientsBusiness
from bdc_oauth.clients.parsers import validate
from bdc_oauth.clients.serializers import get_client_serializer, get_clients_serializer
from bdc_oauth.utils.helpers import return_response
# from bdc_oauth.utils.decorators import jwt_required

api = ns

@api.route('/')
class ClientsController(Resource):

    # @jwt_required
    def get(self):
        try:
            """
            Endpoint responsável listar os clientes que não estão expirados
            """
            clients = ClientsBusiness.get_all()
            return marshal({"clients": clients}, get_clients_serializer()), 200

        except Exception as e:
            return return_response({
                "success": False,
                "message": str(e)
            }, 500)
    
    # @jwt_required
    def post(self):
        try:
            # TODO: get to token
            user_id = '5d12554d4d018840e6f65423'

            """
            Endpoint responsável criar um novo cliente
            """
            data, status = validate(request.json, 'client_create')
            if status is False:
                return return_response(data, 400)

            client = ClientsBusiness.create(user_id, data)
            if not client:
                raise Exception('Error creating client!')

            return marshal(client, get_client_serializer()), 200

        except Exception as e:
            return return_response({
                "success": False,
                "message": str(e)
            }, 500)


@api.route('/<id>')
class ClientController(Resource):

    # @jwt_required
    def get(self, id): 
        try:
            """
            Endpoint responsável listar infos de um cliente que não está expirado
            """
            client = ClientsBusiness.get_by_id(id)
            if not client:
                return return_response({
                    "success": False,
                    "message": "Client not Found!"
                }, 404)
            
            return marshal(client, get_client_serializer()), 200

        except Exception as e:
            return return_response({
                "success": False,
                "message": str(e)
            }, 500)

    # @jwt_required
    def put(self, id):
        try:
            """
            Endpoint responsável atualizar um cliente
            """
            data, status = validate(request.json, 'client_base')
            if status is False:
                return return_response(data, 400)

            client = ClientsBusiness.update(id, data)
            if not client:
                raise Exception('Error updating client!')

            return return_response({
                    "success": True,
                    "message": "Updated Client!"
                }, 200)

        except Exception as e:
            return return_response({
                "success": False,
                "message": str(e)
            }, 500)

    # @jwt_required
    def delete(self, id):
        try:
            """
            Endpoint responsável por deletar um cliente
            """
            status = ClientsBusiness.delete(id)
            if not status:
                return return_response({
                    "success": False,
                    "message": "Client not Found!"
                }, 404)
            
            return return_response({
                    "success": True,
                    "message": "Deleted client!"
                }, 200)

        except Exception as e:
            return return_response({
                "success": False,
                "message": str(e)
            }, 500)

@api.route('/<id>/status/<action>')
class ClientStatusController(Resource):

    def put(self, id, action):
        try:
            if action.lower() not in ['enable', 'disable']:
                raise Exception('Action not found. Set "enable or disable"!')

            data = {}
            if action == 'enable':
                data, status = validate(request.json, 'date_expiration')
                if status is False:
                    return return_response(data, 400)

            """
            Endpoint responsável por desativar ou ativar um Cliente
            """
            status = ClientsBusiness.update_date_expiration(id, action, data.get('expired_at', None))
            if not status:
                return return_response({
                    "success": False,
                    "message": "Client not Found!"
                }, 404)
            
            return return_response({
                    "success": True,
                    "message": "Updated client!"
                }, 200)

        except Exception as e:
            return return_response({
                "success": False,
                "message": str(e)
            }, 500)

@api.route('/<user_id>')
class AdminClientsController(Resource):

    # @jwt_required
    def get(self, user_id):
        try:
            """
            Endpoint responsável listar os clientes criado por um usuário e que não estão expirados
            """
            clients = ClientsBusiness.list_by_userid(user_id)
            return marshal({"clients": clients}, get_clients_serializer()), 200

        except Exception as e:
            return return_response({
                "success": False,
                "message": str(e)
            }, 500)

@api.route('/<id>/new-secret')
class ClientCredentialsController(Resource):

    # @jwt_required
    def put(self, id):
        try:
            """
            Endpoint responsável por gerar uma nova secret para um client
            """
            secret = ClientsBusiness.generate_new_secret(id)
            if not secret:
                raise Exception('Error generate secret!')

            return return_response({
                    "success": True,
                    "new_secret": secret
                }, 200)

        except Exception as e:
            return return_response({
                "success": False,
                "message": str(e)
            }, 500)