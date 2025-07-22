@echo off
cd /d "C:\Users\Gui\MCP_Servers\Facebook3"

echo === FAZENDO COMMIT E PUSH COM CAMINHO COMPLETO ===

echo.
echo 1. Status atual:
"C:\Program Files\Git\bin\git.exe" status

echo.
echo 2. Adicionando arquivos:
"C:\Program Files\Git\bin\git.exe" add .

echo.
echo 3. Removendo arquivos sensiveis:
"C:\Program Files\Git\bin\git.exe" reset .env .env.secure.backup

echo.
echo 4. Status apos add:
"C:\Program Files\Git\bin\git.exe" status

echo.
echo 5. Fazendo commit:
"C:\Program Files\Git\bin\git.exe" commit -m "Security fix: Remove sensitive data and optimize Docker"

echo.
echo 6. Fazendo push:
"C:\Program Files\Git\bin\git.exe" push origin main

echo.
echo === FINALIZADO ===
pause
