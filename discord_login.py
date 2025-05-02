from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import EMAIL, PASSWORD, GUILD_ID, CHANNEL_ID

def login(driver, log):
    driver.get(f"https://discord.com/login?redirect_to=%2Fchannels%2F{GUILD_ID}%2F{CHANNEL_ID}")
    wait = WebDriverWait(driver, 10)
    email_input = wait.until(EC.presence_of_element_located((By.NAME, 'email')))
    password_input = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
    email_input.send_keys(EMAIL)
    password_input.send_keys(PASSWORD)
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()
    log("Triggered login click.")
