'''

Main file for KGBot.

'''

import os # environment variables
import random
import time
from Message.Logging import setup_logging, cleanup_old_logs # log files
from datetime import datetime
from dotenv import load_dotenv # load environment variables
from Message.Backend import go_to_channel
from Message.Backend import send_kd_and_reaction, send_msg, login
from misc import wait_16_minutes
from selenium import webdriver # Selenium WebDriver
from selenium.webdriver.chrome.options import Options # Chrome options
from selenium.webdriver.chrome.service import Service # Chrome service
import threading
from Message.Threading import command_listener

load_dotenv() # load environment variables


###########################################################################################################################


'''

Logger setup

'''
print_lock = threading.Lock()

def safe_log(msg):
    with print_lock:
        print(msg)
        LOGGER.info(msg)

LOGGER = setup_logging()
log = safe_log
cleanup_old_logs(log_folder='log', max_logs=10) # Clean up old logs


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
BOT_ID = os.getenv("BOT_ID")
API_KEY = os.getenv("API_KEY")
SUDO_CHANNEL_ID = "890644443575771166" # BOT_SPAM


###########################################################################################################################


'''

Selenium setup

'''

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
# debug options
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument("--window-size=1920,1080")

# service = Service('C:\\Users\\bryan\\chromedriver-win64\\chromedriver.exe')
service = Service('/usr/bin/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)

###########################################################################################################################


'''

Threading setup

'''
driver_lock = threading.Lock()

sudo_thread = threading.Thread(
    target=command_listener,
    args=(driver, driver_lock, BOT_NAME, GUILD_ID, SUDO_CHANNEL_ID, log),
    daemon=True
)


###########################################################################################################################


'''
Main execution loop. Included here because it calls
functions from all parts of the bot

'''


def execute_loop(driver, driver_lock):
    times = [(m + OFFSET_MINUTES) % 60 for m in [0, 15, 30, 45]]
    first_iteration = True
    failed = False

    while True:
        try:
            start = time.time()
            now = datetime.now()

            executed_first_iteration = False

            if failed or (first_iteration and now.minute % 60 in times and now.second == 0):
                with driver_lock:
                    go_to_channel(driver, GUILD_ID, DROP_CHANNEL_ID)
                    log("Going to drop channel...")
                    send_kd_and_reaction(driver, log)
                    first_iteration = False
                    failed = False
                    executed_first_iteration = True
                    log("Going back to sudo channel...")
                    go_to_channel(driver, GUILD_ID, SUDO_CHANNEL_ID)
                    wait_16_minutes(start)

            if not first_iteration and not executed_first_iteration:
                with driver_lock:
                    go_to_channel(driver, GUILD_ID, DROP_CHANNEL_ID)
                    log("Going to drop channel...")
                    send_kd_and_reaction(driver, log)
                    log("Going back to sudo channel...")
                    go_to_channel(driver, GUILD_ID, SUDO_CHANNEL_ID)
                    wait_16_minutes(start)

            if not executed_first_iteration:
                time.sleep(0.5)

        except Exception as e:
            log(f"Loop error: {e}")
            log("Retrying in 5 seconds...")
            time.sleep(5)
            go_to_channel(driver, GUILD_ID, DROP_CHANNEL_ID)
            failed = True


###########################################################################################################################


# Start
if __name__ == "__main__":

    if not EMAIL or not PASSWORD: raise ValueError("Missing credentials in .env")

    login(driver, log, GUILD_ID, DROP_CHANNEL_ID)

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
            go_to_channel(driver, GUILD_ID, DROP_CHANNEL_ID)

    sudo_thread.start() # Start listening on the command channel

    execute_loop(driver, driver_lock)
