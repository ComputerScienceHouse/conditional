FROM debian:bookworm-slim AS build-frontend
# I'd love to use a node image but our version of node is too old :)

RUN mkdir /opt/conditional

WORKDIR /opt/conditional

ENV NVM_DIR /usr/local/nvm
ENV NODE_VERSION v10.24.1
RUN mkdir -p $NVM_DIR

RUN apt-get -yq update && \
    apt-get -yq install curl git

RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash

RUN /bin/bash -c "source $NVM_DIR/nvm.sh && nvm install $NODE_VERSION"

COPY package.json package-lock.json /opt/conditional/

COPY build*.js webpack.config.js frontend /opt/conditional
COPY gulpfile.js/lib /opt/conditional/gulpfile.js/lib
COPY gulpfile.js/config.json /opt/conditional/gulpfile.js/config.json

RUN /bin/bash -c "source $NVM_DIR/nvm.sh && nvm use --delete-prefix $NODE_VERSION && npm ci && npm run build"

FROM docker.io/python:3.12-bookworm
MAINTAINER Computer Science House <webmaster@csh.rit.edu>

RUN mkdir /opt/conditional

ADD requirements.txt /opt/conditional

WORKDIR /opt/conditional

RUN apt-get -yq update && \
    apt-get -yq install libsasl2-dev libldap2-dev libldap-common libssl-dev gcc g++ make && \
    pip install -r requirements.txt && \
    apt-get -yq clean all

ADD . /opt/conditional
COPY --from=build-frontend /opt/conditional/static /opt/conditional/static

RUN ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime

CMD ["gunicorn", "conditional:app", "--bind=0.0.0.0:8080", "--access-logfile=-", "--timeout=256"]
