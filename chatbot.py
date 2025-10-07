import undetected_chromedriver as uc
from selenium.webdriver.common.keys import  Keys
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
driver.get("https://chatgpt.com/g/g-p-68d82477fda0819186d2894fa194fad0-atendimento/c/68d82533-a3c4-8333-ab33-c4868ab03b02")

print("Aguardando WhatsApp Web carregar...")
wait = WebDriverWait(driver, 5)

# XPath para capturar as mensagens do chatbot
chatbot_messages_xpath = "//article[@data-turn='assistant']//div[contains(@class,'markdown')]"

# Encontrar todos os elementos de resposta do chatbot
wait.until(EC.presence_of_element_located((By.XPATH, chatbot_messages_xpath)))

chatbot_messages = driver.find_elements(By.XPATH, chatbot_messages_xpath)

for msg in chatbot_messages:
    print("Chatbot:", msg.text)
    
input("Digite enter para sair")
	
time.sleep(3)
driver.quit()
