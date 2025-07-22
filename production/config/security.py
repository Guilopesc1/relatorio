# Atualizações de Segurança para app.py
# Este arquivo será usado para aplicar patches de segurança

import os
import logging
import secrets
from functools import wraps
from flask import request, jsonify
import time

# Configurações de segurança
PRODUCTION_MODE = os.getenv('NODE_ENV', 'development') == 'production'
DEBUG_ENABLED = os.getenv('DEBUG', 'False').lower() == 'true'
RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'

# Configuração de logging seguro
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/app.log') if PRODUCTION_MODE else logging.StreamHandler(),
    ]
)

# Geração de chave secreta segura
def generate_secure_secret_key():
    """Gera uma chave secreta segura para produção"""
    if PRODUCTION_MODE:
        # Em produção, usa chave do ambiente ou gera uma nova
        secret_key = os.getenv('SECRET_KEY')
        if not secret_key:
            secret_key = secrets.token_hex(32)
            logging.warning("SECRET_KEY not set, generated a new one. Consider setting it as environment variable.")
        return secret_key
    else:
        # Em desenvolvimento, usa chave fixa
        return 'dev-secret-key-not-for-production'

# Rate limiting simples
class SimpleRateLimiter:
    def __init__(self):
        self.requests = {}
        self.cleanup_time = time.time()
    
    def is_allowed(self, identifier, max_requests=100, window=3600):
        """Verifica se request é permitido"""
        if not RATE_LIMIT_ENABLED:
            return True
            
        current_time = time.time()
        
        # Limpeza periódica
        if current_time - self.cleanup_time > 3600:  # 1 hora
            self.cleanup_old_entries(current_time - window)
            self.cleanup_time = current_time
        
        # Verifica limite
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Remove requests antigas
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if current_time - req_time < window
        ]
        
        # Verifica se excedeu limite
        if len(self.requests[identifier]) >= max_requests:
            return False
        
        # Adiciona request atual
        self.requests[identifier].append(current_time)
        return True
    
    def cleanup_old_entries(self, cutoff_time):
        """Remove entradas antigas"""
        self.requests = {
            identifier: [req_time for req_time in times if req_time > cutoff_time]
            for identifier, times in self.requests.items()
            if any(req_time > cutoff_time for req_time in times)
        }

# Instância do rate limiter
rate_limiter = SimpleRateLimiter()

# Decorador para rate limiting
def rate_limit(max_requests=100, window=3600):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not RATE_LIMIT_ENABLED:
                return f(*args, **kwargs)
                
            # Identifica cliente por IP
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            
            if not rate_limiter.is_allowed(client_ip, max_requests, window):
                logging.warning(f"Rate limit exceeded for IP: {client_ip}")
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': 'Too many requests. Please try again later.'
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Função para mascarar tokens em logs
def mask_sensitive_data(data):
    """Mascara dados sensíveis para logs"""
    if not isinstance(data, (dict, str)):
        return data
    
    if isinstance(data, str):
        # Mascara tokens longos
        if len(data) > 20 and any(keyword in data.lower() for keyword in ['token', 'key', 'secret']):
            return data[:8] + '***' + data[-4:]
        return data
    
    # Para dicionários
    masked = {}
    sensitive_keys = ['token', 'key', 'secret', 'password', 'auth', 'api_key', 'access_token']
    
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            if isinstance(value, str) and len(value) > 8:
                masked[key] = value[:4] + '***' + value[-4:]
            else:
                masked[key] = '***'
        else:
            masked[key] = value
    
    return masked

# Validador de entrada
def validate_date_input(date_string):
    """Valida entrada de data"""
    if not date_string:
        return False, "Data é obrigatória"
    
    try:
        from datetime import datetime
        datetime.strptime(date_string, '%Y-%m-%d')
        return True, None
    except ValueError:
        return False, "Formato de data inválido. Use YYYY-MM-DD"

def validate_client_id(client_id):
    """Valida ID do cliente"""
    if not client_id:
        return False, "ID do cliente é obrigatório"
    
    try:
        client_id = int(client_id)
        if client_id <= 0:
            return False, "ID do cliente deve ser positivo"
        return True, None
    except (ValueError, TypeError):
        return False, "ID do cliente deve ser um número"

# Função para sanitizar entrada
def sanitize_input(value, max_length=1000):
    """Sanitiza entrada do usuário"""
    if not isinstance(value, str):
        return str(value)
    
    # Remove caracteres perigosos
    dangerous_chars = ['<', '>', '"', "'", '&', '\0', '\r', '\n']
    for char in dangerous_chars:
        value = value.replace(char, '')
    
    # Limita tamanho
    if len(value) > max_length:
        value = value[:max_length]
    
    return value.strip()

# Configurações específicas para produção
PRODUCTION_CONFIG = {
    'SECRET_KEY': generate_secure_secret_key(),
    'SESSION_COOKIE_SECURE': True,  # HTTPS only
    'SESSION_COOKIE_HTTPONLY': True,  # No JavaScript access
    'SESSION_COOKIE_SAMESITE': 'Lax',  # CSRF protection
    'PERMANENT_SESSION_LIFETIME': 3600,  # 1 hour
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max upload
}

# Configurações para desenvolvimento
DEVELOPMENT_CONFIG = {
    'SECRET_KEY': 'dev-secret-key-not-for-production',
    'SESSION_COOKIE_SECURE': False,
    'SESSION_COOKIE_HTTPONLY': True,
    'PERMANENT_SESSION_LIFETIME': 86400,  # 24 hours
}

def get_app_config():
    """Retorna configuração baseada no ambiente"""
    if PRODUCTION_MODE:
        logging.info("🔒 Running in PRODUCTION mode with enhanced security")
        return PRODUCTION_CONFIG
    else:
        logging.info("🔧 Running in DEVELOPMENT mode")
        return DEVELOPMENT_CONFIG

# Headers de segurança
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; font-src 'self' https://cdnjs.cloudflare.com; img-src 'self' data:; connect-src 'self';"
}

def add_security_headers(response):
    """Adiciona headers de segurança"""
    if PRODUCTION_MODE:
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
    return response
