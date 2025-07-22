# Facebook Reports System

Sistema de relatórios integrado para Facebook Ads e Google Ads com envio automatizado via WhatsApp.

## 🚀 Deploy no EasyPanel

### Configuração Rápida

1. **Repositório**: `https://github.com/Guilopesc1/relatorio`
2. **Branch**: `main`
3. **Dockerfile**: `Dockerfile` (raiz do projeto)
4. **Port**: `5000`

### Variáveis de Ambiente Obrigatórias

```env
# Supabase Database
SUPABASE_URL=sua_url_supabase
SUPABASE_KEY=sua_chave_supabase

# Facebook API
FACEBOOK_ACCESS_TOKEN=seu_token_facebook
FACEBOOK_APP_ID=seu_app_id
FACEBOOK_APP_SECRET=seu_app_secret

# Google Ads API
GOOGLE_ADS_DEVELOPER_TOKEN=seu_developer_token
GOOGLE_ADS_CLIENT_ID=seu_client_id
GOOGLE_ADS_CLIENT_SECRET=seu_client_secret
GOOGLE_ADS_REFRESH_TOKEN=seu_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=seu_customer_id

# Application Settings
WEB_HOST=0.0.0.0
WEB_PORT=5000
DEBUG=false
TOKEN_RENEWAL_DAYS=50
TOKEN_CHECK_INTERVAL=86400

# Optional: Cron Jobs
ENABLE_CRON=false
DAILY_UPDATE_HOUR=6
```

### Variáveis Opcionais para Evolution API

```env
# Evolution API WhatsApp
EVOLUTION_API_URL=sua_url_evolution
EVOLUTION_API_TOKEN=seu_token_evolution
EVOLUTION_INSTANCE=sua_instancia
```

## 🐳 Desenvolvimento Local

### Com Docker Compose

```bash
# Clone o repositório
git clone https://github.com/Guilopesc1/relatorio.git
cd relatorio

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais

# Execute com Docker
docker-compose up --build
```

### Sem Docker

```bash
# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais

# Execute a aplicação
python app.py
```

## 📋 Endpoints Disponíveis

- `/` - Interface principal
- `/health` - Health check do sistema
- `/api/test_connection` - Teste de conexões com APIs
- `/generate_report` - Geração de relatórios
- `/send_whatsapp` - Envio via WhatsApp
- `/mass_update` - Atualização em massa

## 🔧 Recursos

### ✅ Integração Facebook Ads
- Busca automática de campanhas
- Relatórios personalizados
- Prevenção de duplicatas

### ✅ Integração Google Ads
- Relatórios de campanhas
- Métricas de conversão
- Otimização de consultas

### ✅ WhatsApp Automation
- Integration Evolution API
- Mensagens personalizadas
- Envio automático de relatórios

### ✅ Docker Otimizado
- Multi-stage build
- Usuário não-root para segurança
- Health checks integrados
- Logs estruturados

## 🛡️ Segurança

- Dados sensíveis nunca commitados
- Execução como usuário não-root
- Validação de variáveis de ambiente
- Health checks para monitoramento

## 📦 Estrutura do Projeto

```
.
├── app.py              # Aplicação principal Flask
├── database.py         # Conexão e queries Supabase
├── facebook_api.py     # Integração Facebook Ads API
├── google_ads_api.py   # Integração Google Ads API
├── evolution_api.py    # Integração WhatsApp Evolution API
├── requirements.txt    # Dependências Python
├── Dockerfile         # Container otimizado para produção
├── docker-compose.yml # Desenvolvimento local
├── .env.example       # Template de configuração
└── templates/         # Templates HTML
```

## 🚨 Troubleshooting

### Container não inicia
- Verifique se todas as variáveis obrigatórias estão configuradas
- Confirme que o port 5000 está disponível
- Verifique os logs do container

### Erro de API
- Valide tokens e credenciais
- Use o endpoint `/api/test_connection` para diagnóstico
- Verifique limites de rate da API

### Problems com WhatsApp
- Confirme configuração da Evolution API
- Teste com `/test_evolution`
- Verifique se a instância está conectada

## 📞 Suporte

Para problemas técnicos, verifique:
1. Logs do container/aplicação
2. Endpoint `/health` para status
3. Endpoint `/api/test_connection` para APIs
