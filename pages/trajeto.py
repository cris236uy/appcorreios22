import plotly.graph_objects as go

if coords_rem and coords_dest:
    # --- Distância e mapa Folium (já existente) ---
    dist_km = round(geodesic(coords_rem, coords_dest).km, 2)
    st.success(f"📏 Distância aproximada entre os dois CEPs: **{dist_km} km**")

    # --- Mapa Folium ---
    map_center = [(coords_rem[0] + coords_dest[0]) / 2, (coords_rem[1] + coords_dest[1]) / 2]
    m = folium.Map(location=map_center, zoom_start=7)
    folium.Marker(location=coords_rem, popup="Remetente", icon=folium.Icon(color='blue')).add_to(m)
    folium.Marker(location=coords_dest, popup="Destinatário", icon=folium.Icon(color='red')).add_to(m)
    folium.PolyLine(locations=[coords_rem, coords_dest], color="green", weight=5, opacity=0.7).add_to(m)
    st_folium(m, width=700, height=500)

    # --- Gráfico Plotly ---
    # Definindo os vértices do polígono como os dois CEPs + pequenas variações para fechar o polígono
    lats = [coords_rem[0], coords_dest[0], coords_dest[0]-0.2, coords_rem[0]-0.2]
    lons = [coords_rem[1], coords_dest[1], coords_dest[1]+0.2, coords_rem[1]+0.2]

    fig = go.Figure(go.Scattermapbox(
        fill="toself",
        lon=lons,
        lat=lats,
        marker={'size': 10, 'color': "orange"}
    ))

    fig.update_layout(
        mapbox={
            'style': "open-street-map",
            'center': {'lon': (coords_rem[1]+coords_dest[1])/2, 'lat': (coords_rem[0]+coords_dest[0])/2},
            'zoom': 6
        },
        showlegend=False,
        margin={'l':0,'r':0,'t':0,'b':0}
    )

    st.subheader("📍 Mapa Interativo com Plotly")
    st.plotly_chart(fig, use_container_width=True)
