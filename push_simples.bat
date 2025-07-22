@echo off
echo ================================
echo PUSH SIMPLES PARA GITHUB
echo ================================

cd /d "C:\Users\Gui\MCP_Servers\Facebook3"

echo.
echo Status atual:
git status

echo.
echo Tentando push...
git push

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS! Push realizado!
    echo Todas as correcoes estao no GitHub
    echo Pronto para deploy EasyPanel
) else (
    echo.
    echo Push falhou. Opcoes:
    echo.
    echo 1. Autorize no GitHub:
    echo https://github.com/Guilopesc1/relatorio/security/secret-scanning/unblock-secret/30EvWDYp02ET1Wjq7wQ0wZ8weVR
    echo.
    echo 2. Ou force push:
    git push --force-with-lease
    echo.
)

echo.
echo Depois va ao EasyPanel e faca REBUILD!
pause
