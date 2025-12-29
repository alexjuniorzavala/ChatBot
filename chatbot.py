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
chat_menu_button_xpath ='.//div[contains(@class,"trailing text-token-text-tertiary")]'
chat_rename_input_xpath = '//*[@role="menuitem"]'
chatgpt_input_xpath = '//div[@contenteditable="true" and @id="prompt-textarea"]'
chatgpt_send_button_xpath = '//button[@aria-label="Enviar prompt" or contains(@id, "composer-submit-button")]'
chatgpt_messages_xpath = "//article[@data-turn='assistant']//div[contains(@class,'markdown')]"
chatgpt_stop_streaming_button_xpath = '//button[@aria-label="Parar transmissão"]'

def clear_input_field(input_elem):
    try:
        input_elem.click()
        input_elem.send_keys(Keys.CONTROL + "a")  # Select all
        input_elem.send_keys(Keys.DELETE)  # Delete
        time.sleep(3)
    except Exception as e:
        print(f"Error clearing input field: {e}")
        
def paste_content(driver, el, content):
    try:
        driver.execute_script(
            f'''
const text = `{content}`;
const dataTransfer = new DataTransfer();
dataTransfer.setData('text', text);
const event = new ClipboardEvent('paste', {{
  clipboardData: dataTransfer,
  bubbles: true
}});
arguments[0].dispatchEvent(event)
''',
            el)
    except Exception as e:
        print(f"Error in paste_content: {e}")

def rename_chatgpt_to_contact(title):
    try:
        current_title = driver.title
        if current_title == title:
            return True
        print(f"Renomeando chat para: {title}")

        chat_to_rename_xpath = '//*[@id="history"]/a[@data-active]'
        chat_to_rename = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, chat_to_rename_xpath)))
        print('Achei o chat ativo')
        menu_btn = chat_to_rename.find_element(By.XPATH, chat_menu_button_xpath)
        print('achei o botao de opcoes para renomear')
        menu_btn.click()
        print('Cliquei nele')
        time.sleep(1)
        
        print("clicked the menu button")
        rename_btn = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, chat_rename_input_xpath)))
        rename_btn[2].click()
        print("Clickerd the rename_btn")
        active = driver.switch_to.active_element
        print("Found the body element")
        time.sleep(2)
        active.send_keys(title)
        active.send_keys(Keys.ENTER)
        print(f"Chat renomeado para: {title}")
        return True
    except Exception as e:
        print(f"Erro ao renomear chat: {e}")
        return False
    
def get_chatgpt_response(message):

    # Send message
    for attempt in range(3):  # Retry up to 3 times
        try:
            input_elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, chatgpt_input_xpath))
            )
            clear_input_field(input_elem)
            paste_content(driver, input_elem, message)
            
            # Try clicking send button
            try:
                send_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, chatgpt_send_button_xpath))
                )
                send_button.click()
                print("Sent message to ChatGPT. By Click")                
            except (TimeoutException, NoSuchElementException):
                print("Send button not found, trying Enter key.")
                input_elem.send_keys(Keys.ENTER)
                print("Sent message to ChatGPT. By ENTER")

            
            # Wait for streaming to start
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, chatgpt_stop_streaming_button_xpath))
                )
                print("Streaming started...")
            except TimeoutException:
                print("No streaming button detected, possibly instant response.")
            
            # Wait for streaming to complete (button disappears)
            try:
                WebDriverWait(driver, 60).until(
                    EC.invisibility_of_element_located((By.XPATH, chatgpt_stop_streaming_button_xpath))
                )
                print("Streaming completed.")
            except TimeoutException:
                print("Timeout waiting for streaming to complete, proceeding to capture response.")
            
            # Capture the full response
            for _ in range(3):  # Retry to handle stale elements
                try:
                    messages = driver.find_elements(By.XPATH, chatgpt_messages_xpath)
                    if messages:
                        latest_response = messages[-1].text.strip()
                        if latest_response:
                            print(f"ChatGPT response: {latest_response}")
                            return latest_response
                    time.sleep(3)
                except StaleElementReferenceException:
                    print("Stale element detected, retrying to capture response...")
            print("No response captured after retries.")
            return None
        except (StaleElementReferenceException, NoSuchElementException) as e:
            print(f"Retry {attempt + 1}/3: Error interacting with ChatGPT input: {e}")
            time.sleep(3)
    print("Failed to send message to ChatGPT after retries.")
    return None
    
def find_the_contact(contact):
    chat_name = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.XPATH,
            f"//span[@dir='auto' and normalize-space(.)='{contact}']"
        ))
    )
    return chat_name

contact = '1234'
try:
    chat_name = find_the_contact(contact)
    print(f"Achei o chat_name {contact}")
    chat_name.click()
except:
    print(f"Nao achei o chat_name {contact}. Criando novo chat")
    new_chat_xpath = '//*[@id="stage-slideover-sidebar"]/div/div[2]/nav/aside/a[1]'
    new_chat =  WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.XPATH,
            new_chat_xpath
        ))
    )
    print('Achei o botao para iniciar novo chat')
    new_chat.click()
    print('cliquei no botao')
    get_chatgpt_response("Hola")
    print('Peguei a resposta do chatgpt')
    rename_chatgpt_to_contact(contact)
    print('Renomiei o chat com sucesso')
    
    
    
input()

for _ in range(3):  # Retry up to 3 times
    try:
        print(driver.title)
    except Exception as e:
        print("Nao achei o titulo")
    time.sleep(3)

driver.quit()
