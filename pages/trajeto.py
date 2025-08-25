import streamlit as st
import pandas as pd
import requests
from geopy.distance import geodesic
import folium
from streamlit_folium import st_folium

# --- Configurações ---
st.set_page_config(page_title="Consulta de CEPs", layout="wide")
st.title("📦 Consulta de Endereços e Distância por CEP")

# --- Função para consultar a API ViaCEP ---
def consultar_cep(cep):
    url = f"https://viacep.com.br/ws/{cep}/json/"
    response = requests.get(url)
    if response.status_code == 200 and 'erro' not in response.text:
        return response.json()
    else:
        return None

# --- Função para estimar coordenadas via Nominatim (OpenStreetMap) ---
def get_coords_por_cidade_uf(cidade, uf):
    try:
        url_coords = f"https://nominatim.openstreetmap.org/search?city={cidade}&state={uf}&country=Brasil&format=json"
        response = requests.get(url_coords, headers={'User-Agent': 'Mozilla/5.0'}).json()
        if response:
            lat = float(response[0]['lat'])
            lon = float(response[0]['lon'])
            return (lat, lon)
    except:
        return None

# --- Inicializa variáveis de estado ---
if "consultado" not in st.session_state:
    st.session_state.consultado = False
if "cep_remetente" not in st.session_state:
    st.session_state.cep_remetente = ""
if "cep_destinatario" not in st.session_state:
    st.session_state.cep_destinatario = ""

# --- Entradas ---
col1, col2 = st.columns(2)
with col1:
    cep_remetente = st.text_input("CEP do Remetente:", placeholder="Ex: 01001-000", value=st.session_state.cep_remetente)
with col2:
    cep_destinatario = st.text_input("CEP do Destinatário:", placeholder="Ex: 01310-200", value=st.session_state.cep_destinatario)

# --- Botão para consultar ---
if st.button("Consultar"):
    if cep_remetente and cep_destinatario:
        st.session_state.consultado = True
        st.session_state.cep_remetente = cep_remetente
        st.session_state.cep_destinatario = cep_destinatario
    else:
        st.warning("Informe ambos os CEPs.")
        st.session_state.consultado = False

# --- Mostrar resultados se consultado ---
if st.session_state.consultado:
    cep_remetente = st.session_state.cep_remetente
    cep_destinatario = st.session_state.cep_destinatario

    end_rem = consultar_cep(cep_remetente)
    end_dest = consultar_cep(cep_destinatario)

    if end_rem and end_dest:
        st.subheader("🔎 Detalhes dos Endereços")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Remetente**")
            for k, v in end_rem.items():
                st.write(f"{k.capitalize()}: {v}")

        with col2:
            st.markdown("**Destinatário**")
            for k, v in end_dest.items():
                st.write(f"{k.capitalize()}: {v}")

        # Verifica se é área urbana
        tipo_destino = "Urbana (Aceita entrega)" if end_dest.get("bairro") else "Rural (Pode não aceitar entrega)"
        st.warning(f"📍 Área do destinatário: **{tipo_destino}**")

        # Obter coordenadas aproximadas
        coords_rem = get_coords_por_cidade_uf(end_rem['localidade'], end_rem['uf'])
        coords_dest = get_coords_por_cidade_uf(end_dest['localidade'], end_dest['uf'])

        if coords_rem and coords_dest:
            dist_km = round(geodesic(coords_rem, coords_dest).km, 2)
            st.success(f"📏 Distância aproximada entre os dois CEPs: **{dist_km} km**")

            # --- Mapa com trajeto usando folium ---
            map_center = [(coords_rem[0] + coords_dest[0]) / 2, (coords_rem[1] + coords_dest[1]) / 2]
            m = folium.Map(location=map_center, zoom_start=7)

            folium.Marker(location=coords_rem, popup="Remetente", icon=folium.Icon(color='blue')).add_to(m)
            folium.Marker(location=coords_dest, popup="Destinatário", icon=folium.Icon(color='red')).add_to(m)

            folium.PolyLine(locations=[coords_rem, coords_dest], color="green", weight=5, opacity=0.7).add_to(m)

            st_folium(m, width=700, height=500)

            # --- Exportar CSV ---
            dados = {
                "CEP Remetente": [cep_remetente],
                "Endereço Remetente": [f"{end_rem.get('logradouro', '')}, {end_rem.get('bairro', '')}, {end_rem.get('localidade', '')}-{end_rem.get('uf', '')}"],
                "CEP Destinatário": [cep_destinatario],
                "Endereço Destinatário": [f"{end_dest.get('logradouro', '')}, {end_dest.get('bairro', '')}, {end_dest.get('localidade', '')}-{end_dest.get('uf', '')}"],
                "Área Entrega": [tipo_destino],
                "Distância (km)": [dist_km]
            }
            df_resultado = pd.DataFrame(dados)

            csv = df_resultado.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Baixar CSV", csv, "dados_ceps.csv", "text/csv")

        else:
            st.error("Não foi possível calcular a distância entre os CEPs.")
    else:
        st.error("Um dos CEPs é inválido ou não encontrado.") adicione o grafico que eu coloquei acima quando eu mostrar as informacoes que eu digitar 
