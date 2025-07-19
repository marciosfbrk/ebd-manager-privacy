@echo off
echo ================================================
echo    EBD Manager - Verificacao do Sistema
echo ================================================
echo.

REM Verificar Python
echo 🐍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    python --version
    echo ✅ Python OK
) else (
    echo ❌ Python não encontrado
    echo    Instale em: https://www.python.org/downloads/
)
echo.

REM Verificar Node.js
echo 📦 Verificando Node.js...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    node --version
    npm --version
    echo ✅ Node.js OK
) else (
    echo ❌ Node.js não encontrado
    echo    Instale em: https://nodejs.org/
)
echo.

REM Verificar MongoDB
echo 🗄️  Verificando MongoDB...
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if %errorlevel% equ 0 (
    echo ✅ MongoDB rodando
) else (
    echo ❌ MongoDB não está rodando
    echo    Execute: start_system.bat
)
echo.

REM Verificar Backend
echo 🔙 Verificando Backend...
curl -s http://localhost:8000/api/turmas >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend rodando (http://localhost:8000)
) else (
    echo ❌ Backend não está respondendo
    echo    Execute: start_system.bat
)
echo.

REM Verificar Frontend
echo 🔜 Verificando Frontend...
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend rodando (http://localhost:3000)
) else (
    echo ❌ Frontend não está respondendo
    echo    Execute: start_system.bat
)
echo.

REM Verificar estrutura de pastas
echo 📁 Verificando estrutura...
if exist "backend\venv" (echo ✅ Ambiente Python OK) else (echo ❌ Ambiente Python não encontrado)
if exist "frontend\node_modules" (echo ✅ Node modules OK) else (echo ❌ Node modules não encontrados)
if exist "data" (echo ✅ Pasta de dados OK) else (echo ❌ Pasta de dados não encontrada)
if exist "logs" (echo ✅ Pasta de logs OK) else (echo ❌ Pasta de logs não encontrada)
echo.

REM Verificar logs recentes
echo 📋 Logs recentes...
if exist "logs\backend.log" (
    echo Backend log:
    tail -n 3 logs\backend.log 2>nul || echo    (tail não disponível - use: type logs\backend.log)
) else (
    echo    Backend log não encontrado
)

if exist "logs\frontend.log" (
    echo Frontend log:
    tail -n 3 logs\frontend.log 2>nul || echo    (tail não disponível - use: type logs\frontend.log)
) else (
    echo    Frontend log não encontrado
)
echo.

REM Status geral
echo ================================================
echo 🎯 RESUMO DO STATUS
echo ================================================

REM Contar processos ativos
set /a processes=0
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if %errorlevel% equ 0 set /a processes+=1

tasklist /FI "IMAGENAME eq node.exe" 2>NUL | find /I /N "node.exe">NUL
if %errorlevel% equ 0 set /a processes+=1

tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if %errorlevel% equ 0 set /a processes+=1

if %processes% geq 3 (
    echo ✅ Sistema FUNCIONANDO (%processes%/3 processos ativos)
    echo    Frontend: http://localhost:3000
    echo    Backend:  http://localhost:8000
) else (
    echo ⚠️  Sistema PARCIALMENTE ATIVO (%processes%/3 processos)
    echo    Execute: start_system.bat
)
echo.
pause