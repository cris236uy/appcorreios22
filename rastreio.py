from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def rastrear_objeto(codigo):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")

    driver = webdriver.Chrome(options=chrome_options)
    status = "Não encontrado"

    try:
        driver.get("https://www.muambator.com.br/")
        time.sleep(2)

        campo = driver.find_element(By.ID, "pesquisaPub")
        campo.clear()
        campo.send_keys(codigo)
        time.sleep(1)

        botao = driver.find_element(By.ID, "submitPesqPub")
        driver.execute_script("arguments[0].click();", botao)
        time.sleep(3)

        # Apenas o texto do status principal
        status = driver.find_element(By.CLASS_NAME, "situacao-header").text.strip()

    except Exception as e:
        status = f"Erro: {e}"

    finally:
        driver.quit()

    return status

