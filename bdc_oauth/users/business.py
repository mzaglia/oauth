#
# This file is part of OBT OAuth 2.0.
# Copyright (C) 2019-2020 INPE.
#
# OBT OAuth 2.0 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from copy import deepcopy
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import (InternalServerError,
                                 NotFound, Conflict, Forbidden)

from bdc_oauth.config import Config
from bdc_oauth.utils.base_mongo import mongo
from bdc_oauth.utils.helpers import random_string, send_email

class UsersBusiness():

    @classmethod
    def init_infos(cls):
        return {
            "model": mongo.db.users,
            "model_recover": mongo.db.recover_pass 
        }

    @classmethod
    def get_all(cls):
        model = cls.init_infos()['model']

        users = model.find({"deleted_at": None}, {"credential.password": 0})
        return list(users)

    @classmethod
    def get_by_id(cls, id, return_password=0):
        model = cls.init_infos()['model']

        try:
            user = model.find_one({"_id": ObjectId(id), "deleted_at": None}, {"credential.password": return_password})
            return user
        except Exception:
            raise NotFound("User not Found!")

    @classmethod
    def get_all_by_client(cls, client_id):
        model = cls.init_infos()['model']
        
        users = model.find({"deleted_at": None, "clients_authorized.id": ObjectId(client_id)}, {"credential.password": 0})
        return list(users)

    @classmethod
    def create(cls, infos_user, admin=False):
        model = cls.init_infos()['model']

        """
        check if email is already registered
        """
        user_exits = model.find_one({"email": infos_user["email"], "deleted_at": None})
        if user_exits:
            raise Conflict('Email already registered in the system!')

        infos_user['created_at'] = datetime.now()
        infos_user['deleted_at'] = None

        """
        add user crendentials
        """
        credentials = {
            "username": deepcopy(infos_user['email'].split('@')[0].replace('.', '').replace('_', '')),
            "password": generate_password_hash(deepcopy(infos_user['password'])),
            "grants": ['user']
        }

        infos_user['credential'] = credentials
        infos_user['clients_authorized'] = []
        
        if admin:
            credentials['grants'].append('admin')
            del infos_user['admin']

        del infos_user["password"]
        del infos_user["confirm_password"]

        """
        save in mongodb
        """
        try:
            model.insert_one(infos_user)
            return infos_user

        except Exception:
            return False

    @classmethod
    def update(cls, id, infos_user):
        model = cls.init_infos()['model']

        """
        checks whether the user exists
        """
        user = cls.get_by_id(id)
        if not user:
            raise NotFound('User not Found!')

        """
        save in mongodb
        """
        try:
            model.update_one({"_id": ObjectId(id)}, {"$set": infos_user})
            return True
        except Exception:
            return False


    @classmethod
    def delete(cls, id):
        model = cls.init_infos()['model']

        user = cls.get_by_id(id)
        if not user:
            raise NotFound('User not Found!')

        user['deleted_at'] = datetime.now()
        try:
            model.update_one({"_id": ObjectId(id)}, {"$set": user})
            return True
        except Exception:
            raise InternalServerError("Deleting user error!")


    @classmethod
    def change_password(cls, id, password, new_password):
        model = cls.init_infos()['model']

        user = cls.get_by_id(id, return_password=1)
        if not user:
            raise NotFound('User not Found!')

        if check_password_hash(user['credential']['password'], password) is False:
            raise Forbidden('Incorrent current password!')

        try:
            new_pass = generate_password_hash(new_password)
            model.update_one({'_id': ObjectId(id)}, {'$set': {'credential.password': new_pass}})
            return True
        except Exception:
            return False


    @classmethod
    def send_token_password(cls, username):
        model = cls.init_infos()['model']

        user = model.find_one({'credential.username': username})
        if not user:
            raise NotFound('User not Found!')

        m_recover = cls.init_infos()['model_recover']
        recover = m_recover.find_one({'user_id': user['_id'], 'expired_at': {'$gt': datetime.now()}})
        if recover:
            try:
                url = '{}/auth/recover-pass/{}'.format(Config.BASEPATH_OAUTH_APP, recover['token'])
                status = send_email(user['email'], 'Recover password - OBT OAuth',
                    'send-token-pass.html', name=user['name'], url=url)
                if not status:
                    raise InternalServerError('Error in send email, contact administrators!')

                recover['expired_at'] = datetime.now() + timedelta(days=1)
                m_recover.update_one({"_id": recover['_id']}, {"$set": recover})
                return user
            except Exception:
                return False

        secret_token = random_string(20)
        recover = {
            'token': secret_token,
            'user_id': user['_id'],
            'created_at': datetime.now(),
            'expired_at': datetime.now() + timedelta(days=1)
        }
        try:
            url = '{}/auth/recover-pass/{}'.format(Config.BASEPATH_OAUTH_APP, secret_token)
            status = send_email(user['email'], 'Recover password - OBT OAuth',
                'send-token-pass.html', name=user['name'], url=url)
            if not status:
                raise InternalServerError('Error in send email, contact administrators!')

            m_recover.insert_one(recover)
            return user
        except Exception:
            return False


    @classmethod
    def valid_token_password(cls, token):
        m_recover = cls.init_infos()['model_recover']
        recover = m_recover.find_one({'token': token, 'expired_at': {'$gt': datetime.now()}})
        return recover

    
    @classmethod
    def reset_password(cls, password, token):
        m_recover = cls.init_infos()['model_recover']
        recover = m_recover.find_one({'token': token, 'expired_at': {'$gt': datetime.now()}})
        if not recover:
            raise Forbidden('Token invalid or expired!')
        
        model = cls.init_infos()['model']
        user = cls.get_by_id(str(recover['user_id']))
        try:
            new_pass = generate_password_hash(password)
            model.update_one({'_id': recover['user_id']}, {'$set': {'credential.password': new_pass}})
        except Exception as e:
            return False

        try:
            m_recover.update_one({'_id': recover['_id']}, {'$set': {'expired_at': datetime.now()}})

            send_email(user['email'], 'Password changed successfully - OBT OAuth',
                'recover-pass-success.html', name=user['name'])
            return True
        except Exception:
            return False