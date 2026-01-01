FROM node:25-bookworm-slim AS build-frontend

RUN mkdir /opt/conditional

WORKDIR /opt/conditional

RUN apt-get -yq update && \
    apt-get -yq install curl git

COPY package.json package-lock.json /opt/conditional/

RUN npm ci 

COPY webpack.config.js /opt/conditional
COPY frontend /opt/conditional/frontend

RUN npm run webpack

FROM docker.io/python:3.12-slim-bookworm
MAINTAINER Computer Science House <webmaster@csh.rit.edu>

RUN mkdir /opt/conditional

COPY requirements.txt /opt/conditional

WORKDIR /opt/conditional

RUN apt-get -yq update && \
    apt-get -yq install libsasl2-dev libldap2-dev libldap-common libssl-dev gcc g++ make && \
    pip install -r requirements.txt && \
    apt-get -yq clean all

ARG PORT=8080
ENV PORT=${PORT}
EXPOSE ${PORT}

COPY conditional /opt/conditional/conditional
COPY *.py package.json /opt/conditional
COPY --from=build-frontend /opt/conditional/conditional/static /opt/conditional/conditional/static

RUN ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime

CMD ["sh", "-c", "gunicorn conditional:app --bind=0.0.0.0:${PORT} --access-logfile=- --timeout=256"]
