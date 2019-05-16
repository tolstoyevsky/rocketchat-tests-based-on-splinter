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

"""Module with basic building blocks for tests. """

import collections
import os.path
import re
import sys
import time
import traceback
from curses import tparm, tigetstr, setupterm

import requests
from rocketchat_API.rocketchat import (
    RocketChat,
    RocketAuthenticationException,
    RocketConnectionException
)
from splinter import Browser
from splinter.driver.webdriver.chrome import Options
from selenium.common.exceptions import (
    NoSuchWindowException,
    StaleElementReferenceException,
    WebDriverException
)
from xvfbwrapper import Xvfb


class APIError(Exception):
    """Class for defining API errors. """

    def __init__(self, msg):
        Exception.__init__(self)

        self.msg = msg


class OrderedClassMembers(type):
    """Metaclass for producing the classes which remember the order of the
    methods added to them.
    """

    @classmethod
    def __prepare__(cls, _name, _bases):
        return collections.OrderedDict()

    def __new__(cls, name, bases, classdict):
        exception = ('__module__', '__qualname__')
        classdict['__ordered__'] = \
            [key for key in classdict.keys() if key not in exception]

        return type.__new__(cls, name, bases, classdict)


class SplinterTestCase(metaclass=OrderedClassMembers):  # pylint: disable=too-many-instance-attributes
    """Base class for all the tests based on Splinter. """

    def __init__(self, addr, browser_window_size=(1920, 1080),
                 page_load_timeout=30, sticky_timeout=30):
        setupterm()

        self.addr = addr
        self.sticky_timeout = sticky_timeout
        self.page_load_timeout = page_load_timeout
        self.browser_window_size = browser_window_size

        self._failed_number = 0
        self._succeeded_number = 0

        self._red = tparm(tigetstr('setaf'), 1).decode('utf8')
        self._green = tparm(tigetstr('setaf'), 2).decode('utf8')
        self._reset = tparm(tigetstr('sgr0')).decode('utf8')

        self._make_connections = ['connect_to_browser', ]
        self._close_connections = ['close_browser_connection', ]

        self._pre_test_cases = []
        self._test_cases = []
        self._post_test_cases = []
        for method in self.__ordered__:  # pylint: disable=no-member
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

    def make_connections(self, conn):
        """Makes specified connection. """

        self._make_connections.append(conn)

    def close_connections(self, conn):
        """Implements the graceful closing for specified connection if needed. """

        self._close_connections.append(conn)

    def schedule_pre_test_case(self, test_case_name):
        """Schedules the specified test case as a pre-test case (i.e. the test
        case which will be run before other test cases).
        """

        self._pre_test_cases.append(test_case_name)

    def schedule_test_case(self, test_case_name):
        """Schedules the specified test case which will be run in the same
        order as it appears in the class.
        """

        self._test_cases.append(test_case_name)

    def schedule_post_test_case(self, test_case_name):
        """Schedules the specified test case as a post-test case (i.e. the test
        case which will be run after other test cases).
        """

        self._post_test_cases.append(test_case_name)

    def _run(self):
        exit_code = 0

        if not self._test_cases:
            print('There is nothing to run since the number of test cases is '
                  '0.')
            return exit_code

        start_time = time.time()
        for test_case in self._pre_test_cases + \
                         self._test_cases + \
                         self._post_test_cases:
            method = getattr(self, test_case)
            print('Running {}...'.format(test_case), end=' ', flush=True)

            try:
                method()
                self._color_in_green('success')
                self._succeeded_number += 1
            except AssertionError:
                exit_code = 1
                self._color_in_red('failed')
                _, _, tbe = sys.exc_info()
                tb_info = traceback.extract_tb(tbe)
                _, line, _, text = tb_info[-1]

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
            return exit_code

        self._color_in_green('Succeeded')

        return exit_code


    def run(self):
        """Runs all the available test cases. """

        exit_code = 0

        name = re.findall('[A-Z][^A-Z]*', self.__class__.__name__)
        verbose_script_name = ' '.join(name).lower()
        print('Starting {}'.format(verbose_script_name))

        connected = self._handle_connections(self._make_connections)

        if not connected:
            exit_code = 1

            return exit_code

        try:
            ready_to_run = self._handle_env(self.setup)

            if ready_to_run:
                exit_code = self._run()
            else:
                exit_code = 1

        except KeyboardInterrupt:
            exit_code = 130
            print('\nThe process was stopped by pressing Ctrl+C.')

        except (NoSuchWindowException, WebDriverException):
            exit_code = 1
            print('\nThe process was stopped because the web driver exception has occurred.')

        except ConnectionError:
            exit_code = 1
            print('\nFailed to connect.')

        except requests.ConnectionError:
            exit_code = 1
            print('\nThe internet connection was lost')

        except APIError as error:
            exit_code = 1
            print('\nAPIError: {}'.format(error.msg))

        finally:
            self._handle_env(self.tear_down)
            self._handle_connections(self._close_connections)

            # pylint: disable=lost-exception
            return exit_code

    @staticmethod
    def _handle_env(func):
        try:
            func()

        except APIError as error:
            print('APIError: {}'.format(error.msg))

            return False

        return True

    def _handle_connections(self, connections_lst):
        for connection in connections_lst:
            method = getattr(self, connection)
            connected = method()

            if not connected:
                return False

        return True

    def connect_to_browser(self):
        """Makes connection with browser and with webdriver in case of Docker. """

        if os.path.isfile('/.docker'):
            # xvfb wrapper starting
            print('Using Xvfb')
            kwargs = {}
            if 'XVFB_WIDTH' in os.environ:
                kwargs['width'] = os.environ['XVFB_WIDTH']
            if 'XVFB_HEIGHT' in os.environ:
                kwargs['height'] = os.environ['XVFB_HEIGHT']

            # pylint: disable=attribute-defined-outside-init
            self.xvfb = Xvfb(**kwargs)
            try:
                self.xvfb.start()

            except WebDriverException:
                return False

        options = Options()
        options.add_argument('--no-sandbox')

        try:
            # pylint: disable=attribute-defined-outside-init
            self.browser = Browser('chrome', headless=False, options=options,
                                   wait_time=30,
                                   executable_path='./drivers/chromedriver')

        except ConnectionError:
            print('\nFailed to connect with browser.')
            return False

        self.browser.driver.implicitly_wait(self.sticky_timeout)
        self.browser.driver.set_page_load_timeout(self.page_load_timeout)
        self.browser.driver.set_window_size(*self.browser_window_size)
        self.browser.visit(self.addr)

        return True

    def close_browser_connection(self):
        """Provides graceful closing of browser connection in Docker. """

        if os.path.isfile('/.docker'):
            self.xvfb.stop()

        return True

    def setup(self):
        """Provides abstract setup method to be defined in test cases. """

    def tear_down(self):
        """Provides abstract tear down method to be defined in test cases. """


class RocketChatTestCase(SplinterTestCase):  # pylint: disable=too-many-instance-attributes
    """Test cases related to Rocket.Chat. """

    def __init__(self, addr, username, password, expected_rooms=None,
                 **kwargs):
        SplinterTestCase.__init__(self, addr, **kwargs)

        if expected_rooms:
            self.expected_rooms = expected_rooms.split(',')

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

    def connect_to_rc_api(self):
        """Makes connection to the RocketChat API. """

        try:
            # pylint: disable=attribute-defined-outside-init
            self.rocket = RocketChat(
                self.username,
                self.password,
                server_url=self.addr
            )

        except RocketAuthenticationException:
            print('Rocket.Chat auth error. Incorrect username or password.')
            return False

        except RocketConnectionException:
            print('Could not connect to Rocket.Chat API.')
            return False

        return True

    def delete_all_extra_users(self):
        """Deletes all users except admin with user role via Rocket.Chat API. """

        response = self.rocket.users_list().json()

        try:
            users = response['users']
            to_be_deleted = [user['_id'] for user in users if 'user' in user['roles']]

        except KeyError:
            raise APIError(response.get('error'))

        for user_id in to_be_deleted:
            self.rocket.users_delete(user_id=user_id)

    def delete_all_extra_rooms(self):
        """Deletes all groups and private channels via Rocket.Chat API
        except specified by self.expected_rooms param.
        """
        response = self.rocket.groups_list_all().json()

        try:
            groups = response['groups']
            for group in groups:
                if group['name'] not in self.expected_rooms:
                    self.rocket.groups_delete(group=group['name'])

        except KeyError:
            raise APIError(response.get('error'))

        response = self.rocket.channels_list().json()

        try:
            channels = response['channels']

            for channel in channels:
                if channel['name'] not in self.expected_rooms and not channel['default']:
                    self.rocket.channels_delete(channel=channel['name'])

        except KeyError:
            raise APIError(response.get('error'))

    def check_latest_response_with_retries(self, expected_text,
                                           match=False, messages_number=1,
                                           attempts_number=30):
        """Checks the latest response from the bot with the specified number of
        retries if needed. """

        for _ in range(attempts_number):
            latest_msg = self.browser.driver.find_elements_by_css_selector(
                'div.body.color-primary-font-color ')

            if not latest_msg:
                time.sleep(1)
                continue

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

    def get_message_by_number(self, number):
        """Fetches the message by its number. """

        messages = self.browser.driver.find_elements_by_css_selector(
            'div.body.color-primary-font-color ')
        assert len(messages) >= abs(number)
        return messages[number]

    def switch_channel(self, channel_name):
        """Switches the current channel to the specified one. """

        channels = self.browser.driver.find_elements_by_css_selector(
            'div.sidebar-item__ellipsis'
        )
        assert channels

        channel = list(
            filter(lambda elem: elem.text == channel_name, channels))
        assert len(channel) == 1

        self.browser.driver.execute_script('arguments[0].click();',
                                           channel[0])

    def choose_general_channel(self):
        """Switches the current channel to general. """

        self.switch_channel('general')

    @staticmethod
    def check_with_retries(func, *args, expected_res=True, attemps_num=30):
        """Runs the specified function and compares its return value with the
        specified one. The comparison is done with retries if needed.
        """

        for _ in range(attemps_num):
            res = func(*args)

            if res == expected_res:
                break
            else:
                time.sleep(1)
                continue

        return res

    def does_username_exist(self, username):
        """Checks if the specified username belongs to one of the users from
        the user list.
        """

        response = self.rocket.users_list().json()

        result = [
            i.get('username', None) for i in response['users']
            if i.get('username', None) == username
        ]

        return result != []

    def does_email_exist(self, email):
        """Checks if the specified email belongs to one of the users from the
        user list.
        """

        response = self.rocket.users_list().json()

        emails = []
        for i in response['users']:
            emails += i.get('emails', [])

        result = [i['address'] for i in emails if i['address'] == email]

        return result != []

    def does_room_exist(self, room_name):
        """Checks if the specified room exists. """

        response = self.rocket.rooms_get().json()

        try:
            rooms = response['update']
        except KeyError:
            raise APIError(response.get('error'))

        rooms_existing_map = []

        for room in rooms:
            rooms_existing_map.append(room_name in room.get('name', []))

        return True in rooms_existing_map

    def create_user(self):
        """Creates a test user. """

        response = self.rocket.users_register(
            email=self.test_email,
            name=self.test_full_name,
            password=self.test_password,
            username=self.test_username
            ).json()

        try:
            self.test_user_id = response['user']['_id']

        except KeyError:
            raise APIError(response.get('error'))

    def login(self, use_test_user=False):
        """Logs in into the Rocket.Chat server. """

        self.browser.fill('emailOrUsername',
                          self.test_username
                          if use_test_user else self.username)
        self.browser.fill('pass',
                          self.test_password
                          if use_test_user else self.password)

        login_btn = self.find_by_css('.rc-button.rc-button--primary.login')

        assert login_btn

        login_btn.click()

        welcome_text = self.browser.find_by_text('Welcome to Rocket.Chat!')

        assert welcome_text

    def logout(self):
        """Logs out of the Rocket.Chat server. """

        avatar = self.find_by_css('.avatar')
        assert avatar
        avatar.click()

        logout_btn = self.find_by_css('.rc-popover__item.js-action')
        assert logout_btn
        logout_btn.last.click()

    def _get_rc_version_with_retries(self, attempts_number=60):
        for _ in range(attempts_number):
            info_table = self.browser.find_by_css(".admin-table-row")

            assert info_table

            version_row = info_table.first.text
            try:
                version = '.'.join(version_row.split()[1].split('.')[0:2])
                return version
            except IndexError:
                time.sleep(1)
                continue
        return ''

    def test_check_version(self):
        """Checks if the Rocket.Chat version equals to the one the tests are
        intended for.
        """

        options_btn = self.browser.find_by_css(
            '.sidebar__toolbar-button.rc-tooltip.rc-tooltip--down.js-button'
        )
        assert options_btn
        options_btn.last.click()

        administration_btn = self.browser.find_by_css('.rc-popover__item-text')
        assert administration_btn
        administration_btn.click()

        info_btn = self.browser.driver.find_elements_by_css_selector(
            'a.sidebar-item__link[aria-label="Info"]')

        assert info_btn

        self.browser.driver.execute_script("arguments[0].click();",
                                           info_btn[0])

        version = self._get_rc_version_with_retries()

        assert version

        assert version == self._rc_version

        close_btn = self.find_by_css('button[data-action="close"]')

        assert close_btn

        close_btn.click()

    def _check_modal_window_visibility(self):
        windows = self.browser.driver.find_elements_by_class_name(
            'rc-modal__content-text')
        return not windows

    def remove_user(self):
        """Removes a test user. """

        if not self.test_user_id:
            response = self.rocket.users_list().json()
            try:
                users = response['users']
                self.test_user_id = [user['_id'] for user in users
                                     if user['username'] == self.test_username][0]

            except KeyError:
                raise APIError(response.get('error'))

        self.rocket.users_delete(user_id=self.test_user_id)

    def send_message(self, message_text):
        """Sends the specified message to the current channel. """

        self.browser.fill('msg', message_text)

        send_msg_btn = self.find_by_css('svg.rc-icon.rc-input__icon-svg.'
                                        'rc-input__icon-svg--send')

        assert send_msg_btn

        send_msg_btn.first.click()
