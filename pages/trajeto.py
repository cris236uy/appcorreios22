import streamlit as st
import requests
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

st.set_page_config(page_title="Consulta de CEPs", layout="wide")
st.title("📍 Consulta de CEPs – Remetente e Destinatário")

# Função para consultar dados do CEP via API ViaCEP
def consultar_cep(cep):
    url = f"https://viacep.com.br/ws/{cep}/json/"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        dados = resposta.json()
        if not dados.get("erro"):
            return dados
    return None

# Função para obter coordenadas via endereço completo
def coordenadas_por_cep(dados_cep):
    localizador = Nominatim(user_agent="consulta_cep_app")
    try:
        logradouro = dados_cep.get("logradouro", "")
        bairro = dados_cep.get("bairro", "")
        cidade = dados_cep.get("localidade", "")
        estado = dados_cep.get("uf", "")
        
        endereco = f"{logradouro}, {bairro}, {cidade} - {estado}, Brasil"
        local = localizador.geocode(endereco)
        if local:
            return (local.latitude, local.longitude)
    except:
        pass
    return None

# Interface
with st.form("form_ceps"):
    cep_rem = st.text_input("🔹 CEP do Remetente", placeholder="Ex: 01001-000")
    cep_dest = st.text_input("🔸 CEP do Destinatário", placeholder="Ex: 01310-100")
    submitted = st.form_submit_button("Consultar")

if submitted:
    if not cep_rem or not cep_dest:
        st.error("Por favor, preencha os dois CEPs.")
    else:
        dados_rem = consultar_cep(cep_rem)
        dados_dest = consultar_cep(cep_dest)

        if not dados_rem:
            st.error("❌ CEP do remetente inválido ou não encontrado.")
        elif not dados_dest:
            st.error("❌ CEP do destinatário inválido ou não encontrado.")
        else:
            # Mostra os dados
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📦 Remetente")
                st.json(dados_rem)
            with col2:
                st.subheader("📬 Destinatário")
                st.json(dados_dest)

            # Coordenadas
            coord_rem = coordenadas_por_cep(dados_rem)
            coord_dest = coordenadas_por_cep(dados_dest)

            if coord_rem and coord_dest:
                distancia_km = geodesic(coord_rem, coord_dest).km
                st.success(f"🛣️ Distância estimada: {distancia_km:.2f} km")
            else:
                st.warning("⚠️ Não foi possível calcular a distância entre os CEPs.")

            # Verificação da área de entrega
            def verificar_area_urbana(dados):
                localidade = dados.get("localidade", "").lower()
                if any(palavra in localidade for palavra in ["zona rural", "rural", "interior", "colônia"]):
                    return "❌ Área não urbana (possível restrição de entrega)"
                return "✅ Área urbana (provavelmente recebe entregas)"

            st.markdown("### 📫 Verificação de Área de Entrega")
            st.write("Remetente:", verificar_area_urbana(dados_rem))
            st.write("Destinatário:", verificar_area_urbana(dados_dest))

            # Dados para exportação
            df_resultado = pd.DataFrame([
                {
                    "Tipo": "Remetente",
                    **dados_rem,
                    "Latitude": coord_rem[0] if coord_rem else "",
                    "Longitude": coord_rem[1] if coord_rem else ""
                },
                {
                    "Tipo": "Destinatário",
                    **dados_dest,
                    "Latitude": coord_dest[0] if coord_dest else "",
                    "Longitude": coord_dest[1] if coord_dest else ""
                }
            ])

            st.markdown("### 📁 Exportar Dados")
            csv = df_resultado.to_csv(index=False).encode("utf-8")
            excel = df_resultado.to_excel(index=False, engine='openpyxl')

            st.download_button("⬇️ Baixar CSV", csv, file_name="ceps_consultados.csv", mime="text/csv")

            from io import BytesIO
            excel_buffer = BytesIO()
            df_resultado.to_excel(excel_buffer, index=False, engine='openpyxl')
            st.download_button("⬇️ Baixar Excel", data=excel_buffer.getvalue(), file_name="ceps_consultados.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
