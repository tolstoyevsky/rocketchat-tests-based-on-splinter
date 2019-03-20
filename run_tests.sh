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

. ./essentials.sh

set -x

ADDR=${ADDR:="127.0.0.1"}

PORT=${PORT:=8006}

USERNAME=${USERNAME:=""}

PASSWORD=${PASSWORD:=""}

WAIT=${WAIT:='80'}

PUGS_LIMIT=${PUGS_LIMIT:=5}

PYTHON=${PYTHON:="python3"}

HOST="http://${ADDR}:${PORT}"

set +x

if [ -z "${PYTHON}" ]; then
    >&2 echo "Python interpreter is not specified"
    exit 1
fi

while true; do
    case "$1" in
    -s|--scripts)
        IFS=',' read -ra SCRIPTS <<< $2
        shift 2
        ;;
    *)
        break
        ;;
    esac
done

RUN=()

if [ "${SCRIPTS}" == "all" ]; then
    for i in *_tests.py; do
        test_name="${i%_tests.py}"
        RUN+=("${test_name}")
    done
else
    for i in "${SCRIPTS[@]}"; do
        if ! $(check_if_test_exists "${i}"); then
            fatal "${i}${TEST_SUFFIX} does not exists"
            exit 1
        fi

        RUN+=("${i}")
    done
fi

exit_code=0

info "the following tests are going to be run: ${RUN[@]}"

for i in "${RUN[@]}"; do
    case "${i}" in
        # General tests for Rocket.Chat
        rc)
            ${PYTHON} rc_tests.py --host="${HOST}" --username="${USERNAME}" --password="${PASSWORD}" || exit_code=$?
            ;;
        # Tests for different scripts
        happy_birthder_script)
            ${PYTHON} happy_birthder_script_tests.py --host="${HOST}" --username="${USERNAME}" --password="${PASSWORD}" --wait="${WAIT}" || exit_code=$?
            ;;
        pugme_script)
            ${PYTHON} pugme_script_tests.py --host="${HOST}" --username="${USERNAME}" --password="${PASSWORD}" --pugs_limit="${PUGS_LIMIT}" || exit_code=$?
            ;;
        vote_or_die_script)
            ${PYTHON} vote_or_die_script_tests.py --host="${HOST}" --username="${USERNAME}" --password="${PASSWORD}" || exit_code=$?
            ;;
        *)
            ;;
    esac
done

exit "${exit_code}"

