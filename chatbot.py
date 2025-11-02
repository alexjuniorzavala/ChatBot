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
import os

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
# driver = uc.Chrome(driver_executable_path=path_driver)
# Updated JavaScript snippet for WhatsApp's contenteditable input
# def paste_content(driver, el, content):
    # driver.execute_script(
      # f'''
# const text = `{content}`;
# const dataTransfer = new DataTransfer();
# dataTransfer.setData('text', text);
# const event = new ClipboardEvent('paste', {{
  # clipboardData: dataTransfer,
  # bubbles: true
# }});
# arguments[0].dispatchEvent(event)
# ''',
      # el)


# chat_rows_xpath = '//div[@role="row"]'
# title_element_xpath = './/span[@title]'
# whatsapp_input_xpath = '//div[@aria-owns="emoji-suggestion" and contains(@aria-label, "Escreva na conversa")]'
# attachment_button_xpath = '//span[@data-icon="plus-rounded"]'
# file_input_xpath = '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'  # For images/videos
# document_input_xpath = '//input[@accept="*"]'  # For documents
# send_file_button_xpath = '//div[@class="x1n2onr6"]//div[@aria-label="Enviar"]'

driver.get("https://chatgpt.com")
print("Aguardando WhatsApp Web carregar...")
wait = WebDriverWait(driver, 20)
# WebDriverWait(driver, 600).until(EC.presence_of_element_located((By.ID, "side")))

# # Cada "linha de chat"
# chat_rows = driver.find_elements(By.XPATH, chat_rows_xpath)
# print(f"Found {len(chat_rows)} chat rows.")

# def send_file_to_whatsapp(file_path):
    # try:
        # if not os.path.exists(file_path):
            # print(f"File not found: {file_path}")
            # return False
        
        # # Click attachment button
        # wait.until(EC.element_to_be_clickable((By.XPATH, attachment_button_xpath)))
        # attachment_button = driver.find_element(By.XPATH, attachment_button_xpath)
        # attachment_button.click()
        # print("Clicked attachment button.")

        # # Select file input (assuming image/video for this example)
        # wait.until(EC.presence_of_element_located((By.XPATH, file_input_xpath)))
        # file_input = driver.find_element(By.XPATH, file_input_xpath)
        # file_input.send_keys(file_path)
        # print(f"Selected file: {file_path}")

        # # Wait for preview and click send
        # wait.until(EC.element_to_be_clickable((By.XPATH, send_file_button_xpath)))
        # send_button = driver.find_element(By.XPATH, send_file_button_xpath)
        # send_button.click()
        # print("File sent successfully.")
        # return True
    # except Exception as e:
        # print(f"Error sending file: {e}")
        # return False
# chatgpt_input_xpath = '//div[@contenteditable="true" and @id="prompt-textarea"]'

# if chat_rows:
    # chat_rows[0].click()
    # time.sleep(2)  # Small delay to ensure chat loads
    # wait.until(EC.element_to_be_clickable((By.XPATH, whatsapp_input_xpath)))
    # file_path = r"D:\Alex\Vendas\InfoProdutos\Guia do Empreendedor\Annotation 2025-06-23 114739.png"
time.sleep(30)
# chatgpt_input_xpath = '//div[@contenteditable="true" and @id="prompt-textarea"]'
# WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, chatgpt_input_xpath)))    
# driver.get_screenshot_as_file("screenshot.png")
# print(driver.execute_script("return document.querySelector('div[aria-owns=\"emoji-suggestion\"][aria-label*=\"Escreva na conversa\"], div[aria-owns=\"emoji-suggestion\"][aria-label*=\"Escreva no grupo\"]')"))
# print(driver.execute_script("return document.querySelector('div[@id=\"prompt-textarea\"]')"))





input("Press ENTER to exit")

driver.quit()