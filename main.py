from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
import time
import os
import random
from sys import exit
from dotenv import load_dotenv
import requests
from get_best_position import get_best_position
import logging
from datetime import datetime, timedelta


########################################################################################################################

'''
Get credentials from environment variables
'''

load_dotenv()
EMAIL = os.getenv('DISCORD_EMAIL')
PASSWORD = os.getenv('DISCORD_PASSWORD')
GUILD_ID = os.getenv('DISCORD_GUILD_ID')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')
OFFSET_MINUTES = int(os.getenv('CRON_OFFSET')) 
BOT_NAME = os.getenv("BOT_NAME")



########################################################################################################################

'''
Setup Logger
'''

log_level = os.getenv('LOG_LEVEL', 20)
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.WARNING if log_level is None else int(log_level)) # default log level is WARNING
handler = logging.FileHandler(filename='log.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(filename)s:%(lineno)s: %(message)s'))
LOGGER.addHandler(handler)


########################################################################################################################

'''
Setup Selenium WebDriver
'''

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# service = Service('C:\\Users\\bryan\\chromedriver-win64\\chromedriver.exe')
service = Service('/usr/bin/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)
actions = ActionChains(driver)


########################################################################################################################



def login():
    driver.get(f"https://discord.com/login?redirect_to=%2Fchannels%2F{GUILD_ID}%2F{CHANNEL_ID}")
    
    # Wait until email and PASSWORD fields are available
    wait = WebDriverWait(driver, 10)
    email_input = wait.until(EC.presence_of_element_located((By.NAME, 'email')))
    password_input = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
    
    email_input.send_keys(EMAIL)
    password_input.send_keys(PASSWORD)

    time.sleep(3)
    
    # Click login button
    login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
    login_button.click()
    
    print_log("Triggered log in click.")
    

def send_msg(trigger="kd"):
    try:
        wait = WebDriverWait(driver, 15)

        # Step 1: Get the input box and send the message
        input_box = wait.until(EC.presence_of_element_located((
            By.XPATH, '//div[@role="textbox" and @data-slate-editor="true"]'
        )))
        input_box.click()
        input_box.send_keys(trigger)
        input_box.send_keys(Keys.ENTER)

        print_log(f"Sent message: {trigger}")

        return time.time()

    except Exception as e: raise Exception(f"Failed to send kd: {e}")

def print_log(message):
    print(message)
    LOGGER.info(message)

def wait_and_click_reaction(sent_kd_time):

    def get_message_timestamp(message_element):
        try:
            # Adjust this to match your actual timestamp element class/attribute
            timestamp_el = message_element.find_element(By.XPATH, ".//time")
            return datetime.fromisoformat(timestamp_el.get_attribute("datetime").replace("Z", "+00:00")).timestamp()
        except Exception as e:
            print_log(f"Could not get timestamp: {e}")
            return 0

    def find_valid_mention(driver):
        mentions = driver.find_elements(By.XPATH, f"//span[contains(@class, 'mention') and text()='@{BOT_NAME}']")
        for mention in reversed(mentions):
            message = mention.find_element(By.XPATH, "./ancestor::div[contains(@class, 'message__')]")
            msg_time = get_message_timestamp(message)
            if msg_time > sent_kd_time:
                return message
        return None

    try:
        print_log(f"Waiting for a message that mentions @{BOT_NAME}...")
        msg = WebDriverWait(driver, 30).until(find_valid_mention)
        print_log("Found valid mention after kd.")

        download_image_from_message(msg)

        index, ed = get_best_position()
        print_log(f"Best position: {index+1}, ED: {ed}")

        for _ in range(3):
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: len(msg.find_elements(By.CLASS_NAME, "reactionInner__23977")) >= 4
                )

                reactions = msg.find_elements(By.CLASS_NAME, "reactionInner__23977")
                print_log(f"Clicking reaction at index {index}")
                reactions[index].click()
                print_log("Reaction clicked successfully.")
                break
            except StaleElementReferenceException:
                print_log("Element went stale, refinding...")
                msg = find_valid_mention(driver)

    except Exception as e:
        print_log(f"ERROR: An exception occurred during wait_and_click: {e}")


def download_image_from_message(message_element):
    try:
        link = message_element.find_element(By.TAG_NAME, "a")
        href = link.get_attribute("href")
        print_log(f"Downloading image from: {href}")
        r = requests.get(href)

        with open("discord_image.png", "wb") as f:
            f.write(r.content)

        print_log("Image downloaded as discord_image.png")
    except Exception as e: raise Exception(f"Failed to download image: {e}")

def get_channel(): driver.get(f'https://discord.com/channels/{GUILD_ID}/{CHANNEL_ID}')

def send_kd_and_reaction(now):
    # It's time to execute!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    print_log(f"Executing task at {now.strftime('%Y-%m-%d %H:%M:%S')}")
    time.sleep(2)

    sent_kd_time = send_msg("kd")

    wait_and_click_reaction(sent_kd_time)

    send_msg("kt burn")

def wait_16_minutes(start_time):
    interval = 16 * 60  # 16 minutes = 960 seconds
    elapsed = time.time() - start_time
    sleep_time = max(0, interval - elapsed)
    time.sleep(sleep_time)

def execute_loop():
    execution_minutes = [0, 15, 30, 45]  # minutes in the hour when to execute (before offset)
    execution_times = [(minute + OFFSET_MINUTES) % 60 for minute in execution_minutes]

    first_iteration = True
    __failed = False

    while True:
        try:
            start_time = time.time()
            now = datetime.now()

            current_minute = now.minute
            current_second = now.second

            executed_first_iteration = False

            if __failed or (first_iteration and (current_minute % 60) in execution_times and current_second == 0):
                send_kd_and_reaction(now)
                __failed = False
                first_iteration = False
                executed_first_iteration = True
                wait_16_minutes(start_time) 

            if not first_iteration and not executed_first_iteration:
                send_kd_and_reaction(now)
                wait_16_minutes(start_time)
            
            if not executed_first_iteration:
                time.sleep(0.5)

        except Exception as e:
            __failed = True
            __error_delay = 5
            print_log(f"Error: {e}")
            print_log(f"Retrying in {__error_delay} seconds...")
            time.sleep(__error_delay)
            get_channel() # core of the fix


if __name__ == "__main__":
    
    if not EMAIL or not PASSWORD:
        raise ValueError("Please set your Discord email and password in the environment variables.")
    
    # try to login 3 times
    for _ in range(3):
        try:
            login()
            break # Exit the loop if login is successful
        except Exception as e:
            __login_delay = 5
            print_log(f"Error during login: {e}")
            print_log(f"Retrying login in {__login_delay} seconds...")
            time.sleep(__login_delay)
    
    # Add a delay to handle any dynamic content loading
    time.sleep(random.uniform(5, 8))

    driver.save_screenshot('post-login.png')
    
    # Get buggy Pterodactyl shit out of the way
    for _ in range(20):
        try:
            send_msg(
                trigger=[
                    "Logged in",
                    "Connected",
                    "Initialized",
                    "Ready to go",
                    "All set",
                    "All systems go",
                ][random.randint(0, 5)]
            )
            print_log("Bot is ready to go!")
            break
        except Exception as e:
            if _ >= 19: exit(1)
            __failure_delay = 5
            print_log(f"Failed to send ready message. Retrying in {__failure_delay} seconds... ({e})")
            time.sleep(__failure_delay)
            get_channel()

    execute_loop()