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
    def __init__(self, addr, username, password, pugs_limit, **kwargs):
        RocketChatTestCase.__init__(self, addr, username, password, **kwargs)

        self.schedule_pre_test_case('choose_general_channel')

        self._bot_name = 'meeseeks'
        self._expected_message = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        self._pugs_limit = pugs_limit

    def test_requesting_1_pug(self):
        self.send_message('{} pug me'.format(self._bot_name))

        assert self.check_latest_response_with_retries(self._expected_message,
                                                       match=True)

    def test_pug_bomb_3(self):
        self.send_message('{} pug bomb 3'.format(self._bot_name))

        assert self.check_latest_response_with_retries(self._expected_message,
                                                       match=True, messages_number=3)

    def test_pug_bomb_limit(self):
        self.send_message('{} pug bomb'.format(self._bot_name))

        assert self.check_latest_response_with_retries(self._expected_message,
                                                       match=True, messages_number=int(self._pugs_limit))


def main():
    parser = OptionParser(usage='usage: %prog [options] arguments')
    parser.add_option('-a', '--host', dest='host',
                      help='allows specifying domain or IP of the Rocket.Chat host')
    parser.add_option('-u', '--username', dest='username',
                      help='allows specifying admin username')
    parser.add_option('-p', '--password', dest='password',
                      help='allows specifying admin password')
    parser.add_option('-l', '--pugs_limit', dest='pugs_limit',
                      help='allows specifying limit for pugs')
    options, args = parser.parse_args()

    if not options.host:
        parser.error('Host is not specified')

    if not options.username:
        parser.error('Username is not specified')

    if not options.password:
        parser.error('Password is not specified')

    if not options.pugs_limit:
        parser.error('Pugs limit is not specified')

    test_cases = PugmeScriptTestCase(options.host, options.username, options.password,
                                     pugs_limit=options.pugs_limit)
    test_cases.run()


if __name__ == '__main__':
    main()
