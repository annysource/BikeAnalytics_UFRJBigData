# ⚡ Comandos Rápidos - BikeAnalytics

> **Cola de comandos para executar rapidamente**

---

## 🚀 INICIAR TUDO

```bash
cd "c:\Users\Usuário\Desktop\Pós\Big Data\Projeto\BikeAnalytics_UFRJBigData\Projeto"
docker compose up -d
```

---

## ✅ VERIFICAR STATUS

```bash
# Status dos containers
docker compose ps

# Ver se todos estão UP
docker compose ps | grep "Up"
```

---

## 🔍 VERIFICAR DADOS NO HDFS

```bash
# Contar arquivos coletados
curl -s "http://localhost:9870/webhdfs/v1/citibike/station_status?op=LISTSTATUS" | python3 -m json.tool | grep pathSuffix | wc -l

# Ver últimos 5 arquivos
curl -s "http://localhost:9870/webhdfs/v1/citibike/station_status?op=LISTSTATUS" | python3 -m json.tool | grep pathSuffix | tail -5

# Ver estrutura completa
curl -s "http://localhost:9870/webhdfs/v1/citibike?op=LISTSTATUS" | python3 -m json.tool
```

---

## 📊 MONITORAR

```bash
# Ver logs em tempo real
docker compose logs -f ingest

# Ver uso de recursos
docker stats --no-stream

# Ver logs de todos os serviços
docker compose logs -f
```

---

## 🌐 TESTAR SERVIÇOS

```bash
# Testar HDFS
curl -s http://localhost:9870 | grep title

# Testar Spark
curl -s http://localhost:8080 | grep title

# Testar Dashboard
curl -s http://localhost:5000 | grep title

# Testar Jupyter
curl -s http://localhost:8888 | grep title
```

---

## 🚀 RODAR SPARK (Processamento)

```bash
# Executar análise PySpark
docker compose exec spark-master spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  /opt/spark-apps/process/analyze_citibike.py

# Ver progresso em outro terminal
docker compose logs -f spark-master
```

---

## 🔄 REINICIAR SERVIÇOS

```bash
# Reiniciar um container
docker compose restart ingest
docker compose restart web-ui

# Reiniciar todos
docker compose restart
```

---

## 🛑 PARAR TUDO

```bash
# Parar (mantém dados)
docker compose down

# Parar e apagar dados (cuidado!)
docker compose down -v
```

---

## 🧹 LIMPEZA

```bash
# Limpar containers parados
docker container prune

# Limpar imagens não usadas
docker image prune

# Limpar tudo (cuidado!)
docker system prune -a
```

---

## 📱 URLs DE ACESSO

```
Dashboard:   http://localhost:5000
HDFS Web:    http://localhost:9870
Spark Web:   http://localhost:8080
Jupyter:     http://localhost:8888   (token: citibike)
```

---

## 🔧 COMANDOS DE DIAGNÓSTICO

```bash
# Ver logs de erro
docker compose logs | grep -i error

# Ver logs de um container específico
docker compose logs namenode | tail -50
docker compose logs spark-master | tail -50
docker compose logs ingest | tail -50

# Inspecionar um container
docker inspect citibike-ingest

# Executar comando dentro do container
docker exec citibike-ingest ls -la
docker exec citibike-ingest python3 --version

# Ver processos dentro do container
docker exec citibike-web ps aux
```

---

## 📊 VERIFICAR COLETA AUTOMÁTICA

```bash
# Contar arquivos AGORA
echo "Arquivos agora:"
curl -s "http://localhost:9870/webhdfs/v1/citibike/station_status?op=LISTSTATUS" | python3 -m json.tool | grep pathSuffix | wc -l

# Aguardar 5 minutos
echo "Aguardando 5 minutos..."
sleep 300

# Contar arquivos DEPOIS
echo "Arquivos depois:"
curl -s "http://localhost:9870/webhdfs/v1/citibike/station_status?op=LISTSTATUS" | python3 -m json.tool | grep pathSuffix | wc -l
```

---

## 🎯 SEQUÊNCIA COMPLETA DE INICIALIZAÇÃO

```bash
# 1. Navegar para a pasta
cd "c:\Users\Usuário\Desktop\Pós\Big Data\Projeto\BikeAnalytics_UFRJBigData\Projeto"

# 2. Subir containers
docker compose up -d

# 3. Aguardar 90 segundos
sleep 90

# 4. Verificar status
docker compose ps

# 5. Testar HDFS
curl http://localhost:9870

# 6. Ver dados coletados
curl -s "http://localhost:9870/webhdfs/v1/citibike/station_status?op=LISTSTATUS" | python3 -m json.tool | grep pathSuffix | wc -l

# 7. Abrir navegador
# Dashboard: http://localhost:5000
```

---

## 🆘 TROUBLESHOOTING RÁPIDO

```bash
# Container não está UP
docker compose ps
docker compose restart [nome-do-container]

# Serviço não responde
curl http://localhost:[porta]
docker compose logs [nome-do-container]

# HDFS sem dados
docker compose logs ingest
docker compose restart ingest
sleep 300  # aguardar 5 min

# Recriar tudo do zero (apaga dados!)
docker compose down -v
docker compose up -d
```

---

## 💾 BACKUP DOS DADOS

```bash
# Listar volumes
docker volume ls

# Inspecionar volume do HDFS
docker volume inspect projeto_hadoop_namenode

# Fazer backup (exemplo)
docker run --rm -v projeto_hadoop_namenode:/data -v $(pwd):/backup ubuntu tar czf /backup/hdfs_backup.tar.gz /data
```

---

## 🎓 ANÁLISE EXPLORATÓRIA NO JUPYTER

```bash
# 1. Abrir Jupyter
# URL: http://localhost:8888
# Token: citibike

# 2. Navegar para: work/process/

# 3. Criar novo notebook ou abrir existente

# 4. Testar conexão com HDFS:
```

```python
from hdfs import InsecureClient
client = InsecureClient('http://namenode:9870', user='root')
print(client.list('/citibike/'))
```

---

## 📈 COMANDOS AVANÇADOS

```bash
# Ver tamanho dos volumes
docker system df -v

# Ver rede Docker
docker network ls
docker network inspect projeto_default

# Ver variáveis de ambiente de um container
docker exec citibike-ingest env

# Copiar arquivo do container para host
docker cp citibike-ingest:/app/fetch_citibike.py ./fetch_citibike_backup.py

# Copiar arquivo do host para container
docker cp ./novo_script.py citibike-ingest:/app/

# Entrar no container (shell interativo)
docker exec -it citibike-ingest bash
docker exec -it namenode bash
```

---

## 🔥 ONE-LINERS ÚTEIS

```bash
# Reiniciar tudo rapidamente
docker compose down && docker compose up -d && sleep 90 && docker compose ps

# Ver quantos arquivos foram coletados em todas as pastas
echo "Status: $(curl -s 'http://localhost:9870/webhdfs/v1/citibike/station_status?op=LISTSTATUS' | grep -o pathSuffix | wc -l)" && echo "Info: $(curl -s 'http://localhost:9870/webhdfs/v1/citibike/station_info?op=LISTSTATUS' | grep -o pathSuffix | wc -l)"

# Monitorar crescimento de arquivos a cada 30 segundos
watch -n 30 "curl -s 'http://localhost:9870/webhdfs/v1/citibike/station_status?op=LISTSTATUS' | grep -o pathSuffix | wc -l"

# Abrir todos os serviços no navegador (Windows)
start http://localhost:5000 && start http://localhost:9870 && start http://localhost:8080 && start http://localhost:8888
```

---

**Última atualização:** 2026-05-12