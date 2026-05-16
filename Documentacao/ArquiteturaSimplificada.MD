```
┌─────────────────────────────────────────────────────────────┐
│              FONTES DE DADOS EXTERNAS                       │
├─────────────────┬───────────────────────────────────────────┤
│ GBFS Real-Time  │  Trip History (AWS S3)                   │
│ (a cada 5min)   │  Histórico mensal de viagens             │
└────────┬────────┴───────────────────────┬───────────────────┘
         │                                │
         ▼                                ▼
┌─────────────────────────────────────────────────────────────┐
│          INGESTÃO (Python 3.11)                             │
│                                                             │
│  fetch_citibike.py  →  Coleta GBFS a cada 5 minutos      │
│  fetch_trips.py     →  Baixa CSVs históricos do S3        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼ hdfs://
┌─────────────────────────────────────────────────────────────┐
│           ARMAZENAMENTO DISTRIBUÍDO (HDFS)                  │
│                                                             │
│  /citibike/station_status/  (snapshots ~5 em 5 min)       │
│  /citibike/station_info/    (snapshots ~5 em 5 min)       │
│  /citibike/trips/           (CSVs históricos)              │
│  /citibike/processed/       (resultados do Spark)          │
└──────────────────────┬───────────────────────┬──────────────┘
                       │                       │
          ┌────────────┘                       └─────────────┐
          │                                                  │
          ▼                                                  ▼
┌────────────────────────┐            ┌───────────────────────┐
│  Apache Spark 3.5.1    │            │  Dashboard Streamlit  │
│                        │            │                       │
│ analyze_citibike.py    │            │  • Mapa interativo    │
│                        │            │  • KPIs (bikes, vagas)│
│ • Lê trips do HDFS     │            │  • Estações críticas  │
│ • Calcula estatísticas │            │  • Top 10 movimentadas│
│ • Identifica padrões   │            │  • localhost:5000     │
│ • Salva resultados     │            │                       │
└────────────────────────┘            └───────────────────────┘
```
