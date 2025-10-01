import streamlit as st
import pandas as pd
import requests
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from io import BytesIO
import folium
from streamlit_folium import st_folium
import re

# -----------------------------
# Funções auxiliares
# -----------------------------

# Valida CEP (formato 00000-000 ou 00000000)
def cep_valido(cep):
    return re.fullmatch(r"\d{5}-?\d{3}", cep) is not None

# Consulta CEP na API ViaCEP
def consultar_cep(cep):
    try:
        r = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=10)
        dados = r.json()
        if dados.get("erro"):
            return {"cep": cep, "erro": True}
        return dados
    except Exception as e:
        return {"cep": cep, "erro": True, "mensagem": str(e)}

# Obter coordenadas geográficas de um CEP (com cache para performance)
@st.cache_data
def coordenadas_por_cep(cep):
    localizador = Nominatim(user_agent="consulta_cep_app")
    try:
        local = localizador.geocode(cep + ", Brasil", timeout=10)
        if local:
            return (local.latitude, local.longitude)
    except Exception:
        pass
    return None

# Verificar se o endereço parece rural
def verificar_area_entrega(dados_cep):
    log = dados_cep.get("logradouro", "").lower()
    if not log or any(x in log for x in ["sítio", "chácara", "fazenda", "zona rural"]):
        return "❌ Área Rural - Pode não receber entregas"
    return "✅ Área urbana"

# Converter DataFrame para Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="CEPs")
    output.seek(0)
    return output.read()

# -----------------------------
# Configuração da página
# -----------------------------
st.set_page_config(page_title="🚚 Cálculo de Entrega por CEP", layout="wide")
st.title("🚚 Consulta de Entrega por CEP")

# Inicializar session_state
if "consultas" not in st.session_state:
    st.session_state.consultas = []  # agora guarda histórico
    st.session_state.coord_rem = None
    st.session_state.coord_dest = None

# -----------------------------
# Entradas
# -----------------------------
remetente = st.text_input("CEP do Remetente", placeholder="Ex: 01001-000")
destinatario = st.text_input("CEP do Destinatário", placeholder="Ex: 87083-320")

# Limpar hífen
remetente_clean = remetente.replace("-", "") if remetente else ""
destinatario_clean = destinatario.replace("-", "") if destinatario else ""

# -----------------------------
# Botão de consulta
# -----------------------------
if st.button("Consultar"):
    if not remetente or not destinatario:
        st.warning("Informe os dois CEPs.")
    elif not cep_valido(remetente) or not cep_valido(destinatario):
        st.error("Um dos CEPs está em formato inválido.")
    else:
        with st.spinner("🔎 Consultando CEPs..."):
            dados_rem = consultar_cep(remetente_clean)
            dados_dest = consultar_cep(destinatario_clean)

            if dados_rem.get("erro") or dados_dest.get("erro"):
                st.error("Um dos CEPs não foi encontrado.")
            else:
                coord_rem = coordenadas_por_cep(remetente_clean)
                coord_dest = coordenadas_por_cep(destinatario_clean)

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
                        "Entrega Possível?": entrega,
                    }

                    st.session_state.consultas.append(resultado)
                    st.session_state.coord_rem = coord_rem
                    st.session_state.coord_dest = coord_dest

# -----------------------------
# Exibir resultados
# -----------------------------
if st.session_state.consultas:
    df = pd.DataFrame(st.session_state.consultas)
    st.success("✅ Consulta finalizada")
    st.dataframe(df)

    # Botões de download
    st.download_button(
        "📥 Baixar CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="consulta_ceps.csv",
        mime="text/csv"
    )
    st.download_button(
        "📥 Baixar Excel",
        data=to_excel(df),
        file_name="consulta_ceps.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Exibir mapa (última rota consultada)
    st.subheader("🗺️ Mapa da rota entre os últimos CEPs consultados")
    lat_c = (st.session_state.coord_rem[0] + st.session_state.coord_dest[0]) / 2
    lon_c = (st.session_state.coord_rem[1] + st.session_state.coord_dest[1]) / 2
    m = folium.Map(location=(lat_c, lon_c), zoom_start=6)
    folium.Marker(st.session_state.coord_rem, tooltip="Remetente", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(st.session_state.coord_dest, tooltip="Destinatário", icon=folium.Icon(color="blue")).add_to(m)
    folium.PolyLine([st.session_state.coord_rem, st.session_state.coord_dest], color="red", weight=2.5).add_to(m)
    st_folium(m, width=800, height=500)
