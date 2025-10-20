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
input()
driver.quit()
# XPaths
notif_xpath = ".//span[contains(@class,'x140p0ai')]"
msg_in_xpath = '//div[contains(@class,"message-in")]//span[@dir="ltr"]'
chat_rows_xpath = '//div[@role="row"]'
title_element_xpath = './/span[@title]'
msg_out_xpath = '//div[contains(@class,"message-out")]//span[@dir="ltr"]'
whatsapp_input_xpath = '//div[@aria-owns="emoji-suggestion" and contains(@aria-label, "Escreva na conversa")]'
chatbot_url = "https://chatgpt.com/g/g-p-68d82477fda0819186d2894fa194fad0-atendimento/c/68d82533-a3c4-8333-ab33-c4868ab03b02"

# ChatGPT XPaths
chatgpt_input_xpath = '//div[@contenteditable="true" and @id="prompt-textarea"]'
chatgpt_send_button_xpath = '//button[@aria-label="Enviar prompt" or contains(@id, "composer-submit-button")]'
chatgpt_messages_xpath = "//article[@data-turn='assistant']//div[contains(@class,'markdown')]"
chatgpt_stop_streaming_button_xpath = '//button[@aria-label="Parar transmissão"]'

# Espera até a barra lateral aparecer
WebDriverWait(driver, 600).until(EC.presence_of_element_located((By.ID, "side")))

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
                    messages = driver.find_elements(By.XPATH, chatgpt_messages_xpath)
                    if messages:
                        latest_response = messages[-1].text.strip()
                        if latest_response:
                            print(f"ChatGPT response: {latest_response}")
                            return latest_response
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
                    # input()
                    if title == "Eng. Electrónica UEM 2025":
                        notif_count=0
                    # else:
                        # notif_count=0
                        
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
                                
                                # Send response using JavaScript
                                try:
                                    chat_input = WebDriverWait(driver, 10).until(
                                        EC.element_to_be_clickable((By.XPATH, whatsapp_input_xpath))
                                    )
                                    clear_input_field(chat_input)
                                    paste_content(driver, chat_input, response)
                                    # send = input("Enviar Messagem?(s/n)").strip().lower()                                    
                                    # if send == "s":
                                        # chat_input.send_keys(Keys.ENTER)  # Trigger send
                                        # print(f"Sent response to {title}: {response}")
                                except Exception as e:
                                    print(f"Error sending response to WhatsApp: {e}")
                            else:
                                print("No response from ChatGPT.")

                        except Exception as e:
                            print(f"Error handling chat with {title}: {e}")

                except Exception as e:
                    print(f"Error processing row: {e}")
                    continue

        except Exception as e:
            print(f"General error: {e}")
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)

        time.sleep(5)

        # Optional: Add user input to exit
        # user_input = input("Press Enter to continue checking, or type 'exit' to stop: ").strip().lower()
        # if user_input == 'exit':
            # print("Exiting script...")
            # break

except KeyboardInterrupt:
    print("Script interrupted by user.")

finally:
    # Cleanup
    print("Cleaning up...")
    driver.quit()
    sys.exit(0)