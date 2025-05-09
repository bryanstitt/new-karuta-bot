import os # environment variables
import time
from datetime import datetime
from dotenv import load_dotenv # load environment variables
from Message.Reactions import wait_and_click_reaction
from selenium import webdriver # Selenium WebDriver; used for Syntax Highlighting in this file
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
load_dotenv()


###########################################################################################################################


'''

Environment variables

'''

EMAIL = os.getenv('DISCORD_EMAIL')
PASSWORD = os.getenv('DISCORD_PASSWORD')
GUILD_ID = os.getenv('DISCORD_GUILD_ID')
DROP_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')
OFFSET_MINUTES = int(os.getenv('CRON_OFFSET'))
BOT_NAME = os.getenv("BOT_NAME")


###########################################################################################################################


def send_msg(driver: webdriver.Chrome, trigger, log) -> float:
    input_box = WebDriverWait(driver, 15).until(
        lambda d: d.find_element(By.XPATH, '//div[@role="textbox" and @data-slate-editor="true"]')
    )
    input_box.click()
    input_box.send_keys(trigger)
    input_box.send_keys(Keys.ENTER)
    input_box.send_keys(Keys.ENTER) # for sudo
    log(f"Sent message: {trigger}")
    return time.time()


def send_kd_and_reaction(driver: webdriver.Chrome, log) -> None:
    now = datetime.now()
    log(f"Executing task at {now.strftime('%Y-%m-%d %H:%M:%S')}")

    time.sleep(1)

    sent_kd_time = send_msg(driver, "kd", log)
    index, ed = wait_and_click_reaction(driver, sent_kd_time, log)

    time.sleep(3)
    
    if index == -1:
        log("No image found in message.")
        return
    elif BOT_NAME == "Emilia" and index == 0:
        send_msg(driver, "kt john", log)
    else:
        send_msg(driver, "kt burn", log)


def go_to_channel(driver: webdriver.Chrome, guild_id, channel_id, timeout=30, retry_interval=3) -> None:
    deadline = time.time() + timeout
    url = f'https://discord.com/channels/{guild_id}/{channel_id}'

    while time.time() < deadline:
        try:
            driver.get(url)
            WebDriverWait(driver, retry_interval).until(
                EC.presence_of_element_located((By.XPATH, '//div[@role="textbox" and @data-slate-editor="true"]'))
            )
            return  # Channel loaded successfully
        except TimeoutException:
            print(f"[WARN] Retry loading channel {channel_id}...")
            time.sleep(1)
        except Exception as e:
            print(f"[ERROR] Unexpected error while trying to load channel: {e}")
            time.sleep(1)

    print(f"[ERROR] Failed to load channel {channel_id} after {timeout} seconds.")

def login(driver: webdriver.Chrome, log, guild_id, channel_id) -> None:
    for _ in range(3):
        try:
            driver.get(f"https://discord.com/login?redirect_to=%2Fchannels%2F{guild_id}%2F{channel_id}")
            wait = WebDriverWait(driver, 10)
            email_input = wait.until(EC.presence_of_element_located((By.NAME, 'email')))
            password_input = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
            email_input.send_keys(EMAIL)
            password_input.send_keys(PASSWORD)
            driver.find_element(By.XPATH, '//button[@type="submit"]').click()
            log("Triggered login click.")
            break
        except Exception as e:
            log(f"Login error... Retrying login...")
            time.sleep(5)