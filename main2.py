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
from datetime import datetime
import hashlib
import json
import time
import sys
import os
import re


# Ajuste para manter sessão logada
user_data = r"D:\Alex\Projetos\Python\Chatbot\ChromeProfile"
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
    version_main=141  # Match your Chrome version
)
driver.get("https://web.whatsapp.com")

print("Aguardando WhatsApp Web carregar...")
wait = WebDriverWait(driver, 10)

# XPaths
notif_xpath = ".//span[contains(@class,'x140p0ai')]"
unread_filter_page_xpath = '//div[@aria-placeholder="Procurar nas conversas não lidas"]'
unread_filter_xpath = '//div[@aria-label="chat-list-filters"]//div[@id="unread-filter"]'
all_filter_xpath = '//button[@id="all-filter"]'
search_bar_xpath = '//div[@aria-placeholder="Procurar ou criar uma nova conversa"]'
msg_in_xpath = '//div[@id="main"]//div[@class="x1n2onr6"]//div[contains(@class,"message-in")]//span[@class="_ao3e selectable-text copyable-text"]'
msg_out_xpath = '//div[@id="main"]//div[@class="x1n2onr6"]//div[contains(@class,"message-out")]//span[@class="_ao3e selectable-text copyable-text"]'
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
chatbot_url = "https://chatgpt.com/g/g-p-68f67b7860e481918e75084ecf503779-assistente-de-mensagens/c/68f67c01-4fe0-832f-9316-2d5c15d47752"
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
#Data files
PENDING_FILE = "pending_responses.json"
HISTORY_FILE = "response_history.json"

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

# Filtrar mensagens não lidas
for _ in range(3):  # Retry up to 3 times
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, unread_filter_xpath)))
        unread_filter = driver.find_element(By.XPATH, unread_filter_xpath)
        unread_filter.click()
        print("Filtered for unread messages.")
        break
    except Exception as e:
        print(f"Error clicking unread filter: {e}")
        time.sleep(2)

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
 
 
#Saving Pending responses that failed to load from chatbot response
def save_pending(contact, unread_messages, context_messages, payload):
    pending = {
        "contact": contact,
        "unread_messages": unread_messages,
        "context_messages": context_messages,
        "payload": payload,
        "last_response": None,
        "attempts": 0,
        "timestamp": datetime.now().isoformat()
    }

    data = []
    if os.path.exists(PENDING_FILE):
        try:
            with open(PENDING_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            pass

    # Evita duplicatas
    duplicate = any(
        p["contact"] == contact and
        p["unread_messages"] == unread_messages and
        p["payload"] == payload
        for p in data
    )
    if not duplicate:
        data.append(pending)
        with open(PENDING_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Pendente salvo: {contact}")
    else:
        print(f"Pendente duplicado ignorado: {contact}")
        
#Load response history to try to respond again
def load_response_history():
    if not os.path.exists(HISTORY_FILE):
        return {"last_response": "", "last_contact": "", "last_payload_hash": ""}
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"last_response": "", "last_contact": "", "last_payload_hash": ""}
        
#Save Response History aftar a fail
def save_response_history(contact, response, payload):
    hash_obj = hashlib.md5(payload.encode('utf-8')).hexdigest()
    data = {
        "last_response": response,
        "last_contact": contact,
        "last_payload_hash": hash_obj
    }
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
        
#Clear Pendings
def clear_pending(contact, unread_messages):
    if not os.path.exists(PENDING_FILE):
        return
    try:
        with open(PENDING_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data = [p for p in data if not (p["contact"] == contact and p["unread_messages"] == unread_messages)]
        with open(PENDING_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass

#Process pending Responses
def process_pending_responses():
    if not os.path.exists(PENDING_FILE):
        return False

    try:
        with open(PENDING_FILE, 'r', encoding='utf-8') as f:
            pendentes = json.load(f)
    except:
        return False

    if not pendentes:
        return False

    print(f"{len(pendentes)} respostas pendentes. Processando...")

    # 1. Clique em "Todos"
    try:
        all_filter = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@id="all-filter"]'))
        )
        all_filter.click()
        print("Filtro 'Todos' ativado.")
        time.sleep(2)
    except:
        print("Erro ao clicar em 'Todos'")

    # 2. Processar cada pendente
    for p in pendentes[:]:
        contact = p["contact"]
        payload = p["payload"]
        unread = p["unread_messages"]

        print(f"Processando pendente: {contact}")

        try:
            # Abrir pesquisa
            search_bar = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@aria-placeholder="Procurar ou criar uma nova conversa"]'))
            )
            search_bar.click()
            clear_input_field(search_bar)
            paste_content(driver, search_bar, contact)
            time.sleep(2)

            # Clicar no contato
            contact_row = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f'.//span[@title="{contact}"]'))
            )
            contact_row.click()
            print(f"Contato aberto: {contact}")
            time.sleep(3)

            # Enviar para ChatGPT
            response = get_chatgpt_response(payload)
            if response and response.strip():
                driver.switch_to.window(whatsapp_handle)
                chat_input = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, whatsapp_input_xpath))
                )
                process_ai_response(response, chat_input)
                save_response_history(contact, response, payload)
                clear_pending(contact, unread)
                print(f"Pendente resolvido: {contact}")
            else:
                p["attempts"] += 1
                if p["attempts"] >= 3:
                    print(f"Máximo de tentativas atingido para {contact}. Removendo.")
                    clear_pending(contact, unread)
                else:
                    print(f"Tentativa {p['attempts']} falhou para {contact}")

        except Exception as e:
            print(f"Erro processando pendente {contact}: {e}")

        time.sleep(3)

    # 3. Voltar para "Não lidas"
    try:
        unread_filter = driver.find_element(By.XPATH, unread_filter_xpath)
        unread_filter.click()
        print("Voltou ao filtro 'Não lidas'.")
    except:
        pass

    # Atualizar arquivo
    with open(PENDING_FILE, 'w', encoding='utf-8') as f:
        json.dump([p for p in pendentes if p["attempts"] < 3], f, ensure_ascii=False, indent=2)

    return len(pendentes) > 0

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
        time.sleep(1)  # Pequena pausa entre texto e foto

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
                        time.sleep(1.5)  # Pausa entre fotos
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
        time.sleep(0.5)
    except Exception as e:
        print(f"Error clearing input field: {e}")
      

# Function to send message to ChatGPT and get response
def get_chatgpt_response(message):
    if not open_chatbot_tab():
        return None
    
    # Send message
    for attempt in range(3):  # Retry up to 3 times
        try:
            input_elem = WebDriverWait(driver, 30).until(
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
                print("Sent message to ChatGPT.")
            except:
                print("Send button not found, trying Enter key.")
                input_elem.send_keys(Keys.ENTER)
                print("Sent message to ChatGPT.")
            
            
            # Wait for streaming to start
            try:
                WebDriverWait(driver, 20).until(
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
            captured = False
            latest_response = ""
            for _ in range(5):
                try:
                    messages = driver.find_elements(By.XPATH, chatgpt_messages_xpath)
                    if messages:
                        latest_response = messages[-1].text.strip()
                        if latest_response != history["last_response"] or title != history["last_contact"]:
                            print(f"ChatGPT response: {latest_response}")
                            captured = True
                            break
                    time.sleep(2)
                except:
                    time.sleep(1)

            if not captured:
                print("Nenhuma resposta nova ou repetida detectada → salvando como pendente")
                save_pending(title, unread_messages, 
                           [f"[{ts.strftime('%I:%M %p, %d/%m/%Y')}] {sender}: {text}" 
                            for ts, sender, text in context_messages],
                           final_payload)
                return None

            # Salvar histórico
            save_response_history(title, latest_response, final_payload)
            return latest_response
            
        except (StaleElementReferenceException, NoSuchElementException) as e:
            print(f"Retry {attempt + 1}/3: Error interacting with ChatGPT input: {e}")
            time.sleep(1)
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

try:
    while True:
        try:
            # Switch back to WhatsApp tab
            driver.switch_to.window(whatsapp_handle)
            
            #Process Pending Chats First
            if process_pending_responses():
                time.sleep(5)
                continue
            
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
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, msg_in_xpath))
                            )
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

            time.sleep(3)

        except Exception as e:
            print(f"General error: {e}")

except KeyboardInterrupt:
    print("Script interrupted by user.")

finally:
    # Cleanup
    print("Cleaning up...")
    driver.quit()
    sys.exit(0)