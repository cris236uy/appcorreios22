import streamlit as st
import pandas as pd
import requests

# Configuração da página
st.set_page_config(page_title="📦 Visualizador de Encomendas", layout="wide")

st.title("📦 Visualizador de Encomendas")
st.markdown("Gerencie e filtre sua lista de encomendas com busca inteligente por **CEP** ou **Cidade**.")

# Função para consultar o ViaCEP
def buscar_cep(cep):
    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
        if response.status_code == 200:
            data = response.json()
            if "erro" in data:
                return None
            return data
    except:
        return None

# Upload do arquivo
uploaded_file = st.file_uploader("📁 Faça upload do arquivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()  # Remove espaços nos nomes das colunas

        # Garantir que colunas importantes existem
        if "CEP" not in df.columns:
            st.error("❌ A coluna 'CEP' não foi encontrada no arquivo.")
        else:
            df["CEP"] = df["CEP"].astype(str)

            if "Cidade" not in df.columns:
                df["Cidade"] = ""

            # Campo de busca com API
            with st.expander("🔎 Buscar por CEP ou Cidade", expanded=True):
                termo_busca = st.text_input("Digite um **CEP (8 dígitos)** ou uma **cidade**:")
                
                # Se o termo for um CEP (somente números e 8 dígitos)
                if termo_busca.strip().isdigit() and len(termo_busca.strip()) == 8:
                    cep_info = buscar_cep(termo_busca.strip())
                    if cep_info:
                        st.success("📍 Informações do CEP encontradas:")
                        st.json(cep_info)
                    else:
                        st.warning("⚠️ CEP não encontrado na base do ViaCEP.")

            # Aplicar filtro no DataFrame
            if termo_busca:
                termo_busca_lower = termo_busca.lower()
                df_filtrado = df[
                    df["CEP"].str.contains(termo_busca_lower, case=False, na=False) |
                    df["Cidade"].astype(str).str.lower().str.contains(termo_busca_lower, na=False)
                ]
                st.markdown(f"### 🔍 Resultados encontrados: {len(df_filtrado)}")
            else:
                df_filtrado = df

            # Editor de dados
            st.markdown("### 📝 Tabela de Encomendas")
            st.data_editor(df_filtrado, use_container_width=True, num_rows="dynamic")



# Configuração da página
st.set_page_config(page_title="Automação Kaggle", layout="centered")
st.title("🤖 Automação Selenium no Kaggle")

# Escolha do modo
modo = st.radio("Escolha o modo de execução do Selenium:", ["Normal (visível)", "Headless (oculto)"])

if st.button("Executar Automação"):
    st.write("🔍 Iniciando automação no Kaggle...")
try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://www.kaggle.com")

except Exception as e:
    st.error(f"Erro ao iniciar Selenium: {e}")

finally:
    st.set_page_config(page_title="Automação Kaggle", layout="centered")


        # Inicializa o navegador
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Abre a página do Titanic no Kaggle
        driver.get("https://www.kaggle.com/c/titanic")
        time.sleep(3)

        # Pega o título da competição
        feito = driver.find_element(By.XPATH,
            '//*[@id="site-content"]/div[2]/div/div/div[2]/div[2]/div[1]/h1'
        ).text

        st.success(f"✅ Deu tudo certo! O título da competição é: **{feito}**")

        # Fecha o navegador
        driver.quit()

    except Exception as e:
        st.error(f"❌ Ocorreu um erro: {e}")


    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {e}")
else:
    st.info("⬆️ Envie um arquivo Excel com a coluna **'CEP'** e opcionalmente **'Cidade'**.")
