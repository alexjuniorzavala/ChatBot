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
wait = WebDriverWait(driver, 10)

# XPaths
notif_xpath = ".//span[contains(@class,'x140p0ai')]"
unread_filter_xpath = '//div[@aria-label="chat-list-filters"]//button[@id="unread-filter"]'
msg_in_xpath = '//div[contains(@class,"message-in")]//span[@dir="ltr"]'
chat_rows_xpath = '//div[@role="row"]'
title_element_xpath = './/span[@title]'
msg_out_xpath = '//div[contains(@class,"message-out")]//span[@dir="ltr"]'
whatsapp_input_xpath = '//div[@aria-owns="emoji-suggestion" and contains(@aria-label, "Escreva na conversa") or contains(@aria-label, "Escreva no grupo")]'
attachment_button_xpath = '//span[@data-icon="plus-rounded"]'
file_input_xpath = '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'  # For images/videos
document_input_xpath = '//input[@accept="*"]'  # For documents
send_file_button_xpath = '//div[@class="x1n2onr6"]//div[@aria-label="Enviar"]'

# ChatGPT XPaths
chatbot_url = "https://chatgpt.com/g/g-p-68d82477fda0819186d2894fa194fad0-atendimento/c/68d82533-a3c4-8333-ab33-c4868ab03b02"
chatgpt_input_xpath = '//div[@contenteditable="true" and @id="prompt-textarea"]'
chatgpt_send_button_xpath = '//button[@aria-label="Enviar prompt" or contains(@id, "composer-submit-button")]'
chatgpt_messages_xpath = "//article[@data-turn='assistant']//div[contains(@class,'markdown')]"
chatgpt_links_xpath = "//article[@data-turn='assistant']//div[contains(@class,'markdown')]//a[@href]"  # New XPath for links
chatgpt_stop_streaming_button_xpath = '//button[@aria-label="Parar transmissão"]'

# Espera até a barra lateral aparecer
WebDriverWait(driver, 600).until(EC.presence_of_element_located((By.ID, "side")))

# Filtrar mensagens não lidas
wait.until(EC.presence_of_element_located((By.XPATH, unread_filter_xpath)))
unread_filter = driver.find_element(By.XPATH, unread_filter_xpath)
unread_filter.click()

# Variables for tab handles
whatsapp_handle = driver.current_window_handle
chatbot_handle = None

# JavaScript snippet for WhatsApp's contenteditable input
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

# Function to open ChatGPT tab if not open
def open_chatbot_tab():
    global chatbot_handle
    if chatbot_handle is None:
        driver.execute_script(f"window.open('{chatbot_url}', '_blank');")
        driver.switch_to.window(driver.window_handles[1])
        chatbot_handle = driver.current_window_handle
        print("Opened ChatGPT tab.")
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, chatgpt_input_xpath)))
    else:
        driver.switch_to.window(chatbot_handle)

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
    open_chatbot_tab()
    
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
            except (TimeoutException, NoSuchElementException):
                print("Send button not found, trying Enter key.")
                input_elem.send_keys(Keys.ENTER)
            
            print("Sent message to ChatGPT.")
            
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
                    # Get text content
                    messages = driver.find_elements(By.XPATH, chatgpt_messages_xpath)
                    if not messages:
                        print("No messages found.")
                        return None
                    latest_response = messages[-1].text.strip()
                    
                    # Get links
                    links = []
                    link_elements = latest_response.find_elements(By.XPATH, chatgpt_links_xpath)
                    for link_elem in link_elements:
                        href = link_elem.get_attribute('href')
                        if href:
                            links.append(href)
                    
                    # Combine text and links
                    combined_response = latest_response
                    if links:
                        combined_response += "\nLinks:\n" + "\n".join(links)
                    
                    if combined_response:
                        print(f"ChatGPT response: {combined_response}")
                        return combined_response
                    time.sleep(2)
                except StaleElementReferenceException:
                    print("Stale element detected, retrying to capture response...")
            print("No response captured after retries.")
            return None
        except (StaleElementReferenceException, NoSuchElementException) as e:
            print(f"Retry {attempt + 1}/3: Error interacting with ChatGPT input: {e}")
            time.sleep(1)
    print("Failed to send message to ChatGPT after retries.")
    return None

def send_file_to_whatsapp(chat_input, file_path):
    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
        
        # Click attachment button
        wait.until(EC.element_to_be_clickable((By.XPATH, attachment_button_xpath)))
        attachment_button = driver.find_element(By.XPATH, attachment_button_xpath)
        attachment_button.click()
        print("Clicked attachment button.")

        # Select file input (assuming image/video for this example)
        wait.until(EC.presence_of_element_located((By.XPATH, file_input_xpath)))
        file_input = driver.find_element(By.XPATH, file_input_xpath)
        file_input.send_keys(file_path)
        print(f"Selected file: {file_path}")

        # Wait for preview and click send
        wait.until(EC.element_to_be_clickable((By.XPATH, send_file_button_xpath)))
        send_button = driver.find_element(By.XPATH, send_file_button_xpath)
        send_button.click()
        print("File sent successfully.")
        return True
    except Exception as e:
        print(f"Error sending file: {e}")
        return False

try:
    while True:
        try:
            # Switch back to WhatsApp tab
            driver.switch_to.window(whatsapp_handle)
            
            # Cada "linha de chat"
            chat_rows = driver.find_elements(By.XPATH, chat_rows_xpath)
            print(f"Found {len(chat_rows)} chat rows.")

            for row in chat_rows:
                try:
                    # Nome/título do contato
                    title_element = row.find_element(By.XPATH, title_element_xpath)
                    title = title_element.get_attribute("title")

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

                            # Get all incoming messages
                            messages_in = driver.find_elements(By.XPATH, msg_in_xpath)
                            
                            # Assume the last notif_count are unread
                            unread_messages = [msg.text.strip() for msg in messages_in[-notif_count:]]
                            if not unread_messages:
                                print("No unread messages found.")
                                continue
                            
                            print(f"Unread messages from {title}: {unread_messages}")
                            
                            # Join unread messages into one string
                            combined_message = "\n".join(unread_messages)
                            
                            # Get response from ChatGPT
                            response = get_chatgpt_response(combined_message)
                            if response:
                                # Switch back to WhatsApp
                                driver.switch_to.window(whatsapp_handle)
                                
                                # Send response using paste_content
                                try:
                                    chat_input = WebDriverWait(driver, 10).until(
                                        EC.element_to_be_clickable((By.XPATH, whatsapp_input_xpath))
                                    )
                                    clear_input_field(chat_input)
                                    paste_content(driver, chat_input, response)
                                    chat_input.send_keys(Keys.ENTER)  # Trigger send
                                    print(f"Sent response to {title}: {response}")
                                except Exception as e:
                                    print(f"Error sending response to WhatsApp: {e}")
                            else:
                                print("No response from ChatGPT.")

                        except Exception as e:
                            print(f"Error handling chat with {title}: {e}")

                except Exception as e:
                    print(f"Error processing row: {e}")
                    continue

            # Press ESCAPE to clear any dialogs
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)

            time.sleep(5)

        except Exception as e:
            print(f"General error: {e}")

except KeyboardInterrupt:
    print("Script interrupted by user.")

finally:
    # Cleanup
    print("Cleaning up...")
    driver.quit()
    sys.exit(0)