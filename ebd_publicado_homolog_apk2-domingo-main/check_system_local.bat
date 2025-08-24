@echo off
echo ================================================
echo    EBD Manager - Verificacao do Sistema Local
echo ================================================
echo.

echo 🔍 Verificando status dos serviços...
echo.

REM Verificar MongoDB
echo 🗄️  MongoDB:
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if %errorlevel% equ 0 (
    echo    ✅ Rodando
) else (
    echo    ❌ Parado
)

REM Verificar Backend Python
echo 🐍 Backend Python:
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if %errorlevel% equ 0 (
    echo    ✅ Rodando
) else (
    echo    ❌ Parado
)

REM Verificar Frontend Node
echo ⚛️  Frontend React:
tasklist /FI "IMAGENAME eq node.exe" 2>NUL | find /I /N "node.exe">NUL
if %errorlevel% equ 0 (
    echo    ✅ Rodando
) else (
    echo    ❌ Parado
)

echo.
echo 🌐 Testando conectividade...

REM Testar Backend
echo 🔗 Backend API:
curl -s -o nul -w "%%{http_code}" http://localhost:8000/api/ >temp_response.txt 2>nul
set /p response=<temp_response.txt
del temp_response.txt 2>nul
if "%response%"=="200" (
    echo    ✅ Respondendo (200 OK)
) else (
    echo    ❌ Não responde ou erro (%response%)
)

REM Testar Frontend
echo 🌐 Frontend:
curl -s -o nul -w "%%{http_code}" http://localhost:3000 >temp_response2.txt 2>nul
set /p response2=<temp_response2.txt
del temp_response2.txt 2>nul
if "%response2%"=="200" (
    echo    ✅ Respondendo (200 OK)
) else (
    echo    ❌ Não responde ou erro (%response2%)
)

echo.
echo 📊 Status das pastas:
if exist "data" (
    echo    ✅ Pasta data\ existe
) else (
    echo    ❌ Pasta data\ não encontrada
)

if exist "logs" (
    echo    ✅ Pasta logs\ existe
) else (
    echo    ❌ Pasta logs\ não encontrada
)

if exist "backend\venv" (
    echo    ✅ Ambiente virtual Python existe
) else (
    echo    ❌ Ambiente virtual não encontrado
)

if exist "frontend\node_modules" (
    echo    ✅ Dependências Node.js existem
) else (
    echo    ❌ Dependências Node.js não encontradas
)

echo.
echo 📋 Logs recentes (últimas 5 linhas):
if exist "logs\mongodb.log" (
    echo.
    echo 🗄️  MongoDB:
    powershell "Get-Content 'logs\mongodb.log' -Tail 3"
)

echo.
echo ================================================
echo ✅ Verificação concluída!
echo ================================================
echo.
echo 🚀 Se tudo estiver OK, acesse:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:8000
echo.
pause