# 🚀 Guia Completo: Instalar EBD Manager no Seu Notebook

## 📋 PRÉ-REQUISITOS

### 1. Node.js
- Baixar em: https://nodejs.org/
- Instalar versão LTS
- Testar: `node --version`

### 2. Python  
- Baixar em: https://python.org/downloads/
- Instalar Python 3.8+
- ✅ MARCAR "Add to PATH"
- Testar: `python --version`

### 3. Git
- Baixar em: https://git-scm.com/
- Instalar com configurações padrão

### 4. MongoDB
**Opção A - Local:**
- Baixar: https://www.mongodb.com/try/download/community
- Instalar e iniciar serviço

**Opção B - Cloud (Recomendado):**
- Criar conta: https://cloud.mongodb.com/
- Criar cluster gratuito
- Copiar string de conexão

---

## 📥 BAIXAR O SISTEMA

### Método 1: Download ZIP
1. Baixar este projeto como ZIP
2. Extrair em uma pasta (ex: `C:\EBD_Manager\`)

### Método 2: Git Clone (se tiver Git)
```bash
git clone [URL_DO_REPOSITORIO] EBD_Manager
cd EBD_Manager
```

---

## ⚙️ CONFIGURAÇÃO

### 1. Configurar Backend
```bash
cd backend
```

**Criar arquivo `.env`:**
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=ebd_manager
```

**Se usar MongoDB Cloud, alterar MONGO_URL:**
```
MONGO_URL=sua_string_de_conexao_aqui
DB_NAME=ebd_manager
```

### 2. Configurar Frontend
```bash
cd frontend
```

**Criar arquivo `.env`:**
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

---

## 📦 INSTALAR DEPENDÊNCIAS

### Backend (FastAPI)
```bash
cd backend
python -m pip install -r requirements.txt
```

### Frontend (React)
```bash
cd frontend
npm install
```

---

## 🗄️ IMPORTAR DADOS

### 1. Restaurar Backup Completo
```bash
python restore_backup.py
```

### 2. Importar Dados de Chamada (se necessário)
```bash
python import_genesis.py
python import_primarios.py
python import_juniores.py
python import_pre_adolescentes.py
python import_adolescentes.py
python import_jovens.py
python import_dorcas.py
python import_ebenezer.py
python import_soldados.py
```

---

## 🚀 EXECUTAR O SISTEMA

### Terminal 1 - Backend
```bash
cd backend
python server.py
```
**Deve aparecer:** `Uvicorn running on http://0.0.0.0:8001`

### Terminal 2 - Frontend  
```bash
cd frontend
npm start
```
**Deve abrir:** `http://localhost:3000`

---

## 🔑 LOGIN INICIAL

**Admin:**
- Email: `admin@ebd.com`
- Senha: `123456`

**Professor:**
- Email: `professor@ebd.com` 
- Senha: `123456`

⚠️ **ALTERE AS SENHAS** após primeiro login!

---

## 🔧 COMANDOS ÚTEIS

### Parar os Serviços
- Backend: `Ctrl+C` no terminal
- Frontend: `Ctrl+C` no terminal

### Verificar se está Funcionando
- Backend: http://localhost:8001/docs
- Frontend: http://localhost:3000

### Reinstalar Dependências (se der erro)
```bash
# Backend
cd backend
pip install -r requirements.txt --force-reinstall

# Frontend  
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## ❓ PROBLEMAS COMUNS

### Erro: "python não encontrado"
- Reinstalar Python marcando "Add to PATH"
- Ou usar `python3` em vez de `python`

### Erro: "npm não encontrado"
- Reinstalar Node.js
- Reiniciar o terminal

### Erro: "MongoDB connection failed"
- Verificar se MongoDB está rodando
- Conferir string de conexão no `.env`

### Erro: "Port 3000 already in use"
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID [PID_NUMBER] /F

# Linux/Mac
lsof -i :3000
kill -9 [PID]
```

---

## 📞 SUPORTE

Se tiver problemas:
1. Verificar se todos os pré-requisitos estão instalados
2. Conferir arquivos `.env`
3. Reiniciar os terminais
4. Reinstalar dependências

**Sistema está pronto para uso com todos os dados incluídos!** 🎉