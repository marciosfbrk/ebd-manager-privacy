@echo off
echo ================================================
echo   EBD Manager - Setup Local Completo
echo   10 Turmas + 242 Alunos + Sistema Completo
echo ================================================
echo.

echo 📋 Preparando ambiente local...
echo.

REM Criar estrutura de pastas
echo 📁 Criando estrutura de pastas...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "backups" mkdir backups
if not exist "temp" mkdir temp

REM Verificar se arquivos essenciais existem
echo 🔍 Verificando arquivos essenciais...

if not exist "backend\server.py" (
    echo ❌ Arquivo backend\server.py não encontrado!
    echo    Certifique-se de ter baixado todos os arquivos do projeto.
    pause
    exit /b 1
)

if not exist "frontend\package.json" (
    echo ❌ Arquivo frontend\package.json não encontrado!
    echo    Certifique-se de ter baixado todos os arquivos do projeto.
    pause
    exit /b 1
)

if not exist "backup_ebd_completo_20250803_015454.json" (
    echo ❌ Backup não encontrado!
    echo    Certifique-se de ter o arquivo backup_ebd_completo_20250803_015454.json
    pause
    exit /b 1
)

echo ✅ Todos os arquivos essenciais encontrados!
echo.

REM Configurar Backend
echo 🔧 Configurando Backend...
cd backend
if exist ".env" del .env

echo # Configuracao Local - EBD Manager > .env
echo MONGO_URL=mongodb://localhost:27017 >> .env
echo DB_NAME=ebd_local >> .env
echo # Sistema com 10 turmas e 242 alunos >> .env

cd ..

REM Configurar Frontend  
echo 🔧 Configurando Frontend...
cd frontend
if exist ".env" del .env

echo # Configuracao Local - Frontend > .env
echo REACT_APP_BACKEND_URL=http://localhost:8000 >> .env
echo # Interface completa com todos os dados >> .env

cd ..

echo.
echo ================================================
echo ✅ Setup inicial concluído com sucesso!
echo ================================================
echo.
echo 🎯 Configuração realizada:
echo    ✅ Pastas criadas (data, logs, backups)
echo    ✅ Backend configurado (porta 8000)
echo    ✅ Frontend configurado (porta 3000) 
echo    ✅ MongoDB local configurado
echo    ✅ Backup validado e pronto
echo.
echo 🚀 Próximo passo: execute install_com_backup.bat
echo    Isso instalará tudo e carregará os dados completos!
echo.
pause