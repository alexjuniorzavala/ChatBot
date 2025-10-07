from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options  # Importe isso para opções
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

service = Service(executable_path="msedgedriver.exe")

# Configura opções para usar o perfil existente
options = Options()
options.add_argument(r"--user-data-dir=D:\Alex\Projetos\Python\Chatbot\EdgeProfile")  # Substitua pelo caminho real
options.add_argument("--profile-directory=Default")  # "Default" é o perfil padrão; mude se for outro

# Inicia o driver com as opções
driver = webdriver.Edge(service=service, options=options)

# Abre o WhatsApp Web – se a sessão existir, não pedirá QR Code novamente
driver.get('https://web.whatsapp.com')
print("Aguardando carregamento... Se já logado, deve abrir direto.")

# Search for new notifications
wait = WebDriverWait(driver, 5)
noti_cls = "x1rg5ohu"
time.sleep(20)
noti = driver.find_elements(By.CLASS_NAME, noti_cls)
noti[0].click


input("Pressione Enter após garantir que o WhatsApp Web está carregado...")



driver.quit()