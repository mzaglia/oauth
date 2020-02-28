..
    This file is part of OBT OAuth 2.0.
    Copyright (C) 2019-2020 INPE.

    OBT OAuth 2.0 is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


OBT OAuth 2.0 with Docker Registry
==================================

Prepare and run Registry Service
--------------------------------

Make sure you have generated certificate `.crt` and `.key` files and put them inside `certs` folder. 

The OAuth server requires HTTPS connection to secure and signing communications between browsers and API Clients. 

In this way, we need to generate certificate to guarantee a layer security. 
The certificate could be Self Signed Layer (SSL), Transport Layer Security (TLS). 
The following code illustrate how to create a SSL certificate:

.. code-block:: shell

        $ mkdir certs
        $ openssl req -newkey rsa:4096 -nodes -sha512 -keyout certs/server.key -x509 -days 3650 -out certs/server.crt

Make sure the `oauth` server is running. You can check in the file `Running <./../../RUNNING.rst>`_ for further details.

The `docker-compose.yml` below defines a simple abstraction of how to start docker registry with SSL and OAuth Server. 
Make sure to edit the variable `REGISTRY_AUTH_TOKEN_REALM` to the IP of OAuth Server.

.. code-block:: yaml

        registry:
            restart: always
            image: registry:2
            ports:
                - 5000:5000
            environment:
                - REGISTRY_AUTH_TOKEN_AUTOREDIRECT=false
                - REGISTRY_HTTP_TLS_CERTIFICATE=/certs/server.crt
                - REGISTRY_HTTP_TLS_KEY=/certs/server.key
                - REGISTRY_AUTH=token
                - REGISTRY_AUTH_TOKEN_REALM=http://OAUTH_SERVER_IP:OAUTH_SERVER_PORT/oauth/auth/token
                - REGISTRY_AUTH_TOKEN_SERVICE=registry
                - REGISTRY_AUTH_TOKEN_ISSUER=oauth_server
                - REGISTRY_AUTH_TOKEN_ROOTCERTBUNDLE=/certs/server.crt
            volumes:
                - /certs:/certs

After that, start registry on port 5000:

.. code-block:: shell

        $ docker-compose up -d


Create User
-----------

.. code-block:: shell

        $ curl --header "Content-Type: application/json" \
            -X POST \
            http://localhost:5015/oauth/users/ \
            --data @- << EOF

        {
            "name": "Admin",
            "email": "admin@admin.com",
            "institution": "Admin",
            "occupation": "Administrate",
            "password": "admin1234",
            "confirm_password": "admin1234"
        }
        EOF

Login
-----

.. code-block:: shell

        $ curl --header "Content-Type: application/json" \
            -X POST \
            http://localhost:5015/oauth/auth/login \
            --data @- << EOF

        {
            "username": "admin",
            "password": "admin1234"
        }
        EOF

Take the `access_token` and follow to the next step to create OAuth Client

Create Client
-------------

.. code-block:: shell

        $ docker exec -it \
            mongo-oauth \
            mongo --authenticationDatabase admin \
                bdc_oauth \
                -u bdc \
                -p bdc#key#2019 \
                --eval 'db.users.update({"email": "admin@admin.com"}, {"$set": {"credential.grants": ["user", "admin"]}})'

.. code-block:: shell

        $ curl --header "Content-Type: application/json" \
            --header "Authorization: Bearer PUT_ACCESS_TOKEN_HERE" \
            -X POST \
            http://localhost:5015/oauth/clients/ \
            --data @- << EOF

        {
            "client_name": "registry",
            "client_uri": "http://localhost:8080/oauth",
            "redirect_uri": "http://localhost:8080/oauth",
            "client_secret": "/path/cert/",
            "type_secret": "file"
        }
        EOF

Take the `_id` property from result and now we need to authorize the user with application


Authorize User/Client
---------------------

The request url represents:

http://localhost:5015/oauth/auth/authorize/`USER_ID`/`CLIENT_ID`

In this example, the `USER_ID` is `5d417b6d46e3eea9bc82e6f2` and `CLIENT_ID` is `5d41b7c946e3eea9bc82e6f3`.
The scope authorization are defined as `appname:context:roles` with three fragments delimited by `:`. For example:
Docker Registry defines `repository:user/image:push,pull`. In this example, the `user/image` represents the docker image and `push,pull` the role authorization (pull and push new images)

.. code-block:: shell

        $ curl --header "Content-Type: application/json" \
            --header "Authorization: Bearer PUT_ACCESS_TOKEN_HERE" \
            -X POST \
            http://localhost:5015/oauth/auth/authorize/5d417b6d46e3eea9bc82e6f2/5d41b7c946e3eea9bc82e6f3 \
            --data @- << EOF

        {
            "scope": [
                "registry:catalog:*",
                "repository:*:*"
            ]
        }
        EOF


Docker login
------------

.. code-block:: shell

        $ docker login https://YOUR_IP:5000
        $ docker pull ubuntu:18.04
        $ docker tag ubuntu:18.04 YOUR_IP:5000/admin/ubuntu:18.04
        $ docker push YOUR_IP:5000/admin/ubuntu:18.04

Authenticate with docker client:

.. code-block:: shell

        $ docker login https://YOUR_IP:5000