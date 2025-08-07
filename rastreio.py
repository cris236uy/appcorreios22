import streamlit as st
import pandas as pd
import os

# Configurações iniciais
st.set_page_config(page_title="📦 Visualizador de Encomendas", layout="wide")
st.title("📦 Visualizador de Encomendas - Editável com Filtro por CEP")

# Caminho fixo para salvar o arquivo no servidor
ARQUIVO_SALVO = "base_encomendas.xlsx"

# Se houver upload de novo arquivo, ele substitui o salvo
uploaded_file = st.file_uploader("📁 Faça upload do arquivo Excel", type=["xlsx"])

if uploaded_file:
    try:
        df_temp = pd.read_excel(uploaded_file)

        if "CEP" not in df_temp.columns:
            st.error("❌ A coluna 'CEP' não foi encontrada no arquivo. Renomeie corretamente e tente novamente.")
        else:
            # Salva o arquivo no servidor
            with open(ARQUIVO_SALVO, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("✅ Arquivo salvo com sucesso! A base agora está persistente.")
    except Exception as e:
        st.error(f"❌ Erro ao ler o arquivo: {e}")

# Verifica se existe uma base salva
if os.path.exists(ARQUIVO_SALVO):
    try:
        df = pd.read_excel(ARQUIVO_SALVO)

        # Botão para excluir a base
        if st.button("🗑️ Excluir base permanentemente"):
            os.remove(ARQUIVO_SALVO)
            st.success("✅ Base excluída permanentemente.")
            st.stop()

        st.subheader("📄 Base de Dados Carregada")

        # Campo de busca por CEP
        cep_pesquisado = st.text_input("🔍 Pesquisar CEP (digite completo ou parcial):")

        # Filtra os dados
        if cep_pesquisado:
            df_filtrado = df[df["CEP"].astype(str).str.contains(cep_pesquisado)]
        else:
            df_filtrado = df

        # Exibe a base
        st.data_editor(df_filtrado, use_container_width=True, num_rows="dynamic")

    except Exception as e:
        st.error(f"❌ Erro ao carregar a base salva: {e}")
else:
    st.info("Envie um arquivo Excel (.xlsx) com a coluna 'CEP' para começar.")
            
