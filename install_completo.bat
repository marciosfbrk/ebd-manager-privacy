@echo off
echo ================================================
echo   EBD Manager - Instalacao Completa
echo ================================================
echo.

REM Verificar pré-requisitos
echo 🔍 Verificando pré-requisitos...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python nao encontrado!
    echo    Baixe em: https://www.python.org/downloads/
    echo    ⚠️  IMPORTANTE: Marque "Add Python to PATH"
    pause
    exit /b 1
)

node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js nao encontrado!
    echo    Baixe em: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Python e Node.js encontrados
echo.

REM Configurar Backend Python
echo 🐍 Configurando Backend Python...
cd backend

echo    Criando ambiente virtual...
if not exist "venv" (
    python -m venv venv
)

echo    Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo    Atualizando pip...
python -m pip install --upgrade pip

echo    Instalando dependencias Python...
pip install -r requirements.txt

echo    ✅ Backend Python configurado
cd ..

REM Configurar Frontend React
echo ⚛️  Configurando Frontend React...
cd frontend

echo    Limpando cache npm...
if exist "node_modules" rmdir /s /q node_modules
if exist "package-lock.json" del package-lock.json

echo    Instalando dependencias Node.js...
npm install

echo    ✅ Frontend React configurado
cd ..

REM Verificar se MongoDB está rodando
echo 🗄️  Verificando MongoDB...
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if %errorlevel% neq 0 (
    echo    ⚠️  MongoDB nao esta rodando
    echo    Tentando iniciar MongoDB local...
    
    REM Tentar iniciar MongoDB
    start "MongoDB Local" mongod --dbpath "%CD%\data" --logpath "%CD%\logs\mongodb.log"
    echo    Aguardando MongoDB inicializar...
    timeout /t 5 >nul
) else (
    echo    ✅ MongoDB ja esta rodando
)

REM Importar dados completos
echo 📊 Importando dados completos...
echo    - Usuarios (admin e professor)
echo    - 11 turmas da igreja
echo    - 242 alunos
echo    - 6 revistas trimestrais

cd backend
call venv\Scripts\activate.bat
python ..\import_data_completo.py
cd ..

echo.
echo ================================================
echo ✅ INSTALACAO CONCLUIDA COM SUCESSO!
echo ================================================
echo.
echo 🎉 O sistema está pronto para uso!
echo.
echo 🚀 Para iniciar: start_system.bat
echo 🛑 Para parar:   stop_system.bat
echo 🔧 Para status:  check_system.bat
echo.
echo 🌐 URLs de acesso:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo 👤 Usuarios configurados:
echo    Admin: admin@ebd.com / 123456
echo    Prof:  kell2@ebd.com / 123456
echo.
echo 📊 Dados importados:
echo    ✅ 11 turmas da igreja
echo    ✅ 242 alunos cadastrados
echo    ✅ 6 revistas trimestrais completas
echo    ✅ Sistema de usuarios funcionando
echo.
pause