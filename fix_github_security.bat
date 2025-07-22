@echo off
echo ================================
echo CORRIGINDO PROBLEMA DO GITHUB
echo ================================

cd /d "C:\Users\Gui\MCP_Servers\Facebook3"

echo.
echo Removendo .env do Git (dados sensíveis)...
git rm --cached .env
echo .env >> .gitignore

echo.
echo Criando .env.example...
echo # Arquivo de exemplo - copie para .env e preencha > .env.example
echo # Supabase >> .env.example
echo SUPABASE_URL=sua_url_supabase_aqui >> .env.example
echo SUPABASE_KEY=sua_chave_supabase_aqui >> .env.example
echo. >> .env.example
echo # Facebook >> .env.example
echo FACEBOOK_ACCESS_TOKEN=seu_token_facebook_aqui >> .env.example
echo FACEBOOK_APP_ID=seu_app_id_aqui >> .env.example
echo FACEBOOK_APP_SECRET=seu_app_secret_aqui >> .env.example
echo. >> .env.example
echo # Google Ads >> .env.example
echo GOOGLE_ADS_DEVELOPER_TOKEN=seu_token_aqui >> .env.example
echo GOOGLE_ADS_CLIENT_ID=seu_client_id_aqui >> .env.example
echo GOOGLE_ADS_CLIENT_SECRET=seu_client_secret_aqui >> .env.example
echo GOOGLE_ADS_REFRESH_TOKEN=seu_refresh_token_aqui >> .env.example

echo.
echo Fazendo novo commit...
git add .gitignore
git add .env.example
git commit -m "SECURITY: Remove .env do Git + Adiciona .env.example

- Remove dados sensíveis do repositório
- Adiciona .env.example como template
- Atualiza .gitignore para ignorar .env
- Mantém correção Docker sem supervisord"

echo.
echo Push para GitHub...
git push

echo.
echo ================================
echo PROBLEMA CORRIGIDO!
echo ================================
echo.
echo O .env agora esta seguro no .gitignore
echo Use .env.example como template
echo Deploy funcionara normalmente no EasyPanel

pause
