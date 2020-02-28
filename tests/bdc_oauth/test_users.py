#
# This file is part of OBT OAuth 2.0.
# Copyright (C) 2019-2020 INPE.
#
# OBT OAuth 2.0 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import json
from fixture import test_client
from datetime import datetime
from bson.objectid import ObjectId
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


def login(test_client, username='admin'):
    response = test_client.post('/oauth/auth/login', json=dict(
        username=username,
        password='abcd1234'
    ))
    return response, json.loads(response.data)['access_token']


def test_login(test_client):
    _, _ = setUp()
    response, _ = login(test_client)
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert 'access_token' in r_json
    assert 'user_id' in r_json


###################
## LIST USER/USERS
def test_get_users(test_client):
    _, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.get('/oauth/users/', headers=dict(
        Authorization='Bearer {}'.format(access_token)
    ))
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert len(r_json['users']) == 2

def test_get_users_403_without_token(test_client):
    _, _ = setUp()

    response = test_client.get('/oauth/users/')
    assert response.status_code == 403

def test_get_users_403(test_client):
    _, _ = setUp()

    _, access_token = login(test_client, username='default')
    response = test_client.get('/oauth/users/', headers=dict(
        Authorization='Bearer {}'.format(access_token)
    ))
    assert response.status_code == 403

def test_get_user(test_client):
    u_admin_info, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.get(
        '/oauth/users/{}'.format(str(u_admin_info['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert r_json['_id'] == str(u_admin_info['_id'])

def test_get_user_my_token(test_client):
    _, u_info = setUp()

    _, access_token = login(test_client, username='default')
    response = test_client.get(
        '/oauth/users/{}'.format(str(u_info['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert r_json['_id'] == str(u_info['_id'])

def test_get_user_403_without_token(test_client):
    u_admin_info, _ = setUp()

    response = test_client.get('/oauth/users/{}'.format(str(u_admin_info['_id'])))
    assert response.status_code == 403

def test_get_user_403(test_client):
    u_admin_info, _ = setUp()

    _, access_token = login(test_client, username='default')
    response = test_client.get(
        '/oauth/users/{}'.format(str(u_admin_info['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 403

def test_get_user_not_found(test_client):
    _, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.get('/oauth/users/123',
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 404


###################
## CREATE USER
def test_create_user(test_client):
    _, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.post('/oauth/users/',
        json=dict(
            **USER_BASE,
            email='email@inpe.br'
        ),
        headers=dict(Authorization='Bearer {}'.format(access_token))
    )
    r_json = json.loads(response.data)
    assert response.status_code == 201
    assert '_id' in r_json

def test_create_user_400(test_client):
    _, _ = setUp()

    _, access_token = login(test_client)
    user = dict(
        **USER_BASE,
        email='email@inpe.br'
    )
    del user['name']
    response = test_client.post('/oauth/users/',
        json=user,
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 400

def test_create_user_409(test_client):
    _, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.post('/oauth/users/',
        json=dict(
            **USER_BASE,
            email='admin@admin.com'
        ),
        headers=dict(Authorization='Bearer {}'.format(access_token))
    )
    assert response.status_code == 409

def test_create_user_admin_403(test_client):
    _, _ = setUp()

    response = test_client.post('/oauth/users/?admin=True', json=dict(
        name='Admin',
        email='email@inpe.br',
        institution='INPE',
        occupation='-',
        admin=True,
        password='abcd1234',
        confirm_password='abcd1234'
    ))
    assert response.status_code == 403


###################
## UPDATE USER
def test_update_user_my_token(test_client):
    _, u_info = setUp()

    _, access_token = login(test_client, username='default')
    response = test_client.put(
        '/oauth/users/{}'.format(str(u_info['_id'])),
        json=dict(
            institution='INPE BR'
        ),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert 'message' in r_json

    response = test_client.get(
        '/oauth/users/{}'.format(str(u_info['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert r_json['institution'] == 'INPE BR'

def test_update_user_admin_token(test_client):
    _, u_info = setUp()

    _, access_token = login(test_client)
    response = test_client.put(
        '/oauth/users/{}'.format(str(u_info['_id'])),
        json=dict(
            institution='INPE BR1',
            occupation='-'
        ),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert 'message' in r_json

    response = test_client.get(
        '/oauth/users/{}'.format(str(u_info['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert r_json['institution'] == 'INPE BR1'

def test_update_user_403(test_client):
    u_admin_info, _ = setUp()

    _, access_token = login(test_client, username='default')
    response = test_client.put(
        '/oauth/users/{}'.format(str(u_admin_info['_id'])),
        json=dict(
            institution='INPE BR',
            occupation='-'
        ),
        headers=dict(Authorization='Bearer {}'.format(access_token))
    )
    assert response.status_code == 403

def test_update_user_admin_404(test_client):
    _, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.put(
        '/oauth/users/abc',
        json=dict(
            institution='INPE BR',
            occupation='-'
        ),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 404


###################
## DELETE USER
def test_delete_user_my_token(test_client):
    _, u_info = setUp()

    _, access_token = login(test_client, username='default')
    response = test_client.delete(
        '/oauth/users/{}'.format(str(u_info['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert 'message' in r_json

    response = test_client.get(
        '/oauth/users/{}'.format(str(u_info['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    r_json = json.loads(response.data)
    assert response.status_code == 404

def test_delete_user_403_admin_token(test_client):
    _, u_info = setUp()

    _, access_token = login(test_client)
    response = test_client.delete(
        '/oauth/users/{}'.format(str(u_info['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 403

def test_delete_user_403_without_token(test_client):
    u_admin_info, _ = setUp()

    response = test_client.delete(
        '/oauth/users/{}'.format(str(u_admin_info['_id']))
    )
    assert response.status_code == 403

def test_delete_user_not_found(test_client):
    _, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.delete(
        '/oauth/users/abc',
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 403


######################
## LIST AUTHORS BY APP
def create_cliente(test_client, user_id_1='', user_id_2=''):
    app_1_info = dict(
        client_name='test',
        client_uri='http://localhost:8080/test',
        redirect_uri='http://localhost:8080/test/test',
        type_secret='string',
        client_secret='abc',
        user_id=[user_id_1],
        created_at=datetime.now(),
        expired_at=None,
        _id=ObjectId('5e59557579da4ec3ff04a682')
    )
    app_2_info = dict(
        client_name='registry',
        client_uri='http://localhost:8080/registry',
        redirect_uri='http://localhost:8080/registry/test',
        type_secret='file',
        client_secret='/data/home/key',
        user_id=[user_id_2],
        created_at=datetime.now(),
        expired_at=None,
        _id=ObjectId('5e59557579da4ec3ff04a683')
    )
    mongo.db.clients.insert_many([app_1_info, app_2_info])
    mongo.db.users.update_one({"_id": user_id_1}, {"$set": dict(
        clients_authorized=[dict(
            id=ObjectId('5e59557579da4ec3ff04a682'),
            scope=[]
        )]
    )})
    mongo.db.users.update_one({"_id": user_id_2}, {"$set": dict(
        clients_authorized=[dict(
            id=ObjectId('5e59557579da4ec3ff04a683'),
            scope=[]
        )]
    )})

def test_list_authors_by_user_1(test_client):
    u_admin_info, u_info = setUp()

    create_cliente(test_client,
        user_id_1=u_admin_info['_id'],
        user_id_2=u_info['_id'])

    _, access_token = login(test_client)
    response = test_client.get('/oauth/users/client/5e59557579da4ec3ff04a682',
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert len(r_json['users']) == 1

def test_list_authors_by_user_2(test_client):
    u_admin_info, u_info = setUp()

    create_cliente(test_client,
        user_id_1=u_admin_info['_id'],
        user_id_2=u_info['_id'])

    _, access_token = login(test_client, username='default')
    response = test_client.get('/oauth/users/client/5e59557579da4ec3ff04a683',
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert len(r_json['users']) == 1

def test_list_authors_403(test_client):
    u_admin_info, u_info = setUp()

    create_cliente(
        test_client,
        user_id_1=u_admin_info['_id'],
        user_id_2=u_info['_id'])

    _, access_token = login(test_client)
    response = test_client.get('/oauth/users/client/5e59557579da4ec3ff04a683',
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 403

def test_delete_user_404(test_client):
    u_admin_info, u_info = setUp()

    create_cliente(
        test_client,
        user_id_1=u_admin_info['_id'],
        user_id_2=u_info['_id'])

    _, access_token = login(test_client)
    response = test_client.get('/oauth/users/client/abc',
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 404


##################
## CHANGE PASSWORD
def test_change_password(test_client):
    u_admin_info, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.put(
        '/oauth/users/change-password/{}'.format(str(u_admin_info['_id'])),
        json=dict(
            old_password='abcd1234',
            password='abcd12341',
            confirm_password='abcd12341'
        ),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 200

def test_change_password_403_current_pass(test_client):
    u_admin_info, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.put(
        '/oauth/users/change-password/{}'.format(str(u_admin_info['_id'])),
        json=dict(
            old_password='abcd123433',
            password='abcd12341',
            confirm_password='abcd12341'
        ),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 403

def test_change_password_400(test_client):
    u_admin_info, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.put(
        '/oauth/users/change-password/{}'.format(str(u_admin_info['_id'])),
        json=dict(
            old_password='abcd1234',
            confirm_password='abcd12341'
        ),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 400

def test_change_password_400_diff_pass(test_client):
    u_admin_info, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.put(
        '/oauth/users/change-password/{}'.format(str(u_admin_info['_id'])),
        json=dict(
            old_password='abcd1234',
            password='abcd12341aq',
            confirm_password='abcd12341'
        ),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 400

def test_change_password_403_admin_token(test_client):
    _, u_info = setUp()

    _, access_token = login(test_client)
    response = test_client.put(
        '/oauth/users/change-password/{}'.format(str(u_info['_id'])),
        json=dict(),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 403