@echo off
echo ========================================
echo      INICIANDO EBD MANAGER
echo ========================================
echo.

echo Este arquivo vai abrir 2 janelas:
echo 1. Backend (FastAPI) - porta 8001
echo 2. Frontend (React) - porta 3000
echo.
echo Aguarde ambas iniciarem completamente!
echo.

echo Iniciando Backend...
start "EBD Backend" cmd /k "cd backend && python server.py"

timeout /t 5

echo Iniciando Frontend...  
start "EBD Frontend" cmd /k "cd frontend && npm start"

echo.
echo ✅ Sistema sendo iniciado!
echo.
echo Aguarde uns segundos e acesse: http://localhost:3000
echo.
echo Login:
echo Email: admin@ebd.com  
echo Senha: 123456
echo.
echo Para parar: Feche as 2 janelas que abriram ou pressione Ctrl+C em cada uma
echo.
pause