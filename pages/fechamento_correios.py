# Verifica se a coluna "DATA" existe
if "DATA" not in df.columns:
    st.error("A base de dados deve conter uma coluna chamada 'DATA'.")
else:
    # Converte a coluna de datas se necessário
    if not np.issubdtype(df["DATA"].dtype, np.datetime64):
        df["DATA"] = pd.to_datetime(df["DATA"])

    # Obtém datas mínimas e máximas da base
    data_min = df["DATA"].min().date()
    data_max = df["DATA"].max().date()

    # Seletor de intervalo de datas com base no conteúdo real da planilha
    d = st.date_input(
        "Selecione o intervalo de datas",
        (data_min, data_max),
        min_value=data_min,
        max_value=data_max,
        format="DD/MM/YYYY"
    )

    # Verifica se o usuário selecionou duas datas
    if isinstance(d, tuple) and len(d) == 2:
        start_date, end_date = d

        # 🔍 Filtra o DataFrame pelo intervalo de datas (inclusive mês para mês)
        filtro = df[(df["DATA"].dt.date >= start_date) & (df["DATA"].dt.date <= end_date)]

        # ➕ Soma total do valor no período
        total_valor = filtro["VALOR"].sum()

        # 📊 Soma por centro de custo
        soma_por_centro = filtro.groupby("CENTRO DE CUSTO")["VALOR"].sum().reset_index()

        # ✅ Exibe os dados filtrados
        st.subheader("Dados Filtrados")
        st.dataframe(filtro)

        # 💬 Exibe o total geral
        st.success(f"Total do VALOR no intervalo selecionado: R$ {total_valor:,.2f}")

        # 📋 Exibe o total por centro de custo
        st.subheader("Total por Centro de Custo")
        st.dataframe(soma_por_centro)

        # 📤 Exportar para Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            filtro.to_excel(writer, sheet_name='Filtrados', index=False)
            soma_por_centro.to_excel(writer, sheet_name='Resumo por Centro', index=False)
        output.seek(0)

        st.download_button(
            label="📥 Baixar dados filtrados em Excel",
            data=output,
            file_name="dados_filtrados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Selecione um intervalo de duas datas.")
        
