### OAuth with Docker Registry

Make sure you have generated certificate `.crt` and `.key` files and put them inside `certs` folder. You can follow this step [`Configuring`](#configuring). Make sure the `oauth` server is running. You can check in the section [`Running`](#running) for further details.

The `docker-compose.yml` below defines a simple abstraction of how to start docker registry with SSL and OAuth Server. Make sure to edit the variable `REGISTRY_AUTH_TOKEN_REALM` to the IP of OAuth Server.

```yaml
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
```

After that, start registry on port 5000:

```bash
docker-compose up -d
```

## Users

### Create User

```bash
curl --header "Content-Type: application/json" \
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
```

### Login

```bash
curl --header "Content-Type: application/json" \
     -X POST \
     http://localhost:5015/oauth/auth/login \
     --data @- << EOF

{
    "username": "admin",
    "password": "admin1234"
}
EOF
```

Take the `access_token` and follow to the next step to create OAuth Client

### Create Client

docker exec -it \
    mongo-oauth \
    mongo --authenticationDatabase admin \
        bdc_oauth \
        -u bdc \
        -p bdc#key#2019 \
        --eval 'db.users.update({"email": "admin@admin.com"}, {"$set": {"credential.grants": ["user", "admin"]}})'

```bash
curl --header "Content-Type: application/json" \
     --header "Authorization: Bearer PUT_ACCESS_TOKEN_HERE" \
     -X POST \
     http://localhost:5015/oauth/clients/ \
     --data @- << EOF

{
    "client_name": "registry",
    "client_uri": "http://localhost:8080/oauth",
    "redirect_uri": "http://localhost:8080/oauth"
}
EOF
```

Take the `_id` property from result and now we need to authorize the user with application


### Authorize User/Client

The request url represents:

http://localhost:5015/oauth/auth/authorize/`USER_ID`/`CLIENT_ID`

In this example, the `USER_ID` is `5d417b6d46e3eea9bc82e6f2` and `CLIENT_ID` is `5d41b7c946e3eea9bc82e6f3`.
The scope authorization are defined as `appname:context:roles` with three fragments delimited by `:`. For example:
Docker Registry defines `repository:user/image:push,pull`. In this example, the `user/image` represents the docker image and `push,pull` the role authorization (pull and push new images)

```bash
curl --header "Content-Type: application/json" \
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
```

### Docker login

```bash
docker login https://YOUR_IP:5000

docker pull ubuntu:18.04
docker tag ubuntu:18.04 YOUR_IP:5000/admin/ubuntu:18.04
docker push YOUR_IP:5000/admin/ubuntu:18.04
```

Authenticate with docker client:

```bash
docker login https://YOUR_IP:5000
```