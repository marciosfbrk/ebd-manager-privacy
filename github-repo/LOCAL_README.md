# 🏠 EBD Manager - Versão Local

## 🎯 Instalação Rápida (Windows)

### 1. **Baixar projeto**
```cmd
cd C:\
git clone https://github.com/marciosfbrk/Ebd-v6.git
cd Ebd-v6
```

### 2. **Executar instalação**
```cmd
install.bat
```

### 3. **Iniciar sistema**
```cmd
start_system.bat
```

### 4. **Acessar**
- **Sistema**: http://localhost:3000
- **API**: http://localhost:8000

## 📋 Scripts Disponíveis

| Script | Função |
|--------|--------|
| `install.bat` | Instalação completa |
| `start_system.bat` | Iniciar sistema |
| `stop_system.bat` | Parar sistema |  
| `check_system.bat` | Verificar status |
| `setup_local.bat` | Configuração inicial |

## 🛠️ Pré-requisitos

- **Python 3.9+**: https://www.python.org/downloads/
- **Node.js 18+**: https://nodejs.org/
- **MongoDB**: https://www.mongodb.com/try/download/community
- **Git**: https://git-scm.com/download/win

## 👤 Usuários Padrão

- **Admin**: admin@ebd.com / 123456  
- **Professor**: kell2@ebd.com / 123456

## 📁 Estrutura Local

```
C:\Ebd-v6\
├── backend\          # FastAPI + Python
├── frontend\         # React + Node.js
├── data\            # MongoDB local
├── logs\            # Logs do sistema
├── scripts\         # Scripts Windows
└── *.bat           # Executáveis
```

## 🔧 Desenvolvimento

### Backend
```cmd
cd backend
venv\Scripts\activate
python -m uvicorn server:app --reload
```

### Frontend
```cmd
cd frontend  
npm start
```

### MongoDB
```cmd
mongod --dbpath C:\Ebd-v6\data
```

## 📊 Dados Inclusos

- **11 turmas** da igreja
- **242 alunos** cadastrados
- **Usuários** configurados
- **Sistema completo** funcionando

---

**🚀 Em 5 minutos você terá o EBD Manager rodando localmente!**