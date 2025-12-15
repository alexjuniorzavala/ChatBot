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
driver.get("https://web.whatsapp.com")

print("Aguardando WhatsApp Web carregar...")
wait = WebDriverWait(driver, 10)

#WhatsApp XPaths
notif_xpath = ".//span[contains(@aria-label,'mensagem não lida') or contains(@aria-label,'mensagens não lidas')]"
unread_filter_page_xpath = '//div[@aria-placeholder="Procurar nas conversas não lidas"]'
unread_filter_xpath = '//*[@id="unread-filter"]'
msg_in_xpath = '//div[contains(@class,"message-in")]//span[contains(@class,"_ao3e selectable-text copyable-text")]'
msg_out_xpath = '//div[contains(@class,"message-out")]//span[contains(@class,"_ao3e selectable-text copyable-text")]'
chat_rows_xpath = '//div[contains(@class,"x1g42fcv")]'
title_element_xpath = './/span[@title or contains(@class, "x1qlqyl8")]'
whatsapp_input_xpath = '//div[@aria-owns="emoji-suggestion" and (contains(@aria-label, "Escreva na conversa") or contains(@aria-label, "Escreva no grupo"))]'
attachment_button_xpath = '//span[@data-icon="plus-rounded"]'
file_input_xpath = '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'  # For images/videos
document_input_xpath = '//input[@accept="*"]'  # For documents
send_file_button_xpath = '//div[@class="x1n2onr6"]//div[@aria-label="Enviar"]'
captcha_xpath = '//iframe[contains(@src, "recaptcha")]'
qr_code_xpath = '//canvas[@aria-label="Scan me!"]'

# ChatGPT XPaths
chatbot_url = "https://chatgpt.com"
chat_name_xpath = '//span[@dir="auto"]'
chat_rename_options_xpath ='//*[@id="history"]//div[contains(@class,"trailing text-token-text-tertiary")]'
chat_rename_input_xpath = '//*[@role="menuitem"]'
chatgpt_input_xpath = '//div[@contenteditable="true" and @id="prompt-textarea"]'
chatgpt_send_button_xpath = '//button[@aria-label="Enviar prompt" or contains(@id, "composer-submit-button")]'
chatgpt_messages_xpath = "//article[@data-turn='assistant']//div[contains(@class,'markdown')]"
chatgpt_stop_streaming_button_xpath = '//button[@aria-label="Parar transmissão"]'

# Dicionário de comandos → lista de arquivos
COMANDOS_FOTOS = {
    "PRINTS_LIVRO_DE_RECEITAS": [
        r"D:\Alex\Vendas\InfoProdutos\Receitas\PRINTS_LIVRO_DE_RECEITAS\PRINTS_LIVRO_DE_RECEITAS1.png",
        r"D:\Alex\Vendas\InfoProdutos\Receitas\PRINTS_LIVRO_DE_RECEITAS\PRINTS_LIVRO_DE_RECEITAS2.png",
        # Adicione mais se quiser
    ],
    "AMOSTRA_DO_LIVRO": [
        r"D:\Alex\Vendas\InfoProdutos\Receitas\Amostra_do_livro.pdf"
    ],
    # Adicione outros comandos aqui
}

# Check for CAPTCHA or QR code
# try:
    # WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "side")))
    # print("WhatsApp sidebar loaded.")
# except TimeoutException:
    # print("Sidebar not loaded. Checking for CAPTCHA or QR code...")
    # try:
        # captcha = driver.find_element(By.XPATH, captcha_xpath)
        # print("CAPTCHA detected. Saving screenshot...")
        # driver.save_screenshot("captcha.png")
        # print("CAPTCHA screenshot saved as captcha.png. Solve it manually in non-headless mode.")
        # driver.quit()
        # sys.exit(1)
    # except NoSuchElementException:
        # try:
            # qr_code = driver.find_element(By.XPATH, qr_code_xpath)
            # qr_code.screenshot("qr_code.png")
            # print("QR code detected. Saved as qr_code.png. Scan it with your phone.")
            # WebDriverWait(driver, 600).until(EC.presence_of_element_located((By.ID, "side")))
            # print("WhatsApp sidebar loaded after QR code scan.")
        # except NoSuchElementException:
            # print("Neither CAPTCHA nor QR code found. Ensure Chrome profile has a valid session.")
            # driver.quit()
            # sys.exit(1)


# Variables for tab handles
whatsapp_handle = driver.current_window_handle
chatbot_handle = None

# JavaScript snippet for WhatsApp's contenteditable input
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
        

def process_ai_response(response, chat_input):
    """
    Processa a resposta do ChatGPT:
    - Detecta comandos [ENVIAR_FOTO:XXX]
    - Remove os comandos
    - Envia as fotos correspondentes
    - Envia o texto limpo
    """
    if not response:
        return False

    # Regex para capturar todos os tokens [ENVIAR_FOTO:XXX]
    pattern = r'\[ENVIAR_DOCUMENTO:([^\]]+)\]'
    comandos_encontrados = re.findall(pattern, response)

    # Remove todos os tokens do texto
    texto_limpo = re.sub(pattern, '', response).strip()

    # Envia o texto limpo (se houver)
    if texto_limpo:
        clear_input_field(chat_input)
        paste_content(driver, chat_input, texto_limpo)
        chat_input.send_keys(Keys.ENTER)
        print(f"Texto enviado: {texto_limpo}")
        time.sleep(2)  # Pequena pausa entre texto e foto

    # Envia as fotos, se houver comandos
    if comandos_encontrados:
        for comando in comandos_encontrados:
            if comando in COMANDOS_FOTOS:
                arquivos = COMANDOS_FOTOS[comando]
                for arquivo in arquivos:
                    if os.path.exists(arquivo):
                        sucesso = send_file_to_whatsapp(arquivo)
                        if sucesso:
                            print(f"Foto enviada: {os.path.basename(arquivo)}")
                        time.sleep(3)  # Pausa entre fotos
                    else:
                        print(f"Arquivo não encontrado: {arquivo}")
            else:
                print(f"Comando desconhecido: [ENVIAR_FOTO:{comando}]")
        return True
    return False
        
#Sending files to whatsapp 
def send_file_to_whatsapp(file_path):
    try:
        if not os.path.exists(file_path):
            print(f"Arquivo não encontrado: {file_path}")
            return False

        # Clica no botão de anexar
        attachment_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, attachment_button_xpath))
        )
        driver.execute_script("arguments[0].click();", attachment_button)
        print("Botão de anexar clicado.")

        # Seleciona o arquivo
        document_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, document_input_xpath))
        )
        document_input.send_keys(file_path)
        print(f"Arquivo selecionado: {os.path.basename(file_path)}")

        # Envia
        send_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, send_file_button_xpath))
        )
        driver.execute_script("arguments[0].click();", send_button)
        print("Ficheiro enviado com sucesso!")
        return True

    except Exception as e:
        print(f"Erro ao enviar arquivo: {e}")
        return False

# Function to open ChatGPT tab if not open
def open_chatbot_tab():
    global chatbot_handle
    if chatbot_handle is None:
        driver.execute_script(f"window.open('{chatbot_url}', '_blank');")
        driver.switch_to.window(driver.window_handles[1])
        chatbot_handle = driver.current_window_handle
        print("Opened ChatGPT tab.")
        try:
            WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, chatgpt_input_xpath)))
            print("ChatGPT input field loaded.")
            return True
        except TimeoutException:
            print("Timeout waiting for ChatGPT input field. Refreshing page...")
            driver.refresh()
            try:
                WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, chatgpt_input_xpath)))
                print("ChatGPT input field loaded after refresh.")
                return True
            except TimeoutException:
                print("Failed to load ChatGPT input field after refresh.")
                return False
    else:
        driver.switch_to.window(chatbot_handle)
        return True

# Function to clear input field
def clear_input_field(input_elem):
    try:
        input_elem.click()
        input_elem.send_keys(Keys.CONTROL + "a")  # Select all
        input_elem.send_keys(Keys.DELETE)  # Delete
        time.sleep(3)
    except Exception as e:
        print(f"Error clearing input field: {e}")
      

# Function to send message to ChatGPT and get response
def get_chatgpt_response(message):
    if not open_chatbot_tab():
        return None
    
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

# Function to parse timestamp from data-pre-plain-text
def parse_timestamp(timestamp_str):
    try:
        # Example: "[10:29 AM, 13/10/2025] Livre Expresso: "
        match = re.match(r"\[(\d{1,2}:\d{2}\s[AP]M),\s(\d{2}/\d{2}/\d{4})\]", timestamp_str)
        if match:
            time_str, date_str = match.groups()
            return datetime.strptime(f"{time_str}, {date_str}", "%I:%M %p, %d/%m/%Y")
        return None
    except:
        return None
        
# Filtrar mensagens não lidas
for _ in range(3):  # Retry up to 3 times
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, unread_filter_xpath)))
        unread_filter = driver.find_element(By.XPATH, unread_filter_xpath)
        unread_filter.click()
        print("Filtered for unread messages.")
        break
    except Exception as e:
        print(f"Error clicking unread filter: {e}")
        time.sleep(3)        

try:
    while True:
        try:
            # Switch back to WhatsApp tab
            driver.switch_to.window(whatsapp_handle)
            
            # If element unread_filter_page not found, click unread filter again
            if not driver.find_elements(By.XPATH, unread_filter_page_xpath):
                try:
                    unread_filter = WebDriverWait(driver, 1).until(
                        EC.element_to_be_clickable((By.XPATH, unread_filter_xpath))
                    )
                    unread_filter.click()
                    print("Clicked unread filter again.")
                except Exception as e:
                    print(f"Error clicking unread filter again: {e}")
            
            # Wait for chat list to load
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.XPATH, chat_rows_xpath))
                )
            except TimeoutException:
                print("No chat rows found")
            
            # Cada "linha de chat"
            chat_rows = driver.find_elements(By.XPATH, chat_rows_xpath)
            print(f"Found {len(chat_rows)} chat rows.")

            for row in chat_rows:
                try:
                    # Nome/título do contato
                    try:
                        title_element = row.find_element(By.XPATH, title_element_xpath)
                        title = title_element.get_attribute("title") or title_element.text.strip()
                    except NoSuchElementException:
                        print("Title element not found, skipping row.")
                        continue

                    # Bolinha de notificação (se existir)
                    try:
                        notif_element = row.find_element(By.XPATH, notif_xpath)
                        notif_count = int(notif_element.text)
                    except:
                        notif_count = 0

                    # Skip specific contact
                    if title == "Eng. Electrónica UEM 2025":
                        notif_count = 0
                        
                    print(f"Contact: {title}, Notifications: {notif_count}")
                    
                    # Se houver notificações, abrir o chat
                    if notif_count > 0:
                        try:
                            row.click()
                            print(f"Opened conversation with {title}.")

                            # Wait for messages to load
                            if WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, msg_in_xpath))):
                                print('Achei a msg_in_xpath')
                            # chat_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, whatsapp_input_xpath)))
                            # clear_input_field(chat_input)
                            # chat_input.send_keys("Nao saia... Resposta a caminho" + Keys.ENTER)
                            # Get all incoming and outgoing messages
                            messages_in = driver.find_elements(By.XPATH, msg_in_xpath)
                            messages_out = driver.find_elements(By.XPATH, msg_out_xpath)
                            
                            # Combine and sort messages by timestamp
                            all_messages = []
                            for msg in messages_in:
                                try:
                                    parent = msg.find_element(By.XPATH, "./ancestor::div[@data-pre-plain-text]")
                                    timestamp_str = parent.get_attribute("data-pre-plain-text")
                                    timestamp = parse_timestamp(timestamp_str)
                                    sender = "Client"
                                    all_messages.append((timestamp, sender, msg.text.strip()))
                                except:
                                    continue
                            for msg in messages_out:
                                try:
                                    parent = msg.find_element(By.XPATH, "./ancestor::div[@data-pre-plain-text]")
                                    timestamp_str = parent.get_attribute("data-pre-plain-text")
                                    timestamp = parse_timestamp(timestamp_str)
                                    sender = "Assistant"
                                    all_messages.append((timestamp, sender, msg.text.strip()))
                                except:
                                    continue

                            # Sort by timestamp (newest first) and take last 4
                            all_messages.sort(key=lambda x: x[0], reverse=True)
                            context_messages = all_messages[:4]  # Last 4 interactions
                            
                            # Get unread messages (last notif_count)
                            unread_messages = [msg.text.strip() for msg in messages_in[-notif_count:]]
                            if not unread_messages:
                                print("No unread messages found.")
                                continue
                            
                            print(f"Unread messages from {title}: {unread_messages}")
                            
                            # Build context string
                            contact_line = f"Mensagem enviada por: {title}"
                            context_lines = ["Mensagens de contexto:"]
                            for timestamp, sender, text in context_messages:
                                context_lines.append(f"[{timestamp.strftime('%I:%M %p, %d/%m/%Y')}] {sender}: {text}")
                            context_str = "\n".join(context_lines)
                            unread_str = "\nMensagem não lida:\n" + "\n".join(unread_messages)
                            final_payload = f"{contact_line}\n\n{context_str}\n\n{unread_str}"
                            
                            print(f"Final payload for ChatGPT:\n{final_payload}")
                            
                            # Get response from ChatGPT
                            response = get_chatgpt_response(final_payload)
                            if response:
                                # Switch back to WhatsApp
                                driver.switch_to.window(whatsapp_handle)
                                
                                try:
                                    chat_input = WebDriverWait(driver, 10).until(
                                        EC.element_to_be_clickable((By.XPATH, whatsapp_input_xpath))
                                    )
                                    
                                    # Processa a resposta: envia texto + fotos se necessário
                                    process_ai_response(response, chat_input)
                                    
                                except Exception as e:
                                    print(f"Erro ao processar resposta: {e}")
                            else:
                                print("No response from ChatGPT.")

                        except Exception as e:
                            print(f"Error handling chat with {title}: {e}")

                except Exception as e:
                    print(f"Error processing row: {e}")
                    continue

                # Back Focus to chat rows (titles)
                try:
                    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                    
                except Exception as e:
                    print(f"Error sending ESCAPE key: {e}")

            time.sleep(10)

        except Exception as e:
            print(f"General error: {e}")

except KeyboardInterrupt:
    print("Script interrupted by user.")

finally:
    # Cleanup
    print("Cleaning up...")
    driver.quit()
    sys.exit(0)