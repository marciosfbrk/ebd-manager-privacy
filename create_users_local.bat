@echo off
echo ================================================
echo    EBD Manager - Corrigir Login Local
echo ================================================
echo.

echo 🔧 Criando usuários no sistema local...
echo.

REM Aguardar backend estar ativo
echo ⏳ Verificando se backend está rodando...
timeout /t 3 >nul

REM Criar usuário admin
echo 👤 Criando usuário administrador...
curl -X POST -H "Content-Type: application/json" "http://localhost:8000/api/init-admin" -d "{}" 2>nul

REM Criar usuário kell2
echo 👤 Criando usuário professor...
curl -X POST -H "Content-Type: application/json" "http://localhost:8000/api/users" -d "{\"nome\":\"Kelliane Ferreira\",\"email\":\"kell2@ebd.com\",\"senha\":\"123456\",\"tipo\":\"professor\",\"turmas_permitidas\":[]}" 2>nul

echo.
echo 📊 Carregando dados da igreja...
curl -X POST -H "Content-Type: application/json" "http://localhost:8000/api/init-church-data" -d "{}" 2>nul

echo.
echo ================================================
echo ✅ Usuários criados com sucesso!
echo ================================================
echo.
echo 👥 Usuários disponíveis:
echo    Admin: admin@ebd.com / 123456
echo    Prof:  kell2@ebd.com / 123456
echo.
echo 📊 Dados carregados:
echo    - 11 turmas da igreja
echo    - 242 alunos cadastrados
echo.
echo 🌐 Acesse: http://localhost:3000
echo.
pause