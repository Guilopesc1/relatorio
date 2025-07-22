#!/usr/bin/env python3
"""
Facebook Reports System - Arquivo de Inicialização
Desenvolvido para consulta de dados do Facebook Ads via API
"""

import sys
import os
import subprocess
from pathlib import Path

def check_requirements():
    """Verifica se as dependências estão instaladas"""
    try:
        import flask
        import requests
        import supabase
        import dotenv
        import pandas
        print("✅ Todas as dependências estão instaladas")
        return True
    except ImportError as e:
        print(f"❌ Dependência ausente: {e}")
        print("📦 Instalando dependências...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependências instaladas com sucesso")
            return True
        except subprocess.CalledProcessError:
            print("❌ Erro ao instalar dependências")
            return False

def check_env_file():
    """Verifica se arquivo .env existe e contém as variáveis necessárias"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ Arquivo .env não encontrado")
        return False
    
    required_vars = [
        "FACEBOOK_APP_ID",
        "FACEBOOK_APP_SECRET", 
        "FACEBOOK_ACCESS_TOKEN",
        "SUPABASE_URL",
        "SUPABASE_KEY"
    ]
    
    with open(env_path) as f:
        content = f.read()
        
    missing_vars = []
    for var in required_vars:
        if var not in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variáveis ausentes no .env: {', '.join(missing_vars)}")
        return False
    
    print("✅ Arquivo .env configurado corretamente")
    return True

def main():
    """Função principal de inicialização"""
    print("🚀 Iniciando Facebook Reports System")
    print("=" * 50)
    
    # Verifica dependências
    if not check_requirements():
        print("❌ Falha ao verificar/instalar dependências")
        sys.exit(1)
    
    # Verifica configuração
    if not check_env_file():
        print("❌ Falha na verificação da configuração")
        sys.exit(1)
    
    print("✅ Sistema pronto para iniciar")
    print("=" * 50)
    print("🌐 Iniciando servidor web...")
    
    # Importa e executa a aplicação
    try:
        from app import app
        import os
        
        host = os.getenv('WEB_HOST', '127.0.0.1')
        port = int(os.getenv('WEB_PORT', 5000))
        debug = os.getenv('DEBUG', 'False').lower() == 'true'
        
        print(f"📍 Servidor rodando em: http://{host}:{port}")
        print("🛑 Pressione Ctrl+C para parar")
        
        app.run(host=host, port=port, debug=debug)
        
    except KeyboardInterrupt:
        print("\n👋 Sistema encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar aplicação: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
