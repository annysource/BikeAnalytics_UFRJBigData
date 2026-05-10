"""
analyze_citibike.py
Lê todos os CSVs de viagens do HDFS e gera análises mensais
sobre o sistema CitiBike NYC usando PySpark DataFrame API.

Resultados salvos em: hdfs://namenode:9000/citibike/processed/
"""
import sys
sys.stdout.reconfigure(line_buffering=True)

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import (
    col, radians, sin, cos, sqrt, atan2,
    round as spark_round, hour, date_format,
    avg, count, when, max as spark_max
)
from pyspark.sql.window import Window

# ─── SparkSession ─────────────────────────────────────────────────────────────
spark = SparkSession.builder \
    .appName("CitiBike Analysis") \
    .master("local[*]") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .config("spark.hadoop.dfs.client.use.datanode.hostname", "true") \
    .config("spark.sql.shuffle.partitions", "8") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print("\n" + "="*60)
print("  ANÁLISE CitiBike NYC — Apache Spark + HDFS")
print("="*60 + "\n")

# ─── 1. Leitura de todos os CSVs de viagens ───────────────────────────────────
print("📂 Lendo todos os CSVs de viagens do HDFS...")

df_raw = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv("hdfs://namenode:9000/citibike/trips/*.csv")

total = df_raw.count()
print(f"✅ {total:,} registros carregados de todos os meses\n")

# ─── 2. Limpeza e enriquecimento ──────────────────────────────────────────────
print("🔧 Preparando dados...")

df = df_raw \
    .withColumn("started_at",  F.to_timestamp("started_at")) \
    .withColumn("ended_at",    F.to_timestamp("ended_at")) \
    .withColumn("duration_min",
        spark_round(
            (col("ended_at").cast("long") - col("started_at").cast("long")) / 60, 2
        )
    ) \
    .filter(col("duration_min").between(1, 120)) \
    .withColumn("mes", date_format("started_at", "yyyy-MM")) \
    .withColumn("hora", hour("started_at"))

# Haversine nativo Spark (sem UDF)
R = 6371
df = df \
    .withColumn("lat1", radians(col("start_lat"))) \
    .withColumn("lat2", radians(col("end_lat"))) \
    .withColumn("dlat", radians(col("end_lat")   - col("start_lat"))) \
    .withColumn("dlon", radians(col("end_lng")   - col("start_lng"))) \
    .withColumn("_a",
        sin(col("dlat")/2)**2 +
        cos(col("lat1")) * cos(col("lat2")) * sin(col("dlon")/2)**2
    ) \
    .withColumn("distance_km",
        spark_round(2 * R * atan2(sqrt(col("_a")), sqrt(1 - col("_a"))), 3)
    ) \
    .drop("lat1", "lat2", "dlat", "dlon", "_a") \
    .filter(col("distance_km").between(0.05, 50)) \
    .filter(col("start_station_name").isNotNull()) \
    .filter(col("end_station_name").isNotNull())

df.cache()
print("✅ Dados prontos\n")

# ─── 3. Resumo mensal ─────────────────────────────────────────────────────────
print("📊 [1/6] Resumo mensal...")

resumo_mensal = df.groupBy("mes").agg(
    count("*").alias("total_viagens"),
    spark_round(avg("duration_min"), 2).alias("duracao_media_min"),
    spark_round(F.expr("percentile_approx(duration_min, 0.5)"), 2).alias("duracao_mediana_min"),
    spark_round(avg("distance_km"), 3).alias("distancia_media_km"),
    spark_round(F.expr("percentile_approx(distance_km, 0.5)"), 3).alias("distancia_mediana_km"),
    spark_round(
        F.sum(when(col("member_casual") == "member", 1).otherwise(0)) / count("*") * 100, 1
    ).alias("pct_member"),
    spark_round(
        F.sum(when(col("member_casual") == "casual", 1).otherwise(0)) / count("*") * 100, 1
    ).alias("pct_casual"),
    F.countDistinct("start_station_name").alias("estacoes_partida_unicas"),
    F.countDistinct("end_station_name").alias("estacoes_chegada_unicas")
).orderBy("mes")

resumo_mensal.show(truncate=False)

# ─── 4. Duração por tipo de usuário e mês ─────────────────────────────────────
print("📊 [2/6] Duração por tipo de usuário...")

duracao_por_tipo = df.groupBy("mes", "member_casual").agg(
    count("*").alias("viagens"),
    spark_round(avg("duration_min"), 2).alias("duracao_media_min"),
    spark_round(F.expr("percentile_approx(duration_min, 0.25)"), 2).alias("q1_min"),
    spark_round(F.expr("percentile_approx(duration_min, 0.5)"),  2).alias("mediana_min"),
    spark_round(F.expr("percentile_approx(duration_min, 0.75)"), 2).alias("q3_min"),
    spark_round(spark_max("duration_min"), 2).alias("max_min")
).orderBy("mes", "member_casual")

duracao_por_tipo.show(truncate=False)

# ─── 5. Distância por tipo de usuário e mês ───────────────────────────────────
print("📊 [3/6] Distância por tipo de usuário...")

distancia_por_tipo = df.groupBy("mes", "member_casual").agg(
    count("*").alias("viagens"),
    spark_round(avg("distance_km"), 3).alias("distancia_media_km"),
    spark_round(F.expr("percentile_approx(distance_km, 0.25)"), 3).alias("q1_km"),
    spark_round(F.expr("percentile_approx(distance_km, 0.5)"),  3).alias("mediana_km"),
    spark_round(F.expr("percentile_approx(distance_km, 0.75)"), 3).alias("q3_km"),
    spark_round(spark_max("distance_km"), 3).alias("max_km")
).orderBy("mes", "member_casual")

distancia_por_tipo.show(truncate=False)

# ─── 6. Top 20 estações de partida por mês ────────────────────────────────────
print("📊 [4/6] Top estações de partida...")

w_partida = Window.partitionBy("mes").orderBy(F.desc("viagens"))

top_partida = df.groupBy("mes", "start_station_name", "start_lat", "start_lng").agg(
    count("*").alias("viagens"),
    spark_round(avg("duration_min"), 2).alias("duracao_media_min"),
    spark_round(avg("distance_km"), 3).alias("distancia_media_km")
) \
    .withColumn("rank", F.rank().over(w_partida)) \
    .filter(col("rank") <= 20) \
    .drop("rank") \
    .orderBy("mes", F.desc("viagens"))

top_partida.show(5, truncate=False)

# ─── 7. Top 20 estações de chegada por mês ────────────────────────────────────
print("📊 [5/6] Top estações de chegada...")

w_chegada = Window.partitionBy("mes").orderBy(F.desc("viagens"))

top_chegada = df.groupBy("mes", "end_station_name", "end_lat", "end_lng").agg(
    count("*").alias("viagens"),
    spark_round(avg("duration_min"), 2).alias("duracao_media_min"),
    spark_round(avg("distance_km"), 3).alias("distancia_media_km")
) \
    .withColumn("rank", F.rank().over(w_chegada)) \
    .filter(col("rank") <= 20) \
    .drop("rank") \
    .orderBy("mes", F.desc("viagens"))

top_chegada.show(5, truncate=False)

# ─── 8. Distribuição por hora do dia e mês ────────────────────────────────────
print("📊 [6/6] Distribuição por hora do dia...")

pico_hora = df.groupBy("mes", "hora", "member_casual").agg(
    count("*").alias("viagens"),
    spark_round(avg("duration_min"), 2).alias("duracao_media_min")
).orderBy("mes", "hora", "member_casual")

pico_hora.show(10, truncate=False)

# ─── 9. Top 1000 rotas por mês ────────────────────────────────────────────────
print("📊 [+] Top 1000 rotas por mês...")

w_rotas = Window.partitionBy("mes").orderBy(F.desc("viagens"))

top_rotas = df.groupBy(
    "mes",
    "start_station_name", "start_lat", "start_lng",
    "end_station_name",   "end_lat",   "end_lng"
).agg(
    count("*").alias("viagens"),
    spark_round(avg("duration_min"), 2).alias("duracao_media_min"),
    spark_round(avg("distance_km"),  3).alias("distancia_media_km"),
    spark_round(
        F.sum(when(col("member_casual") == "member", 1).otherwise(0)) / count("*") * 100, 1
    ).alias("pct_member")
) \
    .withColumn("rank", F.rank().over(w_rotas)) \
    .filter(col("rank") <= 1000) \
    .drop("rank") \
    .orderBy("mes", F.desc("viagens"))

top_rotas.show(5, truncate=False)

# ─── 10. Salva todos os resultados no HDFS ────────────────────────────────────
print("\n💾 Salvando em hdfs://namenode:9000/citibike/processed/ ...")

PROCESSED = "hdfs://namenode:9000/citibike/processed"

def salvar(df, nome):
    path = f"{PROCESSED}/{nome}"
    df.coalesce(1).write.mode("overwrite").option("header", "true").json(path)
    print(f"  ✓ {nome}")

salvar(resumo_mensal,      "resumo_mensal")
salvar(duracao_por_tipo,   "duracao_por_tipo")
salvar(distancia_por_tipo, "distancia_por_tipo")
salvar(top_partida,        "top_estacoes_partida")
salvar(top_chegada,        "top_estacoes_chegada")
salvar(pico_hora,          "pico_hora")
salvar(top_rotas,          "top_rotas")

print(f"\n✅ Todos os resultados salvos em {PROCESSED}")
print("Processamento concluído!\n")

spark.stop()
