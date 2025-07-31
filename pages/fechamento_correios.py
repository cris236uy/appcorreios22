import streamlit as st
import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(
    layout="wide",
    page_title="animes mais populares"
)

# Usuários e senhas válidos
usuarios_validos = {
    "admin": "1234",
    "user1": "abcd",
    "user2": "senha2"
}

def tela_login():
    st.title("Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario in usuarios_validos and senha == usuarios_validos[usuario]:
            st.session_state["logado"] = True
            st.session_state["usuario"] = usuario
            st.rerun()  # <- forçar recarregamento
        else:
            st.error("Usuário ou senha incorretos")

# Inicializa estado
if "logado" not in st.session_state:
    st.session_state["logado"] = False

# Se não estiver logado, exibe a tela de login
if not st.session_state["logado"]:
    tela_login()
else:
    # 🔐 AQUI começa o conteúdo protegido
    st.title(f"Página Protegida - Bem vindo {st.session_state['usuario']}!")
    st.write("Você está logado! Conteúdo secreto aqui.")

    # ✅ Lê o Excel
   df = pd.read_excel("pasta definitiva - Copia.xlsx")

    # Editor de dados
    edited_df = st.data_editor(df, num_rows="dynamic")

    # Seletor de datas
    today = datetime.datetime.now()
    next_year = today.year
    jan_1 = datetime.date(next_year, 1, 1)
    dec_31 = datetime.date(next_year, 12, 31)

    d = st.date_input(
        "Selecione o intervalo de datas",
        (jan_1, datetime.date(next_year, 1, 7)),
        jan_1,
        dec_31,
        format="MM.DD.YYYY",
    )

    if isinstance(d, tuple) and len(d) == 2:
        start_date, end_date = d

        # 🔍 Filtrando o DataFrame pelo intervalo de datas
        filtro = df[(df["DATA"].dt.date >= start_date) & (df["DATA"].dt.date <= end_date)]

        # ➕ Somando o total geral
        total_valor = filtro["VALOR"].sum()

        # 📊 Soma por centro de custo
        soma_por_centro = filtro.groupby("CENTRO DE CUSTO")["VALOR"].sum().reset_index()

        # ✅ Exibir o DataFrame filtrado
        st.subheader("Dados Filtrados")
        st.dataframe(filtro)

        # 💬 Mostrar total geral
        st.success(f"Total do VALOR no intervalo selecionado: R$ {total_valor:,.2f}")

        # 📋 Mostrar total por centro de custo
        st.subheader("Total por Centro de Custo")
        st.dataframe(soma_por_centro)
    else:
        st.warning("Selecione um intervalo de duas datas.")
