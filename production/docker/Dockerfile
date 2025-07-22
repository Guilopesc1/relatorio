# Dockerfile para Facebook Reports System - Versão Final Limpa
FROM python:3.11-slim

LABEL maintainer="Facebook Reports System"
LABEL version="2.0.0"
LABEL description="Sistema Facebook/Google Ads - Deploy Final Otimizado"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

# Instala dependências do sistema (SEM supervisord)
RUN apt-get update && apt-get install -y \
    gcc g++ curl cron procps \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Cria usuário não-root
RUN groupadd -r appuser && useradd -r -g appuser -m appuser

# Workdir e permissões
WORKDIR /app
RUN chown appuser:appuser /app

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia aplicação com permissões corretas
COPY --chown=appuser:appuser . .

# Cria estrutura de logs
RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs

# Instala gosu para mudança segura de usuário
RUN curl -o /usr/local/bin/gosu -SL "https://github.com/tianon/gosu/releases/download/1.14/gosu-$(dpkg --print-architecture)" \
    && chmod +x /usr/local/bin/gosu

# Script de inicialização simplificado
RUN echo '#!/bin/bash\n\
set -e\n\
echo "🚀 Facebook Reports - Production Ready"\n\
echo "================================================"\n\
\n\
# Validação básica\n\
for var in SUPABASE_URL SUPABASE_KEY FACEBOOK_ACCESS_TOKEN; do\n\
    if [ -z "${!var}" ]; then\n\
        echo "❌ ERROR: $var not set"\n\
        exit 1\n\
    fi\n\
done\n\
\n\
# Setup logs\n\
mkdir -p /app/logs\n\
touch /app/logs/app.log\n\
chown -R appuser:appuser /app/logs\n\
\n\
# Cron opcional\n\
if [ "$ENABLE_CRON" = "true" ]; then\n\
    echo "0 ${DAILY_UPDATE_HOUR:-6} * * * cd /app && gosu appuser python daily_auto_update.py >> /app/logs/daily_update.log 2>&1" > /tmp/crontab\n\
    crontab -u appuser /tmp/crontab\n\
    service cron start\n\
    echo "✅ Cron enabled"\n\
fi\n\
\n\
echo "🎯 Starting as appuser on port 5000"\n\
echo "================================================"\n\
\n\
# Executa como appuser (SEM SUPERVISORD)\n\
exec gosu appuser "$@"\n\
' > /entrypoint.sh && chmod +x /entrypoint.sh

# Healthcheck simples
RUN echo '#!/bin/bash\npgrep -f "python.*app.py" >/dev/null' > /healthcheck.sh && chmod +x /healthcheck.sh

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD /healthcheck.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app.py"]
