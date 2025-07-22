"""
CRIAR NOVA INSTÂNCIA - Evolution API
Este script criará uma nova instância para usar no sistema
"""

import requests
import json
from datetime import datetime

# Configurações
BASE_URL = "http://lc-evolution-api.qy8om2.easypanel.host"
TOKEN = "712fda67-c327-480f-962e-893574a026f6"

headers = {
    "Content-Type": "application/json",
    "apikey": TOKEN
}

print("🚀 CRIANDO NOVA INSTÂNCIA EVOLUTION API")
print("=" * 50)

# Primeiro, listar instâncias existentes
print("📋 VERIFICANDO INSTÂNCIAS EXISTENTES...")
try:
    url = f"{BASE_URL}/instance/fetchInstances"
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        instances = response.json()
        print(f"✅ Instâncias existentes: {len(instances) if isinstance(instances, list) else 0}")
        
        if isinstance(instances, list) and len(instances) > 0:
            print("📋 Lista de instâncias:")
            for i, instance_data in enumerate(instances):
                if isinstance(instance_data, dict):
                    instance_info = instance_data.get('instance', instance_data)
                    instance_name = instance_info.get('instanceName', 'N/A')
                    connection_status = instance_info.get('connectionStatus', 'N/A')
                    print(f"   {i+1}. {instance_name} - Status: {connection_status}")
        else:
            print("📝 Nenhuma instância encontrada - vamos criar uma!")
            
    else:
        print(f"❌ Erro ao listar instâncias: {response.status_code}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

# Criar nova instância
print(f"\n🔧 CRIANDO NOVA INSTÂNCIA...")
instance_name = f"facebook_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

create_payload = {
    "instanceName": instance_name,
    "qrcode": True,
    "integration": "WHATSAPP-BAILEYS"
}

try:
    url = f"{BASE_URL}/instance/create"
    response = requests.post(url, headers=headers, json=create_payload, timeout=30)
    
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(create_payload, indent=2)}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200 or response.status_code == 201:
        result = response.json()
        print(f"✅ INSTÂNCIA CRIADA COM SUCESSO!")
        print(f"📛 Nome da instância: {instance_name}")
        
        # Verificar se há QR Code
        if 'qrcode' in result:
            print(f"📱 QR Code disponível - escaneie no WhatsApp para conectar")
            print(f"🔗 Ou acesse: {BASE_URL}/manager")
            
        print(f"\n🔧 ATUALIZE SEU CÓDIGO:")
        print(f"Em evolution_api.py, substitua:")
        print(f'self.instance_name = "{instance_name}"')
        
    else:
        print(f"❌ Erro ao criar instância: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

print(f"\n📝 PRÓXIMOS PASSOS:")
print("1. Se a instância foi criada, use o nome fornecido")
print("2. Escaneie o QR Code no WhatsApp")
print("3. Atualize o código com o nome correto")
print("4. Teste novamente o sistema")
print(f"\n🌐 Manager: {BASE_URL}/manager")
