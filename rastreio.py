import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="📦 Visualizador de Encomendas", layout="wide")

# Título da aplicação
st.title("📦 Visualizador de Encomendas")
st.markdown("Gerencie e filtre sua lista de encomendas de forma prática.")

# Upload do arquivo
with st.container():
    uploaded_file = st.file_uploader("📁 Faça upload do arquivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        # Converter colunas relevantes para string para evitar erros
        df.columns = df.columns.str.strip()  # Remove espaços extras
        df["CEP"] = df["CEP"].astype(str)

        # Verifica se a coluna 'Cidade' existe, senão adiciona como vazia
        if "Cidade" not in df.columns:
            df["Cidade"] = ""

        # Filtro por CEP ou Cidade
        with st.expander("🔎 Filtro por CEP ou Cidade", expanded=True):
            termo_busca = st.text_input("Digite o **CEP** ou o nome da **Cidade**:", placeholder="Ex: 01001 ou São Paulo")

        # Aplica filtro se houver termo de busca
        if termo_busca:
            termo_busca_lower = termo_busca.lower()
            df_filtrado = df[
                df["CEP"].astype(str).str.contains(termo_busca_lower, case=False, na=False) |
                df["Cidade"].astype(str).str.lower().str.contains(termo_busca_lower, na=False)
            ]
            st.success(f"🔍 Exibindo {len(df_filtrado)} resultado(s) para: '{termo_busca}'")
        else:
            df_filtrado = df

        # Exibe o dataframe com opção de edição
        st.markdown("### 📝 Tabela de Encomendas")
        st.data_editor(df_filtrado, use_container_width=True, num_rows="dynamic")

    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {e}")
else:
    st.info("⬆️ Envie um arquivo Excel com as colunas **'CEP'** e opcionalmente **'Cidade'** para começar.")
