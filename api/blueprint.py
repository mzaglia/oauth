from flask import Blueprint
from flask_restplus import Api

from api.status.controller import api as status_ns

blueprint = Blueprint('oauth', __name__)

api = Api(blueprint, doc=False)

api.add_namespace(status_ns)