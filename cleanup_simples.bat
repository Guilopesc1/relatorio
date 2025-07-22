@echo off
echo ====================================
echo LIMPEZA FACEBOOK REPORTS - SIMPLES
echo ====================================

cd /d "C:\Users\Gui\MCP_Servers\Facebook3"

echo.
echo Criando backup...
if not exist backup mkdir backup
if not exist backup\old_files mkdir backup\old_files

echo.
echo Aplicando Docker final...
if exist "production\docker\Dockerfile.final" (
    copy "production\docker\Dockerfile.final" "production\docker\Dockerfile"
    echo Dockerfile atualizado!
)

if exist "production\docker\docker-compose.final.yml" (
    copy "production\docker\docker-compose.final.yml" "production\docker\docker-compose.yml"
    echo Docker-compose atualizado!
)

echo.
echo Movendo arquivos desnecessarios...
move docs backup\old_files\ 2>nul
move scripts backup\old_files\ 2>nul
move git_deploy*.* backup\old_files\ 2>nul
move *.md backup\old_files\ 2>nul
move test_*.py backup\old_files\ 2>nul
move debug.bat backup\old_files\ 2>nul
move start.bat backup\old_files\ 2>nul

echo.
echo Limpando cache...
rmdir /s /q __pycache__ 2>nul
del logs\*.log 2>nul

echo.
echo Commit no Git...
git add .
git commit -m "CLEANUP: Projeto limpo + Docker final sem supervisord"
git push

echo.
echo ================================
echo LIMPEZA CONCLUIDA!
echo ================================
echo.
echo Proximos passos:
echo 1. Va ao EasyPanel
echo 2. Clique em Rebuild
echo 3. Configure variaveis:
echo    SUPABASE_URL
echo    SUPABASE_KEY
echo    FACEBOOK_ACCESS_TOKEN
echo 4. Deploy
echo.
echo O erro de privilegios esta resolvido!

pause
