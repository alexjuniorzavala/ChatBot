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
driver.get("https://web.whatsapp.com")

print("Aguardando WhatsApp Web carregar...")
wait = WebDriverWait(driver, 5)

# XPaths
notif_xpath = ".//span[contains(@class,'x140p0ai')]"
msg_in_xpath = '//div[contains(@class,"message-in")]//span[@dir="ltr"]'
chat_rows_xpath = '//div[@role="row"]'
title_element_xpath = './/span[@title]'
msg_out_xpath = '//div[contains(@class,"message-out")]//span[@dir="ltr"]'
sapp_input_xpath = '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[3]/div[1]'
chatbot_url = "https://chatgpt.com/g/g-p-68d82477fda0819186d2894fa194fad0-atendimento/c/68d82533-a3c4-8333-ab33-c4868ab03b02"
# Espera até a barra lateral aparecer
WebDriverWait(driver, 600).until(EC.presence_of_element_located((By.ID, "side")))

while True:
    try:
        # Cada "linha de chat"
        chat_rows = driver.find_elements(By.XPATH, chat_rows_xpath)
        print(f"Found {len(chat_rows)} notification bubbles.")


        for row in chat_rows:
            try:
                # Nome/título do contato
                title_element = row.find_element(By.XPATH, title_element_xpath)
                title = title_element.get_attribute("title")

                # Bolinha de notificação (se existir)
                try:
                    print("Verificando notificações...")
                    notif_element = row.find_element(By.XPATH, notif_xpath)
                    notif_count = notif_element.text
                except:
                    print("No notifications found. notif_count = '0'")
                    notif_count = "0"

                print(f"Contact: {title}, Notifications: {notif_count}")

                # Se houver notificações, abrir o chat
                if notif_count != "0":
                    try:
                        row.click()
                        print("Opened the conversation.")

                        # Mensagens recebidas
                        try:
                            wait.until(EC.presence_of_element_located((By.XPATH, msg_in_xpath)))
                            messages_in = driver.find_elements(By.XPATH, msg_in_xpath)
                            for msg in messages_in:
                                try:
                                    print("Person:", msg.text)
                                except StaleElementReferenceException:
                                    print("Message changed, reloading incoming messages...")
                                    messages_in = driver.find_elements(By.XPATH, msg_in_xpath)
                                    for msg in messages_in:
                                        print("Person:", msg.text)
                        except TimeoutException:
                            print("No incoming messages found yet.")

                        # Mensagens enviadas
                        try:
                            wait.until(EC.presence_of_element_located((By.XPATH, msg_out_xpath)))
                            messages_out = driver.find_elements(By.XPATH, msg_out_xpath)
                            for msg in messages_out:
                                try:
                                    print("Me:", msg.text)
                                except StaleElementReferenceException:
                                    print("Message changed, reloading outgoing  messages...")
                                    messages_out = driver.find_elements(By.XPATH, msg_out_xpath)
                                    for msg in messages_out:
                                        print("Eu:", msg.text)
                        except TimeoutException:
                            print("No outgoing messages found yet.")
                        # Com base no numero de notificacoes pegue as mesagens recebidas nao lidas, abre a pagina chatbot(url na variavel chatgpt_url) numa outra aba(se nao estiver aberto ainda)


                        # Resposta do chatbot
                        try:
                            chat_input = driver.find_element(By.XPATH, sapp_input_xpath)
                            chat_input.send_keys("Hello! This is a test")
                            print("Message sent!")
                        except (NoSuchElementException, StaleElementReferenceException):
                            print("Cannot send messages in this chat (admins only?).")

                        # Pergunta se deseja repetir
                        close = input("Repeat? (Y/N): ").strip().upper()
                        if close == "N":
                            driver.quit()
                            exit()

                    except Exception as e:
                        print("Erro ao manipular chat:", e)

            except:
                continue


    except Exception as e:
        print("General error:", e)
        time.sleep(5)