import streamlit as st
import pandas as pd
import requests
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Configuração da página (apenas uma vez e no início)
st.set_page_config(page_title="📦 Visualizador de Encomendas + Automação Kaggle", layout="wide")

# ----------------------------
# 📦 VISUALIZADOR DE ENCOMENDAS
# ----------------------------
st.title("📦 Visualizador de Encomendas")
st.markdown("Gerencie e filtre sua lista de encomendas com busca inteligente por **CEP** ou **Cidade**.")

# Função para consultar o ViaCEP
def buscar_cep(cep):
    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
        if response.status_code == 200:
            data = response.json()
            if "erro" in data:
                return None
            return data
    except:
        return None

# Upload do arquivo
uploaded_file = st.file_uploader("📁 Faça upload do arquivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()  # Remove espaços nos nomes das colunas

        # Garantir que colunas importantes existem
        if "CEP" not in df.columns:
            st.error("❌ A coluna 'CEP' não foi encontrada no arquivo.")
        else:
            df["CEP"] = df["CEP"].astype(str)

            if "Cidade" not in df.columns:
                df["Cidade"] = ""

            # Campo de busca com API
            with st.expander("🔎 Buscar por CEP ou Cidade", expanded=True):
                termo_busca = st.text_input("Digite um **CEP (8 dígitos)** ou uma **cidade**:")
                
                # Se o termo for um CEP válido
                if termo_busca.strip().isdigit() and len(termo_busca.strip()) == 8:
                    cep_info = buscar_cep(termo_busca.strip())
                    if cep_info:
                        st.success("📍 Informações do CEP encontradas:")
                        st.json(cep_info)
                    else:
                        st.warning("⚠️ CEP não encontrado na base do ViaCEP.")

            # Aplicar filtro no DataFrame
            if termo_busca:
                termo_busca_lower = termo_busca.lower()
                df_filtrado = df[
                    df["CEP"].str.contains(termo_busca_lower, case=False, na=False) |
                    df["Cidade"].astype(str).str.lower().str.contains(termo_busca_lower, na=False)
                ]
                st.markdown(f"### 🔍 Resultados encontrados: {len(df_filtrado)}")
            else:
                df_filtrado = df

            # Editor de dados
            st.markdown("### 📝 Tabela de Encomendas")
            st.data_editor(df_filtrado, use_container_width=True, num_rows="dynamic")

    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {e}")
else:
    st.info("⬆️ Envie um arquivo Excel com a coluna **'CEP'** e opcionalmente **'Cidade'**.")
