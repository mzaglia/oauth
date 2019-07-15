import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS

from bdc_oauth.blueprint import blueprint
from bdc_oauth.config import get_settings
from bdc_oauth.utils.base_mongo import mongo
from bdc_oauth.utils.base_redis import redis

flask_bcrypt = Bcrypt()


def create_app(config):
    app = Flask(__name__)

    with app.app_context():
        app.config.from_object(config)
        app.register_blueprint(blueprint)
        
        # DB
        mongo.init_app(app)
        mongo.app = app

        # DB Cache
        redis.init_app(app)

        flask_bcrypt.init_app(app)

    return app
    
app = create_app(get_settings(os.environ.get('ENVIRONMENT', 'DevelopmentConfig')))

CORS(app, resorces={r'/d/*': {"origins": '*'}})