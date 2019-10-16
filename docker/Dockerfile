FROM registry.dpi.inpe.br/brazildatacube/python-deploy:0.0.1

RUN apk --update add build-essential

COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt