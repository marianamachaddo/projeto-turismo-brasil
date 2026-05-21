
def grafico_crescimento(dados: pd.DataFrame) -> go.Figure | None:
    anos = sorted(dados["ano"].unique())
    if len(anos) < 2:
        return None

    ano_inicial, ano_final = anos[0], anos[-1]
    crescimento = (
        dados[dados["ano"].isin([ano_inicial, ano_final])]
        .groupby(["cidade", "ano"], as_index=False)["turistas"]
        .sum()
        .pivot(index="cidade", columns="ano", values="turistas")
        .fillna(0)
    )
    if ano_inicial not in crescimento.columns or ano_final not in crescimento.columns:
        return None

    crescimento = crescimento[crescimento[ano_inicial] > 0].copy()
    crescimento["crescimento_percentual"] = (
        (crescimento[ano_final] - crescimento[ano_inicial]) / crescimento[ano_inicial] * 100
    )
    crescimento["crescimento_absoluto"] = crescimento[ano_final] - crescimento[ano_inicial]
    crescimento = (
        crescimento.reset_index()
        .sort_values("crescimento_percentual", ascending=False)
        .head(10)
        .sort_values("crescimento_percentual")
    )

    fig = px.bar(
        crescimento,
        x="crescimento_percentual",
        y="cidade",
        orientation="h",
        color="crescimento_percentual",
        color_continuous_scale="Teal",
        text="crescimento_percentual",
        title=f"Destinos com maior crescimento de turistas ({ano_inicial} x {ano_final})",
        labels={"crescimento_percentual": "Crescimento (%)", "cidade": "Cidade"},
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(template="plotly_white", yaxis_title="")
    return fig


def tabela_dinamica(dados: pd.DataFrame) -> pd.DataFrame:
    tabela = pd.pivot_table(
        dados,
        index=["regiao", "uf", "cidade"],
        columns="nivel_temporada",
        values="turistas",
        aggfunc="sum",
        fill_value=0,
        observed=True,
    )
    tabela["Total turistas"] = tabela.sum(axis=1)

    complementos = dados.groupby(["regiao", "uf", "cidade"], observed=True).agg(
        Receita=("faturamento_turismo", "sum"),
        Ocupacao_media=("ocupacao_hoteleira", "mean"),
        Gasto_medio=("gasto_medio", "mean"),
        Eventos=("eventos_realizados", "sum"),
    )
    tabela = tabela.join(complementos).reset_index()
    return tabela.sort_values("Total turistas", ascending=False)


st.title("Turismo no Brasil: análise de dados turísticos")
st.caption("Projeto G2 - Tema 18 | Dados simulados de 2015 a 2024")

st.markdown(
    """
    Esta aplicação investiga padrões do turismo no Brasil, com foco em fluxo de turistas,
    sazonalidade, comparação regional, ocupação hoteleira, clima e impacto econômico.
    Use os filtros laterais para explorar diferentes recortes da base.
    """
)

arquivo_enviado = st.sidebar.file_uploader("Carregar outro CSV", type=["csv"])

try:
    df_original = carregar_dados(arquivo_enviado)
except Exception as erro:
    st.error(f"Não foi possível carregar a base de dados: {erro}")
    st.stop()

dados = filtrar_dados(df_original)

if dados.empty:
    st.warning("Nenhum registro encontrado para os filtros selecionados.")
    st.stop()

kpis = calcular_kpis(dados)
mostrar_kpis(kpis)

st.divider()

aba_geral, aba_destinos, aba_sazonalidade, aba_dados = st.tabs(
    ["Visão geral", "Regiões e destinos", "Sazonalidade e clima", "Dados e conclusão"]
)

with aba_geral:
    st.subheader("Evolução temporal e impacto econômico")
    st.plotly_chart(grafico_temporal(dados), width="stretch")
    st.markdown(texto_interpretativo(dados, kpis))

    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(grafico_regioes(dados), width="stretch")
    with col_b:
        st.plotly_chart(grafico_dispersao_receita(dados), width="stretch")

with aba_destinos:
    st.subheader("Ranking de destinos turísticos")
    limite = st.slider("Quantidade de cidades no ranking", min_value=5, max_value=25, value=10, step=1)
    st.plotly_chart(grafico_cidades(dados, limite), width="stretch")

    grafico = grafico_crescimento(dados)
    if grafico is not None:
        st.plotly_chart(grafico, width="stretch")
    else:
        st.info("Selecione pelo menos dois anos para calcular crescimento entre períodos.")

    st.markdown(
        "A comparação entre cidades permite identificar destinos consolidados e destinos em expansão. "
        "Quando uma cidade cresce acima das demais, isso pode indicar novos investimentos, eventos, "
        "mudanças de preferência dos turistas ou melhor infraestrutura de serviços."
    )

with aba_sazonalidade:
    st.subheader("Sazonalidade, hotelaria e clima")
    st.plotly_chart(heatmap_sazonalidade(dados), width="stretch")

    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(grafico_temporada(dados), width="stretch")
    with col_b:
        st.plotly_chart(grafico_ocupacao(dados), width="stretch")

    st.plotly_chart(grafico_clima(dados), width="stretch")
    st.markdown(
        "A leitura conjunta de mês, temporada, eventos e temperatura ajuda a diferenciar picos sazonais "
        "de movimentos possivelmente associados a eventos específicos ou a características climáticas do destino."
    )

with aba_dados:
    st.subheader("Tabela dinâmica para exploração detalhada")
    tabela = tabela_dinamica(dados)
    st.dataframe(
        tabela,
        width="stretch",
        hide_index=True,
        column_config={
            "Receita": st.column_config.NumberColumn("Receita", format="R$ %.2f"),
            "Ocupacao_media": st.column_config.NumberColumn("Ocupação média (%)", format="%.2f"),
            "Gasto_medio": st.column_config.NumberColumn("Gasto médio", format="R$ %.2f"),
            "Eventos": st.column_config.NumberColumn("Eventos", format="%d"),
        },
    )

    csv_filtrado = dados.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Baixar dados filtrados",
        data=csv_filtrado,
        file_name="turismo_brasil_filtrado.csv",
        mime="text/csv",
    )

    st.subheader("Conclusão executiva")
    st.success(
        "O turismo analisado apresenta forte relevância econômica, com diferenças regionais e sazonais "
        "visíveis nos indicadores. Os resultados indicam que a tomada de decisão no setor deve considerar "
        "não apenas o volume de visitantes, mas também faturamento, ocupação hoteleira, gasto médio, eventos "
        "e condições climáticas. Destinos com maior crescimento merecem acompanhamento, pois podem sinalizar "
        "novas oportunidades para infraestrutura, serviços e políticas públicas."
    )

    st.markdown("#### Qualidade da base")
    st.write(
        f"A base contém **{formatar_inteiro(len(df_original))} registros**, "
        f"**{df_original['cidade'].nunique()} cidades**, **{df_original['uf'].nunique()} estados** "
        f"e período de **{df_original['ano'].min()} a {df_original['ano'].max()}**."
    )
