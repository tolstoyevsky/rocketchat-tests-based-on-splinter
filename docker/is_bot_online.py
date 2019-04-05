#!/usr/bin/env python3
# Copyright 2019 Semyon Suprun <simonsuprun@gmail.com>
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

import sys
from argparse import ArgumentParser
from time import sleep

from base import SplinterTestCase


LOCALHOST = 'http://127.0.0.1:8006'


class WaitUntilBotIsOnline(SplinterTestCase):
    def __init__(self, addr, username, password, **kwargs):
        SplinterTestCase.__init__(self, addr)

        self.username = username
        self.password = password
        self.bot_name = kwargs.get('bot')
        self.wait = kwargs.get('wait')

    def test_if_bot_is_online(self):
        self.browser.fill('emailOrUsername', self.username)
        self.browser.fill('pass', self.password)
        self.find_by_css('.rc-button.rc-button--primary.login').click()

        search_btn = self.find_by_css(
            '.rc-icon.sidebar__toolbar-button-icon'
            '.sidebar__toolbar-button-icon--magnifier'
        )
        assert search_btn
        search_btn.click()

        search = self.browser.find_by_css('.rc-input__element')
        assert search
        search.fill(self.bot_name)

        channels = self.browser.find_by_css('.sidebar-item.popup-item')
        assert channels
        channels.first.click()

        is_online = False
        for _ in range(self.wait):
            status = self.find_by_css('.rc-header__visual-status')
            if status.first.text.lower() == 'offline':
                sleep(1)
            else:
                is_online = True
                break
        assert is_online


def main():
    parser = ArgumentParser(description='usage: %prog [options] arguments')
    parser.add_argument('-a', '--host', dest='host', type=str,
                        help='allows specifying domain or IP '
                             'of the Rocket.Chat host')
    parser.add_argument('-u', '--username', dest='username', type=str,
                        help='allows specifying admin username')
    parser.add_argument('-p', '--password', dest='password', type=str,
                        help='allows specifying admin password')
    parser.add_argument('-w', '--wait', dest='wait', type=int,
                        help='allows specifying time '
                             'for waiting bot running (secs)')
    parser.add_argument('-b', '--bot', dest='bot', type=str,
                        help='allows specifying bot name')

    options = parser.parse_args()
    if not options.host:
        options.host = LOCALHOST
        sys.stderr.write(
            'Host is not specified. Defaults to {}.\n'.format(options.host)
        )

    if not options.username:
        parser.error('Username is not specified')

    if not options.password:
        parser.error('Password is not specified')

    if not options.wait:
        options.wait = 120
        sys.stderr.write(
            'Waiting time is not specified. Defaults to {}.\n'
            .format(options.wait)
        )

    if not options.bot:
        options.bot = 'meeseeks'
        sys.stderr.write(
            'Bot name is not specified. Defaults to {}.\n'.format(options.bot)
        )

    checks = WaitUntilBotIsOnline(
        options.host,
        options.username,
        options.password,
        bot=options.bot,
        wait=options.wait
    )

    exit_code = checks.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
