#
# This file is part of OBT OAuth 2.0.
# Copyright (C) 2019-2020 INPE.
#
# OBT OAuth 2.0 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import json
from datetime import datetime
from bson.objectid import ObjectId
from fixture import test_client
from bdc_oauth.users.business import UsersBusiness
from bdc_oauth.utils.base_mongo import mongo

USER_BASE = dict(
    name='Admin',
    institution='INPE',
    occupation='-',
    admin=False,
    password='abcd1234',
    confirm_password='abcd1234'
)

def cleanUp():
    try:
        mongo.db.users.delete_many({})
        mongo.db.clients.delete_many({})
    except Exception:
        return True

def setUp():
    cleanUp()

    user_admin = dict(
        **USER_BASE,
        email='admin@admin.com'
    )
    user_admin_info = UsersBusiness.create(user_admin, admin=True)
    user = dict(
        **USER_BASE,
        email='default@admin.com'
    )
    user_info = UsersBusiness.create(user, admin=False)
    return user_admin_info, user_info


def login(test_client, username='admin', password='abcd1234'):
    response = test_client.post('/oauth/auth/login', json=dict(
        username=username,
        password=password
    ))
    return response, json.loads(response.data)['access_token'] \
        if response.status_code == 200 else None

###################
## LOGIN
def test_login(test_client):
    _, _ = setUp()
    response, _ = login(test_client)
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert 'access_token' in r_json
    assert 'user_id' in r_json

def test_login_404(test_client):
    _, _ = setUp()
    response, _ = login(test_client, username='user_a')
    assert response.status_code == 404

def test_login_400(test_client):
    _, _ = setUp()
    response, _ = login(test_client, password='aaa')
    assert response.status_code == 400


#########################
## TOKEN
def create_app(user_id):
    app_1_info = dict(
        client_name='registry',
        client_uri='http://localhost:8080/registry',
        redirect_uri='http://localhost:8080/registry/test',
        type_secret='string',
        client_secret='abc',
        user_id=[user_id],
        created_at=datetime.now(),
        expired_at=None,
        _id=ObjectId('5e59557579da4ec3ff04a683')
    )
    mongo.db.clients.insert_many([app_1_info])

def test_generate_token(test_client):
    user_admin_info, _ = setUp()

    create_app(user_admin_info['_id'])
    _, access_token = login(test_client)
    _ = test_client.post(
        '/oauth/auth/authorize/{}/{}'.format(
            user_admin_info['_id'], ObjectId('5e59557579da4ec3ff04a683')),
        json=dict(scope=['registry:repository:*']),
        headers=dict(Authorization='Bearer {}'.format(access_token)))

    response = test_client.get(
        '/oauth/auth/token?service={}&scope={}'.format(
            'registry', 'registry:repository:*'),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert 'token' in r_json

def test_generate_token_insensitive(test_client):
    user_admin_info, _ = setUp()

    create_app(user_admin_info['_id'])
    _, access_token = login(test_client)
    _ = test_client.post(
        '/oauth/auth/authorize/{}/{}'.format(
            user_admin_info['_id'], ObjectId('5e59557579da4ec3ff04a683')),
        json=dict(scope=['registry:repository:POST']),
        headers=dict(Authorization='Bearer {}'.format(access_token)))

    response = test_client.get(
        '/oauth/auth/token?service={}&scope={}'.format(
            'registry', 'REGISTRY:repository:post'),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert 'token' in r_json

def test_generate_token_403_without_auth(test_client):
    user_admin_info, _ = setUp()

    create_app(user_admin_info['_id'])
    _, access_token = login(test_client)
    _ = test_client.post(
        '/oauth/auth/authorize/{}/{}'.format(
            user_admin_info['_id'], ObjectId('5e59557579da4ec3ff04a683')),
        json=dict(scope=['registry:repository:*']),
        headers=dict(Authorization='Bearer {}'.format(access_token)))

    response = test_client.get(
        '/oauth/auth/token?service={}&scope={}'.format(
            'registry', 'registry:repository:*'))
    assert response.status_code == 403

def test_generate_token_403_scope(test_client):
    user_admin_info, _ = setUp()

    create_app(user_admin_info['_id'])
    _, access_token = login(test_client)
    _ = test_client.post(
        '/oauth/auth/authorize/{}/{}'.format(
            user_admin_info['_id'], ObjectId('5e59557579da4ec3ff04a683')),
        json=dict(scope=['registry:repository:*']),
        headers=dict(Authorization='Bearer {}'.format(access_token)))

    response = test_client.get(
        '/oauth/auth/token?service={}&scope={}'.format(
            'registry', 'registry:catalog:*'),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 403

def test_generate_token_403_appname(test_client):
    user_admin_info, _ = setUp()

    create_app(user_admin_info['_id'])
    _, access_token = login(test_client)
    _ = test_client.post(
        '/oauth/auth/authorize/{}/{}'.format(
            user_admin_info['_id'], ObjectId('5e59557579da4ec3ff04a683')),
        json=dict(scope=['registry:repository:*']),
        headers=dict(Authorization='Bearer {}'.format(access_token)))

    response = test_client.get(
        '/oauth/auth/token?service={}&scope={}'.format(
            'registry1', 'registry:catalog:*'),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 403


#########################
## AUTHORIZE/REVOKE SCOPE
def test_authorize_scope(test_client):
    user_admin_info, _ = setUp()

    create_app(user_admin_info['_id'])
    _, access_token = login(test_client)
    response = test_client.post(
        '/oauth/auth/authorize/{}/{}'.format(
            user_admin_info['_id'], ObjectId('5e59557579da4ec3ff04a683')),
        json=dict(scope=['app:action:POST']),
        headers=dict(Authorization='Bearer {}'.format(access_token)))

    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert 'message' in r_json

    response_client = test_client.get(
        '/oauth/users/{}'.format(user_admin_info['_id']),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    r_c_json = json.loads(response_client.data)
    authorization = r_c_json['clients_authorized'][0]
    assert authorization['id'] == str(ObjectId('5e59557579da4ec3ff04a683'))
    assert authorization['scope'] == "['app:action:POST']"

def test_revoke_scope(test_client):
    user_admin_info, _ = setUp()

    create_app(user_admin_info['_id'])
    _, access_token = login(test_client)
    response = test_client.post(
        '/oauth/auth/authorize/{}/{}'.format(
            user_admin_info['_id'], ObjectId('5e59557579da4ec3ff04a683')),
        json=dict(scope=['app:action:POST', 'app:action:GET']),
        headers=dict(Authorization='Bearer {}'.format(access_token)))

    response = test_client.post(
        '/oauth/auth/revoke/{}/{}'.format(
            user_admin_info['_id'], ObjectId('5e59557579da4ec3ff04a683')),
        json=dict(scope=['app:action:GET']),
        headers=dict(Authorization='Bearer {}'.format(access_token)))

    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert 'message' in r_json

    response_client = test_client.get(
        '/oauth/users/{}'.format(user_admin_info['_id']),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    r_c_json = json.loads(response_client.data)
    authorization = r_c_json['clients_authorized'][0]
    assert authorization['id'] == str(ObjectId('5e59557579da4ec3ff04a683'))
    assert authorization['scope'] == "['app:action:POST']"

def test_scope_400(test_client):
    user_admin_info, _ = setUp()

    create_app(user_admin_info['_id'])
    _, access_token = login(test_client)
    response = test_client.post(
        '/oauth/auth/authorize/{}/{}'.format(
            user_admin_info['_id'], ObjectId('5e59557579da4ec3ff04a683')),
        json=dict(scopes=[]),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 400

def test_scope_403(test_client):
    _, u_info = setUp()

    create_app(u_info['_id'])
    _, access_token = login(test_client)
    response = test_client.post(
        '/oauth/auth/authorize/{}/{}'.format(
            u_info['_id'], ObjectId('5e59557579da4ec3ff04a683')),
        json=dict(scopes=['app:action:POST']),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 403

def test_scope_404(test_client):
    _, u_info = setUp()

    create_app(u_info['_id'])
    _, access_token = login(test_client)
    response = test_client.post(
        '/oauth/auth/authorize/abc/{}'.format(u_info['_id']),
        json=dict(scopes=['app:action:POST']),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 404
