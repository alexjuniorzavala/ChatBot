import undetected_chromedriver as uc
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
noti_xpath = "//div[@class='_ak8j']//div[@role='gridcell']//span//div[contains(@class,'_ahlk')]//span//span[contains(@class,'x140p0ai')]"
msg_in_xpath = '//div[contains(@class,"message-in")]//span[@dir="ltr"]'
msg_out_xpath = '//div[contains(@class,"message-out")]//span[@dir="ltr"]'

# Espera até a barra lateral aparecer
WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "side")))

try:
    bolhas = driver.find_elements(By.XPATH, noti_xpath)
    print(f"Encontradas {len(bolhas)} bolinhas de notificação.")

    if bolhas:
        for qty_msg in bolhas:
            print(qty_msg.text)
        
        bolhas[0].click()
        print("Abri a conversa.")

        time.sleep(5)
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, msg_in_xpath)))
        except:
            print("Nenhuma mensagem recebida encontrada ainda.")

        try:
            wait.until(EC.presence_of_element_located((By.XPATH, msg_out_xpath)))
        except:
            print("Nenhuma mensagem enviada encontrada ainda.")

        messages_in = driver.find_elements(By.XPATH, msg_in_xpath)
        messages_out = driver.find_elements(By.XPATH, msg_out_xpath)

        for msg in messages_in:
            print("Pessoa:", msg.text)

        for msg in messages_out:
            print("Eu:", msg.text)

except Exception as e:
    print("Erro:", e)
input("\nPressione Enter para fechar...")
driver.quit()