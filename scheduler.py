import time
from datetime import datetime
from message_utils import send_msg
from reaction_handler import wait_and_click_reaction
from config import OFFSET_MINUTES
from config import GUILD_ID, CHANNEL_ID
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

def get_channel(driver):
    driver.get(f'https://discord.com/channels/{GUILD_ID}/{CHANNEL_ID}')

def send_kd_and_reaction(driver, log):
    now = datetime.now()
    log(f"Executing task at {now.strftime('%Y-%m-%d %H:%M:%S')}")

    for _ in range(3): # this is to avoid "jump to present message" bug
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(0.2)

    time.sleep(1)

    sent_kd_time = send_msg(driver, "kd", log)
    wait_and_click_reaction(driver, sent_kd_time, log)

    time.sleep(3)
    
    send_msg(driver, "kt burn", log)

def wait_16_minutes(start_time):
    elapsed = time.time() - start_time
    time.sleep(max(0, 960 - elapsed))

def execute_loop(driver, log):
    times = [(m + OFFSET_MINUTES) % 60 for m in [0, 15, 30, 45]]
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
