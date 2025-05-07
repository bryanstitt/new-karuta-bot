import time
import re
from selenium.webdriver.common.by import By
from Backend import send_msg, get_channel  # Adjust this import if needed
from main import log

def parse_sudo_command(text, bot_name):
    pattern = r"@{}\\s+sudo\\s+(.+)".format(re.escape(bot_name))
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1) if match else None

def grab_latest_message(driver, bot_name):
    try:
        messages = driver.find_elements(By.XPATH, "//div[contains(@class, 'messageContent')]")
        if not messages:
            return None

        latest_message = messages[-1].text
        return parse_sudo_command(latest_message, bot_name)
    except Exception as e:
        log(f"Error checking command channel: {e}")
        return None

def command_listener(driver, bot_name, command_channel_id):
    last_seen_command = ""
    get_channel(driver, command_channel_id)
    while True:
        command = grab_latest_message(driver, bot_name)
        if command and command != last_seen_command:
            log(f"Received sudo command: {command}")
            send_msg(driver, command)
            last_seen_command = command
        time.sleep(5)
