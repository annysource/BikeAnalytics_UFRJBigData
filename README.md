# 🚴 BikeAnalytics — CitiBike NYC Big Data Pipeline

Projeto de Big Data desenvolvido no MBA de Engenharia de Software da UFRJ.
Pipeline completo de ingestão, armazenamento distribuído, processamento e visualização
dos dados do sistema de bicicletas compartilhadas CitiBike de Nova York.

---

## 🏗️ Arquitetura

┌─────────────────────────────────────────────────────────────────────┐
│                        FONTES EXTERNAS                              │
├──────────────────────────┬──────────────────────────────────────────┤
│   GBFS Real-Time         │   Trip History — S3 AWS                  │
│   gbfs.citibikenyc.com   │   s3.amazonaws.com/tripdata/             │
│                          │                                          │
│   • station_status       │   • 202601-citibike-tripdata.zip (337MB) │
│   • station_information  │   • 202602-citibike-tripdata.zip (226MB) │
│                          │   • 202603, 202604...                    │
└────────────┬─────────────┴───────────────────┬──────────────────────┘
             │ a cada 5 min                    │ incremental (mensal)
             │ JSON                            │ stream → ZIP → CSV
             └──────────────┬──────────────────┘
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│          citibike-ingest  (python:3.11-slim  |  mem: 768m)        │
│                                                                   │
│  fetch_citibike.py  →  loop a cada 300s                           │
│    ├── GET station_status  → JSON → HDFS                          │
│    ├── GET station_info    → JSON → HDFS                          │
│    └── sync_trips()  ──────────────────────────────────────────── │
│                                                                   │
│  fetch_trips.py  →  download streaming sem estourar RAM           │
│    ├── verifica meses já existentes no HDFS                       │
│    ├── baixa ZIP em chunks de 512KB para disco temp               │
│    ├── extrai CSV do ZIP em chunks → HDFS                         │
│    └── remove arquivo temp                                        │
└──────────────────────────────┬────────────────────────────────────┘
                               │ hdfs://namenode:9000
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                    HADOOP HDFS  (hadoop 3.2.1)                   │
│              namenode :9870  ←→  datanode                        │
│                                                                  │
│   /citibike/                                                     │
│   ├── station_status/   ← status_{timestamp}.json  (a cada 5min) │
│   ├── station_info/     ← info_{timestamp}.json    (a cada 5min) │
│   ├── trips/            ← 202601-citibike-tripdata_1.csv (185MB) │
│   │                        202601-citibike-tripdata_2.csv (151MB)│
│   │                        202602-citibike-tripdata_1.csv ...    │
│   └── processed/        ← outputs do Spark                       │
│       ├── top_stations/                                          │
│       └── estacoes_vazias/                                       │
└──────────────┬───────────────────────────────┬───────────────────┘
               │                               │
               ▼                               ▼
┌──────────────────────────┐   ┌───────────────────────────────────┐
│   Apache Spark  (3.5.1)  │   │  Jupyter  (base-notebook + 3.5.1) │
│                          │   │                                   │
│   spark-master   :8080   │   │  :8888  token: citibike           │
│   spark-worker-1 :8081   │   │                                   │
│   spark-worker-2 :8082   │   │  • PySpark local[2]               │
│                          │   │  • Pandas API on Spark            │
│   analyze_citibike.py    │   │  • Plotly interativo (iframe)     │
│   spark-submit →         │   │  • Haversine (distância rotas)    │
│   /citibike/processed/   │   │  • Mapa de rotas Scattermap       │
└──────────────────────────┘   └───────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────────┐
│         citibike-web  (python:3.11-slim  |  mem: 256m)           │
│         Streamlit Dashboard  —  localhost:5000                   │
│                                                                  │
│  • Mapa interativo das estações (Plotly Scattermap)              │
│  • KPIs: bikes disponíveis, e-bikes, vagas, snapshots            │
│  • Top 10 estações mais movimentadas  (← Spark processed)        │
│  • Estações críticas / frequentemente vazias                     │
│  • Histograma de distribuição de bikes                           │
│  • Cache TTL 300s (alinhado à frequência de coleta)              │
└──────────────────────────────────────────────────────────────────┘

---

## 🐳 Serviços Docker

| Serviço | Imagem | Porta | Função |
|---|---|---|---|
| `namenode` | hadoop 3.2.1 | 9870 | HDFS NameNode |
| `datanode` | hadoop 3.2.1 | — | HDFS DataNode |
| `spark-master` | apache/spark:3.5.1 | 8080 / 7077 | Spark Master |
| `spark-worker-1` | apache/spark:3.5.1 | 8081 | Spark Worker |
| `spark-worker-2` | apache/spark:3.5.1 | 8082 | Spark Worker |
| `citibike-ingest` | python:3.11-slim | — | Pipeline de ingestão |
| `citibike-web` | python:3.11-slim | 5000 | Dashboard Streamlit |
| `citibike-jupyter` | jupyter/base-notebook | 8888 | Notebooks de análise |

---

## ⚙️ Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado
- Git
- ~4GB de RAM disponível
- ~10GB de espaço em disco

---

## 🚀 Como rodar

### 1. Clonar o repositório
```bash
git clone https://github.com/annysource/BikeAnalytics_UFRJBigData.git
cd BikeAnalytics_UFRJBigData/Projeto
```

### 2. Subir a infraestrutura
```bash
docker compose up -d
```
> Na primeira vez demora ~5 minutos para baixar as imagens.

### 3. Verificar se tudo subiu
```bash
docker compose ps
```

### 4. Acompanhar a ingestão
```bash
docker compose logs -f ingest
```

### 5. Acessar os serviços

| Serviço | URL | Credencial |
|---|---|---|
| Dashboard | http://localhost:5000 | — |
| Jupyter Notebook | http://localhost:8888 | token: `citibike` |
| HDFS WebUI | http://localhost:9870 | — |
| Spark WebUI | http://localhost:8080 | — |

---

## 📁 Estrutura do Projeto
Projeto/
├── apps/
│ ├── ingest/
│ │ ├── fetch_citibike.py # coleta GBFS em tempo real (5min)
│ │ └── fetch_trips.py # ingestão incremental dos CSVs históricos
│ ├── process/
│ │ ├── analyze_citibike.py # job PySpark
│ │ └── explore_data_citibike.ipynb # análise exploratória
│ └── web/
│ └── app.py # dashboard Streamlit
├── docker-compose.yml
├── hadoop.env
└── ordem_de_eventos.txt