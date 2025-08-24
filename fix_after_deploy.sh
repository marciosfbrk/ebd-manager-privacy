#!/bin/bash

# Script de Auto-Correção Pós-Deploy
# Executa automaticamente as correções necessárias após deploy

echo "🔧 EXECUTANDO AUTO-CORREÇÃO PÓS-DEPLOY..."

# Corrigir URLs do frontend
echo "📝 Corrigindo configurações do frontend..."
cp /app/frontend/.env.deploy /app/frontend/.env
cp /app/frontend/.env.production.deploy /app/frontend/.env.production

# Limpar cache
echo "🧹 Limpando cache..."
cd /app/frontend && rm -rf build && rm -rf node_modules/.cache 2>/dev/null

# Reiniciar serviços
echo "🔄 Reiniciando serviços..."
sudo supervisorctl restart frontend backend

# Aguardar estabilização
echo "⏳ Aguardando estabilização..."
sleep 10

# Testar se funcionou
echo "🧪 Testando sistema..."
RESPONSE=$(curl -s -w "%{http_code}" http://localhost:8001/api/login -X POST -H "Content-Type: application/json" -d '{"email":"admin@ebd.com","senha":"123456"}' -o /dev/null)

if [ "$RESPONSE" = "200" ]; then
    echo "✅ SUCESSO! Sistema funcionando após deploy!"
    echo "🌐 Acesse: https://ebd-dashboard-1.preview.emergentagent.com"
    echo "👤 Admin: admin@ebd.com / 123456"
    echo "👤 Admin 2: marcio@ebd.com.br / 5544%\$Gg"
else
    echo "❌ ERRO detectado! Executando restauração de emergência..."
    bash /app/restore_last_working.sh
fi

echo "🎉 AUTO-CORREÇÃO CONCLUÍDA!"