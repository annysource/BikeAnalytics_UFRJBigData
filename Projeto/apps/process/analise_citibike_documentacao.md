# Documentação da Etapa de Análise — CitiBike NYC

## Visão Geral

Esta documentação descreve as análises implementadas no script `apps/process/analyze_citibike.py`, sua origem de dados, lógica de processamento e como os resultados podem ser consumidos pela aplicação Web UI.

O script é executado via `spark-submit` dentro do container `spark-master` e grava todos os resultados no HDFS, na camada `/citibike/processed/`. A Web UI lê esses dados diretamente via WebHDFS sem depender de execução do Spark em tempo real.

---

## Fonte de Dados

| Item | Detalhe |
|------|---------|
| **Origem** | Arquivos CSV históricos de viagens CitiBike NYC |
| **Localização no HDFS** | `hdfs://namenode:9000/citibike/trips/*.csv` |
| **Cobertura** | Janeiro a Abril de 2026 (11 arquivos, ~1.8 GB) |
| **Total de registros** | ~3,8 milhões de viagens (estimado) |
| **Ingestão** | Realizada por `apps/ingest/fetch_citibike.py` |

### Colunas utilizadas

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `ride_id` | string | Identificador único da viagem |
| `rideable_type` | string | Tipo de bicicleta (classic, electric) |
| `started_at` | timestamp | Data/hora de início |
| `ended_at` | timestamp | Data/hora de fim |
| `start_station_name` | string | Nome da estação de origem |
| `end_station_name` | string | Nome da estação de destino |
| `start_lat` / `start_lng` | double | Coordenadas de origem |
| `end_lat` / `end_lng` | double | Coordenadas de destino |
| `member_casual` | string | Tipo de usuário (`member` ou `casual`) |

---

## Etapas de Pré-processamento

Antes das análises, os dados passam pelas seguintes transformações:

1. **Conversão de timestamps** — colunas `started_at` e `ended_at` convertidas para tipo `timestamp`
2. **Cálculo de duração** — `duration_min = (ended_at - started_at) / 60`, filtrado entre **1 e 120 minutos**
3. **Cálculo de distância** — fórmula de Haversine implementada com funções nativas Spark (sem UDF), filtrada entre **0,05 km e 50 km**
4. **Coluna `mes`** — extraída de `started_at` no formato `yyyy-MM`, usada para particionamento lógico de todas as análises
5. **Coluna `hora`** — hora do dia (0–23) extraída de `started_at`
6. **Filtro de nulos** — registros sem `start_station_name` ou `end_station_name` são descartados

### Fórmula de Haversine

A distância entre dois pontos geográficos é calculada pela fórmula de Haversine:

\[
d = 2R \cdot \arctan2\!\left(\sqrt{a},\, \sqrt{1-a}\right)
\]

onde \(a = \sin^2\!\left(\tfrac{\Delta\phi}{2}\right) + \cos\phi_1\cos\phi_2\sin^2\!\left(\tfrac{\Delta\lambda}{2}\right)\) e \(R = 6371\) km.

---

## Análises Geradas

### 1. Resumo Mensal (`resumo_mensal`)

Visão consolidada do sistema por mês, agregando os principais indicadores operacionais.

| Campo | Descrição |
|-------|-----------|
| `mes` | Mês de referência (yyyy-MM) |
| `total_viagens` | Total de viagens no mês |
| `duracao_media_min` | Duração média das viagens (minutos) |
| `duracao_mediana_min` | Mediana da duração (minutos) |
| `distancia_media_km` | Distância média percorrida (km) |
| `distancia_mediana_km` | Mediana da distância (km) |
| `pct_member` | Percentual de viagens de membros (%) |
| `pct_casual` | Percentual de viagens de usuários casuais (%) |
| `estacoes_partida_unicas` | Número de estações de origem distintas |
| `estacoes_chegada_unicas` | Número de estações de destino distintas |

**Uso na Web UI:** painel principal com KPIs, gráfico de linha de evolução mensal, comparação member vs. casual ao longo do tempo.

---

### 2. Duração por Tipo de Usuário (`duracao_por_tipo`)

Distribuição estatística da duração das viagens, segmentada por mês e tipo de usuário.

| Campo | Descrição |
|-------|-----------|
| `mes` | Mês de referência |
| `member_casual` | Tipo de usuário (`member` / `casual`) |
| `viagens` | Total de viagens no grupo |
| `duracao_media_min` | Média da duração |
| `q1_min` | 1º quartil (25%) |
| `mediana_min` | Mediana (50%) |
| `q3_min` | 3º quartil (75%) |
| `max_min` | Duração máxima registrada |

**Uso na Web UI:** boxplot ou violin plot de duração por tipo de usuário, filtrável por mês.

---

### 3. Distância por Tipo de Usuário (`distancia_por_tipo`)

Mesma estrutura da análise de duração, aplicada à distância percorrida em quilômetros.

| Campo | Descrição |
|-------|-----------|
| `mes` | Mês de referência |
| `member_casual` | Tipo de usuário |
| `viagens` | Total de viagens |
| `distancia_media_km` | Média da distância |
| `q1_km` | 1º quartil |
| `mediana_km` | Mediana |
| `q3_km` | 3º quartil |
| `max_km` | Distância máxima |

**Uso na Web UI:** boxplot de distância, comparação lado a lado com duração.

---

### 4. Top 20 Estações de Partida (`top_estacoes_partida`)

As 20 estações com maior volume de viagens iniciadas, por mês.

| Campo | Descrição |
|-------|-----------|
| `mes` | Mês de referência |
| `start_station_name` | Nome da estação |
| `start_lat` / `start_lng` | Coordenadas da estação |
| `viagens` | Total de viagens partindo da estação |
| `duracao_media_min` | Duração média das viagens originadas |
| `distancia_media_km` | Distância média das viagens originadas |

**Uso na Web UI:** ranking em barra horizontal, mapa com marcadores proporcionais ao volume, filtrável por mês.

---

### 5. Top 20 Estações de Chegada (`top_estacoes_chegada`)

As 20 estações com maior volume de viagens recebidas, por mês. Mesma estrutura da análise de partida, com campos `end_station_name`, `end_lat`, `end_lng`.

**Uso na Web UI:** mesmo padrão visual das estações de partida. Comparar os dois rankings permite identificar desequilíbrios de fluxo (estações que recebem mais do que enviam).

---

### 6. Distribuição por Hora do Dia (`pico_hora`)

Quantidade de viagens iniciadas por hora do dia, segmentada por mês e tipo de usuário. Permite identificar horários de pico de demanda.

| Campo | Descrição |
|-------|-----------|
| `mes` | Mês de referência |
| `hora` | Hora do dia (0–23) |
| `member_casual` | Tipo de usuário |
| `viagens` | Total de viagens iniciadas nessa hora |
| `duracao_media_min` | Duração média das viagens nessa hora |

**Uso na Web UI:** gráfico de área ou barras empilhadas por hora, com curvas separadas para member e casual. Evidencia padrões de commute (picos às 8h e 17–18h para membros) vs. lazer (distribuição mais uniforme nos casuais).

---

### 7. Top 1000 Rotas por Mês (`top_rotas`)

Os 1000 pares de estação origem→destino mais frequentes, por mês.

| Campo | Descrição |
|-------|-----------|
| `mes` | Mês de referência |
| `start_station_name` | Estação de origem |
| `start_lat` / `start_lng` | Coordenadas de origem |
| `end_station_name` | Estação de destino |
| `end_lat` / `end_lng` | Coordenadas de destino |
| `viagens` | Total de viagens no par |
| `duracao_media_min` | Duração média da rota |
| `distancia_media_km` | Distância média da rota |
| `pct_member` | % de viagens realizadas por membros |

**Uso na Web UI:** mapa de fluxo com linhas de rota (espessura proporcional ao volume), filtrável por mês. Marcadores nas estações de origem dimensionados pelo total de saídas.

---

## Localização dos Resultados no HDFS

Todos os resultados são gravados em formato JSON com cabeçalho, no caminho:

```
hdfs://namenode:9000/citibike/processed/
├── resumo_mensal/
├── duracao_por_tipo/
├── distancia_por_tipo/
├── top_estacoes_partida/
├── top_estacoes_chegada/
├── pico_hora/
└── top_rotas/
```

Cada diretório contém um único arquivo `part-00000-*.json` (gerado com `coalesce(1)`) mais um arquivo `_SUCCESS` que indica conclusão bem-sucedida.

---

## Como Consumir os Resultados na Web UI

A Web UI (Streamlit, container `citibike-web`) acessa os dados via **WebHDFS REST API**, exposta pelo Namenode na porta `9870`.

### Leitura via Python (WebHDFS)

```python
from hdfs import InsecureClient
import json

client = InsecureClient("http://namenode:9870", user="root")

def ler_resultado(nome: str) -> list[dict]:
    """Lê um resultado processado do HDFS e retorna lista de dicionários."""
    arquivos = client.list(f"/citibike/processed/{nome}")
    part_file = next(f for f in arquivos if f.startswith("part-"))
    
    with client.read(f"/citibike/processed/{nome}/{part_file}") as f:
        linhas = f.read().decode("utf-8").strip().splitlines()
    
    return [json.loads(linha) for linha in linhas]

# Exemplos de uso
resumo   = ler_resultado("resumo_mensal")
pico     = ler_resultado("pico_hora")
rotas    = ler_resultado("top_rotas")
```

### Filtro por mês no Streamlit

Como todos os datasets possuem a coluna `mes`, o filtro é trivial:

```python
import pandas as pd

df_resumo = pd.DataFrame(ler_resultado("resumo_mensal"))
meses_disponiveis = sorted(df_resumo["mes"].unique())

mes_selecionado = st.selectbox("Selecione o mês", meses_disponiveis)
df_filtrado = df_resumo[df_resumo["mes"] == mes_selecionado]
```

### Dependências necessárias na Web UI

Já configuradas no `docker-compose.yml`:

```
streamlit, hdfs, requests, plotly, pandas
```

---

## Como Executar a Análise

### Execução manual

```bash
docker exec spark-master /opt/spark/bin/spark-submit \
  --master local[*] \
  /opt/spark-apps/process/analyze_citibike.py
```

### Tempo estimado de execução

| Etapa | Tempo estimado |
|-------|----------------|
| Leitura dos CSVs + cache | 3–5 min |
| Resumo mensal | 2–3 min |
| Duração / Distância por tipo | 2–3 min |
| Top estações (partida + chegada) | 3–5 min |
| Pico por hora | 1–2 min |
| Top 1000 rotas | 3–5 min |
| **Total** | **~15–25 min** |

> O tempo varia conforme memória disponível no container `spark-master` (configurado com `mem_limit: 512m`). Em caso de lentidão extrema ou OOM, considere aumentar para `1g` no `docker-compose.yml`.

---

## Nota sobre Dados da API em Tempo Real

O projeto também coleta dados de disponibilidade de estações em tempo real via API CitiBike (`apps/ingest/fetch_citibike.py`), gravados em `hdfs://namenode:9000/citibike/raw/`. Esses dados foram avaliados como complementares e **não integram as análises históricas** descritas neste documento — seu propósito é demonstrar a capacidade de ingestão de dados em streaming para fins acadêmicos.

