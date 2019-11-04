FROM registry.dpi.inpe.br/brazildatacube/python-deploy:0.0.2

RUN apk update \
    && apk add --virtual build-dependencies \
        build-base

COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt