import os
from flask import request
from flask_restplus import Resource, marshal

from bdc_oauth.users import ns
from bdc_oauth.users.business import UsersBusiness
from bdc_oauth.users.parsers import validate
from bdc_oauth.users.serializers import get_user_serializer, get_users_serializer
from bdc_oauth.clients.serializers import get_clients_serializer
from bdc_oauth.utils.helpers import return_response
# from bdc_oauth.utils.decorators import jwt_required

api = ns

@api.route('/')
class UsersController(Resource):

    # @jwt_required
    def get(self):
        try:
            """
            Endpoint responsável listar os usuários
            """
            users = UsersBusiness.get_all()
            return marshal({"users": users}, get_users_serializer()), 200

        except Exception as e:
            return return_response({
                "success": False,
                "message": str(e)
            }, 500)
    
    def post(self):
        try:
            """
            Endpoint responsável criar um novo usuario
            """
            data, status = validate(request.json, 'user_create', validate_password=True)
            if status is False:
                return return_response(data, 400)

            user = UsersBusiness.create(data)
            if not user:
                raise Exception('Error creating user!')

            return marshal(user, get_user_serializer()), 200

        except Exception as e:
            return return_response({
                "success": False,
                "message": str(e)
            }, 500)


@api.route('/<id>')
class UserController(Resource):

    # @jwt_required
    def get(self, id): 
        try:
            """
            Endpoint responsável listar infos de um usuário
            """
            user = UsersBusiness.get_by_id(id)
            if not user:
                return return_response({
                    "success": False,
                    "message": "User not Found!"
                }, 404)
            
            return marshal(user, get_user_serializer()), 200

        except Exception as e:
            return return_response({
                "success": False,
                "message": str(e)
            }, 500)

    # @jwt_required
    def put(self, id):
        try:
            """
            Endpoint responsável atualizar um usuario
            """
            data, status = validate(request.json, 'user_update')
            if status is False:
                return return_response(data, 400)

            user = UsersBusiness.update(id, data)
            if not user:
                raise Exception('Error updating user!')

            return return_response({
                    "success": True,
                    "message": "User updated!"
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
            Endpoint responsável por aplicar o soft_delete em um usuário (inativação)
            """
            status = UsersBusiness.delete(id)
            if not status:
                return return_response({
                    "success": False,
                    "message": "User not Found!"
                }, 404)
            
            return return_response({
                    "success": True,
                    "message": "Deleted user!"
                }, 200)

        except Exception as e:
            return return_response({
                "success": False,
                "message": str(e)
            }, 500)
        

@api.route('/change-password/<id>')
class UserPassController(Resource):

    # @jwt_required
    def put(self, id):
        try:
            """
            Endpoint responsável por alterar a senha do usuário
            """
            data, status = validate(request.json, 'user_change_password', validate_password=True)
            if status is False:
                return return_response(data, 400)

            user = UsersBusiness.change_password(id, data['old_password'], data['password'])
            if not user:
                raise Exception('Error updating user password!')

            return return_response({
                    "success": True,
                    "message": "Password updated!"
                }, 200)

        except Exception as e:
            return return_response({
                "success": False,
                "message": str(e)
            }, 500)


@api.route('/<id>/clients')
class UserClientsController(Resource):

    # @jwt_required
    def get(self, id):
        try:
            """
            Endpoint responsável por listar todos os clientes autorizados de um determinado usuário
            """
            clients = UsersBusiness.list_clients_authorized(id)
            clients = clients[0]['clients'] if len(clients) else []

            return marshal({"clients": clients}, get_clients_serializer()), 200

        except Exception as e:
            return return_response({
                "success": False,
                "message": str(e)
            }, 500)

