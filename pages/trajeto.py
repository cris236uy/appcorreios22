import streamlit as st
import pandas as pd
import requests
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from io import BytesIO
import folium
from streamlit_folium import st_folium

# Função para consultar ViaCEP
def consultar_cep(cep):
    try:
        r = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
        dados = r.json()
        if "erro" in dados:
            return {"cep": cep, "erro": "CEP não encontrado"}
        return dados
    except:
        return {"cep": cep, "erro": "Erro na API"}

# Obter coordenadas geográficas de um CEP
def coordenadas_por_cep(cep):
    localizador = Nominatim(user_agent="consulta_cep_app")
    try:
        local = localizador.geocode(cep + ", Brasil")
        if local:
            return (local.latitude, local.longitude)
    except:
        pass
    return None

# Verificar se o local parece rural (simplesmente por heurística)
def verificar_area_entrega(dados_cep):
    if "localidade" in dados_cep and "logradouro" in dados_cep:
        log = dados_cep["logradouro"].lower()
        if "sítio" in log or "chácara" in log or "fazenda" in log or "zona rural" in log:
            return "❌ Área Rural - Pode não receber entregas"
    return "✅ Área urbana"

# Converter para Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='CEPs')
    return output.getvalue()

# Configuração da página
st.set_page_config(page_title="🚚 Cálculo de Entrega por CEP", layout="wide")
st.title("🚚 Consulta de Entrega por CEP")

# Inicializar session_state
if "consulta_feita" not in st.session_state:
    st.session_state.consulta_feita = False
    st.session_state.df = None
    st.session_state.coord_rem = None
    st.session_state.coord_dest = None

# Entradas
remetente = st.text_input("CEP do Remetente", placeholder="Ex: 01001-000")
destinatario = st.text_input("CEP do Destinatário", placeholder="Ex: 87083-320")

# Botão de consulta
if st.button("Consultar"):
    if not remetente or not destinatario:
        st.warning("Informe os dois CEPs.")
    else:
        dados_rem = consultar_cep(remetente)
        dados_dest = consultar_cep(destinatario)

        if "erro" in dados_rem or "erro" in dados_dest:
            st.error("Um dos CEPs é inválido.")
        else:
            coord_rem = coordenadas_por_cep(remetente)
            coord_dest = coordenadas_por_cep(destinatario)

            if not coord_rem or not coord_dest:
                st.error("Não foi possível localizar coordenadas para um dos CEPs.")
            else:
                km = round(geodesic(coord_rem, coord_dest).km, 2)
                entrega = verificar_area_entrega(dados_dest)

                resultado = {
                    "CEP Remetente": remetente,
                    "Logradouro Remetente": dados_rem.get("logradouro", ""),
                    "Cidade Remetente": dados_rem.get("localidade", ""),
                    "UF Remetente": dados_rem.get("uf", ""),
                    "CEP Destinatário": destinatario,
                    "Logradouro Destinatário": dados_dest.get("logradouro", ""),
                    "Cidade Destinatário": dados_dest.get("localidade", ""),
                    "UF Destinatário": dados_dest.get("uf", ""),
                    "Distância (KM)": km,
                    "Entrega Possível?": entrega
                }

                st.session_state.df = pd.DataFrame([resultado])
                st.session_state.coord_rem = coord_rem
                st.session_state.coord_dest = coord_dest
                st.session_state.consulta_feita = True

# Exibir resultados se consulta foi feita
if st.session_state.consulta_feita:
    st.success("✅ Consulta finalizada")
    st.dataframe(st.session_state.df)

    # Botões de download
    st.download_button(
        "📥 Baixar CSV",
        data=st.session_state.df.to_csv(index=False).encode("utf-8"),
        file_name="consulta_ceps.csv",
        mime="text/csv"
    )
    st.download_button(
        "📥 Baixar Excel",
        data=to_excel(st.session_state.df),
        file_name="consulta_ceps.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Exibir mapa
    st.subheader("🗺️ Mapa da rota entre os CEPs")
    m = folium.Map(location=st.session_state.coord_rem, zoom_start=6)
    folium.Marker(st.session_state.coord_rem, tooltip="Remetente", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(st.session_state.coord_dest, tooltip="Destinatário", icon=folium.Icon(color="blue")).add_to(m)
    folium.PolyLine([st.session_state.coord_rem, st.session_state.coord_dest], color="red", weight=2.5).add_to(m)
    st_folium(m, width=800, height=500)
