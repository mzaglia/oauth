import jwt
import time
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest, NotFound, Forbidden

from bdc_oauth.config import Config
from bdc_oauth.users.business import UsersBusiness
from bdc_oauth.clients.business import ClientsBusiness
from bdc_oauth.utils.base_mongo import mongo
from bdc_oauth.utils.helpers import kid_from_crypto_key


class AuthBusiness():

    @classmethod
    def decode_auth_token(cls, token):
        try:
            payload = jwt.decode(token, Config.AUTH_SECRET_KEY)
            return payload['sub'], True
        except jwt.ExpiredSignatureError:
            return 'This token has expired. Please login', False
        except jwt.InvalidTokenError:
            return 'Invalid token. Please login', False

    @staticmethod
    def encode_auth_token(user_id, grants, user_type):
        payload = {
            'exp': int(time.time()) + int(Config.EXPIRES_IN_AUTH),
            'iat': int(time.time()),
            'sub': {
                'id': user_id,
                'grants': grants
            },
            'type': user_type
        }
        return jwt.encode(
            payload,
            Config.AUTH_SECRET_KEY,
            algorithm='HS512'
        )

    @staticmethod
    def encode_client_token(service, access_type, access_name, access_actions, user_infos, client_infos):
        claim = {
            'iss': 'oauth_server',
            'sub': '',
            'aud': service,
            'exp': int(time.time()) + int(Config.EXPIRES_IN_CLIENT),
            'nbf': int(time.time()) - 30,
            'iat': int(time.time()),
            'access': [
                {
                    'type': access_type,
                    'name': access_name,
                    'actions': access_actions
                }
            ]
        }

        if client_infos['type_secret'] == "file":
            header = {
                'typ': 'JWT',
                'alg': 'HS512'
            }
            return jwt.encode(claim, client_infos['client_secret'],
                            algorithm='HS512',
                            headers=header)

        if client_infos['type_secret'] == "file":
            header = {
                'typ': 'JWT',
                'alg': Config.ALGORITHM,
                'kid': kid_from_crypto_key(client_infos['client_secret'], 'RSA')
            }
            return jwt.encode(claim, open(client_infos['client_secret']).read(),
                              algorithm=Config.ALGORITHM,
                              headers=header)


    @classmethod
    def login(cls, username, password):
        model = UsersBusiness.init_infos()['model']

        user = model.find_one(
            {"credential.username": username, "deleted_at": None})
        if not user:
            raise NotFound('User not found!')

        if check_password_hash(user['credential']['password'], password) is False:
            raise BadRequest('Incorrect password!')

        user_id = str(user['_id'])
        token = cls.encode_auth_token(
            user_id, user['credential']['grants'], 'user')
        result = {
            "user_id": user_id,
            "access_token": token.decode('utf8').replace("'", '"')
        }
        return result

    @classmethod
    def token(cls, user_id, service, scope=''):
        client_infos = ClientsBusiness.get_by_name(service)
        user = UsersBusiness.get_by_id(user_id)

        client = list(
            filter(lambda c: c['id'] == client_infos['_id'], user['clients_authorized']))
        if len(client) <= 0:
            raise Forbidden('Not authorized!')

        authorized = False if scope else True
        typ = ''
        name = ''
        actions = []

        ''' filter and valid scope '''
        if scope:
            params = scope.split(':')
            if len(params) != 3:
                return BadRequest('Invalid scope!')

            typ = params[0]
            name = params[1]
            actions = params[2].split(',')

            for user_scope in client[0]['scope']:
                if not user_scope:
                    raise Forbidden('Not authorized!')
                typ_scope, name_scope, actions_scope = user_scope.split(':')

                if typ_scope == typ:
                    if name_scope == name or name_scope == '*':
                        has_actions = True
                        for action in actions:
                            if action not in actions_scope.split(',') and '*' not in actions_scope:
                                has_actions = False
                        if has_actions:
                            authorized = True
                            break
            if not authorized:
                raise Forbidden('Not authorized!')

        ''' generate client token '''
        token_client = cls.encode_client_token(
            service, typ, name, actions, user, client_infos)
        return {
            "token": token_client.decode('utf8'),
            "access_token": token_client.decode('utf8')
        }

    @classmethod
    def authorize_revoke_client(cls, action, user_id, client_id, scope=[]):
        model = UsersBusiness.init_infos()['model']

        user = UsersBusiness.get_by_id(user_id)
        if not user:
            raise NotFound('User not Found!')

        new_list = []
        if action == 'authorize':
            ''' Authorize client '''
            has_client = False
            for client in user['clients_authorized']:
                if str(client['id']) == str(client_id):
                    client['scope'] = client['scope'] + scope
                    has_client = True
                    break

            if not has_client:
                user['clients_authorized'].append({
                    "id": ObjectId(client_id),
                    "scope": scope
                })
            new_list = user['clients_authorized']

        else:
            ''' Revoke client '''
            new_list = filter(lambda x: str(
                x["id"]) != client_id, user['clients_authorized'])

        try:
            model.update_one({"_id": ObjectId(user_id)}, {
                             "$set": {"clients_authorized": list(new_list)}})
            return True
        except Exception:
            return False
