#!/bin/bash
set -e

echo "🚀 Facebook Reports System - Starting Production Container"
echo "=================================================="

# Validação de variáveis críticas
REQUIRED_VARS=(
    "SUPABASE_URL"
    "SUPABASE_KEY"
    "FACEBOOK_ACCESS_TOKEN"
)

echo "🔍 Validating required environment variables..."
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ ERROR: Required environment variable $var is not set"
        exit 1
    else
        echo "✅ $var is set"
    fi
done

# Cria arquivos de log se não existirem
echo "📁 Setting up log directories..."
mkdir -p /app/logs/history /app/data
touch /app/logs/app.log /app/logs/daily_update.log /app/logs/error.log

# Define permissões corretas
echo "🔐 Setting up permissions..."
chown -R appuser:appuser /app/logs /app/data || true
chmod 755 /app/logs /app/data || true
chmod 644 /app/logs/*.log || true

# Configura timezone
if [ ! -z "$TZ" ]; then
    echo "🌍 Setting timezone to $TZ"
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime || true
    echo $TZ > /etc/timezone || true
fi

# Configura cron job para appuser
HOUR=${DAILY_UPDATE_HOUR:-6}
echo "⏰ Setting up daily update at ${HOUR}:00"

# Instala cron job para appuser
echo "0 ${HOUR} * * * cd /app && python daily_auto_update.py >> /app/logs/daily_update.log 2>&1" | crontab -u appuser -

# Inicia cron daemon
service cron start

echo "🎯 Container starting in production mode"
echo "📊 Web interface will be available on port 5000"
echo "🤖 Daily automation scheduled for ${HOUR}:00 UTC"
echo "📁 Logs location: /app/logs/"
echo "=================================================="

# Inicia processo especificado
exec "$@"
