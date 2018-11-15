FROM python:3.7-slim-stretch

ENV TERM linux

COPY ./docker-entrypoint.sh /usr/bin/docker-entrypoint.sh

WORKDIR /home/app/

RUN apt-get update -y; \
    apt-get install -y\
    xvfb \
    python-xvfbwrapper \
    x11-xkb-utils \
    chromium \
    git

ENTRYPOINT [ "docker-entrypoint.sh" ]