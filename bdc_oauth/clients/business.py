import jwt
import json
from copy import deepcopy
from datetime import datetime, timedelta
from random import randint
from bson.objectid import ObjectId

from bdc_oauth.utils.base_mongo import mongo

class ClientsBusiness():

    @classmethod
    def init_infos(cls): 
        return {
            "model": mongo.db.clients
        }

    @classmethod
    def get_all(cls):
        model = cls.init_infos()['model']

        clients = model.find({
            "$or": [
                { "expired_at": {"$gt": datetime.now()} },
                { "expired_at": None }
            ]
        })
        return list(clients)

    @classmethod
    def get_by_id(cls, id):
        model = cls.init_infos()['model']

        user = model.find_one({
            "_id": ObjectId(id), 
            "$or": [
                { "expired_at": {"$gt": datetime.now()} },
                { "expired_at": None }
            ]
        })
        return user

    @classmethod
    def create(cls, user_id, client_infos):
        pass

    @classmethod
    def update(cls, id, client_infos):
        pass  

    @classmethod
    def delete(cls, id):
        pass

    @classmethod
    def disable(cls, id):
        pass

    @classmethod
    def list_by_userid(cls, user_id):
        pass
    