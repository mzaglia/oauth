from datetime import datetime
from bson.objectid import ObjectId
from werkzeug.exceptions import InternalServerError, BadRequest, NotFound, Conflict

from bdc_oauth.users.business import UsersBusiness
from bdc_oauth.utils.helpers import random_string
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

        try:
            client = model.find_one({
                "_id": ObjectId(id), 
                "$or": [
                    { "expired_at": {"$gt": datetime.now()} },
                    { "expired_at": None }
                ]
            })
            return client
        except Exception:
            raise NotFound("Client not Found!")

    @classmethod
    def list_by_userid(cls, user_id):
        model = cls.init_infos()['model']

        clients = model.find({
            "user_id": ObjectId(user_id),
            "$or": [
                { "expired_at": {"$gt": datetime.now()} },
                { "expired_at": None }
            ]
        })
        return clients

    @classmethod
    def create(cls, user_id, client_infos):
        model = cls.init_infos()['model']

        user = UsersBusiness.get_by_id(user_id)
        if not user:
            raise NotFound('User not Found!')
        
        """
        check if client name is already registered
        """
        client = model.find_one({
            "client_name": client_infos['client_name'],
            "$or": [
                { "expired_at": {"$gt": datetime.now()} },
                { "expired_at": None }
            ]
        })
        if client:
            raise Conflict('A client with this name already exists')

        """
        create client credentials
        """
        client_infos['user_id'] = user['_id']
        client_infos['client_secret'] = random_string(24)
        client_infos['created_at'] = datetime.now()
        client_infos['expired_at'] = client_infos.get('expired_at', None)

        """ 
        save in mongodb
        """
        try:
            model.insert_one(client_infos)
            return client_infos
            
        except Exception:
            return False  

    @classmethod
    def update(cls, id, client_infos):
        model = cls.init_infos()['model']
        
        """ 
        checks whether the user exists
        """
        client = cls.get_by_id(id)
        if not client:
            raise NotFound('Client not Found!')

        """ 
        update in mongodb 
        """
        try:
            model.update_one({"_id": ObjectId(id)}, {"$set": client_infos})
            return True
        except Exception:
            return False 

    @classmethod
    def delete(cls, id):
        model = cls.init_infos()['model']
        
        """ 
        checks whether the user exists
        """
        client = model.find_one({ "_id": ObjectId(id) })
        if not client:
            raise NotFound('Client not Found!')

        """ 
        delete in mongodb 
        """
        try:
            model.delete_one({"_id": ObjectId(id)})
            return True
        except Exception:
            return False

    @classmethod
    def update_date_expiration(cls, id, action, date):
        model = cls.init_infos()['model']
        
        """ 
        checks whether the user exists
        """
        client = model.find_one({ "_id": ObjectId(id) })
        if not client:
            raise NotFound('Client not Found!')
        
        client['expired_at'] = datetime.now() 
        if action == 'enable':
            if date and datetime.strptime(date, '%Y-%m-%d') <= datetime.now():
                raise BadRequest('Expiration date must be greater than today date')
            else:
                client['expired_at'] = datetime.strptime(date, '%Y-%m-%d') if date else None

        """ 
        update in mongodb 
        """
        try:
            model.update_one({"_id": ObjectId(id)}, {"$set": client})
            return True
        except Exception:
            return False 

    @classmethod
    def generate_new_secret(cls, id):
        model = cls.init_infos()['model']
        
        """         
        checks whether the user exists
        """
        client = cls.get_by_id(id)
        if not client:
            raise NotFound('Client not Found!')

        """ 
        update in mongodb 
        """
        try:
            new_secret = random_string(24)
            client['client_secret'] = new_secret 
            model.update_one({"_id": ObjectId(id)}, {"$set": client})
            return new_secret
        except Exception:
            return False 
    