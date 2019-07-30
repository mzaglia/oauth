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

Authenticate with docker client:

```bash
docker login https://localhost:5000
```