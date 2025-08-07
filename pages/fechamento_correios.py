import streamlit as st
import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from io import BytesIO

# Configuração da página
st.set_page_config(
    layout="wide",
    page_title="Animes Mais Populares"
)

# Usuários e senhas válidos
usuarios_validos = {
    "admin": "1234",
    "user1": "abcd",
    "user2": "senha2"
}

# Função de login
def tela_login():
    st.title("Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario in usuarios_validos and senha == usuarios_validos[usuario]:
            st.session_state["logado"] = True
            st.session_state["usuario"] = usuario
            st.rerun()  # Força recarregamento
        else:
            st.error("Usuário ou senha incorretos")

# Inicializa o estado da sessão
if "logado" not in st.session_state:
    st.session_state["logado"] = False

# Exibe a tela de login se o usuário não estiver logado
if not st.session_state["logado"]:
    tela_login()
else:
    # 🔐 Conteúdo protegido
    st.title(f"Página Protegida - Bem-vindo {st.session_state['usuario']}!")
    st.write("Você está logado! Conteúdo secreto aqui.")

    # 📂 Upload de arquivo
    uploaded_file = st.file_uploader("Faça upload da base de dados (.xlsx)", type=["xlsx"])

    if uploaded_file:
        # ✅ Lê o Excel
        df = pd.read_excel(uploaded_file)

        # Converte a coluna de datas se necessário
        if not np.issubdtype(df["DATA"].dtype, np.datetime64):
            df["DATA"] = pd.to_datetime(df["DATA"])

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

        # Verifica se o usuário selecionou duas datas
        if isinstance(d, tuple) and len(d) == 2:
            start_date, end_date = d

            # 🔍 Filtra o DataFrame pelo intervalo de datas
            filtro = df[(df["DATA"].dt.date >= start_date) & (df["DATA"].dt.date <= end_date)]

            # ➕ Soma total do valor no período
            total_valor = filtro["VALOR"].sum()

            # 📊 Soma por centro de custo
            soma_por_centro = filtro.groupby("CENTRO DE CUSTO")["VALOR"].sum().reset_index()

            # ✅ Exibe os dados filtrados
            st.subheader("Dados Filtrados")
            st.dataframe(filtro)

            # 💬 Exibe o total geral
            st.success(f"Total do VALOR no intervalo selecionado: R$ {total_valor:,.2f}")

            # 📋 Exibe o total por centro de custo
            st.subheader("Total por Centro de Custo")
            st.dataframe(soma_por_centro)

            # 📤 Exportar para Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                filtro.to_excel(writer, sheet_name='Filtrados', index=False)
                soma_por_centro.to_excel(writer, sheet_name='Resumo por Centro', index=False)
            output.seek(0)

            st.download_button(
                label="📥 Baixar dados filtrados em Excel",
                data=output,
                file_name="dados_filtrados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Selecione um intervalo de duas datas.")
    else:
        st.info("Por favor, faça o upload de um arquivo Excel para começar.")
                                
