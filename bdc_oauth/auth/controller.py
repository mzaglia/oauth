import os
import json
from flask import request
from werkzeug.exceptions import InternalServerError, BadRequest
from bdc_core.utils.flask import APIResource

from bdc_oauth.auth import ns
from bdc_oauth.auth.business import AuthBusiness
from bdc_oauth.auth.parsers import validate

api = ns

@api.route('/login')
class AuthController(APIResource):
    
    def post(self):
        """
        Endpoint responsável por realizar o login no sistema
        """
        data, status = validate(request.json, 'login')
        if status is False:
            raise BadRequest(json.dumps(data))

        auth = AuthBusiness.login(data['username'], data['password'])
        if not auth:
            raise inte('Error logging!')

        return auth

@api.route('/<action>/<client_id>')
class AuthorizationController(APIResource):
    
    def post(self, action, client_id):
        # TODO: get to token
        user_id = '5d1a1cc632a61a2718cd709a'

        """
        Endpoint responsável por autorizar um cliente
        """
        if action.lower() not in ['authorize', 'revoke']:
            raise BadRequest('Action not found. Set "authorize or revoke"!')

        status = AuthBusiness.authorize_revoke_client(action, user_id, client_id)
        if not status:
            raise InternalServerError('Error while {}'.format(action))

        return {
            "message": "Updated User!"
        }