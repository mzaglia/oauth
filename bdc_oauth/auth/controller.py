import os
from flask import request
from flask_restplus import Resource

from bdc_oauth.auth import ns
from bdc_oauth.auth.business import AuthBusiness
from bdc_oauth.auth.parsers import validate
from bdc_oauth.utils.helpers import return_response

api = ns

@api.route('/login')
class AuthController(Resource):
    
    def post(self):
        try:
            """
            Endpoint responsável por realizar o login no sistema
            """
            data, status = validate(request.json, 'login')
            if status is False:
                return return_response(data, 400)

            auth = AuthBusiness.login(data['username'], data['password'])
            if not auth:
                raise Exception('Error logging!')

            return return_response(auth, 200)

        except Exception as e:
            return return_response({
                "success": False,
                "message": str(e)
            }, 500)

@api.route('/<action>/<client_id>')
class AuthorizationController(Resource):
    
    def post(self, action, client_id):
        try:
            # TODO: get to token
            user_id = '5d1a1cc632a61a2718cd709a'

            """
            Endpoint responsável por autorizar um cliente
            """
            if action.lower() not in ['authorize', 'revoke']:
                raise Exception('Action not found. Set "authorize or revoke"!')

            status = AuthBusiness.authorize_revoke_client(action, user_id, client_id)
            if not status:
                raise Exception('Error while {}'.format(action))

            return return_response({
                "success": True,
                "message": "Updated User!"
            }, 200)

        except Exception as e:
            return return_response({
                "success": False,
                "message": str(e)
            }, 500)