import os

from flask_cors import CORS
from flask_script import Manager

from api import create_app
from api.blueprint import blueprint
from api.config import get_settings

app = create_app(get_settings(os.environ.get('ENVIRONMENT', 'DevelopmentConfig')))
app.register_blueprint(blueprint)

manager = Manager(app)

CORS(app, resorces={r'/d/*': {"origins": '*'}})


@manager.command
def run():
    HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
    try:
        PORT = int(os.environ.get('PORT', '5000'))
    except ValueError:
        PORT = 5000

    app.run(HOST, PORT)


if __name__ == '__main__':
    manager.run()