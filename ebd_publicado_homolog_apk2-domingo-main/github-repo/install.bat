@echo off
echo ================================================
echo    EBD Manager - Instalacao Automatica
echo ================================================
echo.

REM Verificar se Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python nao encontrado!
    echo    Baixe em: https://www.python.org/downloads/
    echo    Marque "Add Python to PATH" durante instalacao
    pause
    exit /b 1
)

REM Verificar se Node esta instalado
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js nao encontrado!
    echo    Baixe em: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Python e Node.js encontrados
echo.

REM Criar estrutura de pastas
echo 📁 Criando estrutura de pastas...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "scripts" mkdir scripts

REM Configurar Backend
echo 🐍 Configurando Backend Python...
cd backend

REM Criar ambiente virtual
if not exist "venv" (
    echo    Criando ambiente virtual...
    python -m venv venv
)

REM Ativar ambiente virtual e instalar dependencias
echo    Instalando dependencias...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

REM Criar .env local
echo    Configurando variaveis de ambiente...
if not exist ".env" (
    echo MONGO_URL=mongodb://localhost:27017 > .env
    echo DB_NAME=ebd_local >> .env
)

cd ..

REM Configurar Frontend
echo ⚛️  Configurando Frontend React...
cd frontend

REM Instalar dependencias Node
echo    Instalando dependencias Node...
call npm install

REM Criar .env local
echo    Configurando variaveis de ambiente...
if not exist ".env" (
    echo REACT_APP_BACKEND_URL=http://localhost:8000 > .env
)

cd ..

REM Importar dados iniciais
echo 📊 Importando dados iniciais...
python migrate_data.py

echo.
echo ================================================
echo ✅ Instalacao concluida com sucesso!
echo ================================================
echo.
echo 🚀 Para iniciar o sistema execute: start_system.bat
echo 🛑 Para parar o sistema execute: stop_system.bat
echo 🔧 Para verificar status execute: check_system.bat
echo.
echo URLs de acesso:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:8000
echo.
echo Usuarios padrão:
echo    Admin: admin@ebd.com / 123456
echo    Prof:  kell2@ebd.com / 123456
echo.
pause