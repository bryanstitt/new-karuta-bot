import time
import random
from datetime import datetime
from message_utils import send_msg
from reaction_handler import wait_and_click_reaction
from config import OFFSET_MINUTES
from config import GUILD_ID, CHANNEL_ID

def get_channel(driver):
    driver.get(f'https://discord.com/channels/{GUILD_ID}/{CHANNEL_ID}')

def send_kd_and_reaction(driver, log):
    now = datetime.now()
    log(f"Executing task at {now.strftime('%Y-%m-%d %H:%M:%S')}")
    time.sleep(2)
    sent_kd_time = send_msg(driver, "kd", log)
    wait_and_click_reaction(driver, sent_kd_time, log)
    time.sleep(3)
    send_msg(driver, "kt burn", log)

def wait_16_minutes(start_time):
    elapsed = time.time() - start_time
    time.sleep(max(0, 960 - elapsed))

def execute_loop(driver, log):
    times = [(m + OFFSET_MINUTES) % 60 for m in [0, 15, 30, 45]]
    first = True
    failed = False

    while True:
        try:
            start = time.time()
            now = datetime.now()
            if failed or (first and now.minute % 60 in times and now.second == 0):
                send_kd_and_reaction(driver, log)
                first = False
                failed = False
                wait_16_minutes(start)
            else:
                time.sleep(0.5)
        except Exception as e:
            log(f"Loop error: {e}")
            time.sleep(5)
            get_channel(driver)
            failed = True
