#!/usr/bin/env python3
# Copyright 2018 Evgeny Golyshev <eugulixes@gmail.com>
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

import datetime
import os
from optparse import OptionParser

from base import RocketChatTestCase

import pyperclip
from selenium.webdriver.common.keys import Keys


class GeneralTestCase(RocketChatTestCase):
    def __init__(self, addr, username, password, **kwargs):
        RocketChatTestCase.__init__(self, addr, username, password, **kwargs)
        self.schedule_pre_test_case('choose_general_channel')

        self._test_string = 'Test string'
        self._base_dividing_message = 'Cat from clipboard'
        self._file_url = os.path.join(os.getcwd(), 'static', 'cat.gif')

    def _get_dividing_message(self):
        return '{0} {1}'.format(self._base_dividing_message,
                                str(datetime.datetime.now()))

    def _copy_string_to_clipboard(self):
        pyperclip.copy(self._test_string)

    def _copy_image_to_clipboard(self):
        self.browser.visit('file://{}'.format(self._file_url))

        img = self.browser.driver.find_element_by_xpath('/html/body')
        assert img

        img.click()
        img.send_keys(Keys.CONTROL, 'c')

        self.browser.back()
        self.choose_general_channel()

    def test_pasting_string_from_clipboard(self):
        self._copy_string_to_clipboard()

        msg = self.browser.driver.find_element_by_name('msg')
        assert msg

        msg.send_keys(Keys.CONTROL, 'v')

        send_msg_btn = self.find_by_css('svg.rc-icon.rc-input__icon-svg.'
                                        'rc-input__icon-svg--send')
        assert len(send_msg_btn)

        send_msg_btn.first.click()

        self.check_latest_response_with_retries(self._test_string)

    def test_pasting_file_from_clipboard(self):
        self._copy_image_to_clipboard()

        msg = self.browser.driver.find_element_by_name('msg')
        assert msg

        msg.send_keys(Keys.CONTROL, 'v')

        file_description = self.find_by_css('input#file-description')
        assert len(file_description)

        description = self._get_dividing_message()
        file_description.first.fill(description)

        confirm_btn = self.browser.driver.find_element_by_css_selector(
            'input.rc-button.rc-button--primary.js-confirm')
        assert confirm_btn

        confirm_btn.click()

        expected_message = 'File Uploaded: Clipboard - [\w,\s,:]*\\n{}'.format(
            description)

        self.check_latest_response_with_retries(expected_message, match=True)

    def test_attaching_file(self):
        plus_msg_btn = self.find_by_css('svg.rc-icon.rc-input__icon-svg.'
                                        'rc-input__icon-svg--plus')
        assert len(plus_msg_btn)

        plus_msg_btn.last.click()

        computer = self.browser.find_by_css('span.rc-popover__item-text')
        assert len(computer)

        computer.last.click()

        self.browser.find_by_id('fileupload-input').fill(self._file_url)

        file_description = self.find_by_css('input#file-description')
        assert len(file_description)

        description = self._get_dividing_message()
        file_description.first.fill(description)

        confirm_btn = self.browser.driver.find_element_by_css_selector(
            'input.rc-button.rc-button--primary.js-confirm')
        assert confirm_btn

        confirm_btn.click()

        expected_message = 'File Uploaded: cat.gif\\n{}'.format(
            description)

        self.check_latest_response_with_retries(expected_message, match=True)


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

    test_cases = GeneralTestCase(options.host, options.username,
                                 options.password, create_test_user=False)
    test_cases.run()


if __name__ == '__main__':
    main()
