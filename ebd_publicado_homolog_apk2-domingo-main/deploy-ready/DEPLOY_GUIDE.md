# 🚀 Guia de Deploy: EBD Manager - Railway + Vercel

## 📋 Pré-requisitos
- [x] Conta GitHub (para conectar com os serviços)
- [x] Conta Vercel (você já tem)
- [ ] Conta Railway (criar em railway.app)
- [ ] Conta MongoDB Atlas (criar em cloud.mongodb.com)

## 🗂️ Estrutura do Projeto
```
projeto/
├── backend/               # FastAPI (vai para Railway)
├── frontend/              # React (vai para Vercel)
├── database_export.json   # Seus dados exportados
├── migrate_data.py        # Script de migração
└── vercel.json           # Config do Vercel
```

---

## 🎯 PASSO 1: Configurar MongoDB Atlas

### 1.1 Criar conta e cluster
1. Acesse: https://cloud.mongodb.com/
2. Clique em "Start Free"
3. Crie sua conta
4. Crie um cluster gratuito (M0)
5. Escolha região: "AWS / São Paulo" (mais próximo)

### 1.2 Configurar acesso
1. Database Access → Add Database User
   - Username: `ebd_user`
   - Password: `gerar password forte`
   - Roles: `Read and write to any database`

2. Network Access → Add IP Address
   - `0.0.0.0/0` (permitir de qualquer lugar)

### 1.3 Obter connection string
1. Clusters → Connect → Connect your application
2. Copie a string que vai parecer com:
   ```
   mongodb+srv://ebd_user:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
3. Substitua `<password>` pela senha real
4. Adicione `/ebd_manager` no final antes do `?`

---

## 🎯 PASSO 2: Configurar Railway (Backend)

### 2.1 Criar conta
1. Acesse: https://railway.app/
2. Clique em "Login" → "Login with GitHub"
3. Autorize o Railway

### 2.2 Fazer deploy do backend
1. No Railway, clique em "New Project"
2. Selecione "Deploy from GitHub repo"
3. Escolha seu repositório
4. Clique em "Deploy Now"

### 2.3 Configurar variáveis de ambiente
1. Vá para o projeto no Railway
2. Clique na aba "Variables"
3. Adicione as variáveis:
   ```
   MONGO_URL=mongodb+srv://ebd_user:SUA_SENHA@cluster0.xxxxx.mongodb.net/ebd_manager?retryWrites=true&w=majority
   DB_NAME=ebd_manager
   ```

### 2.4 Obter URL do backend
1. Na aba "Settings" → "Domains"
2. Clique em "Generate Domain"
3. Copie a URL (ex: `https://ebd-manager-backend-production.up.railway.app`)

---

## 🎯 PASSO 3: Configurar Vercel (Frontend)

### 3.1 Configurar variáveis de ambiente
1. No Vercel Dashboard, vá para seu projeto
2. Settings → Environment Variables
3. Adicione:
   ```
   REACT_APP_BACKEND_URL=https://SUA_URL_DO_RAILWAY
   ```

### 3.2 Fazer deploy
1. No Vercel, clique em "New Project"
2. Importe o repositório do GitHub
3. Configure:
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `build`

---

## 🎯 PASSO 4: Migrar Dados

### 4.1 Importar dados para MongoDB Atlas
1. No seu computador, execute:
   ```bash
   MONGO_URL="mongodb+srv://ebd_user:SUA_SENHA@cluster0.xxxxx.mongodb.net/ebd_manager?retryWrites=true&w=majority" python migrate_data.py import
   ```

### 4.2 Verificar dados
1. Acesse MongoDB Atlas
2. Database → Browse Collections
3. Verifique se os dados estão lá

---

## 🎯 PASSO 5: Testar Sistema

### 5.1 URLs dos serviços
- **Frontend**: `https://seu-projeto.vercel.app`
- **Backend**: `https://seu-projeto.up.railway.app`
- **Database**: MongoDB Atlas

### 5.2 Testar login
- **Admin**: `admin@ebd.com` / `123456`
- **Usuário**: `kell2@ebd.com` / `123456`

---

## 🔧 Troubleshooting

### Erro de CORS
Se der erro de CORS, adicione no Railway:
```
CORS_ORIGINS=https://seu-projeto.vercel.app
```

### Backend não conecta
Verifique:
1. MONGO_URL está correto
2. IP 0.0.0.0/0 está liberado no MongoDB
3. Variáveis de ambiente estão salvas

### Frontend não encontra backend
Verifique:
1. REACT_APP_BACKEND_URL está correto
2. URL do Railway está ativa
3. Rebuild do Vercel

---

## 📊 Resumo dos Custos

| Serviço | Plano | Custo |
|---------|-------|-------|
| MongoDB Atlas | M0 (512MB) | **Gratuito** |
| Railway | 500h/mês | **Gratuito** |
| Vercel | Projetos ilimitados | **Gratuito** |
| **TOTAL** | | **R$ 0,00** |

---

## 🎉 Resultado Final

Você terá:
- ✅ **Frontend rápido** no Vercel (CDN global)
- ✅ **Backend robusto** no Railway (sempre online)
- ✅ **Banco seguro** no MongoDB Atlas (backup automático)
- ✅ **SSL automático** em todos os serviços
- ✅ **Domínio personalizado** (opcional)

**Tudo funcionando 100% gratuito!** 🚀