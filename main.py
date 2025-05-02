'''

Main file for KGBot.

'''



import logging # log files
import os # environment variables
import random
import time

from datetime import datetime
from dotenv import load_dotenv # load environment variables
from Message.Backend import get_channel
from Message.Backend import send_kd_and_reaction, send_msg, login
from misc import wait_16_minutes
from selenium import webdriver # Selenium WebDriver
from selenium.webdriver.chrome.options import Options # Chrome options
from selenium.webdriver.chrome.service import Service # Chrome service
load_dotenv() # load environment variables



###########################################################################################################################



'''

Logger setup

'''

log_level = os.getenv('LOG_LEVEL', 20)
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.WARNING if log_level is None else int(log_level)) # default log level is WARNING
handler = logging.FileHandler(filename='log.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(filename)s:%(lineno)s: %(message)s'))
LOGGER.addHandler(handler)
log = lambda msg: (print(msg), LOGGER.info(msg))



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



'''

Selenium setup

'''

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
service = Service('/usr/bin/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)



###########################################################################################################################



'''

Main execution loop. Included here because it calls
functions from all parts of the bot

'''


def execute_loop(driver):
    times = [(m + os.getenv('CRON_OFFSET')) % 60 for m in [0, 15, 30, 45]]
    first_iteration = True
    failed = False

    while True:
        try:
            start = time.time()
            now = datetime.now()

            executed_first_iteration = False

            if failed or (first_iteration and now.minute % 60 in times and now.second == 0):
                send_kd_and_reaction(driver, log)
                first_iteration = False
                failed = False
                executed_first_iteration = True
                wait_16_minutes(start)
            
            if not first_iteration and not executed_first_iteration:
                send_kd_and_reaction(driver, log)
                wait_16_minutes(start)

            if not executed_first_iteration:
                time.sleep(0.5)

        except Exception as e:
            log(f"Loop error: {e}")
            log("Retrying in 5 seconds...")
            time.sleep(5)
            get_channel(driver)
            failed = True



###########################################################################################################################



# Start
if __name__ == "__main__":

    if not EMAIL or not PASSWORD: raise ValueError("Missing credentials in .env")

    for _ in range(3):
        try:
            login(driver, log)
            break
        except Exception as e:
            log(f"Login error: {e}")
            time.sleep(5)

    time.sleep(random.uniform(5, 8))
    driver.save_screenshot("post-login.png")



    '''
    
    Bot is logged in, now initialize the channel    
    
    '''

    for _ in range(20):
        try:
            send_msg(driver, random.choice([
                "Logged in",
                "Connected",
                "Initialized",
                "Ready to go",
                "All set",
                "All systems go"
            ]), log)
            log("Bot is ready to go!")
            break
        except Exception as e:
            if _ >= 19: exit(1)
            log(f"Send message failed: {e}")
            time.sleep(5)
            get_channel(driver)

    execute_loop(driver)
