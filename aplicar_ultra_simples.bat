@echo off
echo =======================================
echo APLICANDO DOCKERFILE ULTRA-SIMPLES
echo =======================================

cd /d "C:\Users\Gui\MCP_Servers\Facebook3"

echo.
echo Copiando Dockerfile ultra-simples...
copy "production\docker\Dockerfile.ultra" "production\docker\Dockerfile"

echo.
echo Fazendo commit da versao ultra-simples...
git add production/docker/Dockerfile
git add production/docker/Dockerfile.ultra
git commit -m "HOTFIX: Dockerfile ultra-simples sem supervisord

- Remove completamente supervisord
- Execucao direta com su appuser
- Script de start minimalista
- Garante zero conflitos de privilegios"

echo.
echo Push para GitHub...
git push

if %ERRORLEVEL% EQU 0 (
    echo.
    echo 🎉 DOCKERFILE ULTRA-SIMPLES APLICADO!
    echo ===================================
    echo ✅ GitHub atualizado
    echo ✅ Zero supervisord
    echo ✅ Execucao direta Flask
    echo ===================================
    echo.
    echo 🚀 AGORA NO EASYPANEL:
    echo 1. Va na aplicacao
    echo 2. Clique em REBUILD
    echo 3. Aguarde build completar
    echo 4. Verifique logs
    echo.
    echo DEVE APARECER:
    echo "🚀 Facebook Reports - Ultra Simple Start"
    echo "✅ All variables set"  
    echo "🎯 Starting Flask as appuser"
    echo.
    echo NAO DEVE MAIS APARECER:
    echo "supervisord" ou "privilege drop"
) else (
    echo ❌ Erro no push
)

pause
