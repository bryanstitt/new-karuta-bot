import time
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

def send_msg(driver, trigger, log):
    input_box = WebDriverWait(driver, 15).until(
        lambda d: d.find_element(By.XPATH, '//div[@role="textbox" and @data-slate-editor="true"]')
    )
    input_box.click()
    input_box.send_keys(trigger)
    input_box.send_keys(Keys.ENTER)
    log(f"Sent message: {trigger}")
    return time.time()

def download_image_from_message(message_element, log):
    link = message_element.find_element(By.TAG_NAME, "a")
    href = link.get_attribute("href")
    log(f"Downloading image from: {href}")
    r = requests.get(href)
    with open("discord_image.png", "wb") as f:
        f.write(r.content)
    log("Image downloaded as discord_image.png")
