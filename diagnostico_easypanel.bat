@echo off
echo ==========================================
echo DIAGNOSTICO - APLICACAO NAO RESPONDE
echo ==========================================

echo.
echo 🔍 POSSÍVEIS CAUSAS:
echo 1. Aplicacao nao iniciou corretamente
echo 2. Porta incorreta no EasyPanel
echo 3. Variaveis de ambiente faltando
echo 4. Erro no container
echo 5. Healthcheck falhando
echo.

echo 📋 CHECKLIST DE VERIFICACAO NO EASYPANEL:
echo.
echo ✅ 1. VERIFIQUE OS LOGS:
echo    - Va em Logs da aplicacao
echo    - Procure por erros
echo    - Deve aparecer: "Starting application as appuser on port 5000"
echo.
echo ✅ 2. VERIFIQUE A PORTA:
echo    - Configuracoes da aplicacao
echo    - Container Port: 5000
echo    - Expose Port: 80 ou 443
echo.
echo ✅ 3. VERIFIQUE VARIAVEIS OBRIGATORIAS:
echo    - SUPABASE_URL (deve estar preenchida)
echo    - SUPABASE_KEY (deve estar preenchida)  
echo    - FACEBOOK_ACCESS_TOKEN (deve estar preenchida)
echo.
echo ✅ 4. VERIFIQUE O STATUS:
echo    - Container deve estar "Running"
echo    - Health check deve estar "Healthy"
echo.
echo ✅ 5. VERIFIQUE O DOCKERFILE:
echo    - Deve apontar para: production/docker/Dockerfile
echo    - NAO deve usar supervisord
echo.

echo.
echo 🚀 CONFIGURACAO CORRETA EASYPANEL:
echo.
echo Repository: https://github.com/Guilopesc1/relatorio
echo Branch: main
echo Dockerfile: production/docker/Dockerfile
echo.
echo Environment Variables:
echo SUPABASE_URL=sua_url_completa
echo SUPABASE_KEY=sua_chave_publica
echo FACEBOOK_ACCESS_TOKEN=seu_token
echo WEB_HOST=0.0.0.0
echo WEB_PORT=5000
echo DEBUG=false
echo.
echo Port Configuration:
echo Container Port: 5000
echo Expose Port: 80
echo.
echo Health Check:
echo Enable: Yes
echo Path: /
echo.

echo 🔧 PASSOS PARA CORRIGIR:
echo.
echo 1. VA AOS LOGS E COPIE QUALQUER ERRO
echo.
echo 2. VERIFIQUE SE AS 3 VARIAVEIS OBRIGATORIAS ESTAO PREENCHIDAS
echo.
echo 3. SE HOUVER ERRO DE VARIAVEL:
echo    - Adicione as variaveis faltantes
echo    - Rebuild a aplicacao
echo.
echo 4. SE HOUVER ERRO DE PORTA:
echo    - Verifique Container Port = 5000
echo    - Rebuild a aplicacao
echo.
echo 5. SE CONTAINER NAO INICIAR:
echo    - Verifique o Dockerfile aponta para production/docker/Dockerfile
echo    - Rebuild a aplicacao
echo.

echo 💡 COMANDOS DE TESTE LOCAL (OPCIONAL):
echo Para testar localmente se o Docker funciona:
echo.
echo cd "C:\Users\Gui\MCP_Servers\Facebook3"
echo docker build -f production/docker/Dockerfile -t facebook-test .
echo docker run -p 5000:5000 -e SUPABASE_URL=test -e SUPABASE_KEY=test -e FACEBOOK_ACCESS_TOKEN=test facebook-test
echo.
echo Depois acesse: http://localhost:5000
echo.

echo 🎯 RESULTADO ESPERADO NO EASYPANEL:
echo ✅ Container "Running"  
echo ✅ Logs mostram: "Starting application as appuser on port 5000"
echo ✅ Health check "Healthy"
echo ✅ URL responde com interface web
echo.

pause
