# 🚀 Guia Completo de Execução - BikeAnalytics

> **Guia passo a passo para iniciar e explorar o projeto BikeAnalytics CitiBike**

---

## 📋 Pré-requisitos

- Docker Desktop instalado e funcionando
- As imagens Docker já foram baixadas (primeira execução concluída)
- Estar na pasta correta do projeto

---

## 🔧 PARTE 1: Inicialização do Sistema

### **Passo 1: Abrir o Docker Desktop**

1. Abra o **Docker Desktop** no Windows
2. Aguarde até o ícone ficar **verde** (Docker está pronto)
3. ⏱️ Tempo: ~30-60 segundos

---

### **Passo 2: Abrir o Terminal na Pasta do Projeto**

Abra o **Git Bash** ou **PowerShell** e navegue para a pasta:

```bash
cd "c:\Users\Usuário\Desktop\Pós\Big Data\Projeto\BikeAnalytics_UFRJBigData\Projeto"
```

**Confirme que está na pasta correta:**

```bash
pwd
# Deve retornar: /c/Users/Usuário/Desktop/Pós/Big Data/Projeto/BikeAnalytics_UFRJBigData/Projeto
```

```bash
ls
# Deve mostrar: docker-compose.yml, apps/, data/, etc.
```

---

### **Passo 3: Subir Todos os Serviços**

```bash
docker compose up -d
```

**O que vai acontecer:**
- ✅ As imagens já estão baixadas (não demora)
- ✅ Criação/inicialização de 8 containers
- ✅ Montagem dos volumes persistentes
- ⏱️ Tempo: ~30-60 segundos

**Saída esperada:**

```
[+] Running 12/12
 ✔ Network projeto_default           Created
 ✔ Container namenode                Started
 ✔ Container datanode                Started
 ✔ Container spark-master            Started
 ✔ Container spark-worker-1          Started
 ✔ Container spark-worker-2          Started
 ✔ Container citibike-ingest         Started
 ✔ Container citibike-web            Started
 ✔ Container citibike-jupyter        Started
```

---

### **Passo 4: Verificar se Todos os Containers Estão Rodando**

```bash
docker compose ps
```

**Saída esperada - todos com status `Up`:**

```
NAME               STATUS
citibike-ingest    Up X minutes
citibike-jupyter   Up X minutes (healthy)
citibike-web       Up X minutes
datanode           Up X minutes (healthy)
namenode           Up X minutes (healthy)
spark-master       Up X minutes
spark-worker-1     Up X minutes
spark-worker-2     Up X minutes
```

**✅ Se todos estiverem `Up`, você está pronto!**

**❌ Se algum estiver com problema:**

```bash
# Ver logs de um container específico
docker compose logs [nome-do-container]

# Exemplo:
docker compose logs namenode
docker compose logs ingest
```

---

## 🔍 PARTE 2: Verificação e Monitoramento

### **Passo 5: Aguardar Inicialização Completa**

Alguns serviços demoram ~1-2 minutos para ficarem prontos:

```bash
# Aguarde 90 segundos para tudo estabilizar
sleep 90
```

Ou simplesmente aguarde **2 minutos** antes de prosseguir.

---

### **Passo 6: Verificar o HDFS (Armazenamento)**

```bash
# Testar se o HDFS está respondendo
curl -s http://localhost:9870 | grep -o "<title>[^<]*" | head -1
```

**Saída esperada:**
```
<title>Hadoop Administration
```

**Listar arquivos no HDFS:**

```bash
curl -s "http://localhost:9870/webhdfs/v1/?op=LISTSTATUS" | python3 -m json.tool | grep pathSuffix
```

**Saída esperada:**
```json
"pathSuffix": "citibike"
```

---

### **Passo 7: Verificar a Ingestão de Dados**

```bash
# Ver se o container de ingestão está coletando dados
curl -s "http://localhost:9870/webhdfs/v1/citibike?op=LISTSTATUS" | python3 -m json.tool
```

**Saída esperada:**
```json
{
    "FileStatuses": {
        "FileStatus": [
            {
                "pathSuffix": "station_info",
                "type": "DIRECTORY"
            },
            {
                "pathSuffix": "station_status",
                "type": "DIRECTORY"
            }
        ]
    }
}
```

**Contar quantos arquivos já foram coletados:**

```bash
# Station Status
curl -s "http://localhost:9870/webhdfs/v1/citibike/station_status?op=LISTSTATUS" | python3 -m json.tool | grep pathSuffix | wc -l

# Station Info
curl -s "http://localhost:9870/webhdfs/v1/citibike/station_info?op=LISTSTATUS" | python3 -m json.tool | grep pathSuffix | wc -l
```

**Saída esperada:** Números crescentes a cada 5 minutos

---

### **Passo 8: Verificar o Spark Cluster**

```bash
# Testar se o Spark Master está respondendo
curl -s http://localhost:8080 | grep -o "<title>[^<]*" | head -1
```

**Saída esperada:**
```
<title>Spark Master at spark://172.18.0.3:7077
```

**Ver logs do Spark:**

```bash
docker compose logs spark-master | grep -E "(Started|Worker|Master)"
```

**Saída esperada:**
```
spark-master  | INFO Master: Starting Spark master at spark://172.18.0.3:7077
spark-master  | INFO Master: Registering worker 172.18.0.6:36003 with 1 cores, 512.0 MiB RAM
spark-master  | INFO Master: Registering worker 172.18.0.7:44041 with 1 cores, 512.0 MiB RAM
```

---

### **Passo 9: Verificar o Dashboard Streamlit**

```bash
# Testar se o dashboard está respondendo
curl -s http://localhost:5000 | grep -o "<title>[^<]*" | head -1
```

**Saída esperada:**
```
<title>Streamlit
```

---

## 🌐 PARTE 3: Acessando os Serviços

### **Passo 10: Abrir os Serviços no Navegador**

Abra seu navegador e acesse:

#### 1️⃣ **Dashboard Streamlit** (Interface Principal)
```
http://localhost:5000
```

**O que você vai ver:**
- 🗺️ Mapa interativo de NYC com estações
- 📊 KPIs: bikes disponíveis, vagas, estações
- 📈 Gráficos e visualizações

---

#### 2️⃣ **HDFS Web UI** (Explorar Dados)
```
http://localhost:9870
```

**Como navegar:**
1. Clique em **"Utilities"** no menu superior
2. Selecione **"Browse the file system"**
3. Navegue para `/citibike/`
4. Explore as pastas:
   - `station_status/` → arquivos JSON de status (a cada 5 min)
   - `station_info/` → arquivos JSON de informações das estações
5. Clique em qualquer arquivo para ver o conteúdo JSON

---

#### 3️⃣ **Spark Web UI** (Cluster de Processamento)
```
http://localhost:8080
```

**O que você vai ver:**
- 2 Workers ativos (worker-1 e worker-2)
- Status: Alive
- Recursos: 512MB RAM, 1 core cada
- Running/Completed Applications (quando rodar jobs)

---

#### 4️⃣ **Jupyter Notebook** (Análise Exploratória)
```
http://localhost:8888
```

**Credenciais:**
- **Token:** `citibike`

**Como usar:**
1. Digite o token: `citibike`
2. Navegue para `work/process/` ou `notebooks/`
3. Abra o notebook `explore_data_citibike.ipynb` (se disponível)
4. Execute as células com **Shift + Enter**

---

## 🧪 PARTE 4: Testes e Validação

### **Passo 11: Verificar Coleta Automática de Dados**

A ingestão coleta dados **a cada 5 minutos**. Vamos verificar:

```bash
# Ver quantos snapshots existem AGORA
echo "Snapshots atuais:"
curl -s "http://localhost:9870/webhdfs/v1/citibike/station_status?op=LISTSTATUS" | python3 -m json.tool | grep pathSuffix | wc -l

# Aguardar 5 minutos
echo "Aguardando 5 minutos para nova coleta..."
sleep 300

# Ver quantos snapshots existem DEPOIS
echo "Snapshots após 5 minutos:"
curl -s "http://localhost:9870/webhdfs/v1/citibike/station_status?op=LISTSTATUS" | python3 -m json.tool | grep pathSuffix | wc -l
```

**✅ Se o número aumentou, a coleta automática está funcionando!**

---

### **Passo 12: Ver Logs em Tempo Real**

```bash
# Logs do container de ingestão (pode não mostrar nada devido ao buffering)
docker compose logs -f ingest

# Logs do Spark Master
docker compose logs -f spark-master

# Logs do Dashboard Web
docker compose logs -f web-ui

# Logs de todos os serviços
docker compose logs -f
```

**Pressione `Ctrl + C` para sair dos logs**

---

### **Passo 13: Monitorar Uso de Recursos**

```bash
# Ver uso de CPU e memória de todos os containers
docker stats --no-stream

# Ver uso contínuo (atualiza a cada 1 segundo)
docker stats
```

**Saída esperada:**

```
NAME               CPU %     MEM USAGE / LIMIT     MEM %
citibike-ingest    0.5%      150MB / 768MB        19.5%
citibike-web       2.0%      180MB / 256MB        70.3%
namenode           1.0%      350MB / 512MB        68.4%
spark-master       0.8%      320MB / 512MB        62.5%
...
```

**Pressione `Ctrl + C` para sair**

---

## 🚀 PARTE 5: Processamento com Spark (Opcional)

### **Passo 14: Rodar Análise PySpark** ⏱️ ~15-25 minutos

**⚠️ ATENÇÃO:** Só rode isso se quiser processar os dados históricos (CSVs grandes)

**Primeiro, verifique se há dados de trips no HDFS:**

```bash
curl -s "http://localhost:9870/webhdfs/v1/citibike?op=LISTSTATUS" | python3 -m json.tool | grep trips
```

**Se NÃO houver a pasta `trips`, você precisa baixar os dados históricos primeiro:**

```bash
# Baixar dados históricos (pode demorar ~10-30 minutos)
docker compose exec ingest python3 fetch_trips.py
```

**Depois que tiver dados de trips, rode o processamento Spark:**

```bash
docker compose exec spark-master spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  /opt/spark-apps/process/analyze_citibike.py
```

**O que vai acontecer:**
1. ⏱️ Duração: ~15-25 minutos
2. Processamento de ~3,8 milhões de viagens
3. Cálculo de distâncias com Haversine
4. Geração de 7 datasets agregados em `/citibike/processed/`

**Acompanhar o progresso:**

```bash
# Em outro terminal
docker compose logs -f spark-master

# No navegador
http://localhost:8080
```

**Após o processamento, os resultados estarão em:**

```bash
# Verificar resultados
curl -s "http://localhost:9870/webhdfs/v1/citibike/processed?op=LISTSTATUS" | python3 -m json.tool | grep pathSuffix
```

**Saída esperada:**
```
"pathSuffix": "resumo_mensal"
"pathSuffix": "top_estacoes_partida"
"pathSuffix": "top_estacoes_chegada"
"pathSuffix": "distribuicao_hora"
"pathSuffix": "top_rotas"
...
```

---

## 🛠️ PARTE 6: Comandos Úteis

### **Gerenciamento de Containers**

```bash
# Ver status de todos os containers
docker compose ps

# Reiniciar um container específico
docker compose restart [nome-do-container]

# Exemplo:
docker compose restart ingest
docker compose restart web-ui

# Reiniciar todos os containers
docker compose restart

# Parar todos os containers (mantém dados)
docker compose down

# Parar e APAGAR TODOS OS DADOS (cuidado!)
docker compose down -v
```

---

### **Visualização de Dados**

```bash
# Ver últimos arquivos coletados
curl -s "http://localhost:9870/webhdfs/v1/citibike/station_status?op=LISTSTATUS" | python3 -m json.tool | grep pathSuffix | tail -5

# Ver conteúdo de um arquivo específico (substitua YYYYMMDD_HHMMSS)
curl -s "http://localhost:9870/webhdfs/v1/citibike/station_status/status_20260512_103045.json?op=OPEN" | python3 -m json.tool | head -50

# Contar total de arquivos em todas as pastas
echo "Station Status:" && curl -s "http://localhost:9870/webhdfs/v1/citibike/station_status?op=LISTSTATUS" | python3 -m json.tool | grep pathSuffix | wc -l
echo "Station Info:" && curl -s "http://localhost:9870/webhdfs/v1/citibike/station_info?op=LISTSTATUS" | python3 -m json.tool | grep pathSuffix | wc -l
```

---

### **Troubleshooting**

```bash
# Container não está rodando
docker compose ps
docker compose logs [nome-do-container]
docker compose restart [nome-do-container]

# HDFS não está respondendo
docker compose logs namenode
docker compose logs datanode
curl http://localhost:9870

# Dashboard não carrega
docker compose logs web-ui
curl http://localhost:5000

# Spark não está funcionando
docker compose logs spark-master
docker compose logs spark-worker-1
curl http://localhost:8080

# Limpar tudo e recomeçar (APAGA DADOS!)
docker compose down -v
docker compose up -d
```

---

### **Limpeza e Manutenção**

```bash
# Ver uso de espaço em disco do Docker
docker system df

# Limpar imagens não utilizadas
docker image prune

# Limpar containers parados
docker container prune

# Limpar volumes não utilizados (cuidado!)
docker volume prune

# Limpar TUDO (cuidado! apaga todos os dados)
docker system prune -a --volumes
```

---

## ✅ Checklist de Validação

Use este checklist para garantir que tudo está funcionando:

- [ ] Docker Desktop está rodando (ícone verde)
- [ ] Estou na pasta correta (`Projeto/`)
- [ ] `docker compose up -d` executado com sucesso
- [ ] `docker compose ps` mostra 8 containers `Up`
- [ ] HDFS responde em http://localhost:9870
- [ ] Spark responde em http://localhost:8080
- [ ] Dashboard responde em http://localhost:5000
- [ ] Jupyter responde em http://localhost:8888
- [ ] Diretórios `/citibike/station_status/` e `/citibike/station_info/` existem no HDFS
- [ ] Arquivos JSON estão sendo coletados a cada 5 minutos
- [ ] Posso navegar no HDFS Web UI
- [ ] Posso ver o dashboard Streamlit no navegador

---

## 📊 Resumo dos Comandos Essenciais

### **Iniciar:**
```bash
cd "c:\Users\Usuário\Desktop\Pós\Big Data\Projeto\BikeAnalytics_UFRJBigData\Projeto"
docker compose up -d
docker compose ps
```

### **Verificar:**
```bash
curl http://localhost:9870
curl http://localhost:8080
curl http://localhost:5000
```

### **Monitorar:**
```bash
docker compose logs -f ingest
docker stats --no-stream
curl -s "http://localhost:9870/webhdfs/v1/citibike/station_status?op=LISTSTATUS" | python3 -m json.tool | grep pathSuffix | wc -l
```

### **Parar:**
```bash
docker compose down
```

---

## 🎯 URLs de Acesso Rápido

| Serviço | URL | Credencial |
|---------|-----|------------|
| **Dashboard** | http://localhost:5000 | — |
| **HDFS Web UI** | http://localhost:9870 | — |
| **Spark Web UI** | http://localhost:8080 | — |
| **Jupyter** | http://localhost:8888 | Token: `citibike` |

---

## 🆘 Problemas Comuns

### **Erro: "docker compose: command not found"**
```bash
# Use docker-compose (com hífen)
docker-compose up -d
```

### **Erro: "Cannot connect to the Docker daemon"**
- Certifique-se de que o Docker Desktop está rodando
- Aguarde o ícone ficar verde
- Reinicie o Docker Desktop se necessário

### **Container não sobe (EXIT 0 ou EXIT 1)**
```bash
# Ver logs detalhados
docker compose logs [nome-do-container]

# Recriar o container
docker compose up -d --force-recreate [nome-do-container]
```

### **Porta já está em uso**
```bash
# Ver qual processo está usando a porta (exemplo: 5000)
netstat -ano | findstr :5000

# Matar o processo (substitua PID)
taskkill /PID [número] /F

# Ou altere a porta no docker-compose.yml
```

### **HDFS não mostra dados**
```bash
# Aguarde 5 minutos para primeira coleta
sleep 300

# Verifique se o container de ingestão está rodando
docker compose ps ingest

# Reinicie o container de ingestão
docker compose restart ingest
```

---

## 🎉 Pronto!

Agora você tem um guia completo para iniciar, monitorar e explorar o projeto BikeAnalytics!

**Próximos passos sugeridos:**
1. ✅ Executar os comandos da Parte 1 (Inicialização)
2. ✅ Verificar se tudo está funcionando (Parte 2)
3. ✅ Abrir os serviços no navegador (Parte 3)
4. ✅ Explorar o dashboard e visualizações
5. ⚡ (Opcional) Rodar processamento Spark (Parte 5)

**Dúvidas?** Execute os comandos em ordem e verifique os logs se algo não funcionar.

---

**Criado em:** 2026-05-12  
**Versão:** 1.0  
**Projeto:** BikeAnalytics - CitiBike NYC Big Data Pipeline