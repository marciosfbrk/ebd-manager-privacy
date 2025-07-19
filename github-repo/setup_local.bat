@echo off
echo ================================================
echo     EBD Manager - Setup Inicial Local
echo ================================================
echo.

echo 📋 Este script prepara o ambiente para primeira execução
echo.

REM Verificar se já foi configurado
if exist "backend\.env" (
    echo ✅ Backend já configurado
) else (
    echo 🔧 Configurando Backend...
    copy "backend\.env.production" "backend\.env"
)

if exist "frontend\.env" (
    echo ✅ Frontend já configurado
) else (
    echo 🔧 Configurando Frontend...
    copy "frontend\.env.production" "frontend\.env"
)

REM Criar estrutura básica
echo 📁 Criando estrutura...
if not exist "data" mkdir data
if not exist "logs" mkdir logs

echo.
echo ================================================
echo ✅ Setup concluído!
echo ================================================
echo.
echo 🚀 Próximo passo: execute install.bat
echo.
pause