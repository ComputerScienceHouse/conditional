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

FROM astral/uv:python3.12-bookworm-slim
MAINTAINER Computer Science House <webmaster@csh.rit.edu>

WORKDIR /opt/conditional

RUN apt-get -yq update && \
    apt-get -yq install libldap2-dev libldap-common libsasl2-dev libssl-dev gcc g++ make  && \
    apt-get -yq clean all 

COPY requirements.txt /opt/conditional

RUN uv pip install --system -r requirements.txt 

ARG PORT=8080
ENV PORT=${PORT}
EXPOSE ${PORT}

COPY conditional /opt/conditional/conditional
COPY migrations /opt/conditional/migrations
COPY *.py package.json /opt/conditional/
COPY --from=build-frontend /opt/conditional/conditional/static/ /opt/conditional/conditional/static/

RUN ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime

CMD ["sh", "-c", "gunicorn"]

