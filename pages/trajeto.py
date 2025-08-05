import streamlit as st
import pandas as pd
import requests
import folium
from folium import Marker
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from geopy.distance import geodesic
from io import BytesIO
from streamlit_folium import st_folium

# Função para buscar informações do CEP via API gratuita ViaCEP
def buscar_info_cep(cep):
    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

# Função para rastrear código no Muambator
def rastrear_objeto(codigo):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://www.muambator.com.br/")
        driver.implicitly_wait(5)
        campo = driver.find_element(By.ID, "pesquisaPub")
        campo.clear()
        campo.send_keys(codigo)
        botao = driver.find_element(By.ID, "submitPesqPub")
        driver.execute_script("arguments[0].click();", botao)
        driver.implicitly_wait(5)
        status = driver.find_element(By.CLASS_NAME, "situacao-header").text
    except Exception:
        status = "Erro ao rastrear"
    finally:
        driver.quit()
    return status

# Título da aplicação
st.title("📦 Rastreador & Analisador de Encomendas")

# Entrada de CEPs
col1, col2 = st.columns(2)
with col1:
    cep_remetente = st.text_input("CEP do Remetente", placeholder="Ex: 01001-000")
with col2:
    cep_destinatario = st.text_input("CEP do Destinatário", placeholder="Ex: 01310-000")

# Consulta dos dados dos CEPs
if cep_remetente and cep_destinatario:
    info_rem = buscar_info_cep(cep_remetente)
    info_dest = buscar_info_cep(cep_destinatario)

    if not info_rem or "erro" in info_rem:
        st.error("❌ CEP do remetente inválido ou não localizado.")
    elif not info_dest or "erro" in info_dest:
        st.error("❌ CEP do destinatário inválido ou não localizado.")
    else:
        st.success("✅ Endereços localizados com sucesso.")
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("📍 Remetente")
            st.write(info_rem)
        with col4:
            st.subheader("📍 Destinatário")
            st.write(info_dest)

        # Cálculo da distância
        try:
            coord_rem = (float(info_rem['latitude']), float(info_rem['longitude']))
            coord_dest = (float(info_dest['latitude']), float(info_dest['longitude']))
        except:
            # Se não vier latitude/longitude do ViaCEP, usar geopy para buscar
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent="cep_app")
            location_rem = geolocator.geocode(info_rem['logradouro'] + ", " + info_rem['localidade'])
            location_dest = geolocator.geocode(info_dest['logradouro'] + ", " + info_dest['localidade'])
            if location_rem and location_dest:
                coord_rem = (location_rem.latitude, location_rem.longitude)
                coord_dest = (location_dest.latitude, location_dest.longitude)

        distancia_km = geodesic(coord_rem, coord_dest).km
        st.metric("🚛 Distância entre os CEPs", f"{distancia_km:.2f} km")

        # Mapa
        mapa = folium.Map(location=coord_rem, zoom_start=6)
        Marker(coord_rem, tooltip="Remetente", icon=folium.Icon(color="blue")).add_to(mapa)
        Marker(coord_dest, tooltip="Destinatário", icon=folium.Icon(color="red")).add_to(mapa)
        folium.PolyLine(locations=[coord_rem, coord_dest], color='green').add_to(mapa)
        st_folium(mapa, width=700)

# Rastreio de múltiplos códigos
st.subheader("📦 Rastreio de Códigos")
codigos_raw = st.text_area("Cole os códigos de rastreio (um por linha):")

if st.button("🔍 Rastrear Todos"):
    codigos = [c.strip() for c in codigos_raw.strip().split("\n") if c.strip()]
    resultados = []

    with st.spinner("Rastreando..."):
        for i, cod in enumerate(codigos):
            status = rastrear_objeto(cod)
            resultados.append({"Código": cod, "Status": status})
            st.write(f"{i+1}/{len(codigos)} - {cod}: {status}")

    df_resultados = pd.DataFrame(resultados)
    st.success("✅ Rastreamento finalizado!")
    st.dataframe(df_resultados)

    # Download CSV
    st.download_button("⬇ Baixar em CSV", df_resultados.to_csv(index=False).encode("utf-8"), "rastreio.csv", "text/csv")

    # Download Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_resultados.to_excel(writer, index=False, sheet_name="Rastreamento")
    st.download_button("⬇ Baixar em Excel", output.getvalue(), "rastreio.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
