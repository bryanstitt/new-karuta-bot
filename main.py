from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import random
from dotenv import load_dotenv
import requests
from get_best_position import get_best_position
import logging
from datetime import datetime, timedelta

#setup logging
log_level = os.getenv('LOG_LEVEL', 20)
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.WARNING if log_level is None else int(log_level)) # default log level is WARNING
handler = logging.FileHandler(filename='log.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(filename)s:%(lineno)s: %(message)s'))
LOGGER.addHandler(handler)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')


# Set up the WebDriver
# service = Service('C:\\Users\\bryan\\chromedriver-win64\\chromedriver.exe')
service = Service('/usr/bin/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)
actions = ActionChains(driver)

# Login to Discord
def login(email, password):
    driver.get('https://discord.com/login')
    
    # Wait until email and password fields are available
    wait = WebDriverWait(driver, 10)
    email_input = wait.until(EC.presence_of_element_located((By.NAME, 'email')))
    password_input = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
    
    email_input.send_keys(email)
    password_input.send_keys(password)

    time.sleep(3)
    
    # Click login button
    login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
    login_button.click()
    
    print("Triggered log in click.")
    LOGGER.info("Triggered log in click.")
    

def send_kd(trigger="kd"):
    try:
        wait = WebDriverWait(driver, 15)

        # Step 1: Get the input box and send the message
        input_box = wait.until(EC.presence_of_element_located((
            By.XPATH, '//div[@role="textbox" and @data-slate-editor="true"]'
        )))
        input_box.click()
        input_box.send_keys(trigger)
        input_box.send_keys(Keys.ENTER)

        LOGGER.info(f"Sent message: {trigger}")
        print(f"Sent message: {trigger}")

    except Exception as e: raise Exception(f"Failed to send kd: {e}")

def wait_and_get_karuta_message(wait_time=8):
    print(f"Waiting {wait_time} seconds before checking for Karuta message...")
    LOGGER.info(f"Waiting {wait_time} seconds before checking for Karuta message...")
    
    time.sleep(wait_time)
    
    try:
        # After waiting, get the latest messages
        messages = driver.find_elements(By.CLASS_NAME, "message__5126c")
        
        for message in reversed(messages):  # Check from newest to oldest
            try:
                username = message.find_element(By.CLASS_NAME, "username_c19a55").text
                if username.lower() == "karuta":
                    print("Found message from Karuta.")
                    LOGGER.error(f"Found message from Karuta.")
                    return message
            except:
                continue  # If username not found, skip
    except Exception as e: raise Exception(f"Failed to retrieve Karuta messages: {e}")
    
    raise ValueError("No Karuta message found after waiting.")

def download_image_from_message(message_element):
    try:
        link = message_element.find_element(By.TAG_NAME, "a")
        href = link.get_attribute("href")
        print(f"Downloading image from: {href}")
        LOGGER.info(f"Downloading image from: {href}")
        r = requests.get(href)

        with open("discord_image.png", "wb") as f:
            f.write(r.content)

        print("Image downloaded as discord_image.png")
        LOGGER.info("Image downloaded as discord_image.png")
    except Exception as e: raise Exception(f"Failed to download image: {e}")

def send_reaction(index_ed_tuple):
    try:
        index, ed = index_ed_tuple
        print(f"Sending reaction for card {index+1} with ED: {ed}")
        LOGGER.info(f"Sending reaction for card {index-1} with ED: {ed}")

        message_box = driver.find_element("xpath", '//div[@role="textbox"]')
        match index:
            case 0:
                message_box.send_keys('+:one:')
            case 1:
                message_box.send_keys('+:two:')
            case 2:
                message_box.send_keys('+:three:')
            case 3:
                message_box.send_keys('+:four:')
        
        message_box.send_keys(Keys.ENTER)
        time.sleep(3)

        if ed == 7:
            message_box.send_keys('klu')
            message_box.send_keys(Keys.ENTER)            
    except Exception as e: raise Exception(f"Failed to send reaction: {e}")

def get_channel(guild_id, channel_id): driver.get(f'https://discord.com/channels/{guild_id}/{channel_id}')

def execute_loop(offset_minutes):
    execution_minutes = [0, 15, 30, 45]  # minutes in the hour when to execute (before offset)

    execution_times = [(minute + offset_minutes) % 60 for minute in execution_minutes]

    __failed = False
    cooldown_offset = 5
    while True:
        try:
            now = datetime.now()
            current_minute = now.minute
            current_second = now.second + cooldown_offset

            if __failed or (current_minute in execution_times and current_second % 60 == 0):
                __failed = False
                # It's time to execute!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                print(f"Executing{' previously failed' if __failed else ''} task at {now.strftime('%Y-%m-%d %H:%M:%S')}")
                LOGGER.info(f"Executing{' previously failed' if __failed else ''} task at {now.strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(2)

                send_kd()
                cooldown_offset += 5 # add +5 sec to cron each time

                message = wait_and_get_karuta_message()
                download_image_from_message(message)

                index, ed = get_best_position()
                LOGGER.info(f"Best position: {index+1}, ED: {ed}")

                time.sleep(5)

                send_reaction((index, ed))
            else: time.sleep(0.5)
            
        except Exception as e:
            __failed = True
            __error_delay = 5
            print(f"Error: {e}")
            LOGGER.error(f"Error: {e}")
            print(f"Retrying in {__error_delay} seconds...")
            LOGGER.info(f"Retrying in {__error_delay} seconds...")
            time.sleep(__error_delay)
            get_channel(guild_id, channel_id) # core of the fix

# Main execution
if __name__ == "__main__":
    load_dotenv()
    # Get credentials from environment variables
    email = os.getenv('DISCORD_EMAIL')
    password = os.getenv('DISCORD_PASSWORD')
    guild_id = os.getenv('DISCORD_GUILD_ID')
    channel_id = os.getenv('DISCORD_CHANNEL_ID')
    offset_minutes = int(os.getenv('CRON_OFFSET')) 
    
    if not email or not password:
        raise ValueError("Please set your Discord email and password in the environment variables.")
    
    # try to login 3 times
    for _ in range(3):
        try:
            login(email, password)
            break # Exit the loop if login is successful
        except Exception as e:
            __login_delay = 5
            print(f"Error during login: {e}")
            LOGGER.error(f"Error during login: {e}")
            print(f"Retrying login in {__login_delay} seconds...")
            LOGGER.info(f"Retrying login in {__login_delay} seconds...")
            time.sleep(__login_delay)
    
    # Add a delay to handle any dynamic content loading
    time.sleep(random.uniform(5, 8))

    driver.save_screenshot('post-login.png')

    get_channel(guild_id, channel_id)

    time.sleep(random.uniform(1, 2))
    
    driver.save_screenshot('channel-view.png')

    execute_loop(offset_minutes)