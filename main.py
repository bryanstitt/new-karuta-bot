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
    
    print("Logged in successfully.")

# Navigate to a specific server
def navigate_to_server(server_name):
    try:
        actions.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys(Keys.ARROW_DOWN).key_up(Keys.ALT).key_up(Keys.CONTROL).perform()
        print(f"Navigated to {server_name}")
    except Exception as e:
        print(f"Error navigating to server: {e}")

# Navigate to a specific channel
def navigate_to_channel(channel_name):
    try:
        wait = WebDriverWait(driver, 15)
        # Match the div by its exact visible text
        channel_element = wait.until(EC.element_to_be_clickable((
            By.XPATH, f'//div[text()="{channel_name}"]'
        )))
        channel_element.click()
        print(f"Navigated to channel: {channel_name}")
    except Exception as e:
        print(f"Error navigating to channel: {e}")

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
        print(f"Sent message: {trigger}")

    except Exception as e:
        print(f"Error: {e}")

def wait_for_karuta_message(timeout=120, check_interval=1):
    print("Waiting for new Karuta message...")
    start_time = time.time()
    
    # Get initial count of messages to ignore existing ones
    initial_messages = driver.find_elements(By.CLASS_NAME, "message__5126c")
    last_known_count = len(initial_messages)
    
    while time.time() - start_time < timeout:
        try:
            # Get current messages
            current_messages = driver.find_elements(By.CLASS_NAME, "message__5126c")
            current_count = len(current_messages)
            
            # Only proceed if new messages have appeared
            if current_count > last_known_count:
                # Check only the new messages (the ones that appeared since last check)
                for message in current_messages[last_known_count:]:
                    try:
                        username = message.find_element(By.CLASS_NAME, "username_c19a55").text
                        if username.lower() == "karuta":
                            print("Found new message from Karuta.")
                            return message
                    except:
                        continue  # Skip if we can't check this message
                
                # Update the count for next iteration
                last_known_count = current_count
                
        except Exception as e:
            print(f"Error while checking for messages: {str(e)}")
        
        # Wait before checking again
        time.sleep(check_interval)
    
    raise TimeoutError(f"Timed out after {timeout} seconds waiting for new Karuta message.")

def download_image_from_message(message_element):
    try:
        link = message_element.find_element(By.TAG_NAME, "a")
        href = link.get_attribute("href")
        print(f"Downloading image from: {href}")
        r = requests.get(href)

        with open("discord_image.png", "wb") as f:
            f.write(r.content)

        print("Image downloaded as discord_image.png")
    except Exception as e:
        print("Failed to download image:", e)

def send_reaction(index_ed_tuple):
    try:
        index, ed = index_ed_tuple
        print(f"Sending reaction: {index} with ED: {ed}")

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
    except Exception as e:
        print("Failed to send reaction:", e)


# Main execution
if __name__ == "__main__":
    load_dotenv()
    # Get credentials from environment variables
    email = os.getenv('DISCORD_EMAIL')
    password = os.getenv('DISCORD_PASSWORD')
    
    if not email or not password:
        raise ValueError("Please set your Discord email and password in the environment variables.")
    
    login(email, password)
    
    # Add a delay to handle any dynamic content loading
    time.sleep(random.uniform(5, 8))
    
    # Navigate to specific server and channel
    navigate_to_server(" The Boys Hangout")

    time.sleep(random.uniform(1, 2))

    navigate_to_channel("baruta-kots")
    
    print("Initialize")

    while True:

        time.sleep(random.uniform(1, 2))

        send_kd()

        message = wait_for_karuta_message()
        download_image_from_message(message)

        index, ed = get_best_position()

        time.sleep(5)

        send_reaction((index, ed))

        time.sleep(900)