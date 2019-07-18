# OAuth Server - Brazil Data Cube
Oauth server for Brazil Data Cube applications

## Structure

- [`bdc_oauth`](./bdc_oauth) python scripts to manage authetication (Oauth 2) in BDC
- [`docs`](./docs) Documentation of bdc_oauth
- [`spec`](./spec) Documentation of API bdc_oauth

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

## Running

- set environment variable: 
    - PORT = port to running API (default: 5000)
    - ENVIRONMENT = env ([DevelopmentConfig, ProductionConfig, TestingConfig])
    - KEYSYSTEM = key to hash system crypto
    - MONGO_USER = user database
    - MONGO_PASSWORD = password database
    - MONGO_HOST = host database
    - MONGO_PORT = port database
    - MONGO_DBNAME = name
    - REDIS_HOST = host redis
    - REDIS_PORT = port redis
    - REDIS_PASSWORD = password redis
    - KEYJWT = key to jwt crypto 
```
python3 manager.py run
```

### Running with docker
```
docker-compose build
docker-compose up -d
```
