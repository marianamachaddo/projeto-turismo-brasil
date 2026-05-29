from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


DATA_PATH = Path(__file__).parent / "dados" / "simulacao_turismo_brasil.csv"
DATABASE_PATH = Path(__file__).parent / "database" / "turismo.db"

MESES = {
    1: "Jan",
    2: "Fev",
    3: "Mar",
    4: "Abr",
    5: "Mai",
    6: "Jun",
    7: "Jul",
    8: "Ago",
    9: "Set",
    10: "Out",
    11: "Nov",
    12: "Dez",
}

TEMPORADA_ORDEM = ["Baixa", "Média", "Alta"]
CORES = ["#2563EB", "#059669", "#F59E0B", "#DC2626", "#7C3AED", "#0891B2"]


st.set_page_config(
    page_title="Turismo no Brasil",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def formatar_inteiro(valor: float) -> str:
    return f"{valor:,.0f}".replace(",", ".")


def formatar_decimal(valor: float, casas: int = 2) -> str:
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_moeda(valor: float) -> str:
    if pd.isna(valor):
        valor = 0

    if abs(valor) >= 1_000_000_000:
        return f"R$ {formatar_decimal(valor / 1_000_000_000)} bi"
    if abs(valor) >= 1_000_000:
        return f"R$ {formatar_decimal(valor / 1_000_000)} mi"
    return f"R$ {formatar_decimal(valor)}"


def formatar_moeda_curta(valor: float) -> str:
    if pd.isna(valor):
        valor = 0

    if abs(valor) >= 1_000_000_000:
        return f"R$ {formatar_decimal(valor / 1_000_000_000, 0)} bi"
    if abs(valor) >= 1_000_000:
        return f"R$ {formatar_decimal(valor / 1_000_000, 0)} mi"
    if abs(valor) >= 1_000:
        return f"R$ {formatar_decimal(valor / 1_000, 0)} mil"
    return f"R$ {formatar_decimal(valor, 0)}"


def formatar_percentual(valor: float) -> str:
    if pd.isna(valor):
        return "0,0%"
    return f"{formatar_decimal(valor, 1)}%"


def ticks_moeda(valores: pd.Series) -> tuple[np.ndarray, list[str]]:
    valor_maximo = valores.max()
    if pd.isna(valor_maximo) or valor_maximo <= 0:
        return np.array([0]), [formatar_moeda_curta(0)]

    tickvals = np.linspace(0, valor_maximo, 5)
    ticktext = [formatar_moeda_curta(valor) for valor in tickvals]
    return tickvals, ticktext


@st.cache_data
def carregar_dados(arquivo=None) -> tuple[pd.DataFrame, str]:
    if arquivo is not None:
        df = pd.read_csv(arquivo)
        fonte = "CSV enviado pelo usuario"
    elif DATABASE_PATH.exists():
        with sqlite3.connect(DATABASE_PATH) as conexao:
            df = pd.read_sql_query("SELECT * FROM turismo_brasil", conexao)
        fonte = "SQLite (database/turismo.db)"
    else:
        df = pd.read_csv(DATA_PATH)
        fonte = "CSV (dados/simulacao_turismo_brasil.csv)"

    colunas_obrigatorias = {
        "ano",
        "mes",
        "data",
        "regiao",
        "uf",
        "cidade",
        "turistas",
        "turistas_estrangeiros",
        "ocupacao_hoteleira",
        "gasto_medio",
        "faturamento_turismo",
        "eventos_realizados",
        "temperatura_media",
        "nivel_temporada",
    }

    colunas_ausentes = sorted(colunas_obrigatorias.difference(df.columns))
    if colunas_ausentes:
        raise ValueError(f"Colunas ausentes no dataset: {', '.join(colunas_ausentes)}")

    df["data"] = pd.to_datetime(df["data"], errors="coerce")

    numericas = [
        "ano",
        "mes",
        "turistas",
        "turistas_estrangeiros",
        "ocupacao_hoteleira",
        "gasto_medio",
        "faturamento_turismo",
        "eventos_realizados",
        "temperatura_media",
    ]
    for coluna in numericas:
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")

    df = df.dropna(subset=["ano", "mes", "data", "turistas", "faturamento_turismo"])
    df["ano"] = df["ano"].astype(int)
    df["mes"] = df["mes"].astype(int)
    df["mes_nome"] = df["mes"].map(MESES)
    df["ano_mes"] = pd.to_datetime(
        df["ano"].astype(str) + "-" + df["mes"].astype(str).str.zfill(2) + "-01"
    )
    df["participacao_estrangeiros"] = np.where(
        df["turistas"] > 0,
        df["turistas_estrangeiros"] / df["turistas"] * 100,
        0,
    )
    df["receita_por_turista"] = np.where(
        df["turistas"] > 0,
        df["faturamento_turismo"] / df["turistas"],
        0,
    )
    df["nivel_temporada"] = pd.Categorical(
        df["nivel_temporada"], categories=TEMPORADA_ORDEM, ordered=True
    )

    return df.sort_values("data"), fonte


def filtrar_dados(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filtros")

    anos = sorted(df["ano"].unique())
    anos_selecionados = st.sidebar.multiselect("Ano", anos, default=anos)

    meses = sorted(df["mes"].unique())
    meses_selecionados = st.sidebar.multiselect(
        "Mês",
        meses,
        default=meses,
        format_func=lambda mes: f"{mes:02d} - {MESES.get(mes, mes)}",
    )

    dados = df[df["ano"].isin(anos_selecionados) & df["mes"].isin(meses_selecionados)]

    regioes = sorted(dados["regiao"].unique())
    regioes_selecionadas = st.sidebar.multiselect("Região", regioes, default=regioes)
    dados = dados[dados["regiao"].isin(regioes_selecionadas)]

    estados = sorted(dados["uf"].unique())
    estados_selecionados = st.sidebar.multiselect("Estado", estados, default=estados)
    dados = dados[dados["uf"].isin(estados_selecionados)]

    cidades = sorted(dados["cidade"].unique())
    cidades_selecionadas = st.sidebar.multiselect("Cidade", cidades, default=cidades)
    dados = dados[dados["cidade"].isin(cidades_selecionadas)]

    temporadas = [temporada for temporada in TEMPORADA_ORDEM if temporada in dados["nivel_temporada"].astype(str).unique()]
    temporadas_selecionadas = st.sidebar.multiselect(
        "Nível de temporada", temporadas, default=temporadas
    )
    dados = dados[dados["nivel_temporada"].astype(str).isin(temporadas_selecionadas)]

    return dados


def calcular_kpis(dados: pd.DataFrame) -> dict:
    total_turistas = dados["turistas"].sum()
    receita_total = dados["faturamento_turismo"].sum()
    ocupacao_media = dados["ocupacao_hoteleira"].mean()
    gasto_medio = np.average(dados["gasto_medio"], weights=dados["turistas"]) if total_turistas else 0

    cidade_ranking = dados.groupby("cidade", as_index=False)["turistas"].sum()
    cidade_ranking = cidade_ranking.sort_values("turistas", ascending=False)
    cidade_mais_visitada = cidade_ranking.iloc[0] if not cidade_ranking.empty else None

    regiao_ranking = dados.groupby("regiao", as_index=False)["faturamento_turismo"].sum()
    regiao_ranking = regiao_ranking.sort_values("faturamento_turismo", ascending=False)
    regiao_mais_movimentada = regiao_ranking.iloc[0] if not regiao_ranking.empty else None

    return {
        "total_turistas": total_turistas,
        "receita_total": receita_total,
        "ocupacao_media": ocupacao_media,
        "gasto_medio": gasto_medio,
        "cidade_mais_visitada": cidade_mais_visitada,
        "regiao_mais_movimentada": regiao_mais_movimentada,
    }


def mostrar_kpis(kpis: dict) -> None:
    linha_1 = st.columns(3)
    linha_1[0].metric("Total de turistas", formatar_inteiro(kpis["total_turistas"]))
    linha_1[1].metric("Receita total do turismo", formatar_moeda(kpis["receita_total"]))
    linha_1[2].metric("Ocupação hoteleira média", formatar_percentual(kpis["ocupacao_media"]))

    cidade = kpis["cidade_mais_visitada"]
    regiao = kpis["regiao_mais_movimentada"]

    linha_2 = st.columns(3)
    linha_2[0].metric(
        "Cidade mais visitada",
        cidade["cidade"] if cidade is not None else "-",
        formatar_inteiro(cidade["turistas"]) if cidade is not None else None,
    )
    linha_2[1].metric("Gasto médio por turista", formatar_moeda(kpis["gasto_medio"]))
    linha_2[2].metric(
        "Região mais movimentada",
        regiao["regiao"] if regiao is not None else "-",
        formatar_moeda(regiao["faturamento_turismo"]) if regiao is not None else None,
    )


def texto_interpretativo(dados: pd.DataFrame, kpis: dict) -> str:
    cidade = kpis["cidade_mais_visitada"]
    regiao = kpis["regiao_mais_movimentada"]

    mes_pico = (
        dados.groupby("mes", as_index=False)["turistas"].sum().sort_values("turistas", ascending=False).iloc[0]
    )
    temporada_pico = (
        dados.groupby("nivel_temporada", observed=True)["turistas"].sum().sort_values(ascending=False).index[0]
    )
    correlacao = dados[["turistas", "faturamento_turismo"]].corr().iloc[0, 1]

    participacao_receita = 0
    if regiao is not None and kpis["receita_total"] > 0:
        participacao_receita = regiao["faturamento_turismo"] / kpis["receita_total"] * 100

    return (
        f"No recorte filtrado, o turismo movimentou **{formatar_inteiro(kpis['total_turistas'])} turistas** "
        f"e gerou **{formatar_moeda(kpis['receita_total'])}** em faturamento. "
        f"A cidade com maior fluxo foi **{cidade['cidade']}**, enquanto a região com maior receita foi "
        f"**{regiao['regiao']}**, responsável por **{formatar_percentual(participacao_receita)}** do faturamento. "
        f"O mês de maior movimento foi **{MESES.get(int(mes_pico['mes']), mes_pico['mes'])}**, "
        f"e a categoria de temporada com maior volume foi **{temporada_pico}**. "
        f"A correlação entre turistas e faturamento no recorte é **{formatar_decimal(correlacao, 2)}**, "
        "indicando o quanto o volume de visitantes acompanha a receita turística."
    )


def grafico_temporal(dados: pd.DataFrame) -> go.Figure:
    temporal = (
        dados.groupby("ano_mes", as_index=False)
        .agg(
            turistas=("turistas", "sum"),
            faturamento_turismo=("faturamento_turismo", "sum"),
            ocupacao_hoteleira=("ocupacao_hoteleira", "mean"),
        )
        .sort_values("ano_mes")
    )

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=temporal["ano_mes"],
            y=temporal["turistas"],
            mode="lines+markers",
            name="Turistas",
            line=dict(color=CORES[0], width=3),
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=temporal["ano_mes"],
            y=temporal["faturamento_turismo"],
            mode="lines",
            name="Faturamento",
            line=dict(color=CORES[1], width=3),
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title="Evolução mensal de turistas e faturamento",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    tickvals_receita, ticktext_receita = ticks_moeda(temporal["faturamento_turismo"])
    fig.update_yaxes(title_text="Turistas", secondary_y=False)
    fig.update_yaxes(
        title_text="Faturamento",
        tickvals=tickvals_receita,
        ticktext=ticktext_receita,
        secondary_y=True,
    )
    fig.update_xaxes(title_text="Período")
    return fig


def grafico_regioes(dados: pd.DataFrame) -> go.Figure:
    regioes = (
        dados.groupby("regiao", as_index=False)
        .agg(
            turistas=("turistas", "sum"),
            faturamento_turismo=("faturamento_turismo", "sum"),
            ocupacao_hoteleira=("ocupacao_hoteleira", "mean"),
        )
        .sort_values("faturamento_turismo", ascending=False)
    )
    regioes["faturamento_label"] = regioes["faturamento_turismo"].apply(formatar_moeda_curta)
    regioes["turistas_label"] = regioes["turistas"].apply(formatar_inteiro)
    regioes["ocupacao_label"] = regioes["ocupacao_hoteleira"].apply(formatar_percentual)

    fig = px.bar(
        regioes,
        x="regiao",
        y="faturamento_turismo",
        color="turistas",
        text="faturamento_label",
        custom_data=["faturamento_label", "turistas_label", "ocupacao_label"],
        color_continuous_scale="Blues",
        title="Faturamento turístico por região",
        labels={
            "regiao": "Região",
            "faturamento_turismo": "Faturamento",
            "turistas": "Turistas",
        },
    )
    tickvals, ticktext = ticks_moeda(regioes["faturamento_turismo"])
    fig.update_traces(
        texttemplate="%{text}",
        textposition="outside",
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Faturamento: %{customdata[0]}<br>"
            "Turistas: %{customdata[1]}<br>"
            "Ocupação média: %{customdata[2]}"
            "<extra></extra>"
        ),
    )
    fig.update_layout(template="plotly_white", coloraxis_colorbar_title="Turistas")
    fig.update_yaxes(tickvals=tickvals, ticktext=ticktext)
    return fig


def grafico_cidades(dados: pd.DataFrame, limite: int) -> go.Figure:
    cidades = (
        dados.groupby(["cidade", "uf", "regiao"], as_index=False)
        .agg(turistas=("turistas", "sum"), faturamento_turismo=("faturamento_turismo", "sum"))
        .sort_values("turistas", ascending=False)
        .head(limite)
        .sort_values("turistas")
    )
    fig = px.bar(
        cidades,
        x="turistas",
        y="cidade",
        color="regiao",
        orientation="h",
        text="turistas",
        hover_data=["uf", "faturamento_turismo"],
        color_discrete_sequence=CORES,
        title=f"Top {limite} destinos por quantidade de turistas",
        labels={"turistas": "Turistas", "cidade": "Cidade", "regiao": "Região"},
    )
    fig.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    fig.update_layout(template="plotly_white", yaxis_title="")
    return fig


def heatmap_sazonalidade(dados: pd.DataFrame) -> go.Figure:
    sazonalidade = dados.pivot_table(
        index="ano",
        columns="mes",
        values="turistas",
        aggfunc="sum",
        fill_value=0,
    ).sort_index()
    sazonalidade = sazonalidade.reindex(columns=range(1, 13), fill_value=0)
    sazonalidade.columns = [MESES[mes] for mes in sazonalidade.columns]

    fig = px.imshow(
        sazonalidade,
        aspect="auto",
        color_continuous_scale="YlGnBu",
        text_auto=".2s",
        title="Heatmap mensal de turistas",
        labels=dict(x="Mês", y="Ano", color="Turistas"),
    )
    fig.update_layout(template="plotly_white")
    return fig


def grafico_dispersao_receita(dados: pd.DataFrame) -> go.Figure:
    base = (
        dados.groupby(["cidade", "uf", "regiao"], as_index=False)
        .agg(
            turistas=("turistas", "sum"),
            faturamento_turismo=("faturamento_turismo", "sum"),
            ocupacao_hoteleira=("ocupacao_hoteleira", "mean"),
            gasto_medio=("gasto_medio", "mean"),
        )
    )
    fig = px.scatter(
        base,
        x="turistas",
        y="faturamento_turismo",
        size="ocupacao_hoteleira",
        color="regiao",
        hover_name="cidade",
        hover_data=["uf", "gasto_medio"],
        color_discrete_sequence=CORES,
        title="Relação entre turistas e faturamento por destino",
        labels={
            "turistas": "Turistas",
            "faturamento_turismo": "Faturamento (R$)",
            "ocupacao_hoteleira": "Ocupação hoteleira média",
            "regiao": "Região",
        },
    )
    tickvals, ticktext = ticks_moeda(base["faturamento_turismo"])
    fig.update_layout(template="plotly_white")
    fig.update_yaxes(tickvals=tickvals, ticktext=ticktext)
    return fig


def grafico_clima(dados: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        dados,
        x="temperatura_media",
        y="turistas",
        color="nivel_temporada",
        size="eventos_realizados",
        hover_data=["ano", "mes_nome", "cidade", "regiao"],
        color_discrete_sequence=[CORES[3], CORES[2], CORES[1]],
        title="Relação clima x turismo",
        labels={
            "temperatura_media": "Temperatura média (°C)",
            "turistas": "Turistas",
            "nivel_temporada": "Temporada",
            "eventos_realizados": "Eventos realizados",
        },
    )
    fig.update_layout(template="plotly_white")
    return fig


def grafico_ocupacao(dados: pd.DataFrame) -> go.Figure:
    fig = px.box(
        dados,
        x="nivel_temporada",
        y="ocupacao_hoteleira",
        color="nivel_temporada",
        category_orders={"nivel_temporada": TEMPORADA_ORDEM},
        color_discrete_sequence=[CORES[3], CORES[2], CORES[1]],
        title="Distribuição da ocupação hoteleira por temporada",
        labels={"nivel_temporada": "Temporada", "ocupacao_hoteleira": "Ocupação hoteleira (%)"},
    )
    fig.update_layout(template="plotly_white", showlegend=False)
    return fig


def grafico_temporada(dados: pd.DataFrame) -> go.Figure:
    temporada = (
        dados.groupby("nivel_temporada", observed=True, as_index=False)
        .agg(turistas=("turistas", "sum"), faturamento_turismo=("faturamento_turismo", "sum"))
        .sort_values("nivel_temporada")
    )
    fig = px.bar(
        temporada,
        x="nivel_temporada",
        y="turistas",
        color="nivel_temporada",
        text="turistas",
        category_orders={"nivel_temporada": TEMPORADA_ORDEM},
        color_discrete_sequence=[CORES[3], CORES[2], CORES[1]],
        title="Volume de turistas por nível de temporada",
        labels={"nivel_temporada": "Temporada", "turistas": "Turistas"},
    )
    fig.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    fig.update_layout(template="plotly_white", showlegend=False)
    return fig


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
    df_original, fonte_dados = carregar_dados(arquivo_enviado)
except Exception as erro:
    st.error(f"Não foi possível carregar a base de dados: {erro}")
    st.stop()

st.caption(f"Fonte dos dados: {fonte_dados}")

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
