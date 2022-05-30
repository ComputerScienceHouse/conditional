FROM docker.io/python:3.8-buster
MAINTAINER Devin Matte <matted@csh.rit.edu>

RUN mkdir /opt/conditional

ADD requirements.txt /opt/conditional

WORKDIR /opt/conditional

RUN apt-get -yq update && \
    apt-get -yq install libsasl2-dev libldap2-dev libssl-dev gcc g++ make && \
    pip install -r requirements.txt && \
    apt-get -yq clean all

ADD . /opt/conditional

RUN curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
    apt-get -yq update && \
    apt-get -yq install nodejs && \
    npm install && \
    npm run production && \
    rm -rf node_modules && \
    apt-get -yq remove nodejs npm && \
    apt-get -yq clean all

RUN ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime

CMD ["ddtrace-run", "gunicorn", "conditional:app", "--bind=0.0.0.0:8080", "--access-logfile=-", "--timeout=256"]
