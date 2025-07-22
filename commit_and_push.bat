@echo off
cd /d "C:\Users\Gui\MCP_Servers\Facebook3"

echo === FAZENDO COMMIT E PUSH ===

echo.
echo 1. Status atual:
git status

echo.
echo 2. Adicionando arquivos:
git add .

echo.
echo 3. Removendo arquivos sensíveis:
git reset .env .env.secure.backup

echo.
echo 4. Status após add:
git status

echo.
echo 5. Fazendo commit:
git commit -m "Security fix: Remove sensitive data and optimize Docker"

echo.
echo 6. Fazendo push:
git push origin main

echo.
echo === FINALIZADO ===
pause
