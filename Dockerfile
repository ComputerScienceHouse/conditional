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

RUN curl -O -L https://github.com/sass/dart-sass/releases/download/1.93.2/dart-sass-1.93.2-linux-x64.tar.gz && tar -xzvf dart-sass-*.tar.gz
ENV PATH="$PATH:/opt/conditional/dart-sass"

COPY package.json package-lock.json /opt/conditional/

COPY build*.js /opt/conditional
COPY frontend /opt/conditional/frontend

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
COPY --from=build-frontend /opt/conditional/conditional/static /opt/conditional/conditional/static

RUN ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime

CMD ["gunicorn", "conditional:app", "--bind=0.0.0.0:8080", "--access-logfile=-", "--timeout=256"]
