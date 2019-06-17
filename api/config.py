import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def get_settings(env):
    return eval(env)


class Config():
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = False
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'APi-Users-123456'
    REDIS_URL = "redis://:{}@{}:{}/0".format(
        os.environ.get('REDIS_PASSWORD', 'passRedis'), os.environ.get('REDIS_HOST', 'redis'), os.environ.get('REDIS_PORT', '6379'))


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_POOL_RECYCLE = 240
    SQLALCHEMY_POOL_TIMEOUT = 30
    MONGO_URI = 'mongodb://{}:{}@{}:{}/{}?authSource=admin'.format(
        os.environ.get('MONGO_USER'), os.environ.get('MONGO_PASSWORD'), os.environ.get('MONGO_HOST'), 
        os.environ.get('MONGO_PORT'), os.environ.get('MONGO_DBNAME'))


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = False
    SQLALCHEMY_POOL_RECYCLE = 240
    SQLALCHEMY_POOL_TIMEOUT = 30
    MONGO_URI = 'mongodb://{}:{}/{}'.format(os.environ.get('MONGO_HOST'), os.environ.get('MONGO_PORT'), os.environ.get('MONGO_DBNAME'))


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_POOL_RECYCLE = 240
    SQLALCHEMY_POOL_TIMEOUT = 30
    MONGO_URI = 'mongodb://{}:{}/{}'.format(os.environ.get('MONGO_HOST'), os.environ.get('MONGO_PORT'), os.environ.get('MONGO_DBNAME'))


key = Config.SECRET_KEY

