from flask import Blueprint
from flask_restplus import Api

from bdc_oauth.status.controller import api as status_ns
from bdc_oauth.users.controller import api as users_ns

blueprint = Blueprint('oauth', __name__)

api = Api(blueprint, doc=False)

api.add_namespace(status_ns)
api.add_namespace(users_ns)