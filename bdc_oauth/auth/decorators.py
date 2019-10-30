import os
from flask import request
from functools import wraps
from werkzeug.exceptions import Forbidden, HTTPException, NotFound, Unauthorized

from bdc_oauth.auth.business import AuthBusiness
from bdc_oauth.clients.business import ClientsBusiness
from bdc_oauth.users.business import UsersBusiness


def get_userinfo_by_token(client_id=False):
    try:
        bearer, authorization = request.headers['Authorization'].split()
        if 'bearer' not in bearer.lower():
            raise Forbidden('Invalid token!')
    except Exception:
        raise Forbidden('Token is required!')

    if authorization:
        result, status = AuthBusiness.decode_auth_token(authorization)
        if status:
            user = UsersBusiness.get_by_id(result["id"])
            if user:
                if client_id:
                    client = ClientsBusiness.get_by_id(client_id)
                    if not client:
                        raise NotFound('Client not Found!')
                    return str(user['_id']), user['credential']['grants'], client
                return str(user['_id']), user['credential']['grants'], False

            raise NotFound('User not found')
        raise Unauthorized(str(result))
    raise Forbidden('Token is required!')


def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        _, _, _ = get_userinfo_by_token()
        return func(*args, **kwargs)
    return wrapper


def jwt_admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        id, grants, _ = get_userinfo_by_token()
        if not 'admin' in grants:
            raise Forbidden('You need to be an administrator!')
        request.id = id
        request.grants = grants
        return func(*args, **kwargs)
    return wrapper


def jwt_me_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        id, _, _ = get_userinfo_by_token()
        if id != kwargs['id']:
            raise Forbidden('The token does not reference the informed user!')
        return func(*args, **kwargs)
    return wrapper


def jwt_admin_me_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        id, grants, _ = get_userinfo_by_token()
        if not 'admin' in grants and id != kwargs['id']:
            raise Forbidden('You do not have permission!')
        return func(*args, **kwargs)
    return wrapper


def jwt_author_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        id, _, client = get_userinfo_by_token(client_id=kwargs['client_id'])
        if id not in str(client['user_id']):
            raise Forbidden('You do not have permission!')
        return func(*args, **kwargs)
    return wrapper


def jwt_admin_author_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        id, grants, client = get_userinfo_by_token()
        if not 'admin' in grants and id not in str(client['user_id']):
            raise Forbidden('You do not have permission!')
        return func(*args, **kwargs)
    return wrapper
