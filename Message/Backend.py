import os # environment variables
import time
import requests

from datetime import datetime
from dotenv import load_dotenv # load environment variables
from Message.Reactions import wait_and_click_reaction
from selenium import webdriver # Selenium WebDriver; used for Syntax Highlighting in this file
from selenium.webdriver.common.action_chains import ActionChains
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
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')
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
    log(f"Sent message: {trigger}")
    return time.time()



def download_image_from_message(message_element, log) -> None:
    link = message_element.find_element(By.TAG_NAME, "a")
    href = link.get_attribute("href")
    log(f"Downloading image from: {href}")
    r = requests.get(href)
    with open("discord_image.png", "wb") as f:
        f.write(r.content)
    log("Image downloaded as discord_image.png")



def send_kd_and_reaction(driver: webdriver.Chrome, log) -> None:
    now = datetime.now()
    log(f"Executing task at {now.strftime('%Y-%m-%d %H:%M:%S')}")

    for _ in range(3): # this is to avoid "jump to present message" bug
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(0.2)

    time.sleep(1)

    sent_kd_time = send_msg(driver, "kd", log)
    wait_and_click_reaction(driver, sent_kd_time, log)

    time.sleep(3)
    
    send_msg(driver, "kt burn", log) # Add tag logic for slot 1 on Emilia



def get_channel(driver: webdriver.Chrome) -> None: driver.get(f'https://discord.com/channels/{GUILD_ID}/{CHANNEL_ID}/')



def login(driver: webdriver.Chrome, log) -> None:
    driver.get(f"https://discord.com/login?redirect_to=%2Fchannels%2F{GUILD_ID}%2F{CHANNEL_ID}")
    wait = WebDriverWait(driver, 10)
    email_input = wait.until(EC.presence_of_element_located((By.NAME, 'email')))
    password_input = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
    email_input.send_keys(EMAIL)
    password_input.send_keys(PASSWORD)
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()
    log("Triggered login click.")