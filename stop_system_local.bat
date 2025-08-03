@echo off
echo ================================================
echo        EBD Manager - Parar Sistema Local
echo ================================================
echo.

echo 🛑 Parando todos os serviços do EBD Manager...
echo.

REM Parar Frontend React
echo ⚛️  Parando Frontend React...
taskkill /F /IM node.exe 2>nul
if %errorlevel% equ 0 (
    echo    ✅ Frontend parado
) else (
    echo    ⚠️  Frontend já estava parado
)

REM Parar Backend Python  
echo 🐍 Parando Backend Python...
taskkill /F /IM python.exe 2>nul
if %errorlevel% equ 0 (
    echo    ✅ Backend parado
) else (
    echo    ⚠️  Backend já estava parado
)

REM Perguntar sobre MongoDB
echo.
set /p stop_mongo="🗄️  Parar MongoDB também? (s/n): "
if /i "%stop_mongo%"=="s" (
    echo    🛑 Parando MongoDB...
    taskkill /F /IM mongod.exe 2>nul
    if %errorlevel% equ 0 (
        echo    ✅ MongoDB parado
    ) else (
        echo    ⚠️  MongoDB já estava parado
    )
) else (
    echo    📊 MongoDB continuará rodando (recomendado)
)

echo.
echo ================================================
echo ✅ Sistema parado com sucesso!
echo ================================================
echo.
echo 🔄 Para reiniciar: start_system_local.bat
echo 🔧 Para verificar: check_status_local.bat  
echo 📊 Para resetar: python restore_backup.py backup_ebd_completo_20250803_015454.json
echo.
echo 💡 Dica: Deixe o MongoDB rodando para inicialização mais rápida
echo.
pause