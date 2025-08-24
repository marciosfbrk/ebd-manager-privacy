#!/bin/bash

# SCRIPT PARA CORRIGIR LOGIN AUTOMATICAMENTE
# Garante que depois de QUALQUER mudança, o login continue funcionando

echo "🔧 CORREÇÃO AUTOMÁTICA DO LOGIN..."

# 1. Garantir URLs corretas
echo "📝 Corrigindo URLs..."
echo 'REACT_APP_BACKEND_URL=/api' > /app/frontend/.env
echo 'WDS_SOCKET_PORT=443' >> /app/frontend/.env

echo 'REACT_APP_BACKEND_URL="/api"' > /app/frontend/.env.production

# 2. Limpar cache que pode estar causando problema
echo "🧹 Limpando cache..."
cd /app/frontend
rm -rf build 2>/dev/null
rm -rf node_modules/.cache 2>/dev/null

# 3. Reiniciar serviços
echo "🔄 Reiniciando serviços..."
sudo supervisorctl restart frontend backend

# 4. Aguardar estabilização
echo "⏳ Aguardando 15 segundos..."
sleep 15

# 5. Testar login
echo "🧪 Testando login..."
LOGIN_TEST=$(curl -s -X POST http://localhost:8001/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@ebd.com","senha":"123456"}' \
  -w "%{http_code}")

if [[ "$LOGIN_TEST" == *"200"* ]]; then
    echo "✅ LOGIN FUNCIONANDO!"
    echo "🌐 Acesse: https://ebd-dashboard-1.preview.emergentagent.com"
    echo "👤 admin@ebd.com / 123456"
    echo "👤 marcio@ebd.com.br / 5544%\$Gg"
else
    echo "❌ Login com problema. Executando restauração..."
    /app/restore_last_working.sh
fi

echo "🎉 CORREÇÃO CONCLUÍDA!"