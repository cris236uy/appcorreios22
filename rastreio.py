import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# --- Configuração da página
st.set_page_config(page_title="Rastreador de Encomendas", layout="wide")
st.title("🔍 Rastreador de Encomendas (Linketrack)")

# --- Carrega a planilha local
df = pd.read_excel("pasta definitiva - Copia.xlsx")

# --- Função para rastrear código via API do Linketrack
def rastrear_objeto(codigo):
    try:
        url = f"https://api.linketrack.com/track/json?user=SEU_USUARIO&token=SEU_TOKEN&codigo={codigo}"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return f"Erro HTTP: {response.status_code}"
        data = response.json()
        if "eventos" in data and data["eventos"]:
            return data["eventos"][0].get("status", "Status não disponível")
        return "Nenhum evento encontrado"
    except Exception as e:
        return f"Erro: {e}"

# --- Entrada de códigos pelo usuário
lista_codigos = st.text_area("Cole os códigos de rastreio (um por linha):")

# --- Filtro de CEP na barra lateral
cepfilter = df["CEP"].unique()
cepfilter2 = st.sidebar.selectbox("Filtro por CEP", cepfilter)
filtrada = df[df["CEP"] == cepfilter2]

# --- Página principal
st.header("📦 Unidade Cruz Alta")
edited_df = st.data_editor(
    filtrada[["CEP", "DATA", "CENTRO DE CUSTO", "CÓDIGO DE RASTREIO"]],
    num_rows="dynamic"
)

# --- Botão para rastrear
if st.button("🚚 Rastrear Códigos"):
    codigos = [c.strip() for c in lista_codigos.strip().split("\n") if c.strip()]

    if not codigos:
        st.warning("⚠️ Nenhum código informado.")
    else:
        resultados = []
        with st.spinner(f"Rastreando {len(codigos)} objetos..."):
            for i, cod in enumerate(codigos):
                status = rastrear_objeto(cod)
                resultados.append({"Código": cod, "Status": status})
                st.write(f"{i+1}/{len(codigos)} ➜ {cod}: {status}")

        # Resultado final
        df_resultados = pd.DataFrame(resultados)
        st.success("✅ Rastreamento finalizado!")
        st.dataframe(df_resultados)

        # Botões para download
        csv = df_resultados.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Baixar resultado (CSV)", data=csv, file_name="rastreio.csv", mime="text/csv")

        # Criar Excel em memória
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_resultados.to_excel(writer, index=False, sheet_name='Rastreamento')
        output.seek(0)
        st.download_button(
            "📥 Baixar resultado (Excel)",
            data=output,
            file_name="rastreio.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
