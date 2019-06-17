FROM python:3.6.8-jessie

ENV APP_DIR /usr/src/app

RUN	apt-get update && \
    apt-get install -y curl libssl-dev libffi-dev locales locales-all nano git && \
    pip3 install --upgrade pip && \
    rm -rf /var/cache/apk/*

ENV LC_ALL pt_BR.UTF-8
ENV LANG pt_BR.UTF-8
ENV LANGUAGE pt_BR.UTF-8

COPY . ${APP_DIR}
WORKDIR ${APP_DIR}

EXPOSE 5000

RUN pip3 install -r requirements.txt

ENTRYPOINT python3 manage.py run
