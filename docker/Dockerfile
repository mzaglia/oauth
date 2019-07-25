FROM brazildatacube/base:0.1

RUN apt-get update && apt-get install -y build-essential

ADD . /bdc-geoserver

WORKDIR /bdc-geoserver

RUN pip3 install -r requirements.txt

VOLUME /data

EXPOSE 5000

CMD [ "python3", "manage.py", "run" ]