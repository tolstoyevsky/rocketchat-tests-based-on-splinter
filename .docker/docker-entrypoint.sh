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

if [ -f .env ]; then
    . ./.env
fi

set -x

ADDR=${HOST:="http://127.0.0.1:8006"}

USERNAME=${USERNAME:=""}

PASSWORD=${PASSWORD:=""}

WAIT=${WAIT:='80'}

PUGS_LIMIT=${PUGS_LIMIT:=5}

PYTHON=${PYTHON:="python3"}

SCRIPTS=${SCRIPTS='all'}

BRANCH=${BRANCH:='master'}

set +x

if [ -d ./rocketchat-tests-based-on-splinter ]; then
    rm -rf rocketchat-tests-based-on-splinter
fi

git clone --branch $BRANCH https://github.com/tolstoyevsky/rocketchat-tests-based-on-splinter

cd rocketchat-tests-based-on-splinter

pip install -r requirements.txt

. ./essentials.sh

RUN=(rc)

if [ "${SCRIPTS}" == "all" ]; then
    for i in *_tests.py; do
        test_name="${i%_tests.py}"
        if [ "${test_name}" != "rc" ]; then
            RUN+=("${test_name}")
        fi
    done
else
    for i in "${SCRIPTS[@]}"; do
        RUN+=("${i}")
    done
fi

info "the following tests are going to be run: ${RUN[@]}"

for i in "${RUN[@]}"; do
    case "${i}" in
        # General tests for Rocket.Chat
        rc)
            ${PYTHON} rc_tests.py --host="${HOST}" --username="${USERNAME}" --password="${PASSWORD}"
            ;;
        # Tests for different scripts
        happy_birthder_script)
            ${PYTHON} happy_birthder_script_tests.py --host="${HOST}" --username="${USERNAME}" --password="${PASSWORD}" --wait="${WAIT}"
            ;;
        pugme_script)
            ${PYTHON} pugme_script_tests.py --host="${HOST}" --username="${USERNAME}" --password="${PASSWORD}" --pugs_limit="${PUGS_LIMIT}"
            ;;
        vote_or_die_script)
            ${PYTHON} vote_or_die_script_tests.py --host="${HOST}" --username="${USERNAME}" --password="${PASSWORD}"
            ;;
        *)
            ;;
    esac
done

