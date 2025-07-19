# 🏠 EBD Manager - Instalação Local (Windows)

## 📋 Pré-requisitos

### Instalar as seguintes ferramenias:

1. **Python 3.9+**
   - Download: https://www.python.org/downloads/
   - ✅ Marcar "Add Python to PATH" durante instalação

2. **Node.js 18+**
   - Download: https://nodejs.org/
   - Incluí npm automaticamente

3. **MongoDB Community**
   - Download: https://www.mongodb.com/try/download/community
   - Ou usar MongoDB Compass (interface gráfica)

4. **Git**
   - Download: https://git-scm.com/download/win

## 🚀 Instalação Rápida

### 1. Baixar o projeto
```cmd
cd C:\
git clone https://github.com/marciosfbrk/Ebd-v6.git
cd Ebd-v6
```

### 2. Executar instalação automática
```cmd
# Executar script de instalação
install.bat

# OU manualmente:
setup_local.bat
```

### 3. Iniciar sistema
```cmd
start_system.bat
```

### 4. Acessar sistema
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **MongoDB**: mongodb://localhost:27017

## 📁 Estrutura após instalação

```
C:\Ebd-v4\
├── backend\
│   ├── venv\              # Ambiente Python virtual
│   ├── server.py          # Aplicação FastAPI
│   └── .env               # Configurações locais
├── frontend\
│   ├── node_modules\      # Dependências Node
│   ├── src\               # Código React
│   └── .env               # Configurações locais
├── data\                  # Banco MongoDB local
├── logs\                  # Logs do sistema
├── scripts\               # Scripts de automação
├── install.bat            # Instalador automático
├── start_system.bat       # Iniciar sistema
└── stop_system.bat        # Parar sistema
```

## 👥 Usuários padrão
- **Admin**: admin@ebd.com / 123456
- **Professor**: kell2@ebd.com / 123456

## 🔧 Comandos úteis

```cmd
# Iniciar apenas backend
cd backend
python -m uvicorn server:app --reload

# Iniciar apenas frontend
cd frontend
npm start

# Iniciar MongoDB
mongod --dbpath C:\Ebd-v4\data

# Ver logs
type logs\backend.log
type logs\frontend.log
```

## 🛠️ Troubleshooting

### Python não encontrado
```cmd
python --version
# Se não funcionar, reinstalar Python marcando "Add to PATH"
```

### Node não encontrado
```cmd
node --version
npm --version
# Se não funcionar, reinstalar Node.js
```

### MongoDB não conecta
- Verificar se serviço está rodando
- Verificar pasta data\ existe
- Usar MongoDB Compass para conectar

### Porta ocupada
- Frontend padrão: 3000
- Backend padrão: 8000
- Alterar em .env se necessário

## 📞 Suporte

Em caso de problemas:
1. Verificar logs em `logs\`
2. Executar `check_system.bat`
3. Consultar README.md

---

**🎯 Em 5 minutos você terá o sistema rodando localmente!**