#!/bin/bash
# Script de Deploy para EasyPanel - Facebook Reports System

set -e

echo "🚀 Facebook Reports System - EasyPanel Deploy Script"
echo "===================================================="

# Configurações
PROJECT_NAME="facebook-reports"
DOCKER_IMAGE="facebook-reports:latest"
COMPOSE_FILE="production/docker/docker-compose.yml"

# Funções auxiliares
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [DEPLOY] $1"
}

check_requirements() {
    log "Checking requirements..."
    
    # Verifica se está no diretório correto
    if [ ! -f "app.py" ] || [ ! -f "database.py" ]; then
        log "❌ Error: Run this script from the project root directory"
        exit 1
    fi
    
    # Verifica Docker
    if ! command -v docker > /dev/null 2>&1; then
        log "❌ Error: Docker is not installed"
        exit 1
    fi
    
    # Verifica Docker Compose
    if ! docker compose version > /dev/null 2>&1; then
        log "❌ Error: Docker Compose is not available"
        exit 1
    fi
    
    log "✅ Requirements check passed"
}

build_image() {
    log "Building Docker image..."
    
    # Build da imagem
    docker build -f production/docker/Dockerfile -t $DOCKER_IMAGE . \
        --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
        --build-arg VERSION=$(git rev-parse --short HEAD 2>/dev/null || echo "dev")
    
    log "✅ Docker image built successfully"
}

validate_image() {
    log "Validating Docker image..."
    
    # Testa se a imagem funciona
    docker run --rm --name test-container \
        -e SUPABASE_URL="https://test.supabase.co" \
        -e SUPABASE_KEY="test-key" \
        -e FACEBOOK_ACCESS_TOKEN="test-token" \
        $DOCKER_IMAGE python -c "
import sys
try:
    from app import app
    from database import Database  
    from facebook_api import FacebookAPI
    print('✅ All imports successful')
    sys.exit(0)
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
" || {
        log "❌ Image validation failed"
        exit 1
    }
    
    log "✅ Image validation passed"
}

generate_easypanel_config() {
    log "Generating EasyPanel configuration..."
    
    cat > easypanel-config.yml << 'EOF'
# EasyPanel Configuration for Facebook Reports System
name: facebook-reports
services:
  app:
    image: facebook-reports:latest
    ports:
      - target: 5000
        published: 5000
        protocol: tcp
    environment:
      # Sistema
      NODE_ENV: production
      WEB_HOST: 0.0.0.0
      WEB_PORT: 5000
      DEBUG: false
      TZ: America/Sao_Paulo
      
      # ⚠️  CONFIGURE ESTAS VARIÁVEIS NO EASYPANEL:
      
      # Supabase Database
      SUPABASE_URL: ${SUPABASE_URL}
      SUPABASE_KEY: ${SUPABASE_KEY}
      
      # Facebook API
      FACEBOOK_APP_ID: ${FACEBOOK_APP_ID}
      FACEBOOK_APP_SECRET: ${FACEBOOK_APP_SECRET}
      FACEBOOK_ACCESS_TOKEN: ${FACEBOOK_ACCESS_TOKEN}
      
      # Google Ads API
      GOOGLE_ADS_DEVELOPER_TOKEN: ${GOOGLE_ADS_DEVELOPER_TOKEN}
      GOOGLE_ADS_CLIENT_ID: ${GOOGLE_ADS_CLIENT_ID}
      GOOGLE_ADS_CLIENT_SECRET: ${GOOGLE_ADS_CLIENT_SECRET}
      GOOGLE_ADS_REFRESH_TOKEN: ${GOOGLE_ADS_REFRESH_TOKEN}
      GOOGLE_ADS_LOGIN_CUSTOMER_ID: ${GOOGLE_ADS_LOGIN_CUSTOMER_ID}
      
      # Evolution API (WhatsApp)
      EVOLUTION_API_URL: ${EVOLUTION_API_URL}
      EVOLUTION_API_TOKEN: ${EVOLUTION_API_TOKEN}  
      EVOLUTION_INSTANCE: ${EVOLUTION_INSTANCE}
      
      # Configurações opcionais
      DAILY_UPDATE_HOUR: 6
      LOG_LEVEL: INFO
      MAX_LOG_FILES: 30
      
    volumes:
      - facebook-reports-logs:/app/logs
      - facebook-reports-data:/app/data
    
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: 0.5
        reservations:
          memory: 256M
          cpus: 0.25
    
    healthcheck:
      test: ["/healthcheck.sh"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  facebook-reports-logs:
    driver: local
  facebook-reports-data:
    driver: local

networks:
  default:
    name: facebook-reports-net
EOF
    
    log "✅ EasyPanel configuration generated: easypanel-config.yml"
}

create_env_template() {
    log "Creating environment template..."
    
    cat > .env.production.template << 'EOF'
# Facebook Reports System - Variáveis de Produção
# ⚠️  IMPORTANTE: Nunca commite este arquivo com valores reais!

# ===========================================
# BANCO DE DADOS (SUPABASE) - OBRIGATÓRIO
# ===========================================
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-publica-supabase-aqui

# ===========================================
# FACEBOOK API - OBRIGATÓRIO
# ===========================================
FACEBOOK_APP_ID=seu-app-id-facebook
FACEBOOK_APP_SECRET=seu-app-secret-facebook
FACEBOOK_ACCESS_TOKEN=seu-token-de-acesso-facebook

# ===========================================
# GOOGLE ADS API - OPCIONAL
# ===========================================
GOOGLE_ADS_DEVELOPER_TOKEN=seu-developer-token
GOOGLE_ADS_CLIENT_ID=seu-client-id.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=seu-client-secret
GOOGLE_ADS_REFRESH_TOKEN=seu-refresh-token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=seu-customer-id

# ===========================================
# EVOLUTION API (WHATSAPP) - OPCIONAL
# ===========================================
EVOLUTION_API_URL=https://sua-evolution-api.com
EVOLUTION_API_TOKEN=seu-token-evolution
EVOLUTION_INSTANCE=sua-instancia

# ===========================================
# CONFIGURAÇÕES DE PRODUÇÃO - OPCIONAL
# ===========================================
WEB_HOST=0.0.0.0
WEB_PORT=5000
DEBUG=false
LOG_LEVEL=INFO
TZ=America/Sao_Paulo

# Horário da coleta automática (0-23)
DAILY_UPDATE_HOUR=6

# Retenção de logs (dias)
MAX_LOG_FILES=30

# Rate limiting
RATE_LIMIT_ENABLED=true
EOF
    
    log "✅ Environment template created: .env.production.template"
}

show_deployment_instructions() {
    log "Generating deployment instructions..."
    
    cat > DEPLOY_INSTRUCTIONS.md << 'EOF'
# 🚀 Instruções de Deploy no EasyPanel

## 📋 Pré-requisitos

1. ✅ Conta no EasyPanel configurada
2. ✅ Domínio ou subdomínio configurado
3. ✅ Tokens das APIs (Facebook, Google, Evolution) válidos
4. ✅ Banco Supabase configurado

## 🏗️ Processo de Deploy

### Passo 1: Upload do Projeto
1. Faça upload de todo o projeto para seu repositório Git
2. Ou use o método de upload direto do EasyPanel

### Passo 2: Criar Nova Aplicação
1. No EasyPanel, clique em "New App"
2. Escolha "Docker Compose"
3. Cole o conteúdo do arquivo `easypanel-config.yml`

### Passo 3: Configurar Variáveis de Ambiente
**⚠️ CRÍTICO: Configure todas as variáveis abaixo no EasyPanel:**

#### Obrigatórias:
```
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-publica
FACEBOOK_APP_ID=seu-app-id
FACEBOOK_APP_SECRET=seu-secret
FACEBOOK_ACCESS_TOKEN=seu-token
```

#### Opcionais (Google Ads):
```
GOOGLE_ADS_DEVELOPER_TOKEN=seu-token
GOOGLE_ADS_CLIENT_ID=seu-client-id
GOOGLE_ADS_CLIENT_SECRET=seu-secret
GOOGLE_ADS_REFRESH_TOKEN=seu-refresh-token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=seu-customer-id
```

#### Opcionais (WhatsApp):
```
EVOLUTION_API_URL=https://sua-api.com
EVOLUTION_API_TOKEN=seu-token
EVOLUTION_INSTANCE=sua-instancia
```

#### Sistema:
```
TZ=America/Sao_Paulo
DAILY_UPDATE_HOUR=6
LOG_LEVEL=INFO
```

### Passo 4: Deploy
1. Clique em "Deploy"
2. Aguarde o processo de build e início
3. Verifique logs para garantir que está funcionando

### Passo 5: Configurar Domínio
1. No EasyPanel, vá em "Domains"
2. Adicione seu domínio/subdomínio
3. Configure SSL automático

### Passo 6: Teste Inicial
1. Acesse: `https://seu-dominio.com`
2. Teste conexões: `https://seu-dominio.com/api/test_connection`
3. Execute teste manual se necessário
EOF
    
    log "✅ Deployment instructions created: DEPLOY_INSTRUCTIONS.md"
}

create_security_checklist() {
    log "Creating security checklist..."
    
    cat > SECURITY_CHECKLIST.md << 'EOF'
# 🔒 Security Checklist - Facebook Reports System

## ✅ Implementado

### Container Security
- [x] **Usuário não-root**: Container roda como usuário `appuser`
- [x] **Imagem mínima**: Base `python:3.11-slim`
- [x] **Volumes isolados**: Dados persistentes em volumes seguros
- [x] **Rede isolada**: Container em rede bridge privada
- [x] **Health checks**: Monitoramento automático de saúde
- [x] **Resource limits**: CPU e memória limitados
- [x] **Read-only configs**: Arquivos de configuração somente leitura

### Environment Variables
- [x] **Secrets segregados**: Tokens não hardcodados no código
- [x] **Variáveis obrigatórias**: Validação na inicialização
- [x] **Valores padrão seguros**: Configurações conservadoras
- [x] **Debug desabilitado**: Produção sem modo debug

### API Security
- [x] **Rate limiting**: Controle de taxa de requisições
- [x] **Timeouts configurados**: Evita travamentos
- [x] **Validação de entrada**: Sanitização de dados
- [x] **Logs sem secrets**: Tokens mascarados nos logs

### Database Security
- [x] **Conexão SSL**: Supabase com HTTPS
- [x] **Prepared statements**: Proteção contra SQL injection
- [x] **Validação de tipos**: Campos tipados
- [x] **Transações atômicas**: Integridade dos dados
EOF
    
    log "✅ Security checklist created: SECURITY_CHECKLIST.md"
}

# Função principal
main() {
    log "Starting deployment process..."
    
    check_requirements
    build_image
    validate_image
    generate_easypanel_config
    create_env_template
    show_deployment_instructions
    create_security_checklist
    
    log ""
    log "==============================================="
    log "✅ Deploy preparation completed successfully!"
    log "==============================================="
    log ""
    log "📊 Next steps:"
    log "1. Review .env.production.template"
    log "2. Follow DEPLOY_INSTRUCTIONS.md"
    log "3. Configure environment variables in EasyPanel"
    log "4. Deploy using easypanel-config.yml"
    log "5. Review SECURITY_CHECKLIST.md"
    log ""
    log "🎉 Ready for production deployment!"
}

# Executa se chamado diretamente
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
