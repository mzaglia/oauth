..
    This file is part of OBT OAuth 2.0.
    Copyright (C) 2019-2020 INPE.

    OBT OAuth 2.0 is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


=======
Running
=======

Prerequisites
-------------

For the application to work, it is necessary to have an instance of `MongoDB <https://www.mongodb.com/>`_. and one of `Redis <https://redis.io/>`_.
if you do not have these services, run the docker-compose.yml file


Running http server
-------------------

Set environment variables in command line or edit file: bdc_oauth/config.py. Then, run the application.

.. code-block:: shell

        $ bdc-oauth run

or

.. code-block:: shell

        $ MONGO_USER=bdc \
            MONGO_PASSWORD=bdc#key#2019 \
            MONGO_HOST=mongo-oauth \
            MONGO_PORT=27017 \
            MONGO_DBNAME=bdc_oauth \
            REDIS_HOST=redis-oauth \
            REDIS_PORT=6379 \
            REDIS_PASSWORD=passRedis \
            ENVIRONMENT=ProductionConfig \
            KEYSYSTEM=Key#2019@BDC#hash \
            AUTH_SECRET_KEY=key#jwt#2019 \
            ALGORITHM=RS256 \
            EXPIRES_IN_AUTH=86400 \
            EXPIRES_IN_CLIENT=604800 \
            bdc-oauth run
