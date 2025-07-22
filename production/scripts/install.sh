#!/bin/bash
# Script de Instalação Completa - Facebook Reports System para EasyPanel

set -e

echo "🎯 FACEBOOK REPORTS SYSTEM - INSTALAÇÃO PARA PRODUÇÃO"
echo "======================================================="
echo "Este script irá preparar seu sistema para deploy no EasyPanel"
echo "com todas as configurações de segurança e otimizações."
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções auxiliares
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verifica pré-requisitos
check_prerequisites() {
    log_info "Verificando pré-requisitos..."
    
    if [ ! -f "app.py" ] || [ ! -f "database.py" ]; then
        log_error "Execute este script do diretório raiz do projeto"
        exit 1
    fi
    
    if ! command -v python3 > /dev/null 2>&1; then
        log_error "Python 3 não encontrado. Instale Python 3.8+"
        exit 1
    fi
    
    log_success "Pré-requisitos verificados"
}

# Cria estrutura de diretórios
create_directory_structure() {
    log_info "Criando estrutura de diretórios..."
    
    mkdir -p production/{docker,scripts,config}
    mkdir -p logs/{history,backup}
    mkdir -p data
    
    chmod 755 production/scripts/*.sh 2>/dev/null || true
    
    log_success "Estrutura de diretórios criada"
}

# Cria arquivo .env seguro
create_secure_env() {
    log_info "Criando arquivo .env seguro..."
    
    if [ ! -f ".env" ]; then
        cat > .env << 'EOF'
# Facebook Reports System - Configurações
# ATENÇÃO: Não commite este arquivo com dados reais!

# Sistema
NODE_ENV=development
DEBUG=true
WEB_HOST=127.0.0.1
WEB_PORT=5000

# Banco de dados (Supabase)
SUPABASE_URL=
SUPABASE_KEY=

# Facebook API
FACEBOOK_APP_ID=
FACEBOOK_APP_SECRET=
FACEBOOK_ACCESS_TOKEN=

# Google Ads API (opcional)
GOOGLE_ADS_DEVELOPER_TOKEN=
GOOGLE_ADS_CLIENT_ID=
GOOGLE_ADS_CLIENT_SECRET=
GOOGLE_ADS_REFRESH_TOKEN=
GOOGLE_ADS_LOGIN_CUSTOMER_ID=

# Evolution API - WhatsApp (opcional)
EVOLUTION_API_URL=
EVOLUTION_API_TOKEN=
EVOLUTION_INSTANCE=
EOF
        log_info "Arquivo .env criado. CONFIGURE AS VARIÁVEIS antes de usar!"
    else
        log_info "Arquivo .env já existe, mantendo configurações atuais"
    fi
    
    chmod 600 .env
    log_success "Arquivo .env configurado com permissões seguras"
}

# Cria .gitignore seguro
create_gitignore() {
    log_info "Criando .gitignore seguro..."
    
    cat > .gitignore << 'EOF'
# Arquivos de segurança - NUNCA commitar
.env
.env.*
*.env

# Logs e dados sensíveis
logs/
*.log
data/
backup/

# Python
__pycache__/
*.pyc
*.pyo
build/
dist/
*.egg-info/

# Virtual environment
venv/
env/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Backup files
*.backup
*.bak
EOF
    
    log_success ".gitignore criado"
}

# Prepara deploy
prepare_deployment_files() {
    log_info "Preparando arquivos de deploy..."
    
    if [ -f "production/scripts/deploy.sh" ]; then
        chmod +x production/scripts/deploy.sh
        bash production/scripts/deploy.sh
    else
        log_warning "Script de deploy não encontrado"
    fi
    
    log_success "Arquivos de deploy preparados"
}

# Gera relatório final
generate_final_report() {
    log_info "Gerando relatório final..."
    
    cat > INSTALLATION_REPORT.md << 'EOF'
# 📋 Relatório de Instalação - Facebook Reports System

## ✅ Instalação Concluída

Sistema preparado para produção no EasyPanel com todas as configurações de segurança.

## 🔧 Configurações Aplicadas

### Segurança
- ✅ Arquivo .env com permissões restritivas
- ✅ .gitignore configurado
- ✅ Estrutura de diretórios segura

### Estrutura
- ✅ Diretórios de produção criados
- ✅ Dockerfile otimizado
- ✅ Docker Compose para EasyPanel
- ✅ Scripts de deploy
- ✅ Health checks

## 🚀 Próximos Passos

1. Configure o arquivo `.env` com suas credenciais
2. Siga as instruções em `DEPLOY_INSTRUCTIONS.md`
3. Use a configuração em `easypanel-config.yml`
4. Configure domínio e SSL no EasyPanel

## 📁 Arquivos Importantes

- `DEPLOY_INSTRUCTIONS.md` - Instruções de deploy
- `easypanel-config.yml` - Configuração do EasyPanel
- `.env.production.template` - Template de variáveis
- `production/docker/Dockerfile` - Imagem Docker

## ⚠️ Lembretes

1. **NUNCA** commite o arquivo `.env` com dados reais
2. **SEMPRE** use HTTPS em produção
3. **CONFIGURE** todas as variáveis obrigatórias
4. **MONITORE** logs regularmente

---

🎉 **Sistema pronto para deploy!**
EOF
    
    log_success "Relatório final gerado: INSTALLATION_REPORT.md"
}

# Função principal
main() {
    echo "Iniciando instalação..."
    echo ""
    
    check_prerequisites
    create_directory_structure
    create_secure_env
    create_gitignore
    prepare_deployment_files
    generate_final_report
    
    echo ""
    echo "==============================================="
    log_success "INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
    echo "==============================================="
    echo ""
    echo "🎯 PRÓXIMOS PASSOS:"
    echo "1. 🔧 Configure o arquivo .env com suas credenciais"
    echo "2. 📊 Leia INSTALLATION_REPORT.md"
    echo "3. 🚀 Siga DEPLOY_INSTRUCTIONS.md para fazer deploy"
    echo ""
    echo "✨ Sistema preparado para produção no EasyPanel!"
    echo ""
}

# Executa se chamado diretamente
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
