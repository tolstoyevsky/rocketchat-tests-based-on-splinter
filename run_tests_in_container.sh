#!/bin/bash
# Copyright 2019 Evgeny Golyshev <eugulixes@gmail.com>
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

ARGS=()

if [[ -f .env ]]; then
    while IFS='' read -r line; do
        IFS='=' read -ra VAR_VALUE <<< ${line}
        if [[ ${#VAR_VALUE[@]} != 2 ]]; then
            >&2 echo "To assign environment variables, specify them as VAR=VALUE."
            exit 1
        fi

        ARGS+=(--env="${line}")
    done < .env
fi

docker run -it --net=host --rm ${ARGS[@]} rocketchat-tests-based-on-splinter $*

