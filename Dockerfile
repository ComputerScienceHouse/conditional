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

ENV NVM_DIR /usr/local/nvm
ENV NODE_VERSION v10.24.1
RUN mkdir -p $NVM_DIR

RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash

RUN /bin/bash -c "source $NVM_DIR/nvm.sh && nvm install $NODE_VERSION && nvm use --delete-prefix $NODE_VERSION && npm run production"

RUN rm -rf node_modules && \
    apt-get -yq remove nodejs npm && \
    apt-get -yq clean all

RUN ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime

CMD ["ddtrace-run", "gunicorn", "conditional:app", "--bind=0.0.0.0:8080", "--access-logfile=-", "--timeout=256"]
