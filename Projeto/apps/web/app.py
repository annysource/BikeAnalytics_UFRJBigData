"""
app.py — Dashboard CitiBike NYC com Streamlit
Lê dados históricos processados pelo Spark do HDFS.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
HDFS_PROC = "/citibike/processed"

# ─── Conexão HDFS (cached para não reconectar a cada refresh) ─────────────────
@st.cache_resource
def get_hdfs_client():
    return InsecureClient(HDFS_URL, user="root")

client = get_hdfs_client()

# ─── Função de leitura de datasets processados ────────────────────────────────
@st.cache_data(ttl=300)
def ler_resultado(nome: str) -> pd.DataFrame:
    """
    Lê dataset processado do HDFS gerado pelo Spark.
    O Spark salva em formato JSON Lines (uma linha = um objeto JSON).
    """
    try:
        arquivos = client.list(f"{HDFS_PROC}/{nome}")

        # Buscar arquivo part-* (ignora _SUCCESS e outros metadados)
        part_files = [f for f in arquivos if f.startswith("part-")]
        if not part_files:
            return pd.DataFrame()

        registros = []
        for part_file in part_files:
            with client.read(f"{HDFS_PROC}/{nome}/{part_file}") as f:
                conteudo = f.read().decode("utf-8")
                for linha in conteudo.strip().split("\n"):
                    if linha.strip():
                        registros.append(json.loads(linha))

        return pd.DataFrame(registros)
    except Exception:
        return pd.DataFrame()

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.title("🚴 CitiBike NYC — Análise Histórica Big Data")
st.caption(f"Apache Spark + Hadoop HDFS | Período: Jan–Abr 2026 | Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
st.divider()

# ─── CARREGAR DATASETS ────────────────────────────────────────────────────────
with st.spinner("Carregando dados processados do HDFS..."):
    df_resumo = ler_resultado("resumo_mensal")
    df_top_partida = ler_resultado("top_estacoes_partida")
    df_top_chegada = ler_resultado("top_estacoes_chegada")
    df_pico_hora = ler_resultado("pico_hora")
    df_rotas = ler_resultado("top_rotas")
    df_duracao = ler_resultado("duracao_por_tipo")
    df_distancia = ler_resultado("distancia_por_tipo")

# ─── VERIFICAÇÃO DE DADOS DISPONÍVEIS ─────────────────────────────────────────
datasets_vazios = [
    df_resumo.empty, df_top_partida.empty, df_top_chegada.empty,
    df_pico_hora.empty, df_rotas.empty, df_duracao.empty, df_distancia.empty
]

if all(datasets_vazios):
    st.error("❌ Nenhum dataset processado encontrado em `/citibike/processed/`")
    st.info("""
    **Para gerar os dados, execute os seguintes comandos:**

    ```bash
    # 1. Ingerir dados históricos de viagens (Jan-Abr 2026)
    docker compose exec ingest python3 fetch_trips.py

    # 2. Processar com Spark (~15-25 min)
    docker compose exec spark-master spark-submit \\
      --master local[*] \\
      /opt/spark-apps/process/analyze_citibike.py
    ```

    Após a execução, atualize esta página.
    """)
    st.stop()

# ─── SELETOR DE MÊS (SE DISPONÍVEL) ───────────────────────────────────────────
meses_disponiveis = []
if not df_resumo.empty and "mes" in df_resumo.columns:
    meses_disponiveis = sorted(df_resumo["mes"].unique())

if meses_disponiveis:
    mes_selecionado = st.selectbox(
        "📅 Selecione o mês para visualização detalhada",
        meses_disponiveis,
        index=len(meses_disponiveis) - 1  # Último mês por padrão
    )
else:
    mes_selecionado = None
    st.warning("⚠️ Dataset `resumo_mensal` não encontrado. Algumas visualizações podem estar indisponíveis.")

st.divider()

# ─── KPIs DO MÊS SELECIONADO ──────────────────────────────────────────────────
if not df_resumo.empty and mes_selecionado:
    st.subheader(f"📊 Indicadores — {mes_selecionado}")

    dados_mes = df_resumo[df_resumo["mes"] == mes_selecionado].iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "🚴 Total de Viagens",
        f"{int(dados_mes['total_viagens']):,}".replace(",", ".")
    )
    col2.metric(
        "⏱️ Duração Média",
        f"{dados_mes['duracao_media_min']:.1f} min",
        delta=f"Mediana: {dados_mes['duracao_mediana_min']:.1f} min"
    )
    col3.metric(
        "📏 Distância Média",
        f"{dados_mes['distancia_media_km']:.2f} km",
        delta=f"Mediana: {dados_mes['distancia_mediana_km']:.2f} km"
    )
    col4.metric(
        "👥 % Membros",
        f"{dados_mes['pct_member']:.1f}%",
        delta=f"Casuais: {dados_mes['pct_casual']:.1f}%"
    )

    col5, col6 = st.columns(2)
    col5.metric(
        "📍 Estações de Partida Únicas",
        f"{int(dados_mes['estacoes_partida_unicas']):,}".replace(",", ".")
    )
    col6.metric(
        "🎯 Estações de Chegada Únicas",
        f"{int(dados_mes['estacoes_chegada_unicas']):,}".replace(",", ".")
    )

    st.divider()

# ─── EVOLUÇÃO MENSAL ──────────────────────────────────────────────────────────
if not df_resumo.empty:
    st.subheader("📈 Evolução Mensal do Sistema")

    col_esq, col_dir = st.columns(2)

    with col_esq:
        # Gráfico de viagens mensais
        fig_viagens = px.line(
            df_resumo,
            x="mes",
            y="total_viagens",
            markers=True,
            title="Total de Viagens por Mês",
            labels={"mes": "Mês", "total_viagens": "Viagens"}
        )
        fig_viagens.update_traces(line_color="#4f8ef7", line_width=3)
        fig_viagens.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e4f0",
            hovermode="x unified"
        )
        st.plotly_chart(fig_viagens, use_container_width=True)

    with col_dir:
        # Gráfico de % member vs casual
        fig_composicao = go.Figure()
        fig_composicao.add_trace(go.Scatter(
            x=df_resumo["mes"],
            y=df_resumo["pct_member"],
            mode="lines+markers",
            name="Membros",
            line=dict(color="#34c97a", width=3)
        ))
        fig_composicao.add_trace(go.Scatter(
            x=df_resumo["mes"],
            y=df_resumo["pct_casual"],
            mode="lines+markers",
            name="Casuais",
            line=dict(color="#f5a623", width=3)
        ))
        fig_composicao.update_layout(
            title="Composição: Membros vs Casuais (%)",
            xaxis_title="Mês",
            yaxis_title="Percentual (%)",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e4f0",
            hovermode="x unified",
            legend=dict(x=0.7, y=1.0)
        )
        st.plotly_chart(fig_composicao, use_container_width=True)

    st.divider()

# ─── MAPA DE ESTAÇÕES MAIS MOVIMENTADAS ──────────────────────────────────────
if not df_top_partida.empty and mes_selecionado:
    st.subheader(f"🗺️ Top 20 Estações de Partida — {mes_selecionado}")

    df_mapa = df_top_partida[df_top_partida["mes"] == mes_selecionado].copy()

    if not df_mapa.empty:
        fig_mapa = px.scatter_map(
            df_mapa,
            lat="start_lat",
            lon="start_lng",
            size="viagens",
            color="viagens",
            hover_name="start_station_name",
            hover_data={
                "viagens": True,
                "duracao_media_min": ":.1f",
                "distancia_media_km": ":.2f",
                "start_lat": False,
                "start_lng": False
            },
            color_continuous_scale=["#f5a623", "#f25f5c", "#c70039"],
            map_style="carto-darkmatter",
            zoom=11,
            center={"lat": 40.73, "lon": -73.99},
            height=500,
            labels={
                "viagens": "Viagens",
                "duracao_media_min": "Duração Média (min)",
                "distancia_media_km": "Distância Média (km)"
            }
        )
        fig_mapa.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_mapa, use_container_width=True)
    else:
        st.info(f"Nenhum dado de estações de partida para {mes_selecionado}")

    st.divider()

# ─── RANKING DE ESTAÇÕES ──────────────────────────────────────────────────────
if not df_top_partida.empty and mes_selecionado:
    st.subheader(f"🏆 Top 10 Estações — {mes_selecionado}")

    col_partida, col_chegada = st.columns(2)

    with col_partida:
        st.markdown("**🚀 Mais Viagens Iniciadas**")
        df_partida_top10 = df_top_partida[df_top_partida["mes"] == mes_selecionado].nlargest(10, "viagens")

        fig_partida = px.bar(
            df_partida_top10.sort_values("viagens"),
            x="viagens",
            y="start_station_name",
            orientation="h",
            color="viagens",
            color_continuous_scale=["#4f8ef7", "#34c97a"],
            labels={"viagens": "Viagens", "start_station_name": ""}
        )
        fig_partida.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e4f0",
            height=400
        )
        st.plotly_chart(fig_partida, use_container_width=True)

    with col_chegada:
        if not df_top_chegada.empty:
            st.markdown("**🎯 Mais Viagens Finalizadas**")
            df_chegada_top10 = df_top_chegada[df_top_chegada["mes"] == mes_selecionado].nlargest(10, "viagens")

            fig_chegada = px.bar(
                df_chegada_top10.sort_values("viagens"),
                x="viagens",
                y="end_station_name",
                orientation="h",
                color="viagens",
                color_continuous_scale=["#f5a623", "#f25f5c"],
                labels={"viagens": "Viagens", "end_station_name": ""}
            )
            fig_chegada.update_layout(
                showlegend=False,
                coloraxis_showscale=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#e2e4f0",
                height=400
            )
            st.plotly_chart(fig_chegada, use_container_width=True)

    st.divider()

# ─── DISTRIBUIÇÃO POR HORA DO DIA ─────────────────────────────────────────────
if not df_pico_hora.empty and mes_selecionado:
    st.subheader(f"🕐 Distribuição de Viagens por Hora — {mes_selecionado}")

    df_hora_filtrado = df_pico_hora[df_pico_hora["mes"] == mes_selecionado]

    if not df_hora_filtrado.empty:
        # Pivot para ter member e casual como colunas separadas
        df_pivot = df_hora_filtrado.pivot_table(
            index="hora",
            columns="member_casual",
            values="viagens",
            fill_value=0
        ).reset_index()

        fig_hora = go.Figure()

        if "member" in df_pivot.columns:
            fig_hora.add_trace(go.Scatter(
                x=df_pivot["hora"],
                y=df_pivot["member"],
                mode="lines+markers",
                name="Membros",
                line=dict(color="#34c97a", width=3),
                fill="tozeroy",
                fillcolor="rgba(52, 201, 122, 0.2)"
            ))

        if "casual" in df_pivot.columns:
            fig_hora.add_trace(go.Scatter(
                x=df_pivot["hora"],
                y=df_pivot["casual"],
                mode="lines+markers",
                name="Casuais",
                line=dict(color="#f5a623", width=3),
                fill="tozeroy",
                fillcolor="rgba(245, 166, 35, 0.2)"
            ))

        fig_hora.update_layout(
            xaxis_title="Hora do Dia",
            yaxis_title="Número de Viagens",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e4f0",
            hovermode="x unified",
            legend=dict(x=0.02, y=0.98),
            height=400
        )

        st.plotly_chart(fig_hora, use_container_width=True)

        st.caption("💡 **Insight:** Membros apresentam picos às 8h e 17h (commuting). Casuais têm distribuição mais uniforme (lazer).")

    st.divider()

# ─── DURAÇÃO E DISTÂNCIA POR TIPO DE USUÁRIO ──────────────────────────────────
if not df_duracao.empty and mes_selecionado:
    st.subheader(f"📊 Duração e Distância por Tipo de Usuário — {mes_selecionado}")

    col_dur, col_dist = st.columns(2)

    with col_dur:
        df_dur_filtrado = df_duracao[df_duracao["mes"] == mes_selecionado]

        if not df_dur_filtrado.empty:
            fig_dur = px.bar(
                df_dur_filtrado,
                x="member_casual",
                y="duracao_media_min",
                color="member_casual",
                color_discrete_map={"member": "#34c97a", "casual": "#f5a623"},
                labels={
                    "member_casual": "Tipo de Usuário",
                    "duracao_media_min": "Duração Média (min)"
                },
                title="Duração Média das Viagens",
                text="duracao_media_min"
            )
            fig_dur.update_traces(texttemplate='%{text:.1f} min', textposition='outside')
            fig_dur.update_layout(
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#e2e4f0",
                height=350
            )
            st.plotly_chart(fig_dur, use_container_width=True)

    with col_dist:
        if not df_distancia.empty:
            df_dist_filtrado = df_distancia[df_distancia["mes"] == mes_selecionado]

            if not df_dist_filtrado.empty:
                fig_dist = px.bar(
                    df_dist_filtrado,
                    x="member_casual",
                    y="distancia_media_km",
                    color="member_casual",
                    color_discrete_map={"member": "#34c97a", "casual": "#f5a623"},
                    labels={
                        "member_casual": "Tipo de Usuário",
                        "distancia_media_km": "Distância Média (km)"
                    },
                    title="Distância Média Percorrida",
                    text="distancia_media_km"
                )
                fig_dist.update_traces(texttemplate='%{text:.2f} km', textposition='outside')
                fig_dist.update_layout(
                    showlegend=False,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#e2e4f0",
                    height=350
                )
                st.plotly_chart(fig_dist, use_container_width=True)

    st.divider()

# ─── TOP ROTAS ────────────────────────────────────────────────────────────────
if not df_rotas.empty and mes_selecionado:
    st.subheader(f"🛣️ Top 10 Rotas Mais Populares — {mes_selecionado}")

    df_rotas_filtrado = df_rotas[df_rotas["mes"] == mes_selecionado].nlargest(10, "viagens")

    if not df_rotas_filtrado.empty:
        # Criar coluna com rota formatada
        df_rotas_filtrado["rota"] = (
            df_rotas_filtrado["start_station_name"] + " → " + df_rotas_filtrado["end_station_name"]
        )

        fig_rotas = px.bar(
            df_rotas_filtrado.sort_values("viagens"),
            x="viagens",
            y="rota",
            orientation="h",
            color="pct_member",
            color_continuous_scale=["#f5a623", "#34c97a"],
            labels={
                "viagens": "Número de Viagens",
                "rota": "",
                "pct_member": "% Membros"
            },
            hover_data={
                "viagens": True,
                "duracao_media_min": ":.1f",
                "distancia_media_km": ":.2f",
                "pct_member": ":.1f"
            }
        )
        fig_rotas.update_layout(
            coloraxis_colorbar_title="% Membros",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e4f0",
            height=450
        )
        st.plotly_chart(fig_rotas, use_container_width=True)

        st.caption("💡 **Insight:** Rotas com alta % de membros (verde) são típicas de commuting. Rotas com mais casuais (laranja) são mais recreativas.")

    st.divider()

# ─── FOOTER COM INSTRUÇÕES ────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
### 📌 Sobre os Dados

- **Período analisado:** Janeiro a Abril de 2026
- **Fonte:** Trip history CitiBike NYC (S3 AWS)
- **Processamento:** Apache Spark 3.5.1 + PySpark DataFrame API
- **Armazenamento:** Hadoop HDFS 3.2.1
- **Total de viagens:** ~3,8 milhões (estimado)

### 🔄 Atualizar Análises

Para atualizar os dados com novos meses:

```bash
# 1. Baixar novos CSVs
docker compose exec ingest python3 fetch_trips.py

# 2. Reprocessar com Spark
docker compose exec spark-master spark-submit \\
  --master local[*] \\
  /opt/spark-apps/process/analyze_citibike.py
```
""")

# Botão para forçar atualização do cache
if st.button("🔄 Limpar Cache e Recarregar"):
    st.cache_data.clear()
    st.rerun()
