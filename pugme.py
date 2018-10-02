import os
from dotenv import load_dotenv
from base import send_msg_and_try_check_result

load_dotenv()

BOT_NAME = 'meeseeks'
URL_PATTERN = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'


def run_script(browser, log):

    log.info('Click general chat')
    general_chat = browser.driver.find_elements_by_css_selector(
        'div.sidebar-item__ellipsis'
    )[0]
    general_chat.click()
    log.info('success!')

    log.info('Send single pugme request')
    curr_msg = '{0} pug me'.format(BOT_NAME)
    browser.fill('msg', curr_msg)
    last_msg = send_msg_and_try_check_result(browser, URL_PATTERN,
                                             count_of_msg=1, match=1)
    if not last_msg:
        log.error('------------ERROR!!!!!------------')
        return False
    log.info('success!')

    log.info('Send pug bomb')
    curr_msg = '{0} pug bomb'.format(BOT_NAME)
    browser.fill('msg', curr_msg)
    last_msg = send_msg_and_try_check_result(browser, URL_PATTERN,
                                             count_of_msg=int(os.getenv('PUGS_LIMIT')), match=1)
    if not last_msg:
        log.error('------------ERROR!!!!!------------')
        return False
    log.info('success!')

    log.info('Send pug bomb 3')
    curr_msg = '{0} pug bomb 3'.format(BOT_NAME)
    browser.fill('msg', curr_msg)
    last_msg = send_msg_and_try_check_result(browser, URL_PATTERN,
                                             count_of_msg=3, match=1)
    if not last_msg:
        log.error('------------ERROR!!!!!------------')
        return False
    log.info('success!')
    return True
