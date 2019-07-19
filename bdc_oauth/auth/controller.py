import os
import json
from flask import request
from werkzeug.exceptions import InternalServerError, BadRequest
from bdc_core.utils.flask import APIResource

from bdc_oauth.auth import ns
from bdc_oauth.auth.business import AuthBusiness
from bdc_oauth.auth.decorators import jwt_required
from bdc_oauth.auth.parsers import validate

api = ns

@api.route('/token')
class AuthController(APIResource):

    def post(self):
        """
        Logging in to the system
        """
        data, status = validate(request.json, 'login')
        if status is False:
            raise BadRequest(json.dumps(data))

        auth = AuthBusiness.login(data['username'], data['password'])
        if not auth:
            raise InternalServerError('Error logging!')

        return auth

@api.route('/<action>/<client_id>')
class AuthorizationController(APIResource):

    @jwt_required
    def post(self, action, client_id):
        user_id = request.id

        """
        authorize or revoke authorization from a customer
        """
        if action.lower() not in ['authorize', 'revoke']:
            raise BadRequest('Action not found. Set "authorize or revoke"!')

        status = AuthBusiness.authorize_revoke_client(action, user_id, client_id)
        if not status:
            raise InternalServerError('Error while {}'.format(action))

        return {
            "message": "Updated User!"
        }