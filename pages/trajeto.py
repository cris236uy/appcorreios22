        import streamlit as st
import pandas as pd
import requests
from geopy.distance import geodesic

# --- Título ---
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

# --- Função para estimar coordenadas via IBGE ---
def get_coords_por_cidade_uf(cidade, uf):
    try:
        url = f"https://servicodados.ibge.gov.br/api/v2/malhas/municipios?formato=application/vnd.geo+json"
        url_coords = f"https://nominatim.openstreetmap.org/search?city={cidade}&state={uf}&country=Brasil&format=json"
        response = requests.get(url_coords).json()
        if response:
            lat = float(response[0]['lat'])
            lon = float(response[0]['lon'])
            return (lat, lon)
    except:
        return None

# --- Entradas ---
col1, col2 = st.columns(2)
with col1:
    cep_remetente = st.text_input("CEP do Remetente:", placeholder="Ex: 01001-000")
with col2:
    cep_destinatario = st.text_input("CEP do Destinatário:", placeholder="Ex: 01310-200")

# --- Processar ---
if st.button("Consultar"):
    if cep_remetente and cep_destinatario:
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

            # Coordenadas aproximadas
            coords_rem = get_coords_por_cidade_uf(end_rem['localidade'], end_rem['uf'])
            coords_dest = get_coords_por_cidade_uf(end_dest['localidade'], end_dest['uf'])

            if coords_rem and coords_dest:
                dist_km = round(geodesic(coords_rem, coords_dest).km, 2)
                st.success(f"📏 Distância aproximada entre os dois CEPs: **{dist_km} km**")

                # --- Mapa ---
                df_mapa = pd.DataFrame({
                    'Local': ['Remetente', 'Destinatário'],
                    'lat': [coords_rem[0], coords_dest[0]],
                    'lon': [coords_rem[1], coords_dest[1]]
                })
                st.map(df_mapa)

                # --- Exportar ---
                dados = {
                    "CEP Remetente": [cep_remetente],
                    "Endereço Remetente": [f"{end_rem['logradouro']}, {end_rem['bairro']}, {end_rem['localidade']}-{end_rem['uf']}"],
                    "CEP Destinatário": [cep_destinatario],
                    "Endereço Destinatário": [f"{end_dest['logradouro']}, {end_dest['bairro']}, {end_dest['localidade']}-{end_dest['uf']}"],
                    "Área Entrega": [tipo_destino],
                    "Distância (km)": [dist_km]
                }
                df_resultado = pd.DataFrame(dados)

                csv = df_resultado.to_csv(index=False).encode('utf-8')
                excel = df_resultado.to_excel("dados_ceps.xlsx", index=False, engine='openpyxl')

                st.download_button("📥 Baixar CSV", csv, "dados_ceps.csv", "text/csv")
                with open("dados_ceps.xlsx", "rb") as f:
                    st.download_button("📥 Baixar Excel", f, "dados_ceps.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            else:
                st.error("Não foi possível calcular a distância entre os CEPs.")
        else:
            st.error("Um dos CEPs é inválido ou não encontrado.")
    else:
        st.warning("Informe ambos os CEPs.")
