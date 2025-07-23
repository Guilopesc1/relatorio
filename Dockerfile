# Dockerfile otimizado para EasyPanel - Facebook Reports System
FROM python:3.11-slim

LABEL maintainer="Facebook Reports System"
LABEL version="3.0.1"
LABEL description="Sistema de Relatórios Facebook/Google Ads - Produção"

# Variáveis de ambiente para otimização
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependências do sistema e gosu
RUN apt-get update && apt-get install -y \
    gcc g++ \
    curl \
    cron \
    procps \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Instalar gosu para mudança segura de usuário
RUN set -eux; \
    dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')"; \
    curl -o /usr/local/bin/gosu -SL "https://github.com/tianon/gosu/releases/download/1.17/gosu-$dpkgArch"; \
    chmod +x /usr/local/bin/gosu; \
    gosu --version; \
    gosu nobody true

# Criar usuário não-root para segurança
RUN groupadd -r appuser && useradd -r -g appuser -m -d /app appuser

# Configurar diretório de trabalho
WORKDIR /app

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar estruturas necessárias
RUN mkdir -p /app/logs /app/backup /app/static /app/templates && \
    chown -R appuser:appuser /app

# Script de inicialização otimizado
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "🚀 Facebook Reports System - Starting..."\n\
echo "========================================"\n\
\n\
# Verificar variáveis críticas\n\
required_vars="SUPABASE_URL SUPABASE_KEY FACEBOOK_ACCESS_TOKEN"\n\
for var in $required_vars; do\n\
    if [ -z "${!var}" ]; then\n\
        echo "❌ ERROR: Required environment variable $var is not set"\n\
        exit 1\n\
    fi\n\
done\n\
\n\
# Configurar logs\n\
mkdir -p /app/logs\n\
chown -R appuser:appuser /app/logs\n\
\n\
# Configurar cron se habilitado\n\
if [ "${ENABLE_CRON:-false}" = "true" ]; then\n\
    echo "📅 Setting up cron for daily updates..."\n\
    echo "0 ${DAILY_UPDATE_HOUR:-6} * * * cd /app && python daily_auto_update.py >> /app/logs/daily_update.log 2>&1" | crontab -u appuser -\n\
    service cron start\n\
    echo "✅ Cron enabled for daily updates"\n\
fi\n\
\n\
echo "🎯 Starting application on port ${WEB_PORT:-5000}"\n\
echo "✅ User: appuser"\n\
echo "✅ Python: $(python --version)"\n\
echo "✅ Working directory: $(pwd)"\n\
echo "========================================"\n\
\n\
# Executar como usuário não-root usando gosu\n\
exec gosu appuser "$@"\n\
' > /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

# Healthcheck simples sem curl (que pode não estar disponível)
RUN echo '#!/bin/bash\n\
if pgrep -f "python.*app.py" > /dev/null; then\n\
    exit 0\n\
else\n\
    exit 1\n\
fi\n\
' > /healthcheck.sh && chmod +x /healthcheck.sh

# Healthcheck usando verificação de processo
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD /healthcheck.sh

# Configurações finais
EXPOSE 5000

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "app.py"]
