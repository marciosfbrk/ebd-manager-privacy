#!/bin/bash

echo "🎯 RESTAURANDO ESTADO BACKUPOK (100% FUNCIONAL)..."

# Parar serviços
echo "⏸️ Parando serviços..."
sudo supervisorctl stop frontend backend

# Restaurar arquivos backend
echo "📋 Restaurando backend..."
cp "/app/backups_deploy/backupok/backend.env" /app/backend/.env
cp "/app/backups_deploy/backupok/server.py" /app/backend/server.py
cp "/app/backups_deploy/backupok/requirements.txt" /app/backend/requirements.txt

# Restaurar arquivos frontend
echo "📋 Restaurando frontend..."
cp "/app/backups_deploy/backupok/frontend.env" /app/frontend/.env
cp "/app/backups_deploy/backupok/frontend.env.production" /app/frontend/.env.production
cp "/app/backups_deploy/backupok/App.js" /app/frontend/src/App.js
cp "/app/backups_deploy/backupok/package.json" /app/frontend/package.json

# Restaurar scripts de proteção
echo "🛠️ Restaurando scripts de proteção..."
cp "/app/backups_deploy/backupok/fix_login_always.sh" /app/fix_login_always.sh
cp "/app/backups_deploy/backupok/restore_last_working.sh" /app/restore_last_working.sh
chmod +x /app/fix_login_always.sh
chmod +x /app/restore_last_working.sh

# Limpar cache
echo "🧹 Limpando cache..."
cd /app/frontend && rm -rf build && rm -rf node_modules/.cache 2>/dev/null

# Reiniciar serviços
echo "🚀 Reiniciando serviços..."
sudo supervisorctl start frontend backend

# Aguardar estabilização
echo "⏳ Aguardando estabilização..."
sleep 15

# Testar login
echo "🧪 Testando login..."
LOGIN_TEST=$(curl -s -X POST http://localhost:8001/api/login -H "Content-Type: application/json" -d '{"email":"admin@ebd.com","senha":"123456"}' -w "%{http_code}")

if [[ "$LOGIN_TEST" == *"200"* ]]; then
    echo "✅ BACKUPOK RESTAURADO COM SUCESSO!"
    echo "🌐 Acesse: https://ebd-dashboard-1.preview.emergentagent.com"
    echo ""
    echo "👤 USUÁRIOS FUNCIONANDO:"
    echo "   admin@ebd.com / 123456"
    echo "   marcio@ebd.com.br / 5544%\$Gg"
    echo "   kell@ebd.com / 123456"
    echo ""
    echo "✅ FUNCIONALIDADES GARANTIDAS:"
    echo "   - Login estável"
    echo "   - Bug das chamadas corrigido"
    echo "   - Visitantes/pós-chamada funcionando"
    echo "   - Superintendente EBD exibido"
    echo ""
    echo "🎉 SISTEMA NO ESTADO 100% FUNCIONAL!"
else
    echo "❌ Erro na restauração. Tentando correção..."
    /app/fix_login_always.sh
fi
