# Turismo no Brasil - Projeto G2

Projeto de análise e visualização de dados sobre turismo no Brasil entre 2015 e 2024.

O trabalho utiliza Python, Pandas, Plotly e Streamlit para investigar fluxo turístico, sazonalidade, comparação regional, ocupação hoteleira e impacto econômico.

## Objetivos

- Identificar cidades mais visitadas.
- Analisar sazonalidade turística.
- Comparar regiões e estados.
- Investigar faturamento turístico e gasto médio.
- Avaliar ocupação hoteleira.
- Construir um dashboard interativo.

## Estrutura

```text
projeto-turismo-brasil/
├── app.py
├── requirements.txt
├── README.md
├── index.html
├── dados/
│   └── simulacao_turismo_brasil.csv
├── notebooks/
│   └── analise_turismo.ipynb
├── database/
└── imagens/
```

## Dataset

A base `simulacao_turismo_brasil.csv` contém dados simulados de turismo no Brasil, com registros por ano, mês, região, estado e cidade.

Principais colunas:

- `ano`, `mes`, `data`
- `regiao`, `uf`, `cidade`
- `turistas`, `turistas_estrangeiros`
- `ocupacao_hoteleira`
- `gasto_medio`, `faturamento_turismo`
- `eventos_realizados`
- `temperatura_media`
- `nivel_temporada`

## Funcionalidades do Dashboard

- KPIs principais:
  - Total de turistas
  - Cidade mais visitada
  - Receita total do turismo
  - Ocupação hoteleira média
  - Gasto médio por turista
  - Região mais movimentada
- Filtros por ano, mês, região, estado, cidade e nível de temporada.
- Gráfico temporal de turistas e faturamento.
- Comparação por região.
- Ranking de destinos turísticos.
- Heatmap mensal de sazonalidade.
- Dispersão entre turistas e faturamento.
- Análise de clima, eventos e turismo.
- Tabela dinâmica para exploração detalhada.
- Interpretação textual e conclusão executiva.

## Como Executar Localmente

1. Clone ou baixe este repositório.
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Execute o dashboard:

```bash
streamlit run app.py
```

4. Acesse o endereço exibido no terminal, geralmente:

```text
http://localhost:8501
```

## Publicação

Entregas neste repositorio:

- GitHub: https://github.com/marianamachaddo/projeto-turismo-brasil
- GitHub Pages: https://marianamachaddo.github.io/projeto-turismo-brasil/
- Streamlit Cloud: https://projeto-turismo-brasil-qfkh4jgyfqitehy8nkcpez.streamlit.app/

## Conclusão

O projeto mostra como a análise de dados pode apoiar a compreensão de padrões turísticos, diferenças regionais, períodos de alta temporada e impactos econômicos. O dashboard permite transformar a base simulada em informações úteis para planejamento, gestão pública, infraestrutura e serviços.
