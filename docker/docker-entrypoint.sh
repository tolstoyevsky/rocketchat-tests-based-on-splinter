#!/bin/bash
# Copyright 2018 Evgeny Golyshev <eugulixes@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -e

set -x

export ADDR=${ADDR:="rocketchat"}

export BOT_NAME=${BOT_NAME:="meeseeks"}

export PORT=${PORT:=8006}

export USERNAME=${USERNAME:="admin"}

export PASSWORD=${PASSWORD:="pass"}

export PUGS_LIMIT=${PUGS_LIMIT:=5}

export PYTHON=${PYTHON:="python3"}

export RUNNING_WAIT=${RUNNING_WAIT:=120}

export WAIT=${WAIT:=100}

BRANCH=${BRANCH:="master"}

HOST=${HOST:="http://$ADDR:$PORT"}

set +x

cd

git clone --branch "${BRANCH}" https://github.com/tolstoyevsky/rocketchat-tests-based-on-splinter

cd rocketchat-tests-based-on-splinter

pip install -r requirements.txt

wait-for-it.sh -h "${ADDR}" -p "${PORT}" -t 90 -- >&2 echo "Rocket.Chat is ready"

>&2 echo "Rocket.Chat environment initialization"
env PYTHONPATH="/root/rocketchat-tests-based-on-splinter/" ${PYTHON} /root/wizard.py --host="http://${ADDR}:${PORT}" --username="${USERNAME}" --password="${PASSWORD}"

>&2 echo "Checking if ${BOT_NAME} is online"
env PYTHONPATH="/root/rocketchat-tests-based-on-splinter/" ${PYTHON} /root/is_bot_online.py --host="http://${ADDR}:${PORT}" --username="${USERNAME}" --password="${PASSWORD}" --wait="${RUNNING_WAIT}" --bot="${BOT_NAME}"

./run_tests.sh $*

