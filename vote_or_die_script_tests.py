#!/usr/bin/env python3
# Copyright 2018 Anton Maksimovich <antonio.maksimovich@gmail.com>
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

"""Tests related to the hubot-vote-or-die script. """

import sys
import time
from argparse import ArgumentParser

from base import RocketChatTestCase


class VoteOrDieScriptTestCase(RocketChatTestCase):
    """Tests for the hubot-vote-or-die script. """

    def __init__(self, addr, username, password, **kwargs):
        RocketChatTestCase.__init__(self, addr, username, password, **kwargs)

        self.schedule_pre_test_case('choose_general_channel')

    def _wait_value(self, css_selector, position, expected_value, retries=30):
        for _ in range(retries):
            elem_list = self.find_by_css(css_selector)
            assert elem_list

            elem = elem_list[position]
            if elem.value == expected_value:
                return True
            time.sleep(1)
        return False

    def test_creating_poll_with_1_option(self):
        """Tests if it's not possible to create a poll with 1 option. The polls
        require more than 1 options.
        """

        self.send_message('!poll question?, option 1')

        assert self.check_latest_response_with_retries('Provide more than one option.')

    def test_creating_poll_with_2_options(self):
        """Tests if it's possible to create a poll with 2 options. """

        self.send_message('!poll question?, option 1, option 2')

        assert self.check_latest_response_with_retries(
            '_Please vote using reactions_\nquestion?\n0⃣ option 1\n1⃣ option 2')

    def test_creating_poll_with_3_options_and_check_related_emojis(self):
        """Tests if it's possible to create a poll with 3 options and checks if
        there're the corresponding emojis.
        """

        self.send_message('!poll question?, option 1, option 2, option 3')

        assert self.check_latest_response_with_retries(
            '_Please vote using reactions_\nquestion?\n0⃣ option 1\n1⃣ option 2\n2⃣ option 3')

        assert self._wait_value('.reactions ', -1, '0⃣ 1 1⃣ 1 2⃣ 1')

    def test_creating_poll_with_over_12_options(self):
        """Tests if it's not possible to create a poll with more than
        12 options.
        """

        self.send_message(
            '!poll question?, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15')

        assert self.check_latest_response_with_retries(
            'The maximum number of options is limited to 12.')


def main():
    """The main entry point. """

    parser = ArgumentParser(description='usage: %prog [options] arguments')
    parser.add_argument('-a', '--host', dest='host', type=str,
                        help='allows specifying domain or IP of the Rocket.Chat host')
    parser.add_argument('-u', '--username', dest='username', type=str,
                        help='allows specifying admin username')
    parser.add_argument('-p', '--password', dest='password', type=str,
                        help='allows specifying admin password')
    options = parser.parse_args()

    if not options.host:
        options.host = 'http://127.0.0.1:8006'
        sys.stderr.write(
            'Host is not specified. Defaults to {}.\n'.format(options.host)
        )

    if not options.username:
        parser.error('Username is not specified')

    if not options.password:
        parser.error('Password is not specified')

    test_cases = VoteOrDieScriptTestCase(options.host, options.username,
                                         options.password, create_test_user=False)
    exit_code = test_cases.run()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
