#!/usr/bin/env python3
# Copyright 2018 Sergei Bogolepov <s.bogolepov@wis.software>
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

"""Tests related to the hubot-happy-birthder script. """

# pylint: disable=fixme

import re
import sys
import time
from argparse import ArgumentParser
from datetime import datetime, timedelta

from selenium.webdriver.support.wait import WebDriverWait

from base import RocketChatTestCase


class HappyBirthderScriptTestCase(RocketChatTestCase):  # pylint: disable=too-many-public-methods
    """Tests for the hubot-happy-birthder script. """

    def __init__(self, addr, username, password, reminder_interval_time, **kwargs):
        RocketChatTestCase.__init__(self, addr, username, password, **kwargs)

        self.schedule_pre_test_case('choose_general_channel')

        self._reminder_interval_time = int(reminder_interval_time)

        self._test_birthday = '01.01.1990'
        self._test_incorrect_birthdays_dates = ['32.01.2000', '01.13.2000',
                                                '31.02.2000']

        self._bot_name = 'meeseeks'

        self._test_user_for_blacklist = 'test_user_for_blacklist'

        self._fwd_date = datetime.now().replace(year=datetime.now().year - 1).strftime('%d.%m.%Y')

    #
    # Private methods
    #

    @staticmethod
    def _get_date_with_shift(shift):
        return (datetime.now() + timedelta(days=shift)).strftime('%d.%m.%Y')

    @staticmethod
    def _get_channel_pattern(name, date):
        d_m = date[:-5]
        return f'{name}-birthday-channel-{d_m}-id[0-9]{{3}}'

    @staticmethod
    def _get_congratulation_pattern(username):
        pattern = (f'https?://media.tenor.com/images/[0-9a-z]*/tenor.gif\n'
                   f'Today is birthday of @{username}!\n'
                   f'[w+]*')

        return pattern

    @staticmethod
    def _get_fwd_congratulation_pattern(usernames, years_counts):
        pattern = f'.*'
        for name, count in zip(usernames, years_counts):  # pylint: disable=unused-variable
            pattern += (f'\n@{name} has been a part of our team for {count} '
                        f'{"year" if count==1 else "years"} and')

        return pattern[:-4] + "!"

    def _wait_reminder(self):
        time.sleep(self._reminder_interval_time)

    #
    # Public methods
    #

    def test_admins_birthday_set(self):
        """Tests if it's possible on behalf of the admin to set a birth date. """

        self.choose_general_channel()
        # TODO: test with invalid dates
        self.send_message('{} birthday set {} {}'.
                          format(self._bot_name, self.username,
                                 self._test_birthday))

        assert self.check_latest_response_with_retries(
            "Saving {}'s birthday.".format(self.username))

    def test_admins_birthdays_on(self):
        """Tests if it's possible on behalf of the admin to get the list of
        users with the specified birth date.
        """

        day_month = self._test_birthday[:-5]

        # TODO: test with invalid dates
        self.send_message('{} birthdays on {}'.
                          format(self._bot_name, day_month))

        assert self.check_latest_response_with_retries(
            '@{}'.format(self.username))

    def test_invoking_birthday_delete_by_admin(self):
        """Tests if it's possible on behalf of the admin to delete the
        specified birth date.
        """

        self.send_message('{} birthday delete {}'.
                          format(self._bot_name, self.username))

        assert self.check_latest_response_with_retries(
            "Removing {}'s birthday.".format(self.username))

    def test_specifying_date_birth_by_admin(self):
        """Tests if it's possible on behalf of the admin to specify their own
        birth date.
        """

        self.switch_channel(self._bot_name)
        assert self.check_latest_response_with_retries(
            'Hmm...\n'
            'It looks like you forgot to set the date of birth.\n'
            'Please enter it (DD.MM.YYYY).'
        )
        self.send_message(self._test_birthday)
        assert self.check_latest_response_with_retries(
            'I memorized you birthday, well done! 😉'
        )

    def test_specifying_date_birth_by_new_user(self):
        """Tests if it's possible on behalf of an ordinary user to specify
        their own birth date.
        """

        self.create_user()
        close_btn = self.find_by_css('button[data-action="close"]')
        assert close_btn

        close_btn.click()
        self.logout()
        self.login(use_test_user=True)
        self.switch_channel(self._bot_name)
        try:
            assert self.check_latest_response_with_retries(
                'Welcome to WIS Software! 🎉\n'
                'Emm... where was I?\n'
                'Oh! Please, enter your date birth (DD.MM.YYYY).'
            )
        except AssertionError:
            assert self.check_latest_response_with_retries(
                'Hmm...\n'
                'It looks like you forgot to set the date of birth.\n'
                'Please enter it (DD.MM.YYYY).'
            )
        self.send_message(self._test_birthday)
        assert self.check_latest_response_with_retries(
            'I memorized you birthday, well done! 😉'
        )

    def test_invoking_birthday_set_by_ordinary_user(self):
        """Test if it's not possible on behalf of an ordinary user to specify
        someone's birth date.
        """

        self.choose_general_channel()
        self.send_message('{} birthday set {} {}'.format(self._bot_name,
                                                         self.username,
                                                         self._test_birthday))

        assert self.check_latest_response_with_retries('Permission denied.')

    def test_invoking_birthday_delete_by_ordinary_user(self):
        """Test if it's not possible on behalf of an ordinary user to delete
        someone's birth date.
        """

        self.send_message('{} birthday delete {} {}'.format(
            self._bot_name, self.username, self._test_birthday))

        assert self.check_latest_response_with_retries('Permission denied.')

        self.logout()
        self.login()

    def test_creating_birthday_channel(self):
        """Tests if a birthday channel is automatically created. """

        self.choose_general_channel()
        test_date = self._get_date_with_shift(7)
        self.send_message('{} birthday set {} {}'.
                          format(self._bot_name, self.test_username,
                                 test_date))
        assert self.check_latest_response_with_retries(
            "Saving {}'s birthday.".format(self.test_username)
        )

        self._wait_reminder()
        private_channels = self.find_by_css('.rooms-list__list.type-p')

        assert private_channels

        lst_of_channels = private_channels.text.split('\n')

        assert lst_of_channels

        pattern = self._get_channel_pattern(self.test_username,
                                            self._get_date_with_shift(0))

        assert bool(re.match(pattern, lst_of_channels[-1]))

        self.switch_channel(lst_of_channels[-1])
        assert self.check_latest_response_with_retries(
            '@{} is having a birthday soon, so let\'s discuss a present.'
            .format(self.test_username)
        )

    def test_checking_absence_of_test_user_in_channel(self):
        """Tests if the user, who is having a birthday soon, is not in the birthday channel. """

        channel_options = self.find_by_css(
            '.rc-room-actions__action.tab-button.js-action')

        assert len(channel_options) >= 3

        channel_options[2].click()

        members_list = self.find_by_css('.rc-member-list__user')

        assert members_list

        assert all([member.text != self.test_username
                    for member in members_list])

    def test_reminder_of_upcoming_birthday_7_days_in_advance(self):
        """Tests the bot reminds about the upcoming birthday 7 days in advance. """

        self.switch_channel(self._bot_name)
        assert self.check_latest_response_with_retries(
            '@{} is having a birthday on {}.'
            .format(self.test_username, self._get_date_with_shift(7)[:-5])
        )

    def test_reminder_of_upcoming_birthday_1_days_in_advance(self):
        """Makes sure the bot reminds about the upcoming birthday 1 days in advance. """

        self.choose_general_channel()
        self.send_message('{} birthday set {} {}'.
                          format(self._bot_name, self.test_username,
                                 self._get_date_with_shift(1)))
        self.switch_channel(self._bot_name)
        assert self.check_latest_response_with_retries(
            '@{} is having a birthday tomorrow.'.format(self.test_username),
            attempts_number=self._reminder_interval_time
        )

    def test_deleting_birthday_channel(self):
        """Tests if a birthday channel is automatically deleted. """
        self.choose_general_channel()
        test_date = self._get_date_with_shift(-3)
        self.send_message('{} birthday set {} {}'.format(self._bot_name,
                                                         self.test_username,
                                                         test_date))

        self._wait_reminder()
        private_channels = self.find_by_css('.rooms-list__list.type-p')

        assert private_channels

        lst_of_channels = private_channels.text.split('\n')

        assert lst_of_channels

        pattern = self._get_channel_pattern(self.test_username, test_date)

        assert all([not bool(re.match(pattern, channel))
                    for channel in lst_of_channels])

    def test_birthday_message(self):
        """Makes sure the bot writes a birthday message to #general devoted to
        the user who is having a birthday.
        """

        self.choose_general_channel()
        self.send_message('{} birthday set {} {}'.
                          format(self._bot_name, self.username,
                                 self._get_date_with_shift(0)))
        pattern = self._get_congratulation_pattern(self.username)
        assert self.check_latest_response_with_retries(pattern, match=True,
                                                       attempts_number=self._reminder_interval_time)

    def test_birthdays_list_command_with_no_birthday(self):
        """Tests the case when someone is invoking 'birthdays list' but there is
        no any birth date stored.
        """

        self.send_message('{} birthday delete {}'.format(self._bot_name,
                                                         self.username))
        self.send_message('{} birthday delete {}'.format(self._bot_name,
                                                         self.test_username))
        self.send_message('{} birthdays list'.format(self._bot_name))
        assert self.check_latest_response_with_retries('Oops... No results.')


    def test_invoking_birthdays_list_with_1_birth_date(self):
        """Tests the case when someone is invoking 'birthdays list' but there is
        the only birth date stored.
        """

        self.send_message('{} birthday set {} {}'.format(self._bot_name,
                                                         self.username,
                                                         self._test_birthday))
        self.send_message('{} birthdays list'.format(self._bot_name))

        assert self.check_latest_response_with_retries(
            '*Birthdays list*\n@{} was born on {}'.format(self.username,
                                                          self._test_birthday))

    def test_invoking_birthdays_list_with_2_birth_dates(self):
        """Tests the case when someone is invoking 'birthdays list' but there
        are only 2 birth dates stored.
        """

        self.choose_general_channel()
        admins_birthday = self._get_date_with_shift(25)
        self.send_message('{} birthday set {} {}'.format(self._bot_name,
                                                         self.username,
                                                         admins_birthday))
        users_birthday = self._get_date_with_shift(20)
        self.send_message('{} birthday set {} {}'.format(self._bot_name,
                                                         self.test_username,
                                                         users_birthday))
        # test user should be first in birthdays list
        self.send_message('{} birthdays list'.format(self._bot_name))
        assert self.check_latest_response_with_retries(
            '*Birthdays list*\n'
            '@{} was born on {}\n'
            '@{} was born on {}'.format(self.test_username, users_birthday,
                                        self.username, admins_birthday))

    def test_birthday_channel_blacklist(self):  # pylint: disable=too-many-locals,too-many-statements
        """Makes sure that the user, who is in the blacklist, is not invited
        in birthday channels.
        """

        #  create user for blacklist
        options_btn = self.browser.find_by_css(
            '.sidebar__toolbar-button.rc-tooltip.rc-tooltip--down.js-button'
        )
        options_btn.last.click()

        administration_btn = self.browser.find_by_css('.rc-popover__item-text')
        administration_btn.click()

        users_btn = self.browser.driver.find_elements_by_css_selector(
            'a.sidebar-item__link[aria-label="Users"]')

        assert users_btn

        self.browser.driver.execute_script('arguments[0].click();',
                                           users_btn[0])

        add_user_btn = self.find_by_css('button[aria-label="Add User"]')

        assert add_user_btn

        add_user_btn.click()

        input_name_el = self.find_by_css('input#name')

        assert input_name_el

        input_name_el.first.fill(self._test_user_for_blacklist)

        input_username_el = self.find_by_css('input#username')

        assert input_username_el

        input_username_el.first.fill(self._test_user_for_blacklist)

        input_email_el = self.find_by_css('input#email')

        assert input_email_el

        input_email_el.first.fill(
            '{}@nodomain.com'.format(self._test_user_for_blacklist))

        verified_btn = self.find_by_css('label.rc-switch__label')

        assert verified_btn

        verified_btn.first.click()

        input_password_el = self.find_by_css('input#password')

        assert input_password_el

        input_password_el.first.fill('pass')

        verified_btn = self.find_by_css('label.rc-switch__label')

        assert verified_btn

        verified_btn.last.click()

        role_option = self.find_by_css('option[value="user"]')

        assert role_option

        role_option.first.click()

        add_role_btn = self.find_by_css('button#addRole')

        assert add_role_btn

        add_role_btn.first.click()

        welcome_ckbx = self.find_by_css('label[for="sendWelcomeEmail"]')

        assert welcome_ckbx

        welcome_ckbx.first.click()

        save_btn = self.find_by_css('.rc-button.rc-button--primary.save')

        assert save_btn

        save_btn.first.click()

        close_btn = self.find_by_css('button[data-action="close"]')

        assert close_btn

        close_btn.click()

        self.choose_general_channel()
        test_date = self._get_date_with_shift(7)
        self.send_message('{} birthday set {} {}'.
                          format(self._bot_name, self.test_username,
                                 test_date))

        self._wait_reminder()
        private_channels = self.find_by_css('.rooms-list__list.type-p')

        assert private_channels

        lst_of_channels = private_channels.text.split('\n')

        assert lst_of_channels

        self.switch_channel(lst_of_channels[-1])

        channel_options = self.find_by_css(
            '.rc-room-actions__action.tab-button.js-action')

        assert len(channel_options) >= 3

        channel_options[2].click()

        members_list = self.find_by_css('.rc-member-list__user')

        assert len(members_list) == 2

        self.choose_general_channel()
        # for deleting birthdays chat
        test_date = self._get_date_with_shift(-3)
        self.send_message('{} birthday set {} {}'.
                          format(self._bot_name, self.test_username,
                                 test_date))

        self._wait_reminder()

        self.send_message('{} birthday delete {}'.
                          format(self._bot_name, self.test_username))
        self.send_message('{} birthday delete {}'.
                          format(self._bot_name, self.test_username))

        options_btn = self.browser.driver.find_elements_by_css_selector(
            '.sidebar__toolbar-button.rc-tooltip.rc-tooltip--down.js-button')

        assert options_btn

        self.browser.driver.execute_script('arguments[0].click();',
                                           options_btn[-1])

        administration_btn = self.browser.find_by_css('.rc-popover__item-text')
        administration_btn.click()

        users_btn = self.browser.driver.find_elements_by_css_selector(
            'a.sidebar-item__link[aria-label="Users"]')

        assert users_btn

        self.browser.driver.execute_script('arguments[0].click();',
                                           users_btn[0])

        selected_user = self.browser.find_by_xpath(
            '//td[@class="border-component-color"][text()="{0}"]'
            .format(self._test_user_for_blacklist))

        assert selected_user

        selected_user.first.click()

        try:
            delete_btn = self.find_by_xpath(
                '//button[@class="js-action rc-user-info-action__item"]'
                '[text()="Delete"]'
            )

            assert delete_btn

        except AssertionError:
            more_btn = self.find_by_css(
                'button.rc-tooltip.rc-room-actions__button.js-more'
                '[aria-label="More"]'
            )

            assert more_btn

            more_btn.first.click()

            delete_btn = self.find_by_xpath(
                '//li[@class="rc-popover__item js-action"]'
                '/span[text()="Delete"]'
            )

            assert delete_btn

        delete_btn.first.click()

        confirm_btn = self.find_by_css('input[value="Yes, delete it!"]')

        assert confirm_btn

        confirm_btn.first.click()

        WebDriverWait(self.browser.driver, 10).until(
            lambda _: self._check_modal_window_visibility())

        close_btn = self.browser.driver.find_elements_by_css_selector(
            'button[data-action="close"]')

        assert close_btn

        self.browser.driver.execute_script('arguments[0].click();',
                                           close_btn[0])

    def test_fwd_set_for_admin(self):
        """Tests if it's possible on behalf of the admin to specify a first
        working date for a user.
        """

        self.switch_channel(self._bot_name)
        self.send_message('{} fwd set {} {}'.
                          format(self._bot_name, self.username,
                                 self._fwd_date))

        assert self.check_latest_response_with_retries(
            "Saving {}'s first working day.".format(self.username))

    def test_fwd_reminder_for_admin(self):
        """Makes sure the bot writes a message to #general containing a
        congratulation on the work anniversary (the case when there is
        the only user celebrating the work anniversary).
        """

        self.choose_general_channel()

        assert self.check_latest_response_with_retries(
            self._get_fwd_congratulation_pattern([self.username, ], [1, ]),
            match=True, attempts_number=80)

    def test_fwd_reminder_for_new_user(self):
        """Makes sure the bot writes a message to #general containing a
        congratulation on the work anniversary (the case when there are
        two users celebrating the work anniversary).
        """

        self.switch_channel(self._bot_name)
        self.send_message('{} fwd set {} {}'.
                          format(self._bot_name, self.test_username,
                                 self._fwd_date))

        assert self.check_latest_response_with_retries(
            "Saving {}'s first working day.".format(self.test_username))

        self.choose_general_channel()

        users = [self.username, self.test_username]
        assert self.check_latest_response_with_retries(
            self._get_fwd_congratulation_pattern(users, [1, 1]),
            match=True,
            attempts_number=self._reminder_interval_time)

    def test_fwd_list(self):
        """Tests the case when someone is invoking 'fwd list' but there are
        only 2 dates stored.
        """

        self.switch_channel(self._bot_name)
        self.send_message('{} fwd list'.format(self._bot_name))

        assert self.check_latest_response_with_retries(
            '*First working days list*\n'
            '@{} joined our team {}\n'
            '@{} joined our team {}'.format(self.username, self._fwd_date,
                                            self.test_username,
                                            self._fwd_date),
            attempts_number=self._reminder_interval_time)
        self.remove_user()

        self.switch_channel(self._bot_name)
        self.send_message('{} fwd list'.format(self._bot_name))
        assert self.check_latest_response_with_retries(
            '*First working days list*\n'
            '@{} joined our team {}'.format(self.username, self._fwd_date),
            attempts_number=self._reminder_interval_time)


def main():
    """The main entry point. """

    parser = ArgumentParser(description='usage: %prog [options] arguments')
    parser.add_argument('-a', '--host', dest='host', type=str,
                        help='allows specifying domain or IP of the Rocket.Chat host')
    parser.add_argument('-u', '--username', dest='username', type=str,
                        help='allows specifying admin username')
    parser.add_argument('-p', '--password', dest='password', type=str,
                        help='allows specifying admin password')
    parser.add_argument('-w', '--wait', dest='wait', type=int,
                        help="allows specifying time "
                             "for waiting reminder\'s work(secs)")

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

    if not options.wait:
        options.wait = '100'
        sys.stderr.write(
            'Waiting time is not specified. Defaults to {}.\n'.format(options.wait)
        )

    test_cases = HappyBirthderScriptTestCase(options.host, options.username,
                                             options.password,
                                             reminder_interval_time=options.wait,
                                             create_test_user=False)
    exit_code = test_cases.run()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
