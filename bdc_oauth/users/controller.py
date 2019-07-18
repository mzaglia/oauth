import os
import json
from flask import request
from flask_restplus import marshal
from werkzeug.exceptions import InternalServerError, BadRequest, NotFound
from bdc_core.utils.flask import APIResource

from bdc_oauth.users import ns
from bdc_oauth.users.business import UsersBusiness
from bdc_oauth.users.parsers import validate
from bdc_oauth.users.serializers import get_user_serializer, get_users_serializer
from bdc_oauth.clients.serializers import get_clients_serializer
# from bdc_oauth.utils.decorators import jwt_required

api = ns

@api.route('/')
class UsersController(APIResource):

    # @jwt_required
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

        user = UsersBusiness.create(data)
        if not user:
            raise InternalServerError('Error creating user!')

        return marshal(user, get_user_serializer()), 200


@api.route('/<id>')
class UserController(APIResource):

    # @jwt_required
    def get(self, id): 
        """
        user informations by id
        """
        user = UsersBusiness.get_by_id(id)
        if not user:
            raise NotFound("User not Found!")
        
        return marshal(user, get_user_serializer())

    # @jwt_required
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

    # @jwt_required
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
        

@api.route('/change-password/<id>')
class UserPassController(APIResource):

    # @jwt_required
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


@api.route('/<id>/clients')
class UserClientsController(APIResource):

    # @jwt_required
    def get(self, id):
        """
        list all authorized clients of a particular user
        """
        clients = UsersBusiness.list_clients_authorized(id)
        clients = clients[0]['clients'] if len(clients) else []

        return marshal({"clients": clients}, get_clients_serializer())

