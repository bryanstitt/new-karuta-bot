import time
import re
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from .Backend import send_msg, go_to_channel, login  # Adjust this import if needed
from datetime import datetime

def parse_sudo_command(message):
    match = re.search(r"sudo\s+(.*)", message)
    return match.group(1) if match else None

def get_message_timestamp(msg_el, log):
    try:
        time_el = msg_el.find_element(By.XPATH, ".//time")
        return datetime.fromisoformat(time_el.get_attribute("datetime").replace("Z", "+00:00")).timestamp()
    except Exception as e:
        log(f"Could not get timestamp: {e}")
        return 0

def find_valid_mention(driver, bot_name, after_timestamp, log):
    mentions = driver.find_elements(By.XPATH, f"//span[@class='mention wrapper_f61d60 interactive' and text()='@{bot_name}']")
    for mention in reversed(mentions):
        try:
            message = mention.find_element(By.XPATH, "./ancestor::div[@role='article']")
            if get_message_timestamp(message, log) > after_timestamp:
                _ = message.tag_name  # Trigger StaleElementReferenceException early
                return message
        except StaleElementReferenceException:
            continue
    return None


def command_listener(driver, driver_lock, pause_listener, bot_name, guild_id, cmd_channel_id, log):
    last_checked_time = time.time()

    with driver_lock:
        go_to_channel(driver, guild_id, cmd_channel_id)
        log("Navigated to sudo channel")

    while True:
        log("Checking for sudo commands...")

        if pause_listener.is_set():
            time.sleep(0.5)
            continue
        
        with driver_lock:
            msg_element = find_valid_mention(driver, bot_name, last_checked_time, log)
            if msg_element:
                text = msg_element.text
                command = parse_sudo_command(text)
                if command:
                    log(f"Received sudo command: {command}")
                    send_msg(driver, command, log)
                    last_checked_time = get_message_timestamp(msg_element, log)
        time.sleep(0.5)
