import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Visualizador de Encomendas", layout="wide")
st.title("📦 Visualizador de Encomendas (Excel)")

# Upload do arquivo
uploaded_file = st.file_uploader("📁 Faça upload do arquivo Excel", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("✅ Arquivo carregado com sucesso!")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"❌ Erro ao ler o arquivo: {e}")
else:
    st.info("Envie um arquivo Excel (.xlsx) para visualizar os dados.")
