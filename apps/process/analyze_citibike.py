"""
analyze_citibike.py
Lê todos os snapshots JSON do HDFS e gera análises sobre
o sistema CitiBike NYC usando PySpark SQL e DataFrame API.
"""
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# ─── Inicia a SparkSession ────────────────────────────────────────────────────
# O master local[*] usa todos os cores disponíveis no container
# para desenvolvimento. O HDFS é acessado via hdfs://namenode:9000
spark = SparkSession.builder \
    .appName("CitiBike Analysis") \
    .master("local[*]") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")  # reduz verbosidade dos logs

print("\n" + "="*60)
print("  ANÁLISE CitiBike NYC — Apache Spark + HDFS")
print("="*60 + "\n")

# ─── 1. Leitura do HDFS ───────────────────────────────────────────────────────
# O Spark lê TODOS os arquivos JSON do diretório de uma vez.
# Cada linha vira uma Row, e o schema é inferido automaticamente.
# multiLine=True porque cada arquivo é um array JSON (não JSON Lines)
print("Lendo dados do HDFS...")
df_raw = spark.read \
    .option("multiLine", "true") \
    .json("hdfs://namenode:9000/citibike/raw/*.json")

total_registros = df_raw.count()
print(f"Total de registros carregados: {total_registros}")
print(f"Schema detectado automaticamente:")
df_raw.printSchema()

# ─── 2. Análise 1 — Top 10 Estações com Mais Bikes Disponíveis ───────────────
print("\n📊 TOP 10 ESTAÇÕES COM MAIS BIKES DISPONÍVEIS (média)")
print("-"*60)

top_stations = df_raw \
    .groupBy("name", "latitude", "longitude") \
    .agg(
        F.round(F.avg("free_bikes"), 1).alias("media_bikes"),
        F.round(F.avg("empty_slots"), 1).alias("media_vagas"),
        F.count("*").alias("snapshots")
    ) \
    .orderBy(F.desc("media_bikes")) \
    .limit(10)

top_stations.show(truncate=False)

# ─── 3. Análise 2 — Estações Críticas (sem bikes) ────────────────────────────
print("\n🚨 ESTAÇÕES FREQUENTEMENTE VAZIAS (sem bikes em >50% dos snapshots)")
print("-"*60)

estacoes_vazias = df_raw \
    .groupBy("name") \
    .agg(
        F.count("*").alias("total_snapshots"),
        F.sum(F.when(F.col("free_bikes") == 0, 1).otherwise(0)).alias("vezes_vazia")
    ) \
    .withColumn("pct_vazia", F.round(F.col("vezes_vazia") / F.col("total_snapshots") * 100, 1)) \
    .filter(F.col("pct_vazia") > 50) \
    .orderBy(F.desc("pct_vazia")) \
    .limit(10)

estacoes_vazias.show(truncate=False)

# ─── 4. Análise 3 — Resumo Geral do Sistema ──────────────────────────────────
print("\n📈 RESUMO GERAL DO SISTEMA")
print("-"*60)

resumo = df_raw.agg(
    F.countDistinct("name").alias("total_estacoes"),
    F.round(F.avg("free_bikes"), 1).alias("media_bikes_por_estacao"),
    F.sum("free_bikes").alias("total_bikes_disponiveis"),
    F.sum("empty_slots").alias("total_vagas_livres"),
    F.min("collected_at").alias("primeiro_snapshot"),
    F.max("collected_at").alias("ultimo_snapshot")
)

resumo.show(truncate=False, vertical=True)

# ─── 5. Salva resultados no HDFS (camada processed) ──────────────────────────
print("\n💾 Salvando resultados processados no HDFS...")

top_stations \
    .write \
    .mode("overwrite") \
    .json("hdfs://namenode:9000/citibike/processed/top_stations")

estacoes_vazias \
    .write \
    .mode("overwrite") \
    .json("hdfs://namenode:9000/citibike/processed/estacoes_vazias")

print("✓ Resultados salvos em hdfs://namenode:9000/citibike/processed/")
print("\nProcessamento concluído! ✅\n")

spark.stop()