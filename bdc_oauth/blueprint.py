#
# This file is part of OBT OAuth 2.0.
# Copyright (C) 2019-2020 INPE.
#
# OBT OAuth 2.0 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from flask import Blueprint
from flask_restplus import Api

from bdc_oauth.auth.controller import api as auth_ns
from bdc_oauth.status.controller import api as status_ns
from bdc_oauth.users.controller import api as users_ns
from bdc_oauth.clients.controller import api as clients_ns

bp = Blueprint('oauth', __name__, url_prefix='/oauth')

api = Api(bp, doc=False)

api.add_namespace(auth_ns)
api.add_namespace(status_ns)
api.add_namespace(users_ns)
api.add_namespace(clients_ns)