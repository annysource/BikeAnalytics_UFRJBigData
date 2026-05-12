"""
app.py — Dashboard CitiBike NYC com Streamlit
Lê dados diretamente do HDFS e renderiza mapa + gráficos.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import json
from hdfs import InsecureClient
from datetime import datetime

# ─── Configuração da página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="CitiBike NYC — Big Data Dashboard",
    page_icon="🚴",
    layout="wide"
)

HDFS_URL  = "http://namenode:9870"
HDFS_STATUS = "/citibike/station_status"
HDFS_INFO   = "/citibike/station_info"
HDFS_PROC   = "/citibike/processed"

# ─── Conexão HDFS (cached para não reconectar a cada refresh) ─────────────────
@st.cache_resource
def get_hdfs_client():
    return InsecureClient(HDFS_URL, user="root")

client = get_hdfs_client()

# ─── Funções de leitura ───────────────────────────────────────────────────────
@st.cache_data(ttl=300)  # cache por 5 minutos — mesma frequência da coleta
def carregar_ultimo_snapshot():
    """
    Lê station_status + station_info do HDFS e faz merge.
    Retorna DataFrame com: station_id, name, lat, lon, free_bikes, empty_slots, ebikes
    """
    try:
        # 1. Carregar station_status (dados em tempo real)
        arquivos_status = sorted(client.list(HDFS_STATUS))
        if not arquivos_status:
            return pd.DataFrame()

        with client.read(f"{HDFS_STATUS}/{arquivos_status[-1]}") as f:
            status_data = json.load(f)
        df_status = pd.DataFrame(status_data)

        # 2. Carregar station_info (metadados: nome, lat, lon)
        arquivos_info = sorted(client.list(HDFS_INFO))
        if not arquivos_info:
            return pd.DataFrame()

        with client.read(f"{HDFS_INFO}/{arquivos_info[-1]}") as f:
            info_data = json.load(f)
        df_info = pd.DataFrame(info_data)

        # 3. Merge via station_id
        df = pd.merge(
            df_status,
            df_info[["station_id", "name", "lat", "lon", "capacity"]],
            on="station_id",
            how="inner"
        )

        # 4. Renomear colunas para compatibilidade com código existente
        df = df.rename(columns={
            "num_bikes_available": "free_bikes",
            "num_docks_available": "empty_slots",
            "num_ebikes_available": "ebikes"
        })

        # 5. Garantir tipos corretos
        df["free_bikes"]  = pd.to_numeric(df["free_bikes"],  errors="coerce").fillna(0).astype(int)
        df["empty_slots"] = pd.to_numeric(df["empty_slots"], errors="coerce").fillna(0).astype(int)
        df["ebikes"]      = pd.to_numeric(df["ebikes"],      errors="coerce").fillna(0).astype(int)

        return df
    except Exception as e:
        st.error(f"Erro ao ler HDFS: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def carregar_processado(subdir):
    """
    Lê arquivos JSON Lines gerados pelo Spark do HDFS.
    O Spark salva no formato JSON Lines (uma linha = um objeto JSON),
    não como um array. Por isso usamos json.loads() linha por linha.
    Também ignora o arquivo _SUCCESS que o Spark cria como marcador.
    """
    try:
        registros = []
        arquivos = client.list(f"{HDFS_PROC}/{subdir}")
        for arq in arquivos:
            # _SUCCESS é um arquivo vazio de controle do Spark — pular
            if arq.startswith("_") or arq.startswith("."):
                continue
            with client.read(f"{HDFS_PROC}/{subdir}/{arq}") as f:
                conteudo = f.read().decode("utf-8")
                for linha in conteudo.strip().split("\n"):
                    if linha.strip():
                        registros.append(json.loads(linha))
        return pd.DataFrame(registros)
    except Exception as e:
        st.warning(f"Erro ao ler {subdir}: {e}")
        return pd.DataFrame()

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.title("🚴 CitiBike NYC — Big Data Dashboard")
st.caption(f"Apache Spark + Hadoop HDFS | Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
st.divider()

# ─── CARREGAR DADOS ───────────────────────────────────────────────────────────
with st.spinner("Carregando dados do HDFS..."):
    df = carregar_ultimo_snapshot()
    df_top     = carregar_processado("top_stations")
    df_vazias  = carregar_processado("estacoes_vazias")

if df.empty:
    st.warning("⚠️ Nenhum snapshot de station_status disponível. Aguarde a próxima coleta (5 min) ou verifique o container citibike-ingest.")
    st.info("Mapa e KPIs indisponíveis temporariamente. Gráficos de análise Spark (se disponíveis) serão exibidos abaixo.")

# ─── KPIs ─────────────────────────────────────────────────────────────────────
total_bikes  = int(df["free_bikes"].sum())
total_vagas  = int(df["empty_slots"].sum())
total_ebikes = int(df["ebikes"].sum()) if "ebikes" in df.columns else 0

try:
    snapshots = len(client.list(HDFS_STATUS))
except:
    snapshots = 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🚲 Bikes Disponíveis", f"{total_bikes:,}".replace(",", "."))
col2.metric("⚡ E-Bikes",           f"{total_ebikes:,}".replace(",", "."))
col3.metric("🅿️ Vagas Livres",      f"{total_vagas:,}".replace(",", "."))
col4.metric("📍 Estações",          f"{len(df):,}".replace(",", "."))
col5.metric("📁 Snapshots HDFS",    snapshots)

st.divider()

# ─── MAPA ─────────────────────────────────────────────────────────────────────
st.subheader("🗺️ Mapa de Estações em Tempo Real")

# Classifica cada estação por disponibilidade para colorir o mapa
df_mapa = df[["lat", "lon", "name", "free_bikes", "empty_slots"]].dropna(subset=["lat", "lon"])

# Plotly scatter_mapbox — mapa interativo com zoom, hover e cores
fig_mapa = px.scatter_map(
    df_mapa,
    lat="lat",
    lon="lon",
    color="free_bikes",
    size=df_mapa["free_bikes"].clip(lower=1),
    hover_name="name",
    hover_data={"free_bikes": True, "empty_slots": True, "lat": False, "lon": False},
    color_continuous_scale=["#f25f5c", "#f5a623", "#34c97a"],
    range_color=[0, df_mapa["free_bikes"].quantile(0.95)],
    map_style="carto-darkmatter",
    zoom=11,
    center={"lat": 40.73, "lon": -73.99},
    height=500,
    labels={"free_bikes": "Bikes", "empty_slots": "Vagas"}
)
fig_mapa.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, coloraxis_colorbar_title="Bikes")
st.plotly_chart(fig_mapa,  width="stretch")

st.divider()

# ─── GRÁFICOS E TABELAS ───────────────────────────────────────────────────────
col_esq, col_dir = st.columns(2)

with col_esq:
    st.subheader("📊 Top 10 Estações com Mais Bikes")
    if not df_top.empty and "name" in df_top.columns:
        df_top_sorted = df_top.sort_values("media_bikes", ascending=True).tail(10)
        fig_bar = px.bar(
            df_top_sorted,
            x="media_bikes",
            y="name",
            orientation="h",
            color="media_bikes",
            color_continuous_scale=["#4f8ef7", "#34c97a"],
            labels={"media_bikes": "Média de Bikes", "name": "Estação"},
            height=400
        )
        fig_bar.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            yaxis_title="",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e4f0"
        )
        st.plotly_chart(fig_bar,   width="stretch")
    else:
        st.info("Rode o job PySpark para gerar os dados processados.")
        st.caption("Comando: spark-submit .../analyze_citibike.py")

with col_dir:
    st.subheader("🚨 Estações Críticas (Frequentemente Vazias)")
    if not df_vazias.empty and "name" in df_vazias.columns:
        df_show = df_vazias[["name", "pct_vazia", "total_snapshots"]].sort_values(
            "pct_vazia", ascending=False
        ).head(10)
        df_show.columns = ["Estação", "% Vazia", "Snapshots"]
        st.dataframe(
            df_show,
            use_container_width=True,
            hide_index=True,
            column_config={
                "% Vazia": st.column_config.ProgressColumn(
                    "% do Tempo Vazia",
                    min_value=0,
                    max_value=100,
                    format="%.1f%%"
                )
            }
        )
    else:
        st.info("Rode o job PySpark para gerar os dados processados.")

st.divider()

# ─── ANÁLISE EXPLORATÓRIA EXTRA ───────────────────────────────────────────────
st.subheader("📈 Distribuição de Bikes por Estação")
fig_hist = px.histogram(
    df_mapa,
    x="free_bikes",
    nbins=30,
    color_discrete_sequence=["#4f8ef7"],
    labels={"free_bikes": "Bikes Disponíveis", "count": "Nº de Estações"},
    height=300
)
fig_hist.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font_color="#e2e4f0",
    bargap=0.1
)
st.plotly_chart(fig_hist,  width="stretch")

# Botão para forçar atualização dos dados
if st.button("🔄 Atualizar Dados do HDFS"):
    st.cache_data.clear()
    st.rerun()