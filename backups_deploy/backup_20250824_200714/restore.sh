#!/bin/bash
echo "🔄 RESTAURANDO CONFIGURAÇÕES..."

# Parar serviços
sudo supervisorctl stop frontend backend

# Restaurar arquivos
cp "/app/backups_deploy/backup_20250824_200714/frontend.env" /app/frontend/.env
cp "/app/backups_deploy/backup_20250824_200714/frontend.env.production" /app/frontend/.env.production
cp "/app/backups_deploy/backup_20250824_200714/backend.env" /app/backend/.env
cp "/app/backups_deploy/backup_20250824_200714/App.js" /app/frontend/src/App.js
cp "/app/backups_deploy/backup_20250824_200714/server.py" /app/backend/server.py

# Limpar cache
cd /app/frontend && rm -rf build && rm -rf node_modules/.cache

# Reiniciar serviços
sudo supervisorctl start frontend backend

echo "✅ RESTAURAÇÃO COMPLETA!"
echo "🎉 Sistema voltou ao estado funcional!"
