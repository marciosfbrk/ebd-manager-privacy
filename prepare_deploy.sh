#!/bin/bash

# Script para preparar o projeto para deploy
echo "🚀 Preparando projeto para deploy..."

# Verificar se estamos na pasta correta
if [ ! -f "backend/server.py" ]; then
    echo "❌ Execute este script na pasta raiz do projeto!"
    exit 1
fi

# Criar .gitignore se não existir
if [ ! -f ".gitignore" ]; then
    echo "📝 Criando .gitignore..."
    cat > .gitignore << 'EOF'
# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Build files
build/
dist/
*.egg-info/

# Logs
*.log
logs/

# Database
*.db
*.sqlite3

# Backup files
*.backup
database_export.json

# Temporary files
*.tmp
*.temp
EOF
fi

# Criar structure para GitHub
echo "📁 Criando estrutura para GitHub..."
mkdir -p deploy-ready
cp -r backend deploy-ready/
cp -r frontend deploy-ready/
cp vercel.json deploy-ready/
cp DEPLOY_GUIDE.md deploy-ready/
cp migrate_data.py deploy-ready/

# Limpar arquivos desnecessários
echo "🧹 Limpando arquivos desnecessários..."
rm -f deploy-ready/backend/.env
rm -f deploy-ready/frontend/.env
rm -rf deploy-ready/frontend/node_modules
rm -rf deploy-ready/backend/__pycache__

# Criar README para deploy
cat > deploy-ready/README.md << 'EOF'
# EBD Manager - Sistema de Gerenciamento de Escola Bíblica Dominical

Sistema completo para gerenciamento de EBD com React + FastAPI + MongoDB.

## 🚀 Deploy Rápido

### Backend (Railway)
1. Faça fork deste repositório
2. Conecte ao Railway
3. Configure as variáveis de ambiente
4. Deploy automático!

### Frontend (Vercel)
1. Conecte ao Vercel
2. Configure variáveis de ambiente
3. Deploy automático!

## 📋 Variáveis de Ambiente

### Backend (Railway)
```
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/ebd_manager
DB_NAME=ebd_manager
```

### Frontend (Vercel)
```
REACT_APP_BACKEND_URL=https://seu-backend.up.railway.app
```

## 📖 Guia Completo
Veja `DEPLOY_GUIDE.md` para instruções detalhadas.

## 🔧 Funcionalidades
- ✅ Gerenciamento de alunos e turmas
- ✅ Chamadas dominicais
- ✅ Relatórios detalhados
- ✅ Rankings por presença
- ✅ Sistema de usuários
- ✅ Interface mobile responsiva

## 👥 Usuários Padrão
- **Admin**: admin@ebd.com / 123456
- **Professor**: kell2@ebd.com / 123456
EOF

echo "✅ Projeto preparado para deploy!"
echo "📁 Arquivos em: deploy-ready/"
echo "📖 Guia completo: DEPLOY_GUIDE.md"