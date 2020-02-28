#
# This file is part of OBT OAuth 2.0.
# Copyright (C) 2019-2020 INPE.
#
# OBT OAuth 2.0 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def get_settings(env):
    return CONFIG.get(env)


class Config():
    DEBUG = False
    TESTING = False

    AUTH_SECRET_KEY = os.environ.get('AUTH_SECRET_KEY', 'bdc#2019key')
    ALGORITHM = os.environ.get('ALGORITHM', 'RS256')
    EXPIRES_IN_AUTH = int(os.environ.get('EXPIRES_IN_AUTH', '3600'))
    EXPIRES_IN_CLIENT = int(os.environ.get('EXPIRES_IN_CLIENT', '86400'))

    MONGO_URI = 'mongodb://{}:{}@{}:{}/{}?authSource=admin'.format(
        os.environ.get('MONGO_USER'), os.environ.get('MONGO_PASSWORD'),
        os.environ.get('MONGO_HOST'), os.environ.get('MONGO_PORT'),
        os.environ.get('MONGO_DBNAME'))
    REDIS_URL = "redis://:{}@{}:{}/0".format(
        os.environ.get('REDIS_PASSWORD', 'passRedis'),
        os.environ.get('REDIS_HOST', 'redis'),
        os.environ.get('REDIS_PORT', '6379'))


class ProductionConfig(Config):
    """Production Mode."""

    DEBUG = False


class DevelopmentConfig(Config):
    """Development Mode."""

    DEVELOPMENT = True


class TestingConfig(Config):
    """Testing Mode (Continous Integration)."""

    TESTING = True
    DEBUG = True


CONFIG = {
    "DevelopmentConfig": DevelopmentConfig(),
    "ProductionConfig": ProductionConfig(),
    "TestingConfig": TestingConfig()
}
