from argparse import ArgumentParser
from sys import stderr
from time import sleep

from rocketchat_API.rocketchat import RocketChat

from base import SplinterTestCase


LOCALHOST = 'http://127.0.0.1:8006'


class SplinterWizardInit(SplinterTestCase):
    def __init__(self, addr, username, password, wait=10, **kwargs):
        SplinterTestCase.__init__(self, addr, **kwargs)

        self.addr = addr
        self.username = username
        self.password = password
        self.wait = wait

        self.bot_name = 'meeseeks'
        self.bot_password = 'pass'

    def _wait_until_loading_is_completed(self, header, selector):
        for _ in range(self.wait):
            title = self.find_by_css(selector)
            if title.text.lower() == header:
                return True
            sleep(1)
        return False

    def test_administrator_info(self):
        # Admin info
        header = self.find_by_css('.setup-wizard-forms__header-title')
        assert header.text.lower() in 'admin info'

        self.browser.fill('registration-name', self.username)
        self.browser.fill('registration-username', self.username)
        self.browser.fill(
            'registration-email', '{}@mail.ru'.format(self.username)
        )
        self.browser.fill('registration-pass', self.password)
        submit_btn = self.find_by_css(
            '.rc-button.rc-button--primary.setup-wizard-forms__footer-next'
        )
        assert submit_btn
        submit_btn.click()

    def test_organisation_info(self):
        assert self._wait_until_loading_is_completed(
            'organization info',
            '.setup-wizard-forms__header-title'
        )

        submit_btn = self.find_by_css(
            '.rc-button.rc-button--primary.setup-wizard-forms__footer-next'
        )
        assert submit_btn
        submit_btn.click()

    def test_server_information(self):
        assert self._wait_until_loading_is_completed(
            'server info',
            '.setup-wizard-forms__header-title'
        )

        submit_btn = self.find_by_css(
            '.rc-button.rc-button--primary.setup-wizard-forms__footer-next'
        )
        assert submit_btn
        submit_btn.click()

    def test_server_registration(self):
        assert self._wait_until_loading_is_completed(
            'register server',
            '.setup-wizard-forms__header-title'
        )

        tariff_plan = self.find_by_css(
            '.setup-wizard-forms__content-register-radio'
        )
        assert tariff_plan
        tariff_plan.last.click()

        submit_btn = self.find_by_css(
            '.rc-button.rc-button--primary.setup-wizard-forms__footer-next'
        )
        assert submit_btn
        submit_btn.click()

    def test_fin(self):
        assert self._wait_until_loading_is_completed(
            'your workspace is ready to use 🎉',
            '.setup-wizard-info__content-title.setup-wizard-final__box-title'
        )

        submit_btn = self.find_by_css(
            '.rc-button.rc-button--primary.js-finish'
        )
        assert submit_btn
        submit_btn.click()

    def test_creating_bot_account(self):
        options_btn = self.browser.find_by_css(
            '.sidebar__toolbar-button.rc-tooltip.rc-tooltip--down.js-button'
        )
        options_btn.last.click()

        administration_btn = self.browser.find_by_css('.rc-popover__item-text')
        administration_btn.click()

        users_btn = self.browser.driver.find_elements_by_css_selector(
            'a.sidebar-item__link[aria-label="Users"]')

        self.browser.driver.execute_script("arguments[0].click();",
                                           users_btn[0])

        add_user_btn = self.find_by_css('button[aria-label="Add User"]')
        assert add_user_btn
        add_user_btn.click()

        input_name_el = self.find_by_css('input#name')
        assert input_name_el
        input_name_el.first.fill(self.bot_name)

        input_username_el = self.find_by_css('input#username')
        assert input_username_el
        input_username_el.first.fill(self.bot_name)

        input_email_el = self.find_by_css('input#email')
        assert input_email_el
        input_email_el.first.fill('{}@mail.ru'.format(self.bot_name))

        verified_btn = self.find_by_css('label.rc-switch__label')
        assert verified_btn
        verified_btn.first.click()

        input_password_el = self.find_by_css('input#password')
        assert input_password_el
        input_password_el.first.fill(self.bot_password)

        verified_btn = self.find_by_css('label.rc-switch__label')
        assert verified_btn
        verified_btn.last.click()

        role_option = self.find_by_css('option[value="bot"]')
        assert role_option
        role_option.first.click()

        add_role_btn = self.find_by_css('button#addRole')
        assert add_role_btn
        add_role_btn.first.click()

        # Do not send welcome email
        welcome_ckbx = self.find_by_css('label[for="sendWelcomeEmail"]')
        assert welcome_ckbx
        welcome_ckbx.first.click()

        save_btn = self.find_by_css('.rc-button.rc-button--primary.save')
        assert save_btn
        save_btn.first.click()

    def test_adding_permissions_to_bot(self):
        permissions = {
            'view-full-other-user-info': True
        }

        perms_btn = self.browser.driver.find_elements_by_css_selector(
            'a.sidebar-item__link[aria-label="Permissions"]'
        )
        assert perms_btn

        self.browser.driver.execute_script("arguments[0].click();",
                                           perms_btn[0])

        for name in permissions:
            checkbox = self.browser.driver.find_element_by_css_selector(
                'input.role-permission[name="perm[bot][{}]"]'.format(name)
            )
            assert checkbox
            if permissions[name] != bool(checkbox.get_attribute('checked')):
                checkbox.click()

        exit_btn = self.find_by_css(
            '.sidebar-flex__close-button'
        )
        assert exit_btn
        exit_btn.click()

    def test_create_necessary_rooms(self):
        groups = [
            'hr',
            'leave-coordination'
        ]

        rocket = RocketChat(
            self.username,
            self.password,
            server_url=self.addr
        )

        for name in groups:
            rocket.groups_create(name, members=['meeseeks'])


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
                             'for waiting loading of page(secs)')

    options = parser.parse_args()
    if not options.host:
        options.host = LOCALHOST
        stderr.write(
            'Host is not specified. Defaults to {}.\n'.format(options.host)
        )

    if not options.username:
        parser.error('Username is not specified')

    if not options.password:
        parser.error('Password is not specified')

    if not options.wait:
        options.wait = 100
        stderr.write(
            'Waiting time is not specified. Defaults to {}.\n'
            .format(options.wait)
        )

    test_cases = SplinterWizardInit(
        options.host,
        options.username,
        options.password,
        wait=options.wait
    )

    test_cases.run()


if __name__ == "__main__":
    main()
