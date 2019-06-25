import os
from flask import request
from flask_restplus import Resource, marshal

from bdc_oauth.clients import ns
from bdc_oauth.clients.business import ClientsBusiness
from bdc_oauth.clients.parsers import validate
from bdc_oauth.clients.serializers import get_client_serializer, get_clients_serializer
from bdc_oauth.clients.helpers import return_response
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
                "success": False,User
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
            if not useclientr:
                raise Exception('Error updating client!')

            return return_response({
                    "success": True,
                    "message": "Client updated!"
                }, 200)

        except Exception as e:
            return return_response({
                "success": False,
                "message": str(e)
            }, 500)
    

