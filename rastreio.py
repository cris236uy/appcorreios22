import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Visualizador de Encomendas", layout="wide")
st.title("📦 Visualizador de Encomendas - Editável com Filtro por CEP")

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

            # Filtrando o DataFrame se o usuário digitou algo
            if cep_pesquisado:
                df_filtrado = df[df["CEP"].astype(str).str.contains(cep_pesquisado)]
            else:
                df_filtrado = df

            # Exibe editor de tabela
            st.data_editor(df_filtrado, use_container_width=True, num_rows="dynamic")

    except Exception as e:
        st.error(f"❌ Erro ao ler o arquivo: {e}")
else:
    st.info("Envie um arquivo Excel (.xlsx) com a coluna 'CEP' para começar.")
