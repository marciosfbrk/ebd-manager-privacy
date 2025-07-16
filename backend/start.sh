#!/bin/bash

# Script de inicialização para Railway
echo "🚀 Iniciando EBD Manager Backend..."

# Verificar se as variáveis de ambiente estão configuradas
if [ -z "$MONGO_URL" ]; then
    echo "❌ MONGO_URL não configurada!"
    exit 1
fi

if [ -z "$DB_NAME" ]; then
    echo "❌ DB_NAME não configurada!"
    exit 1
fi

echo "✅ Variáveis de ambiente configuradas"
echo "📊 Banco: $DB_NAME"
echo "🔗 MongoDB: ${MONGO_URL:0:30}..."

# Instalar dependências Python
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Iniciar servidor
echo "🚀 Iniciando servidor FastAPI..."
uvicorn server:app --host 0.0.0.0 --port $PORT