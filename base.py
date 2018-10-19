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

import collections
import re
import sys
import time
import traceback
from curses import tparm, tigetstr, setupterm

from splinter import Browser
from selenium.common.exceptions import StaleElementReferenceException


class OrderedClassMembers(type):
    @classmethod
    def __prepare__(mcs, name, bases):
        return collections.OrderedDict()

    def __new__(mcs, name, bases, classdict):
        exception = ('__module__', '__qualname__')
        classdict['__ordered__'] = \
            [key for key in classdict.keys() if key not in exception]

        return type.__new__(mcs, name, bases, classdict)


class SplinterTestCase(metaclass=OrderedClassMembers):
    def __init__(self, addr, browser_window_size=(1920, 1080),
                 page_load_timeout=30, sticky_timeout=30):
        setupterm()

        self.browser = Browser('chrome', headless=False, wait_time=30,
                               executable_path='./drivers/chromedriver')
        self.browser.driver.implicitly_wait(sticky_timeout)
        self.browser.driver.set_page_load_timeout(page_load_timeout)
        self.browser.driver.set_window_size(*browser_window_size)
        self.browser.visit(addr)

        self._failed_number = 0
        self._succeeded_number = 0

        self._red = tparm(tigetstr('setaf'), 1).decode('utf8')
        self._green = tparm(tigetstr('setaf'), 2).decode('utf8')
        self._reset = tparm(tigetstr('sgr0')).decode('utf8')

        self._pre_test_cases = []
        self._test_cases = []
        for method in self.__ordered__:
            if method.startswith('test_'):
                self._test_cases.append(method)

    def _color(self, escape_sec, text):
        sys.stdout.write('{}{}{}\n'.format(escape_sec, text, self._reset))

    def _color_in_red(self, text):
        self._color(self._red, text)

    def _color_in_green(self, text):
        self._color(self._green, text)

    def find_by_css(self, css_selector):
        """A shortcut for self.browser.find_by_css. """

        return self.browser.find_by_css(css_selector)

    def find_by_xpath(self, xpath):
        """A shortcut for self.browser.find_by_xpath. """

        return self.browser.find_by_xpath(xpath)

    def schedule_pre_test_case(self, test_case_name):
        self._pre_test_cases.append(test_case_name)

    def schedule_test_case(self, test_case_name):
        self._test_cases.append(test_case_name)

    def run(self):
        if not self._test_cases:
            print('There is nothing to run since the number of test cases is '
                  '0.')
            return

        start_time = time.time()
        for test_case in self._pre_test_cases + self._test_cases:
            method = getattr(self, test_case)
            print('Running {}...'.format(test_case), end=' ')

            try:
                method()
                self._color_in_green('success')
                self._succeeded_number += 1
            except AssertionError:
                self._color_in_red('failed')
                _, _, tb = sys.exc_info()
                tb_info = traceback.extract_tb(tb)
                filename, line, _, text = tb_info[-1]

                print('Assertion error occurred on line {} in statement {}'.
                      format(line, text))

                self._failed_number += 1

        tests_number = len(self._test_cases)
        print('Ran {} test{} in {:.6f}s.'.format(
            tests_number,
            's' if tests_number > 1 else '',
            time.time() - start_time), end=' ')

        if self._failed_number > 0:
            self._color_in_red('Failed')
            return False

        self._color_in_green('Succeeded')

        return True


class RocketChatTestCase(SplinterTestCase):
    def __init__(self, addr, username, password, create_test_user=True,
                 **kwargs):
        SplinterTestCase.__init__(self, addr, **kwargs)

        self.schedule_pre_test_case('login')
        self.schedule_pre_test_case('test_check_version')

        if create_test_user:
            self.schedule_pre_test_case('create_user')

        self.username = username
        self.password = password
        self._rc_version = '0.69'

        self.test_username = 'noname'
        self.test_full_name = 'No Name'
        self.test_email = 'noname@nodomain.com'
        self.test_password = 'pass'

        if create_test_user:
            self.schedule_test_case('remove_user')

    def __del__(self):
        self.browser.quit()

    def check_latest_response_with_retries(self, expected_text,
                                           match=False, messages_number=1,
                                           attempts_number=30):
        for i in range(attempts_number):
            latest_msg = self.browser.driver.find_elements_by_css_selector(
                'div.body.color-primary-font-color ')

            assert len(latest_msg)

            latest_msg = latest_msg[-messages_number:]
            try:
                if match:
                    done = all([bool(re.match(expected_text, msg.text))
                                for msg in latest_msg])
                else:
                    done = all([(expected_text == msg.text)
                                for msg in latest_msg])
            except StaleElementReferenceException:
                continue

            if not done:
                time.sleep(1)
                continue

            return True

        return False

    def choose_general_channel(self):
        general_channel = self.browser.driver.find_elements_by_css_selector(
            'div.sidebar-item__ellipsis'
        )

        assert len(general_channel)

        general_channel[0].click()

    def create_user(self):
        options_btn = self.browser.find_by_css(
            '.sidebar__toolbar-button.rc-tooltip.rc-tooltip--down.js-button'
        )
        options_btn.last.click()

        administration_btn = self.browser.find_by_css('.rc-popover__item-text')
        administration_btn.click()

        users_btn = self.browser.driver.find_elements_by_css_selector(
            'a.sidebar-item__link[aria-label="Users"]')

        assert len(users_btn)

        self.browser.driver.execute_script("arguments[0].click();",
                                           users_btn[0])

        add_user_btn = self.find_by_css('button[aria-label="Add User"]')

        assert len(add_user_btn)

        add_user_btn.click()

        input_name_el = self.find_by_css('input#name')

        assert len(input_name_el)

        input_name_el.first.fill(self.test_full_name)

        input_username_el = self.find_by_css('input#username')

        assert len(input_username_el)

        input_username_el.first.fill(self.test_username)

        input_email_el = self.find_by_css('input#email')

        assert len(input_email_el)

        input_email_el.first.fill(self.test_email)

        verified_btn = self.find_by_css('label.rc-switch__label')

        assert len(verified_btn)

        verified_btn.first.click()

        input_password_el = self.find_by_css('input#password')

        assert len(input_password_el)

        input_password_el.first.fill(self.test_password)

        verified_btn = self.find_by_css('label.rc-switch__label')

        assert len(verified_btn)

        verified_btn.last.click()

        role_option = self.find_by_css('option[value="bot"]')

        assert len(role_option)

        role_option.first.click()

        add_role_btn = self.find_by_css('button#addRole')

        assert len(add_role_btn)

        add_role_btn.first.click()

        # Do not send welcome email
        welcome_ckbx = self.find_by_css('label[for="sendWelcomeEmail"]')

        assert len(welcome_ckbx)

        welcome_ckbx.first.click()

        save_btn = self.find_by_css('.rc-button.rc-button--primary.save')

        assert len(save_btn)

        save_btn.first.click()

    def login(self):
        self.browser.fill('emailOrUsername', self.username)
        self.browser.fill('pass', self.password)

        login_btn = self.find_by_css('.rc-button.rc-button--primary.login')

        assert len(login_btn)

        login_btn.click()

        welcome_text = self.browser.find_by_text('Welcome to Rocket.Chat!')

        assert len(welcome_text)

    def test_check_version(self):
        options_btn = self.browser.find_by_css(
            '.sidebar__toolbar-button.rc-tooltip.rc-tooltip--down.js-button'
        )
        assert len(options_btn)
        options_btn.last.click()

        administration_btn = self.browser.find_by_css('.rc-popover__item-text')
        assert administration_btn
        administration_btn.click()

        info_btn = self.browser.driver.find_elements_by_css_selector(
            'a.sidebar-item__link[aria-label="Info"]')

        assert len(info_btn)

        self.browser.driver.execute_script("arguments[0].click();",
                                           info_btn[0])

        info_table = self.browser.find_by_css(".admin-table-row")
        assert len(info_table)
        version = '.'.join(info_table.first.text.split()[1].split('.')[0:2])
        assert version == self._rc_version

        close_btn = self.find_by_css('button[data-action="close"]')

        assert len(close_btn)

        close_btn.click()

    def remove_user(self):
        options_btn = self.browser.driver.find_elements_by_css_selector(
            '.sidebar__toolbar-button.rc-tooltip.rc-tooltip--down.js-button')

        assert len(options_btn)

        self.browser.driver.execute_script('arguments[0].click();',
                                           options_btn[-1])

        administration_btn = self.browser.find_by_css('.rc-popover__item-text')
        administration_btn.click()

        users_btn = self.browser.driver.find_elements_by_css_selector(
            'a.sidebar-item__link[aria-label="Users"]')

        assert len(users_btn)

        self.browser.driver.execute_script("arguments[0].click();",
                                           users_btn[0])

        selected_user = self.browser.find_by_xpath(
            '//td[@class="border-component-color"][text()="{0}"]'.
            format(self.test_username))

        assert len(selected_user)

        selected_user.first.click()

        try:
            delete_btn = self.find_by_xpath(
                '//button[@class="js-action rc-user-info-action__item"]'
                '[text()="Delete"]'
            )

            assert len(delete_btn)

        except AssertionError:
            more_btn = self.find_by_css(
                'button.rc-tooltip.rc-room-actions__button.js-more'
                '[aria-label="More"]'
            )

            assert len(more_btn)

            more_btn.first.click()

            delete_btn = self.find_by_xpath(
                '//li[@class="rc-popover__item js-action"]'
                '/span[text()="Delete"]'
            )

            assert len(delete_btn)

        delete_btn.first.click()

        confirm_btn = self.find_by_css('input[value="Yes, delete it!"]')

        assert len(confirm_btn)

        confirm_btn.first.click()

        close_btn = self.browser.driver.find_elements_by_css_selector(
            'button[data-action="close"]')

        assert len(close_btn)

        self.browser.driver.execute_script('arguments[0].click();',
                                           close_btn[0])

    def send_message(self, message_text):
        self.browser.fill('msg', message_text)

        send_msg_btn = self.find_by_css('svg.rc-icon.rc-input__icon-svg.'
                                        'rc-input__icon-svg--send')

        assert len(send_msg_btn)

        send_msg_btn.first.click()
