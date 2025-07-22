#!/bin/bash
# Health Check Script para Facebook Reports System

set -e

# Função de log
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [HEALTHCHECK] $1"
}

# Verifica se a aplicação Flask está respondendo
check_flask() {
    if curl -f -s --max-time 5 http://localhost:5000/health > /dev/null 2>&1; then
        log "✅ Flask application is healthy"
        return 0
    else
        log "❌ Flask application is not responding"
        return 1
    fi
}

# Verifica se o processo Python está rodando
check_process() {
    if pgrep -f "python.*app.py" > /dev/null 2>&1; then
        log "✅ Python process is running"
        return 0
    else
        log "❌ Python process not found"
        return 1
    fi
}

# Verifica conectividade com Supabase
check_supabase() {
    if [ -n "$SUPABASE_URL" ]; then
        if curl -f -s --max-time 10 "$SUPABASE_URL/rest/v1/" \
           -H "apikey: $SUPABASE_KEY" > /dev/null 2>&1; then
            log "✅ Supabase connectivity OK"
            return 0
        else
            log "⚠️  Supabase connectivity issues"
            return 1
        fi
    else
        log "⚠️  SUPABASE_URL not configured"
        return 1
    fi
}

# Verifica espaço em disco
check_disk_space() {
    DISK_USAGE=$(df /app | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -lt 90 ]; then
        log "✅ Disk space OK (${DISK_USAGE}% used)"
        return 0
    else
        log "⚠️  Disk space critical (${DISK_USAGE}% used)"
        return 1
    fi
}

# Verifica logs recentes (última atualização)
check_recent_activity() {
    if [ -f "/app/logs/daily_update.log" ]; then
        # Verifica se houve atividade nas últimas 25 horas
        if find /app/logs/daily_update.log -mtime -1 | grep -q .; then
            log "✅ Recent activity detected"
            return 0
        else
            log "⚠️  No recent activity in logs"
            return 1
        fi
    else
        log "ℹ️  Daily update log not found yet (normal on first run)"
        return 0
    fi
}

# Executa verificações
main() {
    log "Starting health check..."
    
    local exit_code=0
    
    # Verificações críticas (falham o health check)
    check_flask || exit_code=1
    check_process || exit_code=1
    
    # Verificações de warning (não falham, mas alertam)
    check_supabase || true
    check_disk_space || true
    check_recent_activity || true
    
    if [ $exit_code -eq 0 ]; then
        log "✅ Overall health check PASSED"
    else
        log "❌ Overall health check FAILED"
    fi
    
    return $exit_code
}

# Executa health check
main
