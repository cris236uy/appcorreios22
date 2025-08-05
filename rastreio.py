import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# --- Carregar dados do Excel
df = pd.read_excel("C:/Users/Usuário/Downloads/codigos123/pages/pasta definitiva - Copia.xlsx")

# --- Função para rastrear objeto no Muambator
def rastrear_objeto(codigo):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")

    driver = webdriver.Chrome(options=chrome_options)
    status = "Não encontrado"

    try:
        driver.get("https://www.muambator.com.br/")
        time.sleep(3)

        campo = driver.find_element(By.ID, "pesquisaPub")
        campo.clear()
        campo.send_keys(codigo)
        time.sleep(1)

        botao = driver.find_element(By.ID, "submitPesqPub")
        driver.execute_script("arguments[0].click();", botao)
        time.sleep(4)

        status = driver.find_element(By.CLASS_NAME, "situacao-header").text

    except Exception as e:
        status = f"Erro: {e}"

    finally:
        driver.quit()

    return status

# --- Título do aplicativo
st.set_page_config(page_title="Rastreador de Encomendas", layout="wide")
st.title("🔍 Rastreador de Encomendas (Muambator)")

# --- Entrada de códigos de rastreio
lista_codigos = st.text_area("Cole os códigos de rastreio (um por linha):")

# --- Filtro lateral por CEP
st.sidebar.header("Filtro de CEP")
cepfilter = df["CEP"].unique()
cepfilter2 = st.sidebar.selectbox("Selecionar CEP", cepfilter)
filtrada = df[df["CEP"] == cepfilter2]

# --- Tabs com unidades
tab1, tab2, tab3 = st.tabs(["Cruz Alta", "Vertente", "Tanabi"])

with tab1:
    st.header("Unidade Cruz Alta")
    st.data_editor(filtrada[["CEP", "DATA", "CENTRO DE CUSTO", "CÓDIGO DE RASTREIO"]], num_rows="dynamic")

with tab2:
    st.header("Vertente")
    st.image("https://static.streamlit.io/examples/dog.jpg", width=200)

with tab3:
    st.header("Tanabi")
    st.image("https://static.streamlit.io/examples/owl.jpg", width=200)

# --- Botão de rastrear todos
if st.button("Rastrear Tudo"):
    codigos = [c.strip() for c in lista_codigos.strip().split("\n") if c.strip()]

    if not codigos:
        st.warning("Nenhum código informado.")
    else:
        resultados = []
        with st.spinner(f"Rastreando {len(codigos)} objetos..."):
            for i, cod in enumerate(codigos):
                status = rastrear_objeto(cod)
                resultados.append({"Código": cod, "Status": status})
                st.write(f"{i+1}/{len(codigos)} ➔ {cod}: {status}")

        df_resultados = pd.DataFrame(resultados)
        st.success("✅ Rastreamento finalizado!")
        st.dataframe(df_resultados)

        st.download_button("📅 Baixar resultado em CSV", df_resultados.to_csv(index=False).encode("utf-8"), file_name="rastreio.csv", mime="text/csv")
            
