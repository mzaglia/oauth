import os
import json
from flask import request
from werkzeug.exceptions import InternalServerError, BadRequest
from bdc_core.utils.flask import APIResource

from bdc_oauth.auth import ns
from bdc_oauth.auth.business import AuthBusiness
from bdc_oauth.auth.decorators import get_userinfo_by_token, jwt_admin_required, jwt_author_required
from bdc_oauth.auth.parsers import validate

api = ns

@api.route('/login')
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

@api.route('/token')
class AuthClientController(APIResource):

    def get(self):
        """
        Generate token to client application
        """
        service = request.args['service']
        scope = request.args.get('scope')

        if request.authorization:
            username = request.authorization.get('username')
            password = request.authorization.get('password')
            user_id = AuthBusiness.login(username, password)['user_id']
        else:
            user_id, _, _ = get_userinfo_by_token()

        auth_client = AuthBusiness.token(user_id, service, scope)
        return auth_client


@api.route('/<action>/<user_id>/<client_id>')
class AuthorizationController(APIResource):

    @jwt_author_required
    def post(self, action, user_id, client_id):
        """
        authorize or revoke authorization from a customer
        """
        if action.lower() not in ['authorize', 'revoke']:
            raise BadRequest('Action not found. Set "authorize or revoke"!')
        if not request.json or len(request.json.get('scope', [])) <= 0:
            raise BadRequest('Scope is missing!')

        status = AuthBusiness.authorize_revoke_client(action, user_id, client_id, request.json['scope'])
        if not status:
            raise InternalServerError('Error while {}'.format(action))

        return {
            "message": "Updated User!"
        }