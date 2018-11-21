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
import uuid
from optparse import OptionParser

from base import RocketChatTestCase

import pyperclip
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait


class GeneralTestCase(RocketChatTestCase):
    def __init__(self, addr, username, password, **kwargs):
        RocketChatTestCase.__init__(self, addr, username, password, **kwargs)

        self._test_string = 'Test string'
        self._base_dividing_message = 'Cat from clipboard'
        self._file_url = os.path.join(os.getcwd(), 'static', 'cat.gif')

        self._public_channel_name = '{}_{}'.format(
            'public_test_channel', uuid.uuid4())

        self._private_channel_name = '{}_{}'.format(
            'private_test_channel', uuid.uuid4())

        self._read_only_channel_name = '{}_{}'.format(
            'read_only_test_channel', uuid.uuid4())

        self._non_unique_channel_name = 'test_channel'

        self.schedule_test_case('_delete_channels')

    def _delete_channels(self):
        options_btn = self.browser.driver.find_elements_by_css_selector(
            '.sidebar__toolbar-button.rc-tooltip.rc-tooltip--down.js-button')

        assert len(options_btn)

        self.browser.driver.execute_script('arguments[0].click();',
                                           options_btn[-1])

        administration_btn = self.browser.find_by_css('.rc-popover__item-text')
        administration_btn.click()

        rooms_btn = self.browser.driver.find_elements_by_css_selector(
            'a.sidebar-item__link[aria-label="Rooms"]')

        assert len(rooms_btn)

        self.browser.driver.execute_script("arguments[0].click();",
                                           rooms_btn[0])

        selected_room = self.browser.find_by_xpath(
            '//td[@class="border-component-color"][text()="{0}"]'.format(
                self._public_channel_name))

        assert len(selected_room)

        selected_room.click()

        delete_btn = self.browser.driver.find_element_by_class_name('button')

        assert delete_btn

        delete_btn.click()

        confirm_btn = self.find_by_css('input[value="Yes, delete it!"]')

        assert len(confirm_btn)

        confirm_btn.first.click()

        WebDriverWait(self.browser.driver, 10).until(
            lambda _: self._check_modal_window_visibility())

        selected_room = self.browser.find_by_xpath(
            '//td[@class="border-component-color"][text()="{0}"]'.format(
                self._private_channel_name))

        assert len(selected_room)

        selected_room.click()

        delete_btn = self.browser.driver.find_element_by_class_name('button')

        assert delete_btn

        delete_btn.click()

        confirm_btn = self.find_by_css('input[value="Yes, delete it!"]')

        assert len(confirm_btn)

        confirm_btn.first.click()

        WebDriverWait(self.browser.driver, 10).until(
            lambda _: self._check_modal_window_visibility())

        selected_room = self.browser.find_by_xpath(
            '//td[@class="border-component-color"][text()="{0}"]'.format(
                self._read_only_channel_name))

        assert len(selected_room)

        selected_room.click()

        delete_btn = self.browser.driver.find_element_by_class_name('button')

        assert delete_btn

        delete_btn.click()

        confirm_btn = self.find_by_css('input[value="Yes, delete it!"]')

        assert len(confirm_btn)

        confirm_btn.first.click()

        close_btn = self.browser.driver.find_elements_by_css_selector(
            'button[data-action="close"]')

        assert len(close_btn)

        self.browser.driver.execute_script('arguments[0].click();',
                                           close_btn[0])

    def _check_elem_disabled_state(self, elem):
        act = elem._element.get_attribute('disabled')
        return not act

    def _check_modal_window_visibility(self):
        windows = self.browser.driver.find_elements_by_class_name(
            'rc-modal__content-text')
        return not windows

    def _check_hiding_toast_message(self):
        toast_message = self.find_by_css(
            '.toast-message')
        return not toast_message

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

    def test_starring_messages(self):
        WebDriverWait(self.browser.driver, 10).until(
            lambda _: self._check_hiding_toast_message())
        search_btn = self.browser.find_by_css(
            '.sidebar__toolbar-button.rc-tooltip.rc-tooltip--down.js-button'
        )

        assert len(search_btn)

        search_btn.first.click()

        search = self.browser.find_by_css('.rc-input__element')

        assert len(search)

        search.first.fill(self.username)

        chanels = self.browser.find_by_css('.sidebar-item.popup-item')

        assert len(chanels)

        chanels.first.click()

        self.send_message(self._test_string)

        test_message = self.find_by_css(
            'div.body.color-primary-font-color ')

        assert len(test_message)

        test_message.last.mouse_over()
        actions_menu = self.find_by_css('.message-actions__menu')

        assert len(actions_menu)

        actions_menu.last.click()

        menu_items = self.find_by_css('.rc-popover__item')

        assert len(menu_items) == 8

        assert menu_items[5].text == 'Star Message'

        menu_items[5].click()

        room_menu = self.find_by_css('.rc-room-actions__action')

        assert len(room_menu)

        room_menu.last.click()

        starred_messages = self.find_by_css('.rc-popover__item.js-action')

        assert len(starred_messages)

        starred_messages.first.click()

        starred_message = self.find_by_css(
            '.message.background-transparent-dark-hover.own.starred.new-day')

        assert len(starred_message)

        assert starred_message.first.text.split('\n')[1] == self._test_string

        close_button = self.find_by_css(
            '.contextual-bar__header-close.js-close')

        assert len(close_button)

        close_button.first.click()

    def test_unstarring_messages(self):
        test_message = self.find_by_css(
            'div.body.color-primary-font-color ')

        assert len(test_message)

        test_message.last.mouse_over()
        actions_menu = self.find_by_css('.message-actions__menu')

        assert len(actions_menu)

        actions_menu.last.click()

        menu_items = self.find_by_css('.rc-popover__item')

        assert len(menu_items) == 8

        assert menu_items[5].text == 'Remove Star'

        menu_items[5].click()

        room_menu = self.find_by_css('.rc-room-actions__action')

        assert len(room_menu)

        room_menu.last.click()

        starred_messages = self.find_by_css('.rc-popover__item.js-action')

        assert len(starred_messages)

        starred_messages.first.click()

        starred_messages_list = self.find_by_css(
            '.list-view.starred-messages-list.flex-tab__header')

        assert len(starred_messages_list)

        assert starred_messages_list.first.text == 'No starred messages'

        close_button = self.find_by_css(
            '.contextual-bar__header-close.js-close')

        assert len(close_button)

        close_button.first.click()

    def test_creating_public_channel(self):
        create_channel_btn = self.browser.find_by_css(
            '.sidebar__toolbar-button.rc-tooltip.rc-tooltip--down.js-button')

        assert len(create_channel_btn) >= 2

        create_channel_btn[-2].click()

        channel_options = self.find_by_css('label.rc-switch__label')

        assert len(channel_options) >= 3

        channel_options.first.click()

        channel_name = self.browser.find_by_name('name')

        assert len(channel_name)

        channel_name.first.fill(self._public_channel_name)

        create_btn = self.find_by_css('.rc-button.rc-button--primary')

        assert len(create_btn)

        WebDriverWait(self.browser.driver, 10).until(
            lambda _: self._check_elem_disabled_state(create_btn))

        create_btn.first.click()

        channel_header = self.browser.driver.find_element_by_class_name(
            'rc-header__name')

        assert channel_header

        assert channel_header.text == self._public_channel_name

    def test_accessibility_of_public_channel(self):
        self.logout()
        self.login(use_test_user=True)
        search_btn = self.browser.find_by_css(
            '.sidebar__toolbar-button.rc-tooltip.rc-tooltip--down.js-button'
        )

        assert len(search_btn)

        search_btn.first.click()

        search = self.browser.find_by_css('.rc-input__element')

        assert len(search)

        search.first.fill(self._public_channel_name)

        chanels = self.browser.find_by_css('.sidebar-item.popup-item')

        assert len(chanels)

        chanels.last.click()

        join_btn = self.browser.find_by_css('.button.join')

        assert len(join_btn)

        join_btn.first.click()

        assert self.check_latest_response_with_retries(
            'Has joined the channel.')

    def test_leaving_public_channel(self):
        WebDriverWait(self.browser.driver, 10).until(
            lambda _: self._check_hiding_toast_message())
        room_actions = self.browser.find_by_css(
            '.rc-tooltip.rc-tooltip--down.rc-room-actions__button')

        assert len(room_actions)

        room_actions.first.click()

        leave_button = self.browser.find_by_css(
            '.rc-button.rc-button--icon'
            '.rc-button--outline.rc-button--cancel.js-leave')

        assert len(leave_button)

        leave_button.first.click()

        confirm_btn = self.find_by_css('input[value="Yes, leave it!"]')

        assert len(confirm_btn)

        confirm_btn.first.click()

        self.logout()
        self.login()

    def test_creating_private_channel(self):
        create_channel_btn = self.browser.find_by_css(
            '.sidebar__toolbar-button.rc-tooltip.rc-tooltip--down.js-button')

        assert len(create_channel_btn) >= 2

        create_channel_btn[-2].click()

        channel_name = self.browser.find_by_name('name')

        assert len(channel_name)

        channel_name.first.fill(self._private_channel_name)

        create_btn = self.find_by_css('.rc-button.rc-button--primary')

        assert len(create_btn)

        WebDriverWait(self.browser.driver, 10).until(
            lambda _: self._check_elem_disabled_state(create_btn))

        create_btn.first.click()

        channel_header = self.browser.driver.find_element_by_class_name(
            'rc-header__name')

        assert channel_header

        assert channel_header.text == self._private_channel_name

    def test_inaccessibility_of_private_channel(self):
        self.logout()
        self.login(use_test_user=True)

        search_btn = self.browser.find_by_css(
            '.sidebar__toolbar-button.rc-tooltip.rc-tooltip--down.js-button'
        )

        assert len(search_btn)

        search_btn.first.click()

        search = self.browser.find_by_css('.rc-input__element')

        assert len(search)

        search.first.fill(self._private_channel_name)

        channels = self.browser.find_by_css('.sidebar-item.popup-item')

        assert not len(channels)

        close_btn = self.browser.find_by_css(
            '.rc-input__icon.rc-input__icon--right')

        assert close_btn

        if close_btn.first.visible:
            close_btn.first.click()

        self.logout()
        self.login()

    def test_creating_read_only_channel(self):
        create_channel_btn = self.browser.find_by_css(
            '.sidebar__toolbar-button.rc-tooltip.rc-tooltip--down.js-button')

        assert len(create_channel_btn) >= 2

        create_channel_btn[-2].click()

        channel_options = self.find_by_css('label.rc-switch__label')

        assert len(channel_options) >= 3

        channel_options.first.click()

        channel_options[1].click()

        channel_name = self.browser.find_by_name('name')

        assert len(channel_name)

        channel_name.first.fill(self._read_only_channel_name)

        create_btn = self.find_by_css('.rc-button.rc-button--primary')

        assert len(create_btn)

        WebDriverWait(self.browser.driver, 10).until(
            lambda _: self._check_elem_disabled_state(create_btn))

        create_btn.first.click()

        channel_header = self.browser.driver.find_element_by_class_name(
            'rc-header__name')

        assert channel_header

        assert channel_header.text == self._read_only_channel_name

    def test_sending_message_to_read_only_channel_from_creator(self):
        self.send_message(self._test_string)

        self.check_latest_response_with_retries(self._test_string)

    def test_joining_read_only_channel(self):
        self.logout()
        self.login(use_test_user=True)
        search_btn = self.browser.find_by_css(
            '.sidebar__toolbar-button.rc-tooltip.rc-tooltip--down.js-button'
        )

        assert len(search_btn)

        search_btn.first.click()

        search = self.browser.find_by_css('.rc-input__element')

        assert len(search)

        search.first.fill(self._read_only_channel_name)

        channels = self.browser.find_by_css('.sidebar-item.popup-item')

        assert len(channels)

        channels.last.click()

        join_btn = self.browser.find_by_css('.button.join')

        assert len(join_btn)

        join_btn.first.click()

        channel_options = self.find_by_css(
            ".rc-room-actions__action.tab-button.js-action")

        assert len(channel_options) >= 3

        channel_options[2].click()

        members_list = self.find_by_css('.rc-member-list__user')

        assert len(members_list)

        assert members_list.last.text == self.test_username

    # TODO: change the test when https://github.com/RocketChat/Rocket.Chat/issues/11819 is fixed.
    def test_read_only_channel_with_allowed_reacting(self):
        test_message = self.find_by_css(
            'div.body.color-primary-font-color ')

        assert len(test_message)

        test_message.first.mouse_over()

        add_reaction = self.find_by_css('.message-actions__button')

        assert not len(add_reaction)

    def test_read_only_channel_with_disallowed_reacting(self):
        self.logout()
        self.login()
        self.switch_channel(self._read_only_channel_name)
        info_button = self.find_by_css(
            '.rc-tooltip.rc-tooltip--down.rc-room-actions__button')

        assert len(info_button)

        info_button.first.click()

        edit_button = self.find_by_css(
            '.rc-button.rc-button--icon.rc-button--outline.js-edit')

        assert len(edit_button)

        edit_button.first.click()

        reacting = self.find_by_css('label.rc-switch__label')

        assert len(reacting) >= 3

        reacting[2].click()

        save_button = self.find_by_css(
            '.rc-button.rc-button--primary.js-save')

        assert len(save_button)

        save_button.first.click()

        self.logout()
        self.login(use_test_user=True)

        self.switch_channel(self._read_only_channel_name)

        test_message = self.find_by_css(
            'div.body.color-primary-font-color ')

        assert len(test_message)

        test_message.first.mouse_over()

        add_reaction = self.find_by_css('.message-actions__button')

        assert len(add_reaction)

        add_reaction.first.click()

        emoji = self.find_by_css('.emoji-grinning')

        assert len(emoji)

        emoji.first.click()

        reaction = self.find_by_css('.reaction-emoji')

        assert len(reaction)

        assert reaction.text == '😀'

    def test_read_accessibility_of_read_only_channel(self):
        self.check_latest_response_with_retries(self._test_string)

    def test_write_inaccessibility_of_read_only_channel(self):
        stream_info = self.find_by_css('.stream-info')

        assert len(stream_info)

        assert stream_info.first.text == 'This room is read only'

        self.logout()
        self.login()

    # TODO: change the test when https://github.com/RocketChat/Rocket.Chat/issues/12059 is closed.
    def test_recreating_channel_with_same_name(self):
        #  create
        create_channel_btn = self.browser.find_by_css(
            '.sidebar__toolbar-button.rc-tooltip.rc-tooltip--down.js-button')

        assert len(create_channel_btn) >= 2

        create_channel_btn[-2].click()

        channel_options = self.find_by_css('label.rc-switch__label')

        assert len(channel_options) >= 3

        channel_options.first.click()

        channel_name = self.browser.find_by_name('name')

        assert len(channel_name)

        channel_name.first.fill(self._non_unique_channel_name)

        create_btn = self.find_by_css('.rc-button.rc-button--primary')

        assert len(create_btn)

        WebDriverWait(self.browser.driver, 10).until(
            lambda _: self._check_elem_disabled_state(create_btn))

        create_btn.first.click()
        #  delete
        options_btn = self.browser.driver.find_elements_by_css_selector(
            '.sidebar__toolbar-button.rc-tooltip.rc-tooltip--down.js-button')

        assert len(options_btn)

        self.browser.driver.execute_script('arguments[0].click();',
                                           options_btn[-1])

        administration_btn = self.browser.find_by_css('.rc-popover__item-text')
        administration_btn.click()

        rooms_btn = self.browser.driver.find_elements_by_css_selector(
            'a.sidebar-item__link[aria-label="Rooms"]')

        assert len(rooms_btn)

        self.browser.driver.execute_script("arguments[0].click();",
                                           rooms_btn[0])

        selected_room = self.browser.find_by_xpath(
            '//td[@class="border-component-color"][text()="{0}"]'.format(
                self._non_unique_channel_name))

        assert len(selected_room)

        selected_room.click()

        delete_btn = self.browser.driver.find_element_by_class_name('button')

        assert delete_btn

        delete_btn.click()

        confirm_btn = self.find_by_css('input[value="Yes, delete it!"]')

        assert len(confirm_btn)

        confirm_btn.first.click()

        WebDriverWait(self.browser.driver, 10).until(
            lambda _: self._check_modal_window_visibility())

        close_btn = self.browser.driver.find_elements_by_css_selector(
            'button[data-action="close"]')

        assert len(close_btn)

        self.browser.driver.execute_script('arguments[0].click();',
                                           close_btn[0])
        #  create
        create_channel_btn = self.browser.find_by_css(
            '.sidebar__toolbar-button.rc-tooltip.rc-tooltip--down.js-button')

        assert len(create_channel_btn) >= 2

        create_channel_btn[-2].click()

        channel_options = self.find_by_css('label.rc-switch__label')

        assert len(channel_options) >= 3

        channel_options.first.click()

        channel_name = self.browser.find_by_name('name')

        assert len(channel_name)

        channel_name.first.fill(self._non_unique_channel_name)

        create_btn = self.find_by_css('.rc-button.rc-button--primary')

        assert len(create_btn)

        WebDriverWait(self.browser.driver, 10).until(
            lambda _: self._check_elem_disabled_state(create_btn))

        create_btn.first.click()

        msg_box = self.find_by_css('.rc-message-box.rc-new')
        assert len(msg_box)
        #  check non correct behavior
        assert msg_box.first.text == \
               'You are in preview mode of channel #{} JOIN'.format(
                   self._non_unique_channel_name)
        pass
        #  delete
        options_btn = self.browser.driver.find_elements_by_css_selector(
            '.sidebar__toolbar-button.rc-tooltip.rc-tooltip--down.js-button')

        assert len(options_btn)

        self.browser.driver.execute_script('arguments[0].click();',
                                           options_btn[-1])

        administration_btn = self.browser.find_by_css('.rc-popover__item-text')
        administration_btn.click()

        rooms_btn = self.browser.driver.find_elements_by_css_selector(
            'a.sidebar-item__link[aria-label="Rooms"]')

        assert len(rooms_btn)

        self.browser.driver.execute_script("arguments[0].click();",
                                           rooms_btn[0])

        selected_room = self.browser.find_by_xpath(
            '//td[@class="border-component-color"][text()="{0}"]'.format(
                self._non_unique_channel_name))

        assert len(selected_room)

        selected_room.click()

        delete_btn = self.browser.driver.find_element_by_class_name('button')

        assert delete_btn

        delete_btn.click()

        confirm_btn = self.find_by_css('input[value="Yes, delete it!"]')

        assert len(confirm_btn)

        confirm_btn.first.click()

        WebDriverWait(self.browser.driver, 10).until(
            lambda _: self._check_modal_window_visibility())

        close_btn = self.browser.driver.find_elements_by_css_selector(
            'button[data-action="close"]')

        assert len(close_btn)

        self.browser.driver.execute_script('arguments[0].click();',
                                           close_btn[0])

    def test_pasting_string_from_clipboard(self):
        self.choose_general_channel()
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
                                 options.password, create_test_user=True)
    test_cases.run()


if __name__ == '__main__':
    main()
