import streamlit as st
import pandas as pd

# Título do app
st.title("📦 Consulta de CEPs - Dashboard de Encomendas")

# Carrega os dados
df = pd.read_excel("C:/Users/Usuário/Downloads/codigos123/pages/pasta definitiva - Copia.xlsx")

# Filtros com selectbox
cep_list = df["CEP"].dropna().unique()
data_list = df["DATA"].dropna().unique()
centro_list = df["CENTRO DE CUSTO"].dropna().unique()

col1, col2, col3 = st.columns(3)

with col1:
    selected_cep = st.selectbox("🔍 Filtrar por CEP", ["Todos"] + list(cep_list))
with col2:
    selected_data = st.selectbox("📅 Filtrar por Data", ["Todos"] + list(data_list))
with col3:
    selected_centro = st.selectbox("🏢 Filtrar por Centro de Custo", ["Todos"] + list(centro_list))

# Campo de pesquisa livre
search_text = st.text_input("🔎 Buscar por código de rastreio ou qualquer texto:")

# Filtragem dinâmica
filtro_df = df.copy()

if selected_cep != "Todos":
    filtro_df = filtro_df[filtro_df["CEP"] == selected_cep]

if selected_data != "Todos":
    filtro_df = filtro_df[filtro_df["DATA"] == selected_data]

if selected_centro != "Todos":
    filtro_df = filtro_df[filtro_df["CENTRO DE CUSTO"] == selected_centro]

if search_text:
    filtro_df = filtro_df[
        filtro_df.apply(lambda row: search_text.lower() in str(row).lower(), axis=1)
    ]
    st.info(f"🔎 Resultados para: {search_text}")

# Resultado da filtragem
if filtro_df.empty:
    st.warning("⚠️ Nenhum resultado encontrado com os filtros aplicados.")
else:
    st.success(f"✅ {len(filtro_df)} resultados encontrados.")
    st.dataframe(filtro_df, use_container_width=True)
