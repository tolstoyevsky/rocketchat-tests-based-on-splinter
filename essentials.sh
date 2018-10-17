# Copyright (C) 2018 Evgeny Golyshev <eugulixes@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

TEST_SUFFIX="_tests.py"

text_in_red_color=$(tput setaf 1)

text_in_yellow_color=$(tput setaf 3)

reset=$(tput sgr0)

# Prints the specified message with the level info.
# Globals:
#     text_in_yellow_color
#     reset
# Arguments:
#     Message
# Returns:
#     None
info() {
    >&2 echo "${text_in_yellow_color}Info${reset}: $*"
}

# Prints the specified message with the level fatal.
# Globals:
#     text_in_red_color
#     reset
# Arguments:
#     Message
# Returns:
#     None
fatal() {
    >&2 echo "${text_in_red_color}Fatal${reset}: $*"
}

# Checks if the specified test exists.
# Globals:
#     TEST_SUFFIX
# Arguments:
#     Message
# Returns:
#     Boolean
check_if_test_exists() {
    local script=$1
    if [ -f "${script}${TEST_SUFFIX}" ]; then
        true
    else
        false
    fi
}

