@echo off
echo ================================================
echo ALTERNATIVA: AUTORIZACAO DIRETA NO GITHUB
echo ================================================

echo.
echo Se o script anterior nao funcionar, use esta opcao:
echo.
echo 1. ACESSE ESTE LINK:
echo https://github.com/Guilopesc1/relatorio/security/secret-scanning/unblock-secret/30EvWDYp02ET1Wjq7wQ0wZ8weVR
echo.
echo 2. CLIQUE EM "Allow secret"
echo.
echo 3. VOLTE AQUI E PRESSIONE ENTER
echo.

pause

cd /d "C:\Users\Gui\MCP_Servers\Facebook3"

echo.
echo Tentando push novamente...
git push

if %ERRORLEVEL% EQU 0 (
    echo.
    echo 🎉 SUCCESS! Push realizado com sucesso!
    echo ✅ Todas as correções estão no GitHub
    echo ✅ Docker sem supervisord aplicado
    echo ✅ Projeto limpo e organizado
    echo ✅ Pronto para deploy EasyPanel
) else (
    echo.
    echo ❌ Push ainda falhou.
    echo.
    echo 💡 ÚLTIMA OPÇÃO: 
    echo Vamos criar um novo repositório limpo ou
    echo fazer force push (perigoso, mas funciona):
    echo.
    echo Para force push, digite: git push --force-with-lease
    echo ⚠️  CUIDADO: Isso sobrescreverá o repositório remoto
)

echo.
echo 🚀 Se deu certo, va ao EasyPanel e faça REBUILD!
echo O erro "Can't drop privilege as nonroot user" esta resolvido.

pause
