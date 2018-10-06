#!/usr/bin/env python3
# Copyright 2018 Sergei Bogolepov <s.bogolepov@wis.software>
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


class HappyBirthderScriptTestCase(RocketChatTestCase):
    def __init__(self, addr, username, password, **kwargs):
        RocketChatTestCase.__init__(self, addr, username, password, **kwargs)

        self.schedule_pre_test_case('choose_general_channel')

        self._test_user_birthday = '01.01.2000'

        self._bot_name = 'meeseeks'

    def test_requesting_birthday_set(self):
        self.send_message('{} birthday set {} {}'.
                          format(self._bot_name, self.test_username,
                                 self._test_user_birthday))

        assert self.check_latest_response_with_retries(
            "Saving {}'s birthday.".format(self.test_username))

    def test_requesting_birthdays_on(self):
        day_month = self._test_user_birthday[:-5]

        self.send_message('{} birthdays on {}'.
                          format(self._bot_name, day_month))

        assert self.check_latest_response_with_retries(
            '@{}'.format(self.test_username))

    def test_requesting_birthdays_delete(self):
        self.send_message('{} birthday delete {}'.
                          format(self._bot_name, self.test_username))

        assert self.check_latest_response_with_retries(
            "Removing {}'s birthday.".format(self.test_username))


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

    test_cases = HappyBirthderScriptTestCase(options.host, options.username,
                                             options.password)
    test_cases.run()


if __name__ == '__main__':
    main()
