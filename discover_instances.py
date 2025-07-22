"""
DESCOBRIR INSTÂNCIAS DISPONÍVEIS - Evolution API
Este script vai mostrar todas as instâncias disponíveis
"""

import requests
import json

# Configurações
BASE_URL = "http://lc-evolution-api.qy8om2.easypanel.host"
TOKEN = "712fda67-c327-480f-962e-893574a026f6"

headers = {
    "Content-Type": "application/json",
    "apikey": TOKEN
}

print("🔍 DESCOBRINDO INSTÂNCIAS DISPONÍVEIS")
print("=" * 50)

try:
    # Buscar todas as instâncias
    url = f"{BASE_URL}/instance/fetchInstances"
    response = requests.get(url, headers=headers, timeout=10)
    
    print(f"URL: {url}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        instances = response.json()
        print(f"\n📋 INSTÂNCIAS ENCONTRADAS:")
        print(f"Total: {len(instances) if isinstance(instances, list) else 'N/A'}")
        print("-" * 50)
        
        if isinstance(instances, list) and len(instances) > 0:
            for i, instance_data in enumerate(instances):
                print(f"\n🔹 INSTÂNCIA #{i+1}:")
                
                if isinstance(instance_data, dict):
                    # Estrutura típica: {"instance": {...}}
                    instance_info = instance_data.get('instance', instance_data)
                    
                    # Informações principais
                    instance_name = instance_info.get('instanceName', 'N/A')
                    instance_id = instance_info.get('instanceId', 'N/A')  
                    connection_status = instance_info.get('connectionStatus', 'N/A')
                    
                    print(f"   📛 Nome: {instance_name}")
                    print(f"   🆔 ID: {instance_id}")
                    print(f"   🔗 Status: {connection_status}")
                    
                    # Outras informações úteis
                    if 'owner' in instance_info:
                        print(f"   👤 Owner: {instance_info.get('owner', 'N/A')}")
                    
                    if 'profileName' in instance_info:
                        print(f"   📝 Profile: {instance_info.get('profileName', 'N/A')}")
                        
                    if 'profilePictureUrl' in instance_info:
                        print(f"   🖼️ Foto: {instance_info.get('profilePictureUrl', 'N/A')}")
                    
                    # Verifica se é a instância que procuramos
                    if instance_name == "888c8d37-756e-42f7-baf2-71cdcc2cffdd":
                        print(f"   ✅ ESTA É A NOSSA INSTÂNCIA!")
                    elif instance_id == "888c8d37-756e-42f7-baf2-71cdcc2cffdd":
                        print(f"   ✅ ESTA É A NOSSA INSTÂNCIA (por ID)!")
                        
                    # Mostra estrutura completa para debug
                    print(f"   🔍 Dados completos:")
                    for key, value in instance_info.items():
                        if key not in ['instanceName', 'instanceId', 'connectionStatus', 'owner', 'profileName', 'profilePictureUrl']:
                            print(f"      {key}: {value}")
                
                else:
                    print(f"   📄 Dados: {instance_data}")
                
                print("-" * 30)
                
        elif isinstance(instances, list) and len(instances) == 0:
            print("❌ NENHUMA INSTÂNCIA ENCONTRADA!")
            print("Você precisa criar uma instância primeiro no manager da Evolution API")
            print(f"Acesse: {BASE_URL}/manager")
            
        else:
            print(f"⚠️ Formato inesperado da resposta:")
            print(f"Tipo: {type(instances)}")
            print(f"Conteúdo: {instances}")
            
    else:
        print(f"❌ Erro HTTP: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

print(f"\n🎯 PRÓXIMOS PASSOS:")
print("1. Se encontrou instâncias, use o instanceName correto")
print("2. Se não tem instâncias, crie uma no manager:")
print(f"   🌐 {BASE_URL}/manager")
print("3. Verifique se a instância está 'connected'")
print("4. Atualize o código com o instanceName correto")

print(f"\n📝 CÓDIGO PARA ATUALIZAR:")
print("Se encontrou a instância correta, atualize em evolution_api.py:")
print('self.instance_name = "NOME_DA_INSTANCIA_CORRETA"')
