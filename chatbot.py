import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    NoSuchElementException
)
import time
import sys
import os
import re
from datetime import datetime

# Ajuste para manter sessão logada
user_data = r"D:\Alex\Projetos\Python\Chatbot\ChromeProfileNodeJs"
profile_dir = "Default"

path_driver = r"D:\Alex\Projetos\Python\Chatbot\chromedriver.exe"

options = uc.ChromeOptions()
options.add_argument(f"--user-data-dir={user_data}")
options.add_argument(f"--profile-directory={profile_dir}")
# options.add_argument("--headless=new")  # Enable headless mode
options.add_argument("--disable-gpu")  # Disable GPU for headless
options.add_argument("--window-size=1920,1080")  # Set window size for headless
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
options.add_argument("--disable-infobars")
options.add_argument("--disable-notifications")
options.add_argument("--blink-settings=imagesEnabled=true")
options.add_argument("--disable-features=OnlyBlockMainFrame")
options.add_argument("--disable-web-security")

driver = uc.Chrome(
    driver_executable_path=path_driver,
    options=options,
    version_main=143  # Match your Chrome version
)
driver.get("https://chatgpt.com")

print("Aguardando chatgpt carregar...")
wait = WebDriverWait(driver, 10)


# ChatGPT XPaths
chatbot_url = "https://chatgpt.com"
chat_name_xpath = '//span[@dir="auto"]'
chat_rename_options_xpath ='//*[@id="history"]//div[contains(@class,"trailing text-token-text-tertiary")]'
chat_rename_input_xpath = '//*[@role="menuitem"]'
chatgpt_input_xpath = '//div[@contenteditable="true" and @id="prompt-textarea"]'
chatgpt_send_button_xpath = '//button[@aria-label="Enviar prompt" or contains(@id, "composer-submit-button")]'
chatgpt_messages_xpath = "//article[@data-turn='assistant']//div[contains(@class,'markdown')]"
chatgpt_stop_streaming_button_xpath = '//button[@aria-label="Parar transmissão"]'

def rename_chat(new_name):
    try:
        button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, chat_rename_options_xpath)))
        print("found the rename option")
        try:
            button.click()
            print("Clicked the button")
            try:
                input_dir = WebDriverWait(driver, 60).until(EC.presence_of_all_elements_located((By.XPATH, chat_rename_input_xpath)))
                print("Found the input to rename the dir")
                input_dir[2].click()
                print("clicked the input")
            except:
                print("Didn't found the input")
        except:
            print("Failed to click the rename option button")
    except:
        print("Didn't found! the rename option")
        
rename_chat("a")
    
input()

for _ in range(3):  # Retry up to 3 times
    try:
        print(driver.title)
    except Exception as e:
        print("Nao achei o titulo")
    time.sleep(3)

driver.quit()
