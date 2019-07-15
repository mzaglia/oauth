import jwt
from copy import deepcopy
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest, NotFound

from bdc_oauth.config import Config
from bdc_oauth.users.business import UsersBusiness
from bdc_oauth.utils.base_mongo import mongo

class AuthBusiness():

    @classmethod
    def decode_auth_token(cls, token):
        try:
            payload = jwt.decode(token, Config.SECRET_KEY)
            return payload['sub'], True
        except jwt.ExpiredSignatureError:
            return 'This token has expired. Please login', False
        except jwt.InvalidTokenError:
            return 'Invalid token. Please login', False

    @staticmethod
    def encode_auth_token(user_id, grants, user_type):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1, seconds=5),
            'iat': datetime.utcnow(),
            'sub': {
                'id': user_id,
                'grants': grants
            },
            'type': user_type
        }
        return jwt.encode(
            payload,
            Config.SECRET_KEY,
            algorithm='HS512'
        )

    @classmethod
    def login(cls, username, password):
        model = UsersBusiness.init_infos()['model']

        user = model.find_one({"credential.username": username, "deleted_at": None})
        if not user:
            raise NotFound('User not found!')
        
        if check_password_hash(user['credential']['password'], password) is False:
            raise BadRequest('Incorrect password!')
        
        user_id = str(user['_id'])
        token = cls.encode_auth_token(user_id, user['credential']['grants'], 'user')
        result = {
            "user_id": user_id,
            "access_token": token.decode('utf8').replace("'", '"')
        }
        return result

    @classmethod
    def authorize_revoke_client(cls, action, user_id, client_id):
        model = UsersBusiness.init_infos()['model']

        user = UsersBusiness.get_by_id(user_id)
        if not user:
            raise NotFound('User not Found!')

        new_list = []
        if action == 'authorize':
            ''' Authorize client '''
            if client_id in user['clients_authorized']:
                return True
            user['clients_authorized'].append(client_id)
            new_list = user['clients_authorized']

        else:
            ''' Revoke client '''
            if client_id not in user['clients_authorized']:
                return True
            new_list = filter(lambda x: x != client_id, user['clients_authorized'])

        try:
            model.update_one({"_id": ObjectId(user_id)}, {"$set": {"clients_authorized": list(new_list)}})
            return True
        except Exception:
            return False