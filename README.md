# Turismo no Brasil - Projeto G2

Projeto desenvolvido por Mariana Machado Macedo. 
Disciplina: Linguagem de Programação. 
Professor: Alexandre Neves Louzada. 

Projeto de analise e visualizacao de dados sobre turismo no Brasil entre 2015 e 2024.

O trabalho utiliza Python, Pandas, Plotly e Streamlit para investigar fluxo turistico, sazonalidade, comparacao regional, ocupacao hoteleira e impacto economico.

## Links do Projeto

- GitHub: https://github.com/marianamachaddo/projeto-turismo-brasil
- GitHub Pages: https://marianamachaddo.github.io/projeto-turismo-brasil/
- Streamlit Cloud: https://projeto-turismo-brasil-h9l2mopjby4iqy5izsjvak.streamlit.app/

## Objetivos

- Identificar cidades mais visitadas.
- Analisar sazonalidade turistica.
- Comparar regioes e estados.
- Investigar faturamento turistico e gasto medio.
- Avaliar ocupacao hoteleira.
- Construir um dashboard interativo.

## Estrutura

```text
projeto-turismo-brasil/
|-- app.py
|-- requirements.txt
|-- README.md
|-- index.html
|-- dados/
|   |-- simulacao_turismo_brasil.csv
|-- notebooks/
|   |-- analise_turismo.ipynb
|-- database/
|   |-- turismo.db
|-- imagens/
```

## Dataset

A base `simulacao_turismo_brasil.csv` contem dados simulados de turismo no Brasil, com registros por ano, mes, regiao, estado e cidade.

Principais colunas:

- `ano`, `mes`, `data`
- `regiao`, `uf`, `cidade`
- `turistas`, `turistas_estrangeiros`
- `ocupacao_hoteleira`
- `gasto_medio`, `faturamento_turismo`
- `eventos_realizados`
- `temperatura_media`
- `nivel_temporada`

Tambem foi gerado o arquivo `database/turismo.db`, com a tabela `turismo_brasil`, para incluir persistencia em SQLite como recurso avancado.

## Funcionalidades do Dashboard

- KPIs principais:
  - Total de turistas
  - Cidade mais visitada
  - Receita total do turismo
  - Ocupacao hoteleira media
  - Gasto medio por turista
  - Regiao mais movimentada
- Filtros por ano, mes, regiao, estado, cidade e nivel de temporada.
- Grafico temporal de turistas e faturamento.
- Comparacao por regiao.
- Ranking de destinos turisticos.
- Heatmap mensal de sazonalidade.
- Dispersao entre turistas e faturamento.
- Analise de clima, eventos e turismo.
- Tabela dinamica para exploracao detalhada.
- Interpretacao textual e conclusao executiva.

## Como Executar Localmente

1. Clone ou baixe este repositorio.
2. Instale as dependencias:

```bash
pip install -r requirements.txt
```

3. Execute o dashboard:

```bash
streamlit run app.py
```

4. Acesse o endereco exibido no terminal, geralmente:

```text
http://localhost:8501
```

## Publicacao

Este projeto foi organizado para publicacao em:

- GitHub, para codigo-fonte e base de dados.
- GitHub Pages, usando o arquivo `index.html`.
- Streamlit Cloud, usando o arquivo principal `app.py`.

## Conclusao

O projeto mostra como a analise de dados pode apoiar a compreensao de padroes turisticos, diferencas regionais, periodos de alta temporada e impactos economicos. O dashboard permite transformar a base simulada em informacoes uteis para planejamento, gestao publica, infraestrutura e servicos.
