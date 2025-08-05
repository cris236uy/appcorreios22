if coords_rem and coords_dest:
    dist_km = round(geodesic(coords_rem, coords_dest).km, 2)
    st.success(f"📏 Distância aproximada entre os dois CEPs: **{dist_km} km**")

    # --- Mapa com trajeto usando folium ---
    import folium
    from streamlit_folium import st_folium

    map_center = [(coords_rem[0] + coords_dest[0]) / 2, (coords_rem[1] + coords_dest[1]) / 2]
    m = folium.Map(location=map_center, zoom_start=7)

    folium.Marker(location=coords_rem, popup="Remetente", icon=folium.Icon(color='blue')).add_to(m)
    folium.Marker(location=coords_dest, popup="Destinatário", icon=folium.Icon(color='red')).add_to(m)

    folium.PolyLine(locations=[coords_rem, coords_dest], color="green", weight=5, opacity=0.7).add_to(m)

    st_folium(m, width=700, height=500)

    # --- Exportar (mantém igual) ---
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
    st.download_button("📥 Baixar CSV", csv, "dados_ceps.csv", "text/csv")
    # Removi o Excel para evitar criar arquivo no disco desnecessariamente
else:
    st.error("Não foi possível calcular a distância entre os CEPs.")
    
