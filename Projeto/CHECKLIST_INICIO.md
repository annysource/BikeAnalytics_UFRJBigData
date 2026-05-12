# ✅ Checklist de Inicialização - BikeAnalytics

> **Use este checklist para garantir que tudo está funcionando**

---

## 📋 PRÉ-REQUISITOS

- [ ] Docker Desktop está **instalado**
- [ ] Docker Desktop está **rodando** (ícone verde)
- [ ] Terminal aberto (**Git Bash** ou **PowerShell**)

---

## 🚀 PASSO 1: NAVEGAÇÃO

- [ ] Abri o terminal
- [ ] Executei o comando:
```bash
cd "c:\Users\Usuário\Desktop\Pós\Big Data\Projeto\BikeAnalytics_UFRJBigData\Projeto"
```
- [ ] Confirmei que estou na pasta correta:
```bash
pwd
# Saída esperada: /c/Users/Usuário/Desktop/Pós/Big Data/Projeto/BikeAnalytics_UFRJBigData/Projeto
```
- [ ] Verifiquei que o arquivo `docker-compose.yml` existe:
```bash
ls docker-compose.yml
```

---

## 🐳 PASSO 2: INICIALIZAÇÃO DOS CONTAINERS

- [ ] Executei o comando:
```bash
docker compose up -d
```
- [ ] Vi a mensagem de sucesso:
```
✔ Container namenode                Started
✔ Container datanode                Started
✔ Container spark-master            Started
✔ Container spark-worker-1          Started
✔ Container spark-worker-2          Started
✔ Container citibike-ingest         Started
✔ Container citibike-web            Started
✔ Container citibike-jupyter        Started
```
- [ ] **Aguardei 2 minutos** para inicialização completa

---

## 🔍 PASSO 3: VERIFICAÇÃO DOS CONTAINERS

- [ ] Executei o comando:
```bash
docker compose ps
```
- [ ] Confirmei que **8 containers** estão com status `Up`:
  - [ ] `namenode` - Up (healthy)
  - [ ] `datanode` - Up (healthy)
  - [ ] `spark-master` - Up
  - [ ] `spark-worker-1` - Up
  - [ ] `spark-worker-2` - Up
  - [ ] `citibike-ingest` - Up
  - [ ] `citibike-web` - Up
  - [ ] `citibike-jupyter` - Up (healthy)

---

## 🌐 PASSO 4: TESTE DOS SERVIÇOS WEB

### HDFS Web UI (porta 9870)
- [ ] Executei:
```bash
curl -s http://localhost:9870 | grep title
```
- [ ] Vi a saída: `<title>Hadoop Administration`
- [ ] **OU** Abri no navegador: http://localhost:9870
- [ ] A página carregou corretamente

### Spark Web UI (porta 8080)
- [ ] Executei:
```bash
curl -s http://localhost:8080 | grep title
```
- [ ] Vi a saída: `<title>Spark Master at spark://...`
- [ ] **OU** Abri no navegador: http://localhost:8080
- [ ] Vejo **2 Workers** listados (worker-1 e worker-2)

### Dashboard Streamlit (porta 5000)
- [ ] Executei:
```bash
curl -s http://localhost:5000 | grep title
```
- [ ] Vi a saída: `<title>Streamlit`
- [ ] **OU** Abri no navegador: http://localhost:5000
- [ ] O dashboard carregou com mapa e KPIs

### Jupyter Notebook (porta 8888)
- [ ] Abri no navegador: http://localhost:8888
- [ ] A tela de login apareceu
- [ ] Digitei o token: `citibike`
- [ ] Consegui acessar o Jupyter

---

## 📊 PASSO 5: VERIFICAÇÃO DE DADOS NO HDFS

### Estrutura de Diretórios
- [ ] Executei:
```bash
curl -s "http://localhost:9870/webhdfs/v1/citibike?op=LISTSTATUS" | python3 -m json.tool | grep pathSuffix
```
- [ ] Vi as pastas:
  - [ ] `"pathSuffix": "station_info"`
  - [ ] `"pathSuffix": "station_status"`

### Arquivos Coletados
- [ ] Executei:
```bash
curl -s "http://localhost:9870/webhdfs/v1/citibike/station_status?op=LISTSTATUS" | python3 -m json.tool | grep pathSuffix | wc -l
```
- [ ] O número retornado é **maior que 0** (pelo menos 1 arquivo)
- [ ] **Aguardei 5 minutos** e executei novamente
- [ ] O número **aumentou** (confirma coleta automática)

---

## 📱 PASSO 6: EXPLORAÇÃO NO NAVEGADOR

### Dashboard (http://localhost:5000)
- [ ] Vejo o **mapa de NYC** com pontos das estações
- [ ] Vejo os **KPIs** no topo:
  - [ ] Bikes Disponíveis
  - [ ] E-bikes Disponíveis
  - [ ] Vagas Livres
  - [ ] Total de Estações
  - [ ] Total de Snapshots
- [ ] Cliquei em **"🔄 Atualizar dados"** e os dados mudaram

### HDFS Web UI (http://localhost:9870)
- [ ] Cliquei em **"Utilities" → "Browse the file system"**
- [ ] Naveguei para `/citibike/`
- [ ] Cliquei em `station_status/`
- [ ] Vejo arquivos JSON nomeados `status_YYYYMMDD_HHMMSS.json`
- [ ] Cliquei em um arquivo e vi o conteúdo JSON

### Spark Web UI (http://localhost:8080)
- [ ] Vejo **Spark Master** no topo
- [ ] Vejo **2 Workers** na seção "Workers"
- [ ] Cada worker tem:
  - [ ] State: ALIVE
  - [ ] Memory: 512.0 MB
  - [ ] Cores: 1

---

## 🧪 PASSO 7: MONITORAMENTO

### Logs
- [ ] Executei:
```bash
docker compose logs --tail=20 ingest
```
- [ ] Vi logs de instalação do pip (esperado, logs de coleta podem não aparecer devido ao buffering)

### Recursos
- [ ] Executei:
```bash
docker stats --no-stream
```
- [ ] Vejo o uso de **CPU** e **Memória** de cada container
- [ ] Nenhum container está usando 100% da memória

---

## ✅ VALIDAÇÃO FINAL

- [ ] ✅ **8 containers** rodando
- [ ] ✅ **HDFS** respondendo e com dados
- [ ] ✅ **Spark** cluster ativo com 2 workers
- [ ] ✅ **Dashboard** acessível e mostrando mapa
- [ ] ✅ **Jupyter** acessível com token
- [ ] ✅ **Coleta automática** funcionando (arquivos aumentam a cada 5 min)
- [ ] ✅ Posso navegar no **HDFS Web UI**
- [ ] ✅ Posso ver **KPIs** no dashboard

---

## 🎯 SE TODOS OS ITENS ESTIVEREM MARCADOS:

### 🎉 **PARABÉNS! O SISTEMA ESTÁ 100% FUNCIONAL!**

Você pode agora:

1. **Explorar o Dashboard**
   - Ver estações em tempo real
   - Monitorar KPIs
   - Visualizar gráficos

2. **Navegar nos Dados**
   - Explorar arquivos JSON no HDFS
   - Ver snapshots coletados a cada 5 minutos

3. **Usar o Jupyter**
   - Criar notebooks de análise
   - Conectar ao HDFS
   - Processar dados com PySpark

4. **(Opcional) Rodar Análise Spark**
   - Baixar dados históricos
   - Processar ~3,8M viagens
   - Gerar datasets agregados

---

## ❌ SE ALGO NÃO FUNCIONOU:

### 🔧 Troubleshooting Rápido

**Container não está UP:**
```bash
docker compose ps
docker compose restart [nome-do-container]
docker compose logs [nome-do-container]
```

**HDFS não responde:**
```bash
docker compose logs namenode
docker compose restart namenode
sleep 60
curl http://localhost:9870
```

**Dashboard não carrega:**
```bash
docker compose logs web-ui
docker compose restart web-ui
sleep 30
curl http://localhost:5000
```

**Nenhum arquivo no HDFS:**
```bash
# Aguarde 5 minutos para primeira coleta
sleep 300

# Verifique novamente
curl -s "http://localhost:9870/webhdfs/v1/citibike/station_status?op=LISTSTATUS" | python3 -m json.tool | grep pathSuffix | wc -l

# Se ainda zero, reinicie o container de ingestão
docker compose restart ingest
```

**Recomeçar do zero (apaga dados!):**
```bash
docker compose down -v
docker compose up -d
sleep 120
docker compose ps
```

---

## 📚 PRÓXIMOS PASSOS

- [ ] Li o arquivo `GUIA_EXECUCAO.md` para comandos detalhados
- [ ] Li o arquivo `COMANDOS_RAPIDOS.md` para referência rápida
- [ ] Explorei o dashboard por pelo menos 5 minutos
- [ ] Naveguei no HDFS Web UI
- [ ] Abri o Jupyter e criei um notebook de teste
- [ ] (Opcional) Rodei análise PySpark

---

## 🆘 AJUDA

**Arquivos de Referência:**
- `GUIA_EXECUCAO.md` - Guia completo passo a passo
- `COMANDOS_RAPIDOS.md` - Cola de comandos
- `CHECKLIST_INICIO.md` - Este arquivo
- `README.md` - Documentação do projeto

**Comandos Essenciais:**
```bash
docker compose ps              # Ver status
docker compose logs -f         # Ver logs
docker stats                   # Ver recursos
docker compose restart         # Reiniciar
docker compose down            # Parar tudo
```

---

**Data:** 2026-05-12  
**Versão:** 1.0  
**Status:** ✅ Checklist Completo