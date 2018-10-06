#!/usr/bin/env python3
# Copyright 2018 Anton Maksimovich <antonio.maksimovich@gmail.com>
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

from optparse import OptionParser

from base import RocketChatTestCase


class PugmeScriptTestCase(RocketChatTestCase):
    def __init__(self, addr, username, password, **kwargs):
        RocketChatTestCase.__init__(self, addr, username, password, **kwargs)

        self.schedule_pre_test_case('choose_general_channel')

        self._bot_name = 'meeseeks'
        self._expected_message = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'

    def test_requesting_1_pug(self):
        self.send_message('{} pug me'.format(self._bot_name))
        # TODO: need to check the response

    def test_pug_bomb_3(self):
        self.send_message('{} pug bomb 3'.format(self._bot_name))
        # TODO: need to check the response

    def test_pug_bomb_limit(self):
        self.send_message('{} pug bomb'.format(self._bot_name))
        # TODO: need to check the response


def main():
    parser = OptionParser(usage='usage: %prog [options] arguments')
    parser.add_option('-a', '--host', dest='host',
                      help='allows specifying admin username')
    parser.add_option('-u', '--username', dest='username',
                      help='allows specifying admin username')
    parser.add_option('-p', '--password', dest='password',
                      help='allows specifying admin password')
    options, args = parser.parse_args()

    if not options.host:
        parser.error('Host is not specified')

    if not options.username:
        parser.error('Username is not specified')

    if not options.password:
        parser.error('Password is not specified')

    test_cases = PugmeScriptTestCase(options.host, options.username,
                                     options.password, create_test_user=False)
    test_cases.run()


if __name__ == '__main__':
    main()



