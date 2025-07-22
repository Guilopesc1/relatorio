#!/bin/bash
# Script de Validação Final - Facebook Reports System
# Executa todos os testes antes do deploy em produção

set -e

echo "🔍 FACEBOOK REPORTS SYSTEM - VALIDAÇÃO FINAL"
echo "=============================================="
echo "Executando todos os testes antes do deploy..."
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_TOTAL=0

log_test() {
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[✅ PASS]${NC} $1"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}[❌ FAIL]${NC} $1"
    fi
}

# Teste 1: Estrutura de arquivos
echo -e "${BLUE}[1/8]${NC} Verificando estrutura de arquivos..."
(
    [ -f "app.py" ] && 
    [ -f "database.py" ] &&
    [ -f "daily_auto_update.py" ] &&
    [ -f "requirements.txt" ] &&
    [ -d "production" ] &&
    [ -f "production/docker/Dockerfile" ] &&
    [ -f "production/docker/docker-compose.yml" ] &&
    [ -f "production/scripts/deploy.sh" ] &&
    [ -f "production/scripts/install.sh" ] &&
    [ -f "production/scripts/entrypoint.sh" ] &&
    [ -f "production/scripts/healthcheck.sh" ] &&
    [ -f "production/config/security.py" ] &&
    [ -f "production/config/supervisord.conf" ]
)
log_test "Estrutura de arquivos"

# Teste 2: Permissões de arquivos
echo -e "${BLUE}[2/8]${NC} Verificando permissões..."
(
    [ -r ".env" ] &&
    [ "$(stat -c %a .env)" = "600" ] 2>/dev/null ||
    [ "$(stat -f %A .env)" = "600" ] 2>/dev/null
)
log_test "Permissões do .env"

# Teste 3: Sintaxe Python
echo -e "${BLUE}[3/8]${NC} Validando sintaxe Python..."
(
    python3 -m py_compile app.py &&
    python3 -m py_compile database.py &&
    python3 -m py_compile daily_auto_update.py &&
    python3 -c "import production.config.security; print('Security module OK')" 2>/dev/null
)
log_test "Sintaxe Python"

# Teste 4: Dependências
echo -e "${BLUE}[4/8]${NC} Verificando dependências..."
(
    python3 -c "
import sys
required = ['flask', 'requests', 'supabase', 'python-dotenv', 'google-ads']
missing = []
for pkg in required:
    try:
        __import__(pkg.replace('-', '_'))
    except ImportError:
        missing.append(pkg)
if missing:
    print(f'Missing: {missing}')
    sys.exit(1)
print('All dependencies available')
    " 2>/dev/null
)
log_test "Dependências Python"

# Teste 5: Configuração Docker
echo -e "${BLUE}[5/8]${NC} Validando configuração Docker..."
(
    [ -f "production/docker/Dockerfile" ] &&
    grep -q "FROM python:3.11-slim" production/docker/Dockerfile &&
    grep -q "USER appuser" production/docker/Dockerfile &&
    [ -f "production/docker/docker-compose.yml" ] &&
    grep -q "facebook-reports" production/docker/docker-compose.yml
)
log_test "Configuração Docker"

# Teste 6: Scripts executáveis
echo -e "${BLUE}[6/8]${NC} Verificando scripts executáveis..."
(
    [ -x "production/scripts/deploy.sh" ] &&
    [ -x "production/scripts/install.sh" ] &&
    bash -n production/scripts/entrypoint.sh &&
    bash -n production/scripts/healthcheck.sh
)
log_test "Scripts executáveis"

# Teste 7: Arquivos de configuração
echo -e "${BLUE}[7/8]${NC} Validando arquivos de configuração..."
(
    [ -f ".env" ] &&
    [ -f ".gitignore" ] &&
    grep -q ".env" .gitignore &&
    grep -q "logs/" .gitignore &&
    [ -f "production/config/supervisord.conf" ] &&
    [ -f "production/config/crontab" ]
)
log_test "Arquivos de configuração"

# Teste 8: Documentação
echo -e "${BLUE}[8/8]${NC} Verificando documentação..."
(
    [ -f "DEPLOY_INSTRUCTIONS.md" ] &&
    [ -f "SECURITY_CHECKLIST.md" ] &&
    [ -f ".env.production.template" ] &&
    [ -f "easypanel-config.yml" ] &&
    [ -f "PRODUCTION_README.md" ]
)
log_test "Documentação"

# Resultado final
echo ""
echo "=============================================="
echo -e "📊 RESULTADO DA VALIDAÇÃO"
echo "=============================================="
echo -e "Testes aprovados: ${GREEN}$TESTS_PASSED${NC}/${TESTS_TOTAL}"

if [ $TESTS_PASSED -eq $TESTS_TOTAL ]; then
    echo -e "${GREEN}🎉 TODOS OS TESTES PASSARAM!${NC}"
    echo -e "${GREEN}✅ Sistema está pronto para deploy em produção${NC}"
    echo ""
    echo "🚀 PRÓXIMOS PASSOS:"
    echo "1. Configure o arquivo .env com suas credenciais"
    echo "2. Execute deploy: bash production/scripts/deploy.sh"
    echo "3. Configure variáveis no EasyPanel"
    echo "4. Faça deploy usando easypanel-config.yml"
    echo ""
    exit 0
else
    FAILED=$((TESTS_TOTAL - TESTS_PASSED))
    echo -e "${RED}❌ $FAILED TESTE(S) FALHARAM${NC}"
    echo -e "${YELLOW}⚠️ Corrija os problemas antes do deploy${NC}"
    echo ""
    echo "💡 DICAS:"
    echo "• Execute novamente o instalador: ./production/scripts/install.sh"
    echo "• Verifique se todas as dependências estão instaladas"
    echo "• Confirme se os arquivos foram criados corretamente"
    echo ""
    exit 1
fi
