@echo off
echo ================================================
echo     EBD Manager - Verificação de Status Local
echo ================================================
echo.

echo 🔍 Verificando status de todos os serviços...
echo.

REM Verificar MongoDB
echo 🗄️  MongoDB:
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if %errorlevel% equ 0 (
    echo    ✅ Rodando
    echo    📁 Dados: %CD%\data
    echo    📝 Log: %CD%\logs\mongodb.log
) else (
    echo    ❌ Parado
    echo    💡 Execute: mongod --dbpath data
)

echo.

REM Verificar Backend Python
echo 🐍 Backend Python:
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if %errorlevel% equ 0 (
    echo    ✅ Rodando
    echo    🔗 URL: http://localhost:8000
) else (
    echo    ❌ Parado
    echo    💡 Execute: start_system_local.bat
)

echo.

REM Verificar Frontend React
echo ⚛️  Frontend React:
tasklist /FI "IMAGENAME eq node.exe" 2>NUL | find /I /N "node.exe">NUL
if %errorlevel% equ 0 (
    echo    ✅ Rodando  
    echo    🌐 URL: http://localhost:3000
) else (
    echo    ❌ Parado
    echo    💡 Execute: start_system_local.bat
)

echo.
echo 🌐 Testando conectividade...

REM Testar Backend API
echo.
echo 🔗 Backend API:
curl -s -o nul -w "%%{http_code}" http://localhost:8000/api/ >temp_backend.txt 2>nul
set /p backend_response=<temp_backend.txt
del temp_backend.txt 2>nul

if "%backend_response%"=="200" (
    echo    ✅ API respondendo (200 OK)
) else (
    echo    ❌ API não responde (código: %backend_response%)
)

REM Testar Frontend
echo.
echo 🌐 Frontend:
curl -s -o nul -w "%%{http_code}" http://localhost:3000 >temp_frontend.txt 2>nul
set /p frontend_response=<temp_frontend.txt
del temp_frontend.txt 2>nul

if "%frontend_response%"=="200" (
    echo    ✅ Interface respondendo (200 OK)
) else (
    echo    ❌ Interface não responde (código: %frontend_response%)
)

echo.
echo 📊 Verificando dados...

REM Verificar se backup existe
if exist "backup_ebd_completo_20250803_015454.json" (
    echo    ✅ Backup disponível (0.45 MB)
) else (
    echo    ❌ Backup não encontrado
)

REM Verificar estrutura de pastas
echo.
echo 📁 Estrutura de pastas:
if exist "data" (
    echo    ✅ data\ - Dados MongoDB
) else (
    echo    ❌ data\ - Pasta não encontrada
)

if exist "logs" (
    echo    ✅ logs\ - Arquivos de log
) else (
    echo    ❌ logs\ - Pasta não encontrada  
)

if exist "backend\venv" (
    echo    ✅ backend\venv\ - Ambiente Python
) else (
    echo    ❌ backend\venv\ - Não encontrado
)

if exist "frontend\node_modules" (
    echo    ✅ frontend\node_modules\ - Dependências React
) else (
    echo    ❌ frontend\node_modules\ - Não encontradas
)

echo.
echo ================================================
echo ✅ Verificação concluída!
echo ================================================
echo.
echo 🎯 Se todos os serviços estiverem rodando, acesse:
echo    🌐 Sistema Principal: http://localhost:3000
echo    🔧 API Documentation: http://localhost:8000/docs
echo.
echo 👤 Logins disponíveis:
echo    Admin: admin@ebd.com / 123456
echo    Prof:  kell@ebd.com / 123456  
echo.
echo 🚀 Para iniciar tudo: start_system_local.bat
echo 🛑 Para parar tudo: stop_system_local.bat
echo.
pause