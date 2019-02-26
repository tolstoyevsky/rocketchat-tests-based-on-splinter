FROM python:3.7-slim-stretch

ENV PYTHONUNBUFFERED 0

ENV TERM linux

WORKDIR /home/app/

RUN apt-get update -y \
 && apt-get install -y \
    chromium \
    curl \
    git \
    python-xvfbwrapper \
    x11-xkb-utils \
    xvfb \
 && curl -O https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
 && chmod +x wait-for-it.sh \
 && mv wait-for-it.sh /usr/local/bin \
 && touch /.docker \
 && apt-get purge -y \
    curl \
 && apt-get autoremove -y \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY ./docker-entrypoint.sh /usr/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]

