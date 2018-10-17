#!/usr/bin/env python3
# Copyright 2018 Anton Maksimovich <antonio.maksimovich@gmail.com>
# Copyright 2018 Simon Suprun <simonsuprun@gmail.com>
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

from datetime import datetime, timedelta
from optparse import OptionParser

from base import RocketChatTestCase


class VivaLasVegasScriptTestCase(RocketChatTestCase):
    def __init__(self, addr, username, password, **kwargs):
        RocketChatTestCase.__init__(self, addr, username, password, **kwargs)

        self.schedule_pre_test_case('choose_general_channel')

        self._bot_name = 'meeseeks'

        self._vacation_start_date = (datetime.now() + timedelta(days=15)).strftime('%d.%m')

        self._too_close_start_date = (datetime.now() + timedelta(days=1)).strftime('%d.%m')

        self._vacation_end_date = (datetime.now() + timedelta(days=29)).strftime('%d.%m')

        self._too_long_end_date = (datetime.now() + timedelta(days=44)).strftime('%d.%m')

        self._invalid_dates = ('99.99', '31.09', '30.02')

    def _send_vacation_request(self):
        self.send_message('{} хочу в отпуск'.format(self._bot_name))
        assert self.check_latest_response_with_retries(
            'Ok, с какого числа? (дд.мм)')

        self.send_message('{} хочу в отпуск'.format(self._bot_name))
        assert self.check_latest_response_with_retries(
            'Давай по порядку!\nC какого числа ты хочешь уйти в отпуск? (дд.мм)')

    def _input_start_date(self):
        for date in self._invalid_dates:
            self.send_message('{0} {1}'.format(self._bot_name, date))
            assert self.check_latest_response_with_retries(
                'Указанная дата является невалидной. Попробуй еще раз.')

        self.send_message('{0} {1}'.format(self._bot_name, self._too_close_start_date))
        assert self.check_latest_response_with_retries(
            'Нужно запрашивать отпуск минимум за 14 дней, а до твоего - только 0 дней. '
            'Попробуй выбрать дату позднее %s.' % (datetime.now() + timedelta(days=14)).strftime('%d.%m.%Y'))

        self.send_message('{0} {1}'.format(self._bot_name, self._vacation_start_date))
        assert self.check_latest_response_with_retries('Отлично, по какое? (дд.мм)')

    def _input_end_date(self):
        for date in self._invalid_dates:
            self.send_message('{0} {1}'.format(self._bot_name, date))
            assert self.check_latest_response_with_retries(
                'Указанная дата является невалидной. Попробуй еще раз.')

        self.send_message('{0} {1}'.format(self._bot_name, self._too_long_end_date))
        assert self.check_latest_response_with_retries(
            'Отпуск продолжительностью 29 дней выглядит круто (особенно если он оплачиваемый 😂), '
            'но ты можешь претендовать максимум на 28 дней.')

        self.send_message('{0} {1}'.format(self._bot_name, self._vacation_end_date))
        assert self.check_latest_response_with_retries('Значит ты планируешь находиться в отпуске 14 дней. '
                                                       'Все верно? (да/нет)')

    def _confirm_dates(self, confirm=True):
        self.send_message('{0} {1}'.format(self._bot_name, 'да' if confirm else 'нет'))
        assert self.check_latest_response_with_retries(
            'Заявка на отпуск отправлена. Ответ поступит не позже чем через 7 дней.'
            if confirm
            else 'Я прервал процесс формирования заявки на отпуск.')

    def _approve_vacation(self, is_admin=True):
        self.send_message('{0} одобрить заявку @{1}'.format(self._bot_name, self.username))
        if is_admin:
            assert self.check_latest_response_with_retries(
                "Заявка @{} одобрена. Я отправлю ему уведомление об этом.".format(self.username))
        else:
            assert self.check_latest_response_with_retries(
                'У тебя недостаточно прав для этой команды 🙄')

    def _reject_vacation(self, is_admin=True):
        self.send_message('{0} отклонить заявку @{1}'.format(self._bot_name, self.username))
        if is_admin:
            assert self.check_latest_response_with_retries(
                "Заявка @{} отклонена. Я отправлю ему уведомление об этом.".format(self.username))
        else:
            assert self.check_latest_response_with_retries(
                'У тебя недостаточно прав для этой команды 🙄')

    def _cancel_vacation(self, is_admin=True):
        self.send_message('{0} отменить заявку @{1}'.format(self._bot_name, self.username))
        if is_admin:
            assert self.check_latest_response_with_retries(
                "Отпуск пользователя @{} отменен.".format(self.username))
        else:
            assert self.check_latest_response_with_retries(
                'У тебя недостаточно прав для этой команды 🙄')

    def test_viva_las_vegas_with_approve(self):
        self.choose_general_channel()
        self._send_vacation_request()
        self._input_start_date()
        self._input_end_date()
        self._confirm_dates()
        self._approve_vacation()
        self._cancel_vacation()

    def test_viva_las_vegas_with_reject(self):
        self._send_vacation_request()
        self._input_start_date()
        self._input_end_date()
        self._confirm_dates()
        self._reject_vacation()

    def test_approve_notification(self):
        self.choose_general_channel()
        self._send_vacation_request()
        self._input_start_date()
        self._input_end_date()
        self._confirm_dates()
        self._approve_vacation()

    def test_reject_notification(self):
        pass

    def test_cancel_notification(self):
        pass

    def test_viva_las_vegas_approve_without_permission(self):
        self.logout()
        self.login(use_test_user=True)
        self.choose_general_channel()

        self._send_vacation_request()
        self._input_start_date()
        self._input_end_date()
        self._confirm_dates()
        self._approve_vacation(is_admin=False)

        self.logout()
        self.login()
        self._approve_vacation()
        self._cancel_vacation()

    def test_viva_las_vegas_reject_without_permission(self):
        self.logout()
        self.login(use_test_user=True)
        self.choose_general_channel()

        self._send_vacation_request()
        self._input_start_date()
        self._input_end_date()
        self._confirm_dates()
        self._reject_vacation(is_admin=False)

        self.logout()
        self.login()
        self.choose_general_channel()
        self._reject_vacation()


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

    test_cases = VivaLasVegasScriptTestCase(options.host, options.username, options.password,
                                            create_test_user=True)
    test_cases.run()


if __name__ == '__main__':
    main()
