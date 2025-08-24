#!/bin/bash

# Script de Backup Automático Antes de Deploy
# Evita sofrimento de perder configurações funcionais

echo "🔄 INICIANDO BACKUP AUTOMÁTICO ANTES DO DEPLOY..."

# Criar diretório de backup com timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/app/backups_deploy/backup_$TIMESTAMP"
mkdir -p "$BACKUP_DIR"

echo "📂 Criando backup em: $BACKUP_DIR"

# Backup dos arquivos críticos
echo "📋 Fazendo backup de arquivos críticos..."
cp -r /app/frontend/.env "$BACKUP_DIR/frontend.env"
cp -r /app/frontend/.env.production "$BACKUP_DIR/frontend.env.production"
cp -r /app/backend/.env "$BACKUP_DIR/backend.env"
cp -r /app/frontend/src/App.js "$BACKUP_DIR/App.js"
cp -r /app/backend/server.py "$BACKUP_DIR/server.py"

# Backup da base de dados
echo "💾 Fazendo backup da base de dados..."
curl -s http://localhost:8001/api/backup/generate > "$BACKUP_DIR/database_backup.json"

# Criar arquivo de restore rápido
cat > "$BACKUP_DIR/restore.sh" << EOF
#!/bin/bash
echo "🔄 RESTAURANDO CONFIGURAÇÕES..."

# Parar serviços
sudo supervisorctl stop frontend backend

# Restaurar arquivos
cp "$BACKUP_DIR/frontend.env" /app/frontend/.env
cp "$BACKUP_DIR/frontend.env.production" /app/frontend/.env.production
cp "$BACKUP_DIR/backend.env" /app/backend/.env
cp "$BACKUP_DIR/App.js" /app/frontend/src/App.js
cp "$BACKUP_DIR/server.py" /app/backend/server.py

# Limpar cache
cd /app/frontend && rm -rf build && rm -rf node_modules/.cache

# Reiniciar serviços
sudo supervisorctl start frontend backend

echo "✅ RESTAURAÇÃO COMPLETA!"
echo "🎉 Sistema voltou ao estado funcional!"
EOF

chmod +x "$BACKUP_DIR/restore.sh"

echo "✅ BACKUP COMPLETO!"
echo "📍 Para restaurar este estado:"
echo "   bash $BACKUP_DIR/restore.sh"
echo ""
echo "🛡️ AGORA VOCÊ PODE FAZER DEPLOY COM SEGURANÇA!"