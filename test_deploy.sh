#!/bin/bash

# Script de teste para verificar se o sistema está funcionando
echo "🧪 Testando EBD Manager..."

# Verificar se o arquivo de dados existe
if [ ! -f "database_export.json" ]; then
    echo "❌ Arquivo database_export.json não encontrado!"
    echo "Execute: python migrate_data.py"
    exit 1
fi

# Verificar estrutura do projeto
echo "📁 Verificando estrutura do projeto..."

if [ ! -f "backend/server.py" ]; then
    echo "❌ backend/server.py não encontrado!"
    exit 1
fi

if [ ! -f "frontend/package.json" ]; then
    echo "❌ frontend/package.json não encontrado!"
    exit 1
fi

if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ backend/requirements.txt não encontrado!"
    exit 1
fi

# Contar dados exportados
echo "📊 Verificando dados exportados..."
TURMAS=$(cat database_export.json | jq '.turmas | length')
ALUNOS=$(cat database_export.json | jq '.students | length')
USERS=$(cat database_export.json | jq '.users | length')

echo "   - Turmas: $TURMAS"
echo "   - Alunos: $ALUNOS"
echo "   - Usuários: $USERS"

if [ "$TURMAS" -eq 0 ]; then
    echo "⚠️  Nenhuma turma encontrada! Execute init-church-data primeiro."
fi

# Verificar se os arquivos de configuração existem
echo "⚙️  Verificando configurações..."

if [ -f "backend/.env.production" ]; then
    echo "✅ backend/.env.production encontrado"
else
    echo "❌ backend/.env.production não encontrado!"
fi

if [ -f "frontend/.env.production" ]; then
    echo "✅ frontend/.env.production encontrado"
else
    echo "❌ frontend/.env.production não encontrado!"
fi

if [ -f "DEPLOY_GUIDE.md" ]; then
    echo "✅ DEPLOY_GUIDE.md encontrado"
else
    echo "❌ DEPLOY_GUIDE.md não encontrado!"
fi

echo ""
echo "🎉 Verificação concluída!"
echo "📖 Consulte DEPLOY_GUIDE.md para instruções de deploy"
echo "🚀 Pronto para deploy no Railway + Vercel!"