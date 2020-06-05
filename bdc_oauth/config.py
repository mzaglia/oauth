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
        os.environ.get('MONGO_USER', 'mongo'),
        os.environ.get('MONGO_PASSWORD', 'mongo'),
        os.environ.get('MONGO_HOST', 'localhost'),
        os.environ.get('MONGO_PORT', '27018'),
        os.environ.get('MONGO_DBNAME', 'bdc_oauth_test'))
    REDIS_URL = "redis://:{}@{}:{}/0".format(
        os.environ.get('REDIS_PASSWORD', 'passRedis'),
        os.environ.get('REDIS_HOST', 'redis'),
        os.environ.get('REDIS_PORT', '6379'))

    BASE_PATH_TEMPLATES = os.getenv('BASE_PATH_TEMPLATES', os.path.join(BASE_DIR, 'utils/templates-email'.format(os.getcwd())))
    SMTP_PORT = os.getenv('SMTP_PORT', 587)
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.somedomain.com')
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', 'youremail@email.com')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your_password')

    BASEPATH_OAUTH_APP = os.getenv('BASEPATH_OAUTH_APP', 'http://oauth.dpi.inpe.br')


class ProductionConfig(Config):
    """Production Mode."""
    APM_APP_NAME = os.environ.get('APM_APP_NAME', None)
    APM_HOST = os.environ.get('APM_HOST', None)
    APM_SECRET_TOKEN = os.environ.get('APM_SECRET_TOKEN', None)


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
