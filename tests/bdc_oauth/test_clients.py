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

    app_1_info = dict(
        client_name='test',
        client_uri='http://localhost:8080/test',
        redirect_uri='http://localhost:8080/test/test',
        type_secret='string',
        client_secret='abc',
        user_id=[user_admin_info['_id']],
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
        user_id=[user_info['_id']],
        created_at=datetime.now(),
        expired_at=None,
        _id=ObjectId('5e59557579da4ec3ff04a683')
    )
    mongo.db.clients.insert_many([app_1_info, app_2_info])
    return user_admin_info, user_info


def login(test_client, username='admin'):
    response = test_client.post('/oauth/auth/login', json=dict(
        username=username,
        password='abcd1234'
    ))
    return response, json.loads(response.data)['access_token']


###################
## LIST CLIENT/CLIENTS
def test_get_apps(test_client):
    _, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.get('/oauth/clients/', headers=dict(
        Authorization='Bearer {}'.format(access_token)
    ))
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert len(r_json['clients']) == 2
    assert 'client_secret' not in r_json['clients']

def test_get_apps_403_without_token(test_client):
    _, _ = setUp()

    response = test_client.get('/oauth/clients/')
    assert response.status_code == 403

def test_get_apps_401_invalid_token(test_client):
    _, _ = setUp()

    response = test_client.get('/oauth/users/', headers=dict(
        Authorization='Bearer asdf'
    ))
    assert response.status_code == 401

def test_get_app(test_client):
    u_admin_info, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.get(
        '/oauth/clients/{}'.format('5e59557579da4ec3ff04a682'),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert 'client_secret' in r_json

def test_get_app_only_author(test_client):
    u_admin_info, _ = setUp()

    _, access_token = login(test_client, username='default')
    response = test_client.get(
        '/oauth/clients/{}'.format('5e59557579da4ec3ff04a683'),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert 'client_secret' in r_json

def test_get_app_403_without_token(test_client):
    u_admin_info, _ = setUp()

    response = test_client.get('/oauth/clients/{}'.format('5e59557579da4ec3ff04a682'))
    assert response.status_code == 403

def test_get_app_403_no_author(test_client):
    _, u_info = setUp()

    _, access_token = login(test_client)
    response = test_client.get(
        '/oauth/clients/{}'.format('5e59557579da4ec3ff04a683'),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 403

def test_get_user_not_found(test_client):
    _, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.get(
        '/oauth/clients/123',
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 404

###################
## LIST CLIENTS BY AUTHOR
def test_get_apps_by_author(test_client):
    u_admin_info, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.get(
        '/oauth/clients/users/{}'.format(str(u_admin_info['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token))
    )
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert len(r_json['clients']) == 1
    assert str(r_json['clients'][0]['_id']) == '5e59557579da4ec3ff04a682'
    assert 'client_secret' in r_json['clients'][0]

def test_get_apps_by_author_403(test_client):
    u_admin_info, _ = setUp()

    response = test_client.get(
        '/oauth/clients/users/{}'.format(str(u_admin_info['_id'])))
    assert response.status_code == 403

###################
## CREATE CLIENT
def test_create_app(test_client):
    _, _ = setUp()

    _, access_token = login(test_client)
    new_client = dict(
        client_name='app-test',
        client_uri='http://localhost:8080/app-test',
        redirect_uri='http://localhost:8080/app-test/redirect',
        type_secret='string',
        client_secret='abc-key'
    )
    response = test_client.post(
        '/oauth/clients/',
        json=new_client,
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    r_json = json.loads(response.data)
    assert response.status_code == 201
    assert '_id' in r_json

def test_create_app_400(test_client):
    _, _ = setUp()

    _, access_token = login(test_client)
    new_client = dict(
        client_name='app-test',
        client_uri='http://localhost:8080/app-test',
        redirect_uri='http://localhost:8080/app-test/redirect',
    )
    response = test_client.post(
        '/oauth/clients/',
        json=new_client,
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 400

def test_create_app_400_without_name(test_client):
    _, _ = setUp()

    _, access_token = login(test_client)
    new_client = dict(
        client_uri='http://localhost:8080/app-test',
        redirect_uri='http://localhost:8080/app-test/redirect',
        type_secret='string',
        client_secret='abc-key'
    )
    response = test_client.post(
        '/oauth/clients/',
        json=new_client,
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 400

def test_create_app_400_incorrect_type(test_client):
    _, _ = setUp()

    _, access_token = login(test_client)
    new_client = dict(
        client_name='app-test1',
        client_uri='http://localhost:8080/app-test1',
        redirect_uri='http://localhost:8080/app-test1/redirect',
        type_secret='abc',
        client_secret='abc-key'
    )
    response = test_client.post(
        '/oauth/clients/',
        json=new_client,
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 400

def test_create_app_409(test_client):
    _, _ = setUp()

    _, access_token = login(test_client)
    new_client = dict(
        client_name='test',
        client_uri='http://localhost:8080/test',
        redirect_uri='http://localhost:8080/test/test',
        type_secret='string',
        client_secret='abc'
    )
    response = test_client.post(
        '/oauth/clients/',
        json=new_client,
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 409

def test_create_app_admin_403(test_client):
    _, _ = setUp()

    new_client = dict(
        client_name='test-1',
        client_uri='http://localhost:8080/test-1',
        redirect_uri='http://localhost:8080/test-1/test-1',
        type_secret='string',
        client_secret='abc'
    )
    response = test_client.post(
        '/oauth/clients/',
        json=new_client)
    assert response.status_code == 403

def test_create_app_admin_403_no_admn(test_client):
    _, _ = setUp()

    _, access_token = login(test_client, username='default')
    new_client = dict(
        client_name='test-1',
        client_uri='http://localhost:8080/test-1',
        redirect_uri='http://localhost:8080/test-1/test-1',
        type_secret='string',
        client_secret='abc'
    )
    response = test_client.post(
        '/oauth/clients/',
        json=new_client,
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 403


###################
## UPDATE USER
def test_update_app(test_client):
    _, _ = setUp()

    _, access_token = login(test_client)
    client_updated = dict(
        client_name='app-test-2',
        client_uri='http://localhost:8080/app-test',
        redirect_uri='http://localhost:8080/app-test/redirect',
        type_secret='string',
        client_secret='abc-key'
    )
    response = test_client.put(
        '/oauth/clients/{}'.format('5e59557579da4ec3ff04a682'),
        json=client_updated,
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    r_json = json.loads(response.data)
    assert response.status_code == 200

    response = test_client.get(
        '/oauth/clients/{}'.format('5e59557579da4ec3ff04a682'),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert r_json['client_name'] == 'app-test-2'

def test_update_app_403_no_author(test_client):
    _, _ = setUp()

    _, access_token = login(test_client)
    client_updated = dict(
        client_name='app-test-2',
        client_uri='http://localhost:8080/app-test',
        redirect_uri='http://localhost:8080/app-test/redirect',
        type_secret='string',
        client_secret='abc-key'
    )
    response = test_client.put(
        '/oauth/clients/{}'.format('5e59557579da4ec3ff04a683'),
        json=client_updated,
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 403

def test_update_app_400(test_client):
    _, _ = setUp()

    _, access_token = login(test_client)
    client_updated = dict(
        client_uri='http://localhost:8080/app-test',
        redirect_uri='http://localhost:8080/app-test/redirect',
        type_secret='string',
    )
    response = test_client.put(
        '/oauth/clients/{}'.format('5e59557579da4ec3ff04a682'),
        json=client_updated,
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 400

def test_update_app_403(test_client):
    _, _ = setUp()

    client_updated = dict(
        client_name='app-test-2',
        client_uri='http://localhost:8080/app-test',
        redirect_uri='http://localhost:8080/app-test/redirect',
        type_secret='string',
        client_secret='abc-key'
    )
    response = test_client.put(
        '/oauth/clients/{}'.format('5e59557579da4ec3ff04a682'),
        json=client_updated)
    assert response.status_code == 403

def test_update_app_admin_404(test_client):
    _, _ = setUp()

    _, access_token = login(test_client)
    client_updated = dict(
        client_name='app-test-2',
        client_uri='http://localhost:8080/app-test',
        redirect_uri='http://localhost:8080/app-test/redirect',
        type_secret='string',
        client_secret='abc-key'
    )
    response = test_client.put(
        '/oauth/clients/abc',
        json=client_updated,
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 404


###################
## DELETE USER
def test_delete_app(test_client):
    _, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.delete(
        '/oauth/clients/{}'.format('5e59557579da4ec3ff04a682'),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 200

    response = test_client.get(
        '/oauth/clients/{}'.format('5e59557579da4ec3ff04a682'),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 404

def test_delete_app_403_no_author(test_client):
    _, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.delete(
        '/oauth/clients/{}'.format('5e59557579da4ec3ff04a683'),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 403

def test_delete_app_403(test_client):
    _, _ = setUp()

    response = test_client.delete(
        '/oauth/clients/{}'.format('5e59557579da4ec3ff04a683'))
    assert response.status_code == 403

def test_delete_app_admin_404(test_client):
    _, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.put(
        '/oauth/clients/abc',
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 404


##################
## ADD AUTHOR
def test_add_author_app(test_client):
    _, u_infos = setUp()

    _, access_token = login(test_client)
    response = test_client.post(
        '/oauth/clients/{}/author/{}'.format(
            '5e59557579da4ec3ff04a682',
            str(u_infos['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 200

    _, access_token = login(test_client, username='default')
    response = test_client.get(
        '/oauth/clients/users/{}'.format(str(u_infos['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token))
    )
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert len(r_json['clients']) == 2
    assert 'client_secret' in r_json['clients'][0]

def test_add_author_app_duplicate(test_client):
    u_admin_infos, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.post(
        '/oauth/clients/{}/author/{}'.format(
            '5e59557579da4ec3ff04a682',
            str(u_admin_infos['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 200

    _, access_token = login(test_client)
    response = test_client.get(
        '/oauth/clients/users/{}'.format(str(u_admin_infos['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token))
    )
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert len(r_json['clients']) == 1
    assert 'client_secret' in r_json['clients'][0]

def test_add_author_app_403(test_client):
    u_admin_infos, _ = setUp()

    response = test_client.post(
        '/oauth/clients/{}/author/{}'.format(
            '5e59557579da4ec3ff04a682',
            str(u_admin_infos['_id'])))
    assert response.status_code == 403

def test_add_author_app_403_no_author(test_client):
    u_admin_infos, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.post(
        '/oauth/clients/{}/author/{}'.format(
            '5e59557579da4ec3ff04a683',
            str(u_admin_infos['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 403

def test_add_author_app_404(test_client):
    u_admin_infos, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.post(
        '/oauth/clients/{}/author/{}'.format(
            'abc',
            str(u_admin_infos['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 404


##################
## DELETE AUTHOR
def test_delete_author_app(test_client):
    _, u_infos = setUp()

    _, access_token = login(test_client)
    response = test_client.post(
        '/oauth/clients/{}/author/{}'.format(
            '5e59557579da4ec3ff04a682',
            str(u_infos['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 200

    _, access_token = login(test_client, username='default')
    response = test_client.get(
        '/oauth/clients/users/{}'.format(str(u_infos['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token))
    )
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert len(r_json['clients']) == 2

    response = test_client.delete(
        '/oauth/clients/{}/author/{}'.format(
            '5e59557579da4ec3ff04a682',
            str(u_infos['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 200

    _, access_token = login(test_client, username='default')
    response = test_client.get(
        '/oauth/clients/users/{}'.format(str(u_infos['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token))
    )
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert len(r_json['clients']) == 1

def test_delete_author_app_only_author(test_client):
    u_admin_infos, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.delete(
        '/oauth/clients/{}/author/{}'.format(
            '5e59557579da4ec3ff04a682',
            str(u_admin_infos['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 200

    _, access_token = login(test_client)
    response = test_client.get(
        '/oauth/clients/users/{}'.format(str(u_admin_infos['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token))
    )
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert len(r_json['clients']) == 1

def test_delete_author_app_no_associated(test_client):
    _, u_infos = setUp()

    _, access_token = login(test_client)
    response = test_client.delete(
        '/oauth/clients/{}/author/{}'.format(
            '5e59557579da4ec3ff04a682',
            str(u_infos['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 200

    _, access_token = login(test_client, username='default')
    response = test_client.get(
        '/oauth/clients/users/{}'.format(str(u_infos['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token))
    )
    r_json = json.loads(response.data)
    assert response.status_code == 200
    assert len(r_json['clients']) == 1

def test_delete_author_app_403(test_client):
    u_admin_infos, _ = setUp()

    response = test_client.delete(
        '/oauth/clients/{}/author/{}'.format(
            '5e59557579da4ec3ff04a682',
            str(u_admin_infos['_id'])))
    assert response.status_code == 403

def test_delete_author_app_403_no_author(test_client):
    u_admin_infos, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.delete(
        '/oauth/clients/{}/author/{}'.format(
            '5e59557579da4ec3ff04a683',
            str(u_admin_infos['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 403

def test_delete_author_app_404(test_client):
    u_admin_infos, _ = setUp()

    _, access_token = login(test_client)
    response = test_client.delete(
        '/oauth/clients/{}/author/{}'.format(
            'abc',
            str(u_admin_infos['_id'])),
        headers=dict(Authorization='Bearer {}'.format(access_token)))
    assert response.status_code == 404
