@echo off
echo ========================================
echo AUTORIZACAO RAPIDA NO GITHUB
echo ========================================

echo.
echo 1. ABRA ESTE LINK NO SEU NAVEGADOR:
echo.
echo https://github.com/Guilopesc1/relatorio/security/secret-scanning/unblock-secret/30EvWDYp02ET1Wjq7wQ0wZ8weVR
echo.
echo 2. CLIQUE EM "Allow secret"
echo.
echo 3. VOLTE AQUI E PRESSIONE ENTER
echo.

pause

cd /d "C:\Users\Gui\MCP_Servers\Facebook3"

echo Fazendo push apos autorizacao...
git push

if %ERRORLEVEL% EQU 0 (
    echo.
    echo 🎉 SUCCESS! PROBLEMA RESOLVIDO!
    echo ✅ Push realizado com sucesso
    echo ✅ Codigo no GitHub atualizado
    echo 🚀 VA AO EASYPANEL E FACA REBUILD!
) else (
    echo ❌ Ainda falhou. Use a opcao 2.
)

pause
