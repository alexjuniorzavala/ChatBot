from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options  # Importe isso para opções
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Caminho para o driver (ajuste se necessário)
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
input("Pressione Enter após garantir que o WhatsApp Web está carregado...")
# Seu loop de monitoramento aqui (do código anterior)
# ...

driver.quit()