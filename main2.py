import undetected_chromedriver as uc
from selenium.webdriver.common.keys import  Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
driver.get("https://web.whatsapp.com")

print("Aguardando WhatsApp Web carregar...")
wait = WebDriverWait(driver, 5)

# XPaths
noti_xpath = "//div[@class='_ak8j']//div[@role='gridcell']//span//span//span[contains(@class,'x140p0ai')]"
msg_in_xpath = '//div[contains(@class,"message-in")]//span[@dir="ltr"]'
msg_out_xpath = '//div[contains(@class,"message-out")]//span[@dir="ltr"]'
sapp_input_xpath = '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[3]/div[1]'

# Espera até a barra lateral aparecer
WebDriverWait(driver, 240).until(EC.presence_of_element_located((By.ID, "side")))

while True:
    bolhas = driver.find_elements(By.XPATH, noti_xpath)
    print(f"Encontradas {len(bolhas)} bolinhas de notificação.")

    if bolhas:
        for chat in bolhas:
            print(chat.text)
            chat.click()
            print("Abri a conversa.")

            time.sleep(5)
            
            #Finding received Messages
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, msg_in_xpath)))
                messages_in = driver.find_elements(By.XPATH, msg_in_xpath)
                
                for msg in messages_in:
                    print("Pessoa:", msg.text)    
            except:
                print("Nenhuma mensagem recebida encontrada ainda.")
                
            #Finding sent Messages
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, msg_out_xpath)))
                messages_out = driver.find_elements(By.XPATH, msg_out_xpath)
                
                for msg in messages_out:
                    print("Eu:", msg.text)
            except:
                print("Nenhuma mensagem enviada encontrada ainda.")
                
            #Chatbot Response
            chat_input = driver.find_element(By.XPATH, sapp_input_xpath)
            try:
                chat_input.send_keys("Ola! Isso é um teste" + Keys.ENTER)
            except:
                print("Apenas administradores podem enviar mensagens!")
            close = input("Repetir?S/N")
            if close == "S":
                driver.quit()
