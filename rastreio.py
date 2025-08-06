import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Filtro de Encomendas", layout="wide")
st.title("📦 Filtro de Encomendas por CEP, Data e Código")

# Upload do arquivo
uploaded_file = st.file_uploader("📁 Faça upload do arquivo Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Mostra as colunas disponíveis no Excel
    st.subheader("Colunas encontradas no arquivo:")
    st.write(df.columns.tolist())

    # Verifica se todas as colunas necessárias estão no arquivo
    colunas_necessarias = ["CEP", "DATA", "CENTRO DE CUSTO", "CÓDIGO DE RASTREIO"]
    if not all(coluna in df.columns for coluna in colunas_necessarias):
        st.error(f"⚠️ O arquivo precisa conter as colunas: {', '.join(colunas_necessarias)}")
    else:
        # Filtros interativos
        col1, col2, col3 = st.columns(3)

        with col1:
            cep_filtro = st.selectbox("Filtrar por CEP:", options=["Todos"] + sorted(df["CEP"].dropna().unique().tolist()))

        with col2:
            data_filtro = st.selectbox("Filtrar por Data:", options=["Todos"] + sorted(df["DATA"].astype(str).dropna().unique().tolist()))

        with col3:
            centro_filtro = st.selectbox("Filtrar por Centro de Custo:", options=["Todos"] + sorted(df["CENTRO DE CUSTO"].dropna().unique().tolist()))

        # Campo de busca por código
        codigo_busca = st.text_input("🔍 Buscar por Código de Rastreio:")

        # Aplica os filtros
        df_filtrado = df.copy()

        if cep_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado["CEP"] == cep_filtro]

        if data_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado["DATA"].astype(str) == data_filtro]

        if centro_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado["CENTRO DE CUSTO"] == centro_filtro]

        if codigo_busca:
            df_filtrado = df_filtrado[df_filtrado["CÓDIGO DE RASTREIO"].str.contains(codigo_busca, case=False, na=False)]

        # Exibe os resultados
        st.markdown(f"### Resultados encontrados: {len(df_filtrado)}")
        st.dataframe(df_filtrado, use_container_width=True)
else:
    st.warning("Por favor, faça upload de um arquivo Excel (.xlsx) para continuar.")
