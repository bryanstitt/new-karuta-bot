import time
import random
from logger import setup_logger
from driver_setup import create_driver
from discord_login import login
from scheduler import execute_loop, get_channel
from message_utils import send_msg

logger = setup_logger()
log = lambda msg: (print(msg), logger.info(msg))

if __name__ == "__main__":
    from config import EMAIL, PASSWORD

    if not EMAIL or not PASSWORD:
        raise ValueError("Missing credentials in .env")

    driver = create_driver()

    for _ in range(3):
        try:
            login(driver, log)
            break
        except Exception as e:
            log(f"Login error: {e}")
            time.sleep(5)

    time.sleep(random.uniform(5, 8))
    driver.save_screenshot("post-login.png")

    for _ in range(20):
        try:
            send_msg(driver, random.choice([
                "Logged in", "Connected", "Initialized", "Ready to go", "All set", "All systems go"
            ]), log)
            log("Bot is ready to go!")
            break
        except Exception as e:
            if _ >= 19: exit(1)
            log(f"Send message failed: {e}")
            time.sleep(5)
            get_channel(driver)

    execute_loop(driver, log)
