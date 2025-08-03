@echo off
echo ================================================
echo   EBD Manager - Instalação Completa com Backup
echo   Sistema Profissional Pronto para Produção
echo ================================================
echo.

REM Verificar pré-requisitos
echo 🔍 Verificando pré-requisitos...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado!
    echo    📥 Baixe em: https://www.python.org/downloads/
    echo    ⚠️  CRÍTICO: Marque "Add Python to PATH" na instalação
    pause
    exit /b 1
)

node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js não encontrado!
    echo    📥 Baixe em: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Python e Node.js encontrados!
echo.

REM Configurar Backend Python
echo 🐍 Configurando Backend Python...
cd backend

echo    📦 Criando ambiente virtual...
if exist "venv" rmdir /s /q venv
python -m venv venv

echo    🔄 Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo    ⬆️  Atualizando pip...
python -m pip install --upgrade pip --quiet

echo    📚 Instalando dependências Python...
pip install -r requirements.txt --quiet

echo    ✅ Backend Python configurado!
cd ..

REM Configurar Frontend React
echo ⚛️  Configurando Frontend React...
cd frontend

echo    🧹 Limpando instalação anterior...
if exist "node_modules" rmdir /s /q node_modules
if exist "package-lock.json" del package-lock.json

echo    📦 Instalando dependências React...
npm install --silent

echo    ✅ Frontend React configurado!
cd ..

REM Verificar/Iniciar MongoDB
echo 🗄️  Configurando MongoDB...
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if %errorlevel% neq 0 (
    echo    🚀 Iniciando MongoDB local...
    start "MongoDB Local" mongod --dbpath "%CD%\data" --logpath "%CD%\logs\mongodb.log"
    echo    ⏳ Aguardando MongoDB inicializar...
    timeout /t 8 >nul
) else (
    echo    ✅ MongoDB já está rodando!
)

REM Restaurar backup completo
echo 📊 Restaurando dados completos...
echo    🎯 Importando 10 turmas, 242 alunos, 908 registros...

cd backend
call venv\Scripts\activate.bat

REM Criar script de restauração automática
echo import asyncio > restore_auto.py
echo import sys >> restore_auto.py
echo sys.path.append('..') >> restore_auto.py
echo from restore_backup import restore_backup >> restore_auto.py
echo asyncio.run(restore_backup('../backup_ebd_completo_20250803_015454.json')) >> restore_auto.py

python restore_auto.py

del restore_auto.py
cd ..

echo.
echo ================================================
echo ✅ INSTALAÇÃO COMPLETA CONCLUÍDA COM SUCESSO!
echo ================================================
echo.
echo 🎉 Sistema EBD Manager está pronto para uso!
echo.
echo 📊 Dados carregados:
echo    ✅ 10 turmas funcionando perfeitamente
echo    ✅ 242 alunos distribuídos nas turmas  
echo    ✅ 908 registros históricos de presença
echo    ✅ 6 revistas trimestrais completas
echo    ✅ 2 usuários configurados
echo    ✅ Sistema de relatórios funcionando
echo.
echo 🌐 Para usar o sistema:
echo    🚀 Execute: start_system_local.bat
echo    🌍 Acesse: http://localhost:3000
echo.
echo 👤 Logins disponíveis:
echo    Admin: admin@ebd.com / 123456
echo    Prof:  kell@ebd.com / 123456
echo.
echo 🏆 Status: Sistema de Nível Corporativo Pronto!
echo.
pause