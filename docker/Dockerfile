FROM python:3.7-slim-stretch

ENV PYTHONUNBUFFERED 0

ENV TERM linux

ENV XVFB_WIDTH 1920

ENV XVFB_HEIGHT 1080

WORKDIR /home/app/

RUN apt-get update -y \
 && apt-get install -y \
    gnupg \
    wget \
 && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
 && echo deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main >> /etc/apt/sources.list \
 && apt-get update -y \
 && apt-get install -y \
    curl \
    git \
    google-chrome-stable \
    libfontconfig1 \
    libgconf-2-4 \
    libglib2.0-0 \
    libnss3 \
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

COPY ./is_bot_online.py /root/is_bot_online.py

COPY ./wizard.py /root/wizard.py

ENTRYPOINT ["docker-entrypoint.sh"]

