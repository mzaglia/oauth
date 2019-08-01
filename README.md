# OAuth Server - Brazil Data Cube
Oauth server for Brazil Data Cube applications

## Overview

- [`Structure`](#structure)
- [`Installation`](#installation)
  - [`Requirements`](#requirements)
- [`Configuring`](#configuring)
- [`Running`](#running)
  - [`Running with docker`](#running-with-docker)
  - [`User creation`](#users)
- [`Examples`](#examples)
  - [`OAuth Server with Docker Registry`](./examples/oauth-docker-registry/README.md)


## Structure

- [`bdc_oauth`](./bdc_oauth) python scripts to manage authetication (Oauth 2) in BDC
- [`docs`](./docs) Documentation of bdc_oauth
- [`spec`](./spec) Documentation of API bdc_oauth

## Configuring

The OAuth server requires HTTPS connection to secure and signing communications between browsers and API Clients. In this way,
we need to generate certificate to guarantee a layer security. The certificate could be *Self Signed Layer (SSL)*, *Transport Layer Security (TLS)*. The following code illustrate how to create a SSL certificate:

```bash
mkdir certs
openssl req -newkey rsa:4096 -nodes -sha512 -keyout certs/server.key -x509 -days 3650 -out certs/server.crt
```

## Installation

### Requirements

Make sure you have the following libraries installed:

- [`Python 3`](https://www.python.org/)
- [`mongoDB`](https://www.mongodb.com/)
- [`redis`](https://redis.io/)

After that, install Python dependencies with the following command:

```bash
pip3 install -r requirements.txt
```

if necessary, use as package:

```bash
python3 setup.py install
```

## Running

We strongly recommend to run `oauth` server with docker containers. You can check further details in [`Running with Docker`](#running-with-docker), but you can run manually without docker. **Make sure** the *Redis* and *MongoDB* is running.

- set environment variable:
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
    - CLIENT_SECRET_KEY = path of certificate file key. Example: '/certs/server.key'
    - ALGORITHM = algorithm to jwt crypto
    - EXPIRES_IN_AUTH = time to expirate user token
    - EXPIRES_IN_CLIENT = time to expirate client token

```bash
python3 manager.py run
```

### Running with docker

You can configure the environment to run through Docker containers. In order to do that, build the image brazildatacube/oauth:

```bash
docker-compose build
```

After that, you can run the application with command:

```bash
docker-compose up -d
```

You can also generate the documentation on http://localhost:5001:

```bash
docker-compose run --rm \
                   --name oauth_app_docs \
                   --publish 5001:5001 \
                   --entrypoint="python3 manage.py docs --serve" \
                   bdc-oauth
```