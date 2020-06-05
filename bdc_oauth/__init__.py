#
# This file is part of OBT OAuth 2.0.
# Copyright (C) 2019-2020 INPE.
#
# OBT OAuth 2.0 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_redoc import Redoc

from . import config
from .version import __version__

flask_bcrypt = Bcrypt()

def create_app(config_name='DevelopmentConfig'):
    """Create Brazil Data Cube application from config object.
    Args:
        config_name (string) Config instance name
    Returns:
        Flask Application with config instance scope
    """
    app = Flask(__name__)
    conf = config.get_settings(config_name)
    app.config.from_object(conf)
    app.config['REDOC'] = {
        'title': 'Web service to authentication (Oauth 2) - OBT',
        'spec_route': '/oauth/docs'
    }

    if app.config.get('APM_APP_NAME') and app.config.get('APM_SECRET_TOKEN'):
        from elasticapm.contrib.flask import ElasticAPM
        app.config['ELASTIC_APM'] = {
            'SERVICE_NAME': app.config['APM_APP_NAME'],
            'SECRET_TOKEN': app.config['APM_SECRET_TOKEN'],
            'SERVER_URL': app.config['APM_HOST']
        }
        ElasticAPM(app)

    with app.app_context():
        CORS(app, resources={r"/*": {"origins": "*"}})
        _ = Redoc('./spec/openapi.yaml', app)

        # DB
        from bdc_oauth.utils.base_mongo import mongo
        mongo.init_app(app)
        mongo.app = app

        # DB Cache
        from bdc_oauth.utils.base_redis import redis
        redis.init_app(app)

        flask_bcrypt.init_app(app)

        # Setup blueprint
        from bdc_oauth.blueprint import bp
        app.register_blueprint(bp)

    return app

app = create_app(os.environ.get('ENVIRONMENT', 'DevelopmentConfig'))

__all__ = (
    '__version__',
    'create_app',
)
