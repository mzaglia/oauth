import json
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_compress import Compress
from flask_wtf.csrf import CSRFProtect

from bdc_oauth.utils.base_mongo import mongo
from bdc_oauth.utils.base_redis import redis

flask_bcrypt = Bcrypt()


def create_app(config_name):
    app = Flask(__name__)

    with app.app_context():
        CSRFProtect(app)

        app.config.from_object(config_name)
        app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/oauth')
        
        # DB
        mongo.init_app(app)
        mongo.app = app

        # DB Cache
        redis.init_app(app)

        flask_bcrypt.init_app(app)
        compress = Compress()
        compress.init_app(app)

    return app


class PrefixMiddleware(object):

    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):

        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return ["This url does not belong to the app.".encode()]
