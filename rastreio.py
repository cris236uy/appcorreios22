import streamlit as st
import pandas as pd
import requests

# Configuração da página
st.set_page_config(page_title="📦 Visualizador de Encomendas", layout="wide")
st.title("📦 Visualizador de Encomendas - Editável com Filtro por CEP e Rastreamento")

# === CONFIG SUA API WONCA ===
API_KEY = "wSuBhlk5nnC2UKZ6no-BtobdA27e4e9C57i6TXzpQaU"
API_URL = "https://api-labs.wonca.com.br/wonca.labs.v1.LabsService/Track"

# Função para rastrear um código
def rastrear_codigo(codigo):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Apikey {API_KEY}'
    }
    payload = {"code": codigo}
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            return {
                "Código": codigo,
                "Último Status": data.get("track", [{}])[0].get("status", "Sem dados"),
                "Data": data.get("track", [{}])[0].get("date", "Sem dados"),
                "Local": data.get("track", [{}])[0].get("place", "Sem dados")
            }
        else:
            return {"Código": codigo, "Último Status": f"Erro {response.status_code}", "Data": "-", "Local": "-"}
    except Exception as e:
        return {"Código": codigo, "Último Status": f"Erro: {e}", "Data": "-", "Local": "-"}

# Upload do arquivo
uploaded_file = st.file_uploader("📁 Faça upload do arquivo Excel", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        # Verifica se existe a coluna CEP
        if "CEP" not in df.columns:
            st.error("❌ A coluna 'CEP' não foi encontrada no arquivo. Renomeie corretamente e tente novamente.")
        else:
            # Campo de busca por CEP
            cep_pesquisado = st.text_input("🔍 Pesquisar CEP (digite completo ou parcial):")
            if cep_pesquisado:
                df_filtrado = df[df["CEP"].astype(str).str.contains(cep_pesquisado)]
            else:
                df_filtrado = df

            st.data_editor(df_filtrado, use_container_width=True, num_rows="dynamic")

    except Exception as e:
        st.error(f"❌ Erro ao ler o arquivo: {e}")
else:
    st.info("Envie um arquivo Excel (.xlsx) com a coluna 'CEP' para começar.")

# === RASTREAMENTO ===
st.subheader("📦 Rastrear Encomendas")
codigos_input = st.text_area("Digite um ou vários códigos de rastreio (um por linha):")

if st.button("🔍 Consultar Rastreamento"):
    if codigos_input.strip():
        codigos_lista = [c.strip() for c in codigos_input.split("\n") if c.strip()]
        resultados = [rastrear_codigo(c) for c in codigos_lista]
        df_resultados = pd.DataFrame(resultados)
        st.dataframe(df_resultados, use_container_width=True)
    else:
        st.warning("⚠️ Digite pelo menos um código de rastreio.")
