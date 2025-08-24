@echo off
echo ================================================
echo      EBD Manager - Iniciando Sistema
echo ================================================
echo.

REM Verificar se MongoDB está rodando
echo 🗄️  Verificando MongoDB...
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if %errorlevel% neq 0 (
    echo    Iniciando MongoDB local...
    start "MongoDB" mongod --dbpath "%CD%\data" --logpath "%CD%\logs\mongodb.log"
    timeout /t 3 >nul
) else (
    echo ✅ MongoDB já está rodando
)

REM Iniciar Backend
echo 🐍 Iniciando Backend FastAPI...
cd backend
start "EBD Backend" cmd /k "venv\Scripts\activate.bat && python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1"
cd ..

REM Aguardar backend iniciar
echo    Aguardando backend inicializar...
timeout /t 5 >nul

REM Iniciar Frontend
echo ⚛️  Iniciando Frontend React...
cd frontend
start "EBD Frontend" cmd /k "npm start > ../logs/frontend.log 2>&1"
cd ..

echo.
echo ================================================
echo ✅ Sistema iniciado com sucesso!
echo ================================================
echo.
echo 🌐 URLs de acesso:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:8000/docs
echo    API:      http://localhost:8000/api
echo.
echo 👤 Usuarios padrão:
echo    Admin: admin@ebd.com / 123456
echo    Prof:  kell2@ebd.com / 123456
echo.
echo 📋 Comandos uteis:
echo    stop_system.bat  - Parar sistema
echo    check_system.bat - Verificar status
echo.
echo ⏳ Aguarde alguns segundos para o sistema carregar...
echo    O navegador abrirá automaticamente em http://localhost:3000
echo.
timeout /t 10 >nul

REM Abrir navegador automaticamente
start http://localhost:3000

echo 🚀 Sistema pronto para uso!
pause