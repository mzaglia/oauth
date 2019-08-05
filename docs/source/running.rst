.. _running:

Running
=======
In order to run BDC_OAUTH, you must define variable `ENVIRONMENT`. By default, the application runs on development mode. You can change to
`ProductionConfig` or `TestingConfig` with the following command:

.. code-block:: sh

    $ export ENVIRONMENT=ProductionConfig
    $ python manager.py run

It will runs on host `0.0.0.0` with port `5000`. You can access directly through `http://127.0.0.1:5000/oauth/status`

others available environment variable:
 - PORT = port to running API (default: 5000)
 - ENVIRONMENT = env ([DevelopmentConfig, ProductionConfig, TestingConfig])
 - MONGO_USER = user database
 - MONGO_PASSWORD = password database
 - MONGO_HOST = host database
 - MONGO_PORT = port database
 - MONGO_DBNAME = name
 - REDIS_HOST = host redis
 - REDIS_PORT = port redis
 - REDIS_PASSWORD = password redis
 - AUTH_SECRET_KEY = key to jwt crypto
 - CLIENT_SECRET_KEY = path of certificate
 - ALGORITHM = algorithm to jwt crypto
 - EXPIRES_IN_AUTH = time to expirate user token
 - EXPIRES_IN_CLIENT = time to expirate client token