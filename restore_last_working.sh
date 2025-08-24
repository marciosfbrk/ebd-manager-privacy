#!/bin/bash

# Script de Restauração Rápida - Volta ao último estado funcionando

echo "🚨 RESTAURAÇÃO DE EMERGÊNCIA ATIVADA!"
echo "🔄 Procurando último backup..."

# Encontrar o backup mais recente
LAST_BACKUP=$(ls -t /app/backups_deploy/ | head -n 1)

if [ -z "$LAST_BACKUP" ]; then
    echo "❌ Nenhum backup encontrado!"
    exit 1
fi

BACKUP_PATH="/app/backups_deploy/$LAST_BACKUP"
echo "📂 Usando backup: $BACKUP_PATH"

# Executar restauração
if [ -f "$BACKUP_PATH/restore.sh" ]; then
    echo "🚀 Executando restauração..."
    bash "$BACKUP_PATH/restore.sh"
    echo ""
    echo "🎉 EMERGÊNCIA RESOLVIDA!"
    echo "✅ Sistema restaurado para estado funcionando!"
    echo "🌐 Teste em: https://ebd-dashboard-1.preview.emergentagent.com"
else
    echo "❌ Script de restauração não encontrado!"
    exit 1
fi