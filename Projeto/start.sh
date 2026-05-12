#!/bin/bash
# Script de inicialização rápida - BikeAnalytics
# Uso: ./start.sh

echo "🚴 BikeAnalytics - CitiBike NYC Pipeline"
echo "========================================"
echo ""

# Verificar se Docker está rodando
echo "📋 Verificando Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando!"
    echo "   Por favor, abra o Docker Desktop e aguarde até o ícone ficar verde."
    exit 1
fi
echo "✅ Docker está rodando"
echo ""

# Subir os containers
echo "🚀 Iniciando containers..."
docker compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Erro ao iniciar containers!"
    exit 1
fi
echo ""

# Aguardar inicialização
echo "⏳ Aguardando inicialização dos serviços (90 segundos)..."
for i in {1..90}; do
    echo -n "."
    sleep 1
done
echo ""
echo ""

# Verificar status
echo "📊 Status dos containers:"
docker compose ps
echo ""

# Testar serviços
echo "🔍 Testando serviços..."
echo ""

# HDFS
echo -n "   HDFS (9870): "
if curl -s http://localhost:9870 > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FALHOU"
fi

# Spark
echo -n "   Spark (8080): "
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FALHOU"
fi

# Dashboard
echo -n "   Dashboard (5000): "
if curl -s http://localhost:5000 > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FALHOU"
fi

# Jupyter
echo -n "   Jupyter (8888): "
if curl -s http://localhost:8888 > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FALHOU"
fi

echo ""

# Verificar dados no HDFS
echo "📁 Verificando dados no HDFS..."
STATION_STATUS_COUNT=$(curl -s "http://localhost:9870/webhdfs/v1/citibike/station_status?op=LISTSTATUS" 2>/dev/null | grep -o "pathSuffix" | wc -l)
STATION_INFO_COUNT=$(curl -s "http://localhost:9870/webhdfs/v1/citibike/station_info?op=LISTSTATUS" 2>/dev/null | grep -o "pathSuffix" | wc -l)

echo "   Station Status: $STATION_STATUS_COUNT arquivos"
echo "   Station Info: $STATION_INFO_COUNT arquivos"
echo ""

# URLs de acesso
echo "🌐 URLs de Acesso:"
echo "   Dashboard:  http://localhost:5000"
echo "   HDFS Web:   http://localhost:9870"
echo "   Spark Web:  http://localhost:8080"
echo "   Jupyter:    http://localhost:8888 (token: citibike)"
echo ""

# Comandos úteis
echo "📚 Comandos Úteis:"
echo "   Ver logs:        docker compose logs -f [container]"
echo "   Monitorar:       docker stats"
echo "   Parar tudo:      docker compose down"
echo "   Ver este guia:   cat GUIA_EXECUCAO.md"
echo ""

echo "✅ Sistema iniciado com sucesso!"
echo "🎯 Abra seu navegador e acesse: http://localhost:5000"
echo ""
