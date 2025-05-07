import time
import re
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from .Backend import send_msg, go_to_channel  # Adjust this import if needed
from datetime import datetime

def parse_sudo_command(text, bot_name):
    pattern = r"@{}\\s+sudo\\s+(.+)".format(re.escape(bot_name))
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1) if match else None

def get_message_timestamp(msg_el, log):
    try:
        time_el = msg_el.find_element(By.XPATH, ".//time")
        return datetime.fromisoformat(time_el.get_attribute("datetime").replace("Z", "+00:00")).timestamp()
    except Exception as e:
        log(f"Could not get timestamp: {e}")
        return 0

def find_valid_mention(driver, bot_name, after_timestamp, log):
    mentions = driver.find_elements(By.XPATH, f"//span[contains(@class, 'mention') and text()='@{bot_name}']")
    for mention in reversed(mentions):
        try:
            message = mention.find_element(By.XPATH, "./ancestor::div[contains(@class, 'message__')]")
            if get_message_timestamp(message, log) > after_timestamp:
                _ = message.tag_name  # Trigger StaleElementReferenceException early
                return message
        except StaleElementReferenceException:
            continue
    return None


def command_listener(driver, bot_name, guild_id, cmd_channel_id, log):
    last_checked_time = time.time()

    go_to_channel(driver, guild_id, cmd_channel_id)

    while True:
        msg_element = find_valid_mention(driver, bot_name, last_checked_time, log)
        if msg_element:
                text = msg_element.text
                command = parse_sudo_command(text, bot_name)
                if command:
                    log(f"Received sudo command: {command}")
                    send_msg(driver, command, log)
                    last_checked_time = get_message_timestamp(msg_element, log)
        time.sleep(0.5)
