@echo off
echo ================================================
echo      EBD Manager - Parando Sistema Local
echo ================================================
echo.

echo 🛑 Parando processos do EBD Manager...

REM Parar processos Node.js (Frontend)
echo    Parando Frontend React...
taskkill /F /IM node.exe 2>nul
if %errorlevel% equ 0 (
    echo    ✅ Frontend parado
) else (
    echo    ⚠️  Frontend já estava parado
)

REM Parar processos Python (Backend)
echo    Parando Backend Python...
taskkill /F /IM python.exe 2>nul
if %errorlevel% equ 0 (
    echo    ✅ Backend parado
) else (
    echo    ⚠️  Backend já estava parado
)

REM Parar MongoDB (opcional)
echo.
set /p stop_mongo="🗄️  Parar MongoDB também? (s/n): "
if /i "%stop_mongo%"=="s" (
    echo    Parando MongoDB...
    taskkill /F /IM mongod.exe 2>nul
    if %errorlevel% equ 0 (
        echo    ✅ MongoDB parado
    ) else (
        echo    ⚠️  MongoDB já estava parado
    )
) else (
    echo    📊 MongoDB continuará rodando
)

echo.
echo ================================================
echo ✅ Sistema parado com sucesso!
echo ================================================
echo.
echo 🚀 Para reiniciar: start_system_local.bat
echo 🔧 Para verificar: check_system_local.bat
echo.
pause