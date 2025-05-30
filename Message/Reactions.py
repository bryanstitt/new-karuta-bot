import os
import time
from datetime import datetime
from dotenv import load_dotenv
from Message.ImageAnalysis import get_best_position, download_image_from_message
from selenium import webdriver # Selenium WebDriver; used for Syntax Highlighting in this file
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException

load_dotenv()

def wait_and_click_reaction(driver:webdriver.Chrome, sent_kd_time, log):
    def get_message_timestamp(msg_el):
        try:
            time_el = msg_el.find_element(By.XPATH, ".//time")
            return datetime.fromisoformat(time_el.get_attribute("datetime").replace("Z", "+00:00")).timestamp()
        except Exception as e:
            log(f"Could not get timestamp: {e}")
            return 0

    def find_valid_mention(driver:webdriver.Chrome):
        mentions = driver.find_elements(By.XPATH, f"//span[contains(@class, 'mention') and text()='@{os.getenv('BOT_NAME')}']")
        for mention in reversed(mentions):
            try:
                message = mention.find_element(By.XPATH, "./ancestor::div[contains(@class, 'message__')]")
                if get_message_timestamp(message) > sent_kd_time:
                    _ = message.tag_name  # Trigger potential StaleElementReferenceException
                    return message
            except StaleElementReferenceException:
                continue
        return None

    def dismiss_new_message_bar():
        try:
            bar = driver.find_element(By.CSS_SELECTOR, "[id^='NewMessagesBarJumpToNewMessages']")
            driver.execute_script("arguments[0].click();", bar)
            time.sleep(0.3)
            log("Dismissed new message bar.")
        except Exception:
            pass

    def scroll_and_click(element):
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.3)
        try:
            element.click()
        except ElementClickInterceptedException as e:
            log(f"Click intercepted, using JS click fallback: {e}")
            driver.execute_script("arguments[0].click();", element)

    try:
        for _ in range(3):
            try:
                log(f"Waiting for message mentioning @{os.getenv('BOT_NAME')}...")
                msg = WebDriverWait(driver, 30).until(find_valid_mention)
                log("Found valid mention.")
                break
            except StaleElementReferenceException:
                log("Retrying after stale element...")
                time.sleep(1)
        else:
            raise Exception("Could not find valid message.")

        download_image_from_message(msg, log)
        index, ed = get_best_position()
        log(f"Best position: {index+1}, ED: {ed}")

        for _ in range(3):
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: len(msg.find_elements(By.CLASS_NAME, "reactionInner__23977")) >= 4
                )
                reactions = msg.find_elements(By.CLASS_NAME, "reactionInner__23977")
                
                dismiss_new_message_bar()
                scroll_and_click(reactions[index])

                log("Reaction clicked successfully.")
                break
            except StaleElementReferenceException:
                log("Reactions went stale, refinding message...")
                msg = find_valid_mention(driver)
            except IndexError:
                log("Index out of range for reactions.")
                break
    except Exception as e:
        log(f"ERROR in wait_and_click_reaction: {e}")
