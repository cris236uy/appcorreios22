import streamlit as st
import pandas as pd
import requests
from geopy.distance import geodesic
import folium
from streamlit_folium import st_folium

# --- Função para consultar dados do CEP via API ViaCEP
def consultar_cep(cep):
    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

# --- Função para verificar se o local é área de entrega
def verifica_area_entrega(dados_cep):
    if dados_cep and not dados_cep.get("erro"):
        if "rural" in dados_cep.get("bairro", "").lower():
            return "❌ Não recebe entregas"
        return "✅ Área de entrega"
    return "❓ CEP inválido"

# --- Função para coordenadas (utilizando Nominatim via API)
def get_lat_lon(endereco):
    try:
        response = requests.get(f"https://nominatim.openstreetmap.org/search?q={endereco}&format=json")
        if response.status_code == 200 and response.json():
            resultado = response.json()[0]
            return float(resultado["lat"]), float(resultado["lon"])
    except:
        return None, None

# --- Configuração da página
st.set_page_config(page_title="Consulta de CEPs", layout="wide")
st.title("📍 Consulta de CEPs, Área de Entrega e Distância")

# --- Upload ou entrada manual
opcao = st.radio("Escolha como deseja informar os dados:", ["📄 Planilha Excel", "✍️ Inserção Manual"])

if opcao == "📄 Planilha Excel":
    arquivo = st.file_uploader("Envie a planilha com colunas 'CEP_REMETENTE' e 'CEP_DESTINATARIO'", type=["xlsx"])
    if arquivo:
        df = pd.read_excel(arquivo)
else:
    st.markdown("### Inserção Manual")
    cep_remetente = st.text_input("CEP do Remetente")
    cep_destinatario = st.text_input("CEP do Destinatário")
    if cep_remetente and cep_destinatario:
        df = pd.DataFrame([{"CEP_REMETENTE": cep_remetente, "CEP_DESTINATARIO": cep_destinatario}])
    else:
        df = pd.DataFrame()

# --- Processamento
if not df.empty:
    resultados = []

    for _, row in df.iterrows():
        cep_r = str(row["CEP_REMETENTE"]).strip().replace("-", "")
        cep_d = str(row["CEP_DESTINATARIO"]).strip().replace("-", "")

        dados_r = consultar_cep(cep_r)
        dados_d = consultar_cep(cep_d)

        end_r = f"{dados_r.get('logradouro','')}, {dados_r.get('bairro','')}, {dados_r.get('localidade','')}, {dados_r.get('uf','')}" if dados_r else ""
        end_d = f"{dados_d.get('logradouro','')}, {dados_d.get('bairro','')}, {dados_d.get('localidade','')}, {dados_d.get('uf','')}" if dados_d else ""

        lat_r, lon_r = get_lat_lon(end_r)
        lat_d, lon_d = get_lat_lon(end_d)

        if lat_r and lat_d:
            km = round(geodesic((lat_r, lon_r), (lat_d, lon_d)).km, 2)
        else:
            km = "❓"

        resultados.append({
            "CEP Remetente": cep_r,
            "Área Entrega Remetente": verifica_area_entrega(dados_r),
            "CEP Destinatário": cep_d,
            "Área Entrega Destinatário": verifica_area_entrega(dados_d),
            "Distância (km)": km
        })

    df_resultado = pd.DataFrame(resultados)

    st.success("✅ Consulta finalizada!")
    st.dataframe(df_resultado)

    # Botões para download
    st.download_button("📥 Baixar em CSV", df_resultado.to_csv(index=False).encode("utf-8"), file_name="ceps.csv", mime="text/csv")
    st.download_button("📥 Baixar em Excel", df_resultado.to_excel(index=False, engine="openpyxl"), file_name="ceps.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # --- Mapa
    st.markdown("### 🗺️ Visualização no Mapa")

    mapa = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)

    for idx, row in df_resultado.iterrows():
        lat1, lon1 = get_lat_lon(row["CEP Remetente"])
        lat2, lon2 = get_lat_lon(row["CEP Destinatário"])

        if lat1 and lon1:
            folium.Marker(location=[lat1, lon1], popup=f"Remetente: {row['CEP Remetente']}", icon=folium.Icon(color="blue")).add_to(mapa)
        if lat2 and lon2:
            folium.Marker(location=[lat2, lon2], popup=f"Destinatário: {row['CEP Destinatario']}", icon=folium.Icon(color="green")).add_to(mapa)

        if lat1 and lat2:
            folium.PolyLine(locations=[(lat1, lon1), (lat2, lon2)], color="gray").add_to(mapa)

    st_folium(mapa, width=900, height=500)
