@echo off
echo ========================================
echo   INSTALACAO EBD MANAGER - BACKEND
echo ========================================
echo.

echo 1. Instalando dependencias do Python...
cd backend
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependencias Python
    echo Verifique se Python esta instalado e no PATH
    pause
    exit /b 1
)

echo.
echo 2. Verificando arquivo .env...
if not exist .env (
    echo Criando arquivo .env...
    echo MONGO_URL=mongodb://localhost:27017> .env
    echo DB_NAME=ebd_manager>> .env
    echo REACT_APP_BACKEND_URL=http://localhost:8001>> .env
)

echo.
echo ========================================
echo   INSTALACAO EBD MANAGER - FRONTEND  
echo ========================================
echo.

echo 3. Instalando dependencias do React...
cd ..\frontend
call npm install
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependencias Node.js
    echo Verifique se Node.js esta instalado
    pause
    exit /b 1
)

echo.
echo 4. Verificando arquivo .env frontend...
if not exist .env (
    echo Criando arquivo .env frontend...
    echo REACT_APP_BACKEND_URL=http://localhost:8001> .env
)

cd ..

echo.
echo ========================================
echo   IMPORTANDO DADOS COMPLETOS
echo ========================================
echo.

echo 5. Restaurando backup completo...
python restore_backup.py
if %errorlevel% neq 0 (
    echo Aviso: Erro ao restaurar backup, mas continuando...
)

echo.
echo ✅ INSTALACAO CONCLUIDA COM SUCESSO!
echo.
echo Para iniciar o sistema:
echo 1. Abra um terminal e execute: python backend/server.py
echo 2. Abra outro terminal e execute: cd frontend && npm start
echo 3. Acesse: http://localhost:3000
echo.
echo Login inicial:
echo Email: admin@ebd.com
echo Senha: 123456
echo.
pause