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

import requests
from rocketchat_API.rocketchat import RocketChat
from splinter import Browser
from selenium.common.exceptions import (
    NoSuchWindowException,
    StaleElementReferenceException,
    WebDriverException
)
from selenium.webdriver.support.wait import WebDriverWait


class APIError(Exception):
    def __init__(self, msg):
        self.msg = msg


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
        self._post_test_cases = []
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

    def _run(self):
        if not self._test_cases:
            print('There is nothing to run since the number of test cases is '
                  '0.')
            return

        start_time = time.time()
        for test_case in self._pre_test_cases + self._test_cases:
            method = getattr(self, test_case)
            print('Running {}...'.format(test_case), end=' ', flush=True)

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


    def run(self):
        try:
            ready_to_run = self.handle_env(self.setup)
            if ready_to_run:
                self._run()

        except KeyboardInterrupt:
            print('\nThe process was stopped by pressing Ctrl+C.')
            
        except (NoSuchWindowException, WebDriverException):
            print('\nThe process was stopped, because the browser was closed.')

        except requests.ConnectionError:
            print('\nThe internet connection was lost')

        except APIError as e:
            print('\nAPIError: {}'.format(e.msg))

        finally:
            self.handle_env(self.tear_down)

    @staticmethod
    def handle_env(func):
        print('Starting {}...'.format(func.__name__))
        try:
            func()

        except APIError as e:
            print('{} failed.'.format(func.__name__.capitalize()))
            print('APIError: {}'.format(e.msg))

            return False

        print('{} done.'.format(func.__name__.capitalize()))

        return True

    def setup(self):
        pass

    def tear_down(self):
        pass


class RocketChatTestCase(SplinterTestCase):
    def __init__(self, addr, username, password, expected_groups=None, **kwargs):
        SplinterTestCase.__init__(self, addr, **kwargs)

        self.rocket = RocketChat(username, password, server_url=addr)

        if expected_groups:
            self.expected_groups = expected_groups.split(',')

        self.schedule_pre_test_case('login')
        self.schedule_pre_test_case('test_check_version')

        self.username = username
        self.password = password
        self._rc_version = '0.70'

        self.test_user_id = None
        self.test_username = 'noname'
        self.test_full_name = 'No Name'
        self.test_email = 'noname@nodomain.com'
        self.test_password = 'pass'

    def __del__(self):
        self.browser.quit()

    def delete_all_extra_users(self):
        all = self.rocket.users_list().json()
        to_be_deleted = [i['_id'] for i in all['users'] if 'user' in i['roles']]

        for user_id in to_be_deleted:
            self.rocket.users_delete(user_id=user_id)

    def delete_all_extra_groups(self):
        all = self.rocket.groups_list_all().json()
        to_be_deleted = \
            [i['name'] for i in all['groups'] if i['name'] not in self.expected_groups]

        for group_name in to_be_deleted:
            self.rocket.groups_delete(group=group_name)

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

    def switch_channel(self, channel_name):
        channels = self.browser.driver.find_elements_by_css_selector(
            'div.sidebar-item__ellipsis'
        )
        assert len(channels)

        channel = list(
            filter(lambda elem: elem.text == channel_name, channels))
        assert len(channel) == 1

        self.browser.driver.execute_script('arguments[0].click();',
                                           channel[0])

    def choose_general_channel(self):
        self.switch_channel('general')

    def check_with_retries(self, func, *args, expected_res=True, attemps_num=30):
        for i in range(attemps_num):
            res = func(*args)

            if res == expected_res:
                break
            else:
                continue

        return res

    def does_username_exist(self, username):
        response = self.rocket.users_list().json()

        result = [
            i.get('username', None) for i in response['users']
            if i.get('username', None) == username
        ]

        return result != []

    def does_email_exist(self, email):
        response = self.rocket.users_list().json()

        emails = []
        for i in response['users']:
            emails += i.get('emails', [])

        result = [i['address'] for i in emails if i['address'] == email]

        return result != []


    def create_user(self):
        response = self.rocket.users_register(
            email=self.test_email,
            name=self.test_full_name,
            password=self.test_password,
            username=self.test_username
            ).json()

        if not response['success']:
            raise APIError(response['error'])

        self.test_user_id = response['user']['_id']

    def login(self, use_test_user=False):
        self.browser.fill('emailOrUsername',
                          self.test_username
                          if use_test_user else self.username)
        self.browser.fill('pass',
                          self.test_password
                          if use_test_user else self.password)

        login_btn = self.find_by_css('.rc-button.rc-button--primary.login')

        assert len(login_btn)

        login_btn.click()

        welcome_text = self.browser.find_by_text('Welcome to Rocket.Chat!')

        assert len(welcome_text)

    def logout(self):
        avatar = self.find_by_css('.avatar')
        assert avatar
        avatar.click()

        logout_btn = self.find_by_css('.rc-popover__item.js-action')
        assert logout_btn
        logout_btn.last.click()

    def _get_rc_version_with_retries(self, attempts_number=60):
        for _ in range(attempts_number):
            info_table = self.browser.find_by_css(".admin-table-row")

            assert len(info_table)

            version_row = info_table.first.text
            try:
                version = '.'.join(version_row.split()[1].split('.')[0:2])
                return version
            except IndexError:
                time.sleep(1)
                continue
        return ''

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

        version = self._get_rc_version_with_retries()

        assert version

        assert version == self._rc_version

        close_btn = self.find_by_css('button[data-action="close"]')

        assert len(close_btn)

        close_btn.click()

    def _check_modal_window_visibility(self):
        windows = self.browser.driver.find_elements_by_class_name(
            'rc-modal__content-text')
        return not windows

    def remove_user(self):
        if not self.test_user_id:
            response = self.rocket.users_list().json()
            self.test_user_id = [
                i.get('_id', None) for i in response['users']
                if i.get('username', None) == self.test_username
            ][0]

        self.rocket.users_delete(user_id=self.test_user_id)

    def send_message(self, message_text):
        self.browser.fill('msg', message_text)

        send_msg_btn = self.find_by_css('svg.rc-icon.rc-input__icon-svg.'
                                        'rc-input__icon-svg--send')

        assert len(send_msg_btn)

        send_msg_btn.first.click()
