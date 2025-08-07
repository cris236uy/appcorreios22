import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Visualizador de Encomendas", layout="wide")
st.title("📦 Visualizador de Encomendas - Editável com Filtro por CEP")

# Inicializa o estado se não estiver presente
if "df" not in st.session_state:
    st.session_state.df = None

# Upload do arquivo
uploaded_file = st.file_uploader("📁 Faça upload do arquivo Excel", type=["xlsx"])

# Se um novo arquivo for enviado
if uploaded_file:
    try:
        df_temp = pd.read_excel(uploaded_file)

        if "CEP" not in df_temp.columns:
            st.error("❌ A coluna 'CEP' não foi encontrada no arquivo. Renomeie corretamente e tente novamente.")
        else:
            st.session_state.df = df_temp  # Salva o DataFrame no estado
            st.success("✅ Arquivo carregado com sucesso!")

    except Exception as e:
        st.error(f"❌ Erro ao ler o arquivo: {e}")

# Se já existe uma base carregada no estado
if st.session_state.df is not None:
    st.subheader("📄 Base de Dados Carregada")

    # Botão para excluir a base
    if st.button("🗑️ Excluir base carregada"):
        st.session_state.df = None
        st.success("✅ Base excluída.")
        st.stop()  # Para de executar o restante do script

    df = st.session_state.df

    # Campo de busca por CEP
    cep_pesquisado = st.text_input("🔍 Pesquisar CEP (digite completo ou parcial):")

    # Filtrando o DataFrame se o usuário digitou algo
    if cep_pesquisado:
        df_filtrado = df[df["CEP"].astype(str).str.contains(cep_pesquisado)]
    else:
        df_filtrado = df

    # Exibe editor de tabela
    st.data_editor(df_filtrado, use_container_width=True, num_rows="dynamic")
else:
    st.info("Envie um arquivo Excel (.xlsx) com a coluna 'CEP' para começar.")
