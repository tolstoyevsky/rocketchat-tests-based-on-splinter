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

export ADDR=${ADDR:="127.0.0.1"}

export PORT=${PORT:=8006}

export USERNAME=${USERNAME:=""}

export PASSWORD=${PASSWORD:=""}

export PUGS_LIMIT=${PUGS_LIMIT:=5}

export PYTHON=${PYTHON:="python3"}

export WAIT=${WAIT:=100}

BRANCH=${BRANCH:="master"}

HOST=${HOST:="http://$ADDR:$PORT"}

set +x

cd

git clone --branch "${BRANCH}" https://github.com/tolstoyevsky/rocketchat-tests-based-on-splinter

cd rocketchat-tests-based-on-splinter

pip install -r requirements.txt

wait-for-it.sh -h "${ADDR}" -p "${PORT}" -t 90 -- >&2 echo "Rocket.Chat is ready"

./run_tests.sh $*

