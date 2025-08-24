@echo off
echo ================================================
echo    EBD Manager - Reset do Banco de Dados
echo ================================================
echo.

echo ⚠️  ATENÇÃO: Esta operação irá:
echo    - Apagar todos os dados atuais
echo    - Restaurar dados originais (242 alunos, 11 turmas, 6 revistas)
echo    - Resetar usuários para padrão
echo.
set /p confirm="Tem certeza? (digite 'SIM' para confirmar): "
if not "%confirm%"=="SIM" (
    echo ❌ Operação cancelada
    pause
    exit /b 0
)

echo.
echo 🗄️  Verificando se MongoDB está rodando...
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if %errorlevel% neq 0 (
    echo    Iniciando MongoDB...
    if not exist "data" mkdir data
    start "MongoDB" mongod --dbpath "%CD%\data" --logpath "%CD%\logs\mongodb.log"
    timeout /t 5 >nul
)

echo 📊 Reimportando dados completos...
cd backend
call venv\Scripts\activate.bat
python ..\import_data_completo.py
cd ..

echo.
echo ================================================
echo ✅ Reset concluído com sucesso!
echo ================================================
echo.
echo 🎉 Dados restaurados:
echo    👤 Admin: admin@ebd.com / 123456
echo    👨‍🏫 Prof: kell2@ebd.com / 123456
echo    🏫 11 turmas da igreja
echo    👥 242 alunos cadastrados
echo    📚 6 revistas trimestrais
echo.
echo 🚀 Para usar o sistema: start_system_local.bat
echo.
pause