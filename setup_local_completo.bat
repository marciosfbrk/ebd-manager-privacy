@echo off
echo ================================================
echo  EBD Manager - Setup Completo Local
echo ================================================
echo.

echo 📋 Preparando ambiente para instalacao completa
echo    Este script configura todos os arquivos necessarios
echo.

REM Verificar se estrutura básica existe
echo 📁 Criando estrutura de pastas...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "backups" mkdir backups

REM Configurar Backend
echo 🔧 Configurando Backend...
cd backend
if not exist ".env" (
    echo MONGO_URL=mongodb://localhost:27017 > .env
    echo DB_NAME=ebd_local >> .env
    echo # Configuracao local >> .env
    echo # Todos os dados serao importados automaticamente >> .env
)
cd ..

REM Configurar Frontend  
echo 🔧 Configurando Frontend...
cd frontend
if not exist ".env" (
    echo REACT_APP_BACKEND_URL=http://localhost:8000 > .env
    echo # Configuracao local >> .env
    echo # Backend rodara na porta 8000 >> .env
)
cd ..

echo.
echo ================================================
echo ✅ Setup inicial concluído!
echo ================================================
echo.
echo 🚀 Próximo passo: execute install_completo.bat
echo    Isso instalará todas as dependências e importará
echo    os dados completos (usuários, turmas, alunos, revistas)
echo.
pause