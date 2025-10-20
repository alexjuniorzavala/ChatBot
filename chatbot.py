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

# Ajuste para manter sessão logada
user_data = r"D:\Alex\Projetos\Python\Chatbot\ChromeProfile"
profile_dir = "Default"

path_driver = r"D:\Alex\Projetos\Python\Chatbot\chromedriver.exe"

options = uc.ChromeOptions()
options.add_argument(f"--user-data-dir={user_data}")
options.add_argument(f"--profile-directory={profile_dir}")
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = uc.Chrome(driver_executable_path=path_driver, options=options)

# Updated JavaScript snippet for WhatsApp's contenteditable input
def paste_content(driver, el, content):
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


chat_rows_xpath = '//div[@role="row"]'
title_element_xpath = './/span[@title]'
whatsapp_input_xpath = '//div[@aria-owns="emoji-suggestion" and contains(@aria-label, "Escreva na conversa")]'

driver.get("https://web.whatsapp.com")
print("Aguardando WhatsApp Web carregar...")
wait = WebDriverWait(driver, 20)
WebDriverWait(driver, 600).until(EC.presence_of_element_located((By.ID, "side")))

# Cada "linha de chat"
chat_rows = driver.find_elements(By.XPATH, chat_rows_xpath)
print(f"Found {len(chat_rows)} chat rows.")

if chat_rows:
    chat_rows[0].click()
    time.sleep(2)  # Small delay to ensure chat loads
    wait.until(EC.element_to_be_clickable((By.XPATH, whatsapp_input_xpath)))
    input_elem = driver.find_element(By.XPATH, whatsapp_input_xpath)  # Use find_element (singular)
    
    input('Press Enter to send "Ola"')
    msg="👏ola"
    paste_content(driver, input_elem, msg)
    input_elem.send_keys(Keys.ENTER)  # Send the message

    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)

input("Press ENTER to exit")

driver.quit()