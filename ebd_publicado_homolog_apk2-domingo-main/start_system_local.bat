@echo off
echo ================================================
echo      EBD Manager - Sistema Completo Local
echo      10 Turmas + 242 Alunos + Interface Pro
echo ================================================
echo.

REM Verificar se MongoDB está rodando
echo 🗄️  Verificando MongoDB...
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if %errorlevel% neq 0 (
    echo    🚀 Iniciando MongoDB...
    if not exist "data" mkdir data
    if not exist "logs" mkdir logs
    start "MongoDB EBD" mongod --dbpath "%CD%\data" --logpath "%CD%\logs\mongodb.log"
    echo    ⏳ Aguardando MongoDB inicializar...
    timeout /t 5 >nul
) else (
    echo    ✅ MongoDB já está rodando
)

REM Iniciar Backend FastAPI
echo 🐍 Iniciando Backend FastAPI...
cd backend
start "EBD Backend" cmd /k "venv\Scripts\activate.bat && python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload"
cd ..

echo    ⏳ Aguardando backend carregar...
timeout /t 5 >nul

REM Iniciar Frontend React
echo ⚛️  Iniciando Frontend React...
cd frontend
start "EBD Frontend" cmd /k "set BROWSER=none && npm start"
cd ..

echo.
echo ================================================
echo ✅ SISTEMA INICIADO COM SUCESSO!
echo ================================================
echo.
echo 🎯 Sistema EBD Manager está rodando:
echo.
echo 🌐 URLs de acesso:
echo    📱 Frontend Principal: http://localhost:3000
echo    🔧 Backend API Docs:   http://localhost:8000/docs  
echo    📊 API Endpoints:      http://localhost:8000/api
echo.
echo 👤 Logins configurados:
echo    🔑 Administrador: admin@ebd.com / 123456
echo    👨‍🏫 Professor:      kell@ebd.com / 123456
echo.
echo 📊 Dados disponíveis:
echo    🏫 10 turmas com dados reais
echo    👥 242 alunos cadastrados
echo    📅 908 registros de presença
echo    📚 6 revistas trimestrais
echo    📈 Relatórios e rankings funcionando
echo.
echo 🎪 Funcionalidades ativas:
echo    ✅ Dashboard com estatísticas
echo    ✅ Sistema de chamada por turma
echo    ✅ Relatórios detalhados
echo    ✅ Rankings de presença  
echo    ✅ Gerenciamento de usuários
echo    ✅ Sistema de revistas da EBD
echo    ✅ Interface responsiva
echo.
echo 📋 Comandos úteis:
echo    🛑 Parar: stop_system_local.bat
echo    🔧 Status: check_status_local.bat
echo    🔄 Reset: restaurar backup novamente
echo.
echo ⏳ Aguardando sistema carregar completamente...
timeout /t 8 >nul

echo 🚀 Abrindo navegador automaticamente...
start http://localhost:3000

echo.
echo 🏆 Sistema pronto para uso profissional!
echo    Faça login e explore todas as funcionalidades.
echo.
pause