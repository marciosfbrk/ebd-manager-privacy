@echo off
echo ================================================
echo      EBD Manager - Parando Sistema
echo ================================================
echo.

echo 🛑 Parando processos do EBD Manager...

REM Parar processos Node (React)
echo    Parando Frontend React...
taskkill /F /IM node.exe 2>nul
if %errorlevel% equ 0 (
    echo ✅ Frontend parado
) else (
    echo ⚠️  Frontend não estava rodando
)

REM Parar processos Python (FastAPI)
echo    Parando Backend FastAPI...
taskkill /F /IM python.exe 2>nul
if %errorlevel% equ 0 (
    echo ✅ Backend parado
) else (
    echo ⚠️  Backend não estava rodando
)

REM Parar MongoDB (opcional - comentado para preservar dados)
REM echo    Parando MongoDB...
REM taskkill /F /IM mongod.exe 2>nul

REM Fechar janelas de comando abertas pelo sistema
echo    Fechando janelas do sistema...
taskkill /F /FI "WINDOWTITLE eq EBD Backend*" 2>nul
taskkill /F /FI "WINDOWTITLE eq EBD Frontend*" 2>nul

echo.
echo ================================================
echo ✅ Sistema parado com sucesso!
echo ================================================
echo.
echo 📝 Nota: MongoDB continua rodando para preservar dados
echo    Para parar também o MongoDB execute:
echo    taskkill /F /IM mongod.exe
echo.
echo 🚀 Para reiniciar execute: start_system.bat
echo.
pause