@echo off
echo ========================================
echo    PARANDO SERVICOS EBD MANAGER
echo ========================================
echo.

echo Parando servicos na porta 3000 (Frontend)...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3000"') do taskkill /f /pid %%a 2>nul

echo Parando servicos na porta 8001 (Backend)...  
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8001"') do taskkill /f /pid %%a 2>nul

echo.
echo ✅ Servicos parados!
echo.
pause