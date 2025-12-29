import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import random
import os

# ================= CONFIGURAÇÕES =================

URL = "https://chat.deepseek.com/a/chat/s/04095441-fa00-4360-92e8-53c7f1998d05"

USER_DATA_DIR = r"D:\Alex\Projetos\Python\Chatbot\ChromeProfilePython"
PROFILE_DIR = "Default"
CHROMEDRIVER_PATH = r"D:\Alex\Projetos\Python\Chatbot\chromedriver.exe"

ARQUIVO_PERGUNTAS = "perguntas.txt"

# ================= FUNÇÕES =================

def ler_perguntas_txt(caminho):
    if not os.path.exists(caminho):
        raise FileNotFoundError(f"Arquivo {caminho} não encontrado")

    with open(caminho, "r", encoding="utf-8") as f:
        return [linha.strip() for linha in f if linha.strip()]


def limpar_input(input_elem):
    input_elem.click()
    input_elem.send_keys(Keys.CONTROL + "a")
    input_elem.send_keys(Keys.DELETE)
    time.sleep(0.5)


def escrever_pergunta(wait, pergunta):
    input_box = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, '//textarea[contains(@class,"ds-scroll-area")]')
        )
    )
    limpar_input(input_box)
    input_box.send_keys(pergunta)
    input_box.send_keys(Keys.ENTER)


def esperar_ciclo_completo_resposta(driver, wait):
    """
    Estados:
    1) disabled (idle)
    2) spinner (processando)
    3) streaming
    4) disabled (idle final)
    """

    # 1️⃣ Esperar spinner aparecer (se aparecer)
    try:
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.ds-loading")
            )
        )
        print("🌀 Spinner apareceu")
    except TimeoutException:
        print("ℹ️ Spinner não apareceu")

    # 2️⃣ Esperar spinner desaparecer
    try:
        wait.until(
            EC.invisibility_of_element_located(
                (By.CSS_SELECTOR, "div.ds-loading")
            )
        )
        print("✅ Spinner desapareceu")
    except TimeoutException:
        print("⚠️ Spinner demorou demais")

    # 3️⃣ Esperar botão voltar ao estado idle (disabled sem spinner)
    def estado_final(driver):
        botao = driver.find_element(
            By.CSS_SELECTOR, "div._7436101[role='button']"
        )

        aria = botao.get_attribute("aria-disabled")
        classes = botao.get_attribute("class")

        spinner_existe = len(
            driver.find_elements(By.CSS_SELECTOR, "div.ds-loading")
        ) > 0

        return (
            aria == "true"
            and "ds-icon-button--disabled" in classes
            and not spinner_existe
        )

    wait.until(estado_final)
    print("🏁 Resposta finalizada (idle)")


# ================= MAIN =================

def main():
    perguntas = ler_perguntas_txt(ARQUIVO_PERGUNTAS)
    print(f"📄 {len(perguntas)} perguntas carregadas")

    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    options.add_argument(f"--profile-directory={PROFILE_DIR}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(
        driver_executable_path=CHROMEDRIVER_PATH,
        options=options,
        version_main=143
    )

    driver.get(URL)
    wait = WebDriverWait(driver, 180)

    input("🔐 Confirma que estás logado e pressiona ENTER...")

    for i, pergunta in enumerate(perguntas, start=1):
        print(f"\n➡️ Pergunta {i}/{len(perguntas)}")
        print(pergunta)

        escrever_pergunta(wait, pergunta)

        print("🧠 Aguardando resposta...")
        esperar_ciclo_completo_resposta(driver, wait)

        pausa = random.uniform(2, 4)
        time.sleep(pausa)

    print("\n✅ Todas as perguntas foram processadas!")
    input("Pressiona ENTER para fechar...")
    driver.quit()


if __name__ == "__main__":
    main()
