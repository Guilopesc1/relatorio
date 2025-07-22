import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv
from whatsapp_formatter import WhatsAppMessageFormatter

load_dotenv()

class EvolutionAPI:
    def __init__(self):
        """Inicializa a classe com configurações da Evolution API"""
        # Configurações corretas baseadas no webhook recebido
        self.base_url = os.getenv('EVOLUTION_BASE_URL', "https://lc-evolution-api.qy8om2.easypanel.host")
        self.instance_name = os.getenv('EVOLUTION_INSTANCE', "Guilherme")
        self.token = os.getenv('EVOLUTION_TOKEN', "3D1F8FB65596-4C32-A0FF-7AD3C64DF81D")
        self.api_url = f"{self.base_url}/message/sendText/{self.instance_name}"
        
        # Headers padrão baseados na documentação
        self.headers = {
            "Content-Type": "application/json",
            "apikey": self.token
        }
        
        # Inicializa o formatador de mensagens
        self.message_formatter = WhatsAppMessageFormatter()
    
    def send_message(self, phone_number, message):
        """
        Envia mensagem de texto via Evolution API
        
        Args:
            phone_number (str): Número do WhatsApp no formato brasileiro
            message (str): Mensagem a ser enviada
            
        Returns:
            dict: Resposta da API ou erro
        """
        try:
            # Formata o número brasileiro (remove caracteres especiais e adiciona 55)
            clean_number = self._format_brazilian_number(phone_number)
            
            # Payload baseado na documentação oficial Evolution API
            payload = {
                "number": clean_number,
                "text": message
            }
            
            print(f"[EvolutionAPI] === DEBUG COMPLETO ===")
            print(f"[EvolutionAPI] Base URL: {self.base_url}")
            print(f"[EvolutionAPI] Instance: {self.instance_name}")
            print(f"[EvolutionAPI] Full URL: {self.api_url}")
            print(f"[EvolutionAPI] Token: {self.token[:20]}...")
            print(f"[EvolutionAPI] Clean Number: {clean_number}")
            print(f"[EvolutionAPI] Headers: {self.headers}")
            print(f"[EvolutionAPI] Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            print(f"[EvolutionAPI] === RESPONSE ===")
            print(f"[EvolutionAPI] Status Code: {response.status_code}")
            print(f"[EvolutionAPI] Response Headers: {dict(response.headers)}")
            print(f"[EvolutionAPI] Response Text: {response.text}")
            
            if response.status_code == 200 or response.status_code == 201:
                return {
                    "success": True,
                    "message": "Mensagem enviada com sucesso!",
                    "data": response.json() if response.content else {}
                }
            else:
                return {
                    "success": False,
                    "message": f"Erro na API: {response.status_code}",
                    "error": response.text,
                    "status_code": response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            print(f"[EvolutionAPI] Erro de conexão: {str(e)}")
            return {
                "success": False,
                "message": f"Erro de conexão: {str(e)}",
                "error": str(e)
            }
        except Exception as e:
            print(f"[EvolutionAPI] Erro geral: {str(e)}")
            return {
                "success": False,
                "message": f"Erro interno: {str(e)}",
                "error": str(e)
            }
    
    def _format_brazilian_number(self, phone_number):
        """
        Formata número brasileiro para o padrão da Evolution API
        
        Args:
            phone_number (str): Número brasileiro
            
        Returns:
            str: Número formatado (ex: 5548999319622)
        """
        # Remove todos os caracteres não numéricos
        clean_number = ''.join(filter(str.isdigit, phone_number))
        
        # Se o número não começar com 55 (código do Brasil), adiciona
        if not clean_number.startswith('55'):
            clean_number = '55' + clean_number
        
        # Verifica se tem o formato correto (55 + DDD + número)
        if len(clean_number) == 13:  # 55 + 2 dígitos DDD + 9 dígitos
            return clean_number
        elif len(clean_number) == 12:  # 55 + 2 dígitos DDD + 8 dígitos (adiciona 9)
            return clean_number[:4] + '9' + clean_number[4:]
        
        return clean_number
    
    def test_connection(self):
        """
        Testa a conexão com a Evolution API - Múltiplos testes
        
        Returns:
            dict: Status da conexão
        """
        results = []
        
        # Teste 1: Endpoint raiz
        print(f"[TEST 1] Testando endpoint raiz: {self.base_url}")
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            result = {
                "test": "root_endpoint",
                "url": self.base_url,
                "status_code": response.status_code,
                "response": response.text[:200],
                "success": response.status_code == 200
            }
            results.append(result)
            print(f"[TEST 1] Status: {response.status_code}")
        except Exception as e:
            results.append({
                "test": "root_endpoint",
                "url": self.base_url,
                "error": str(e),
                "success": False
            })
            print(f"[TEST 1] Erro: {e}")
        
        # Teste 2: Listar instâncias
        instances_url = f"{self.base_url}/instance/fetchInstances"
        print(f"[TEST 2] Testando listar instâncias: {instances_url}")
        try:
            response = requests.get(instances_url, headers=self.headers, timeout=10)
            result = {
                "test": "fetch_instances",
                "url": instances_url,
                "status_code": response.status_code,
                "response": response.text,
                "success": response.status_code == 200
            }
            results.append(result)
            print(f"[TEST 2] Status: {response.status_code}")
        except Exception as e:
            results.append({
                "test": "fetch_instances",
                "url": instances_url,
                "error": str(e),
                "success": False
            })
            print(f"[TEST 2] Erro: {e}")
        
        # Teste 3: Conectar instância
        connect_url = f"{self.base_url}/instance/connect/{self.instance_name}"
        print(f"[TEST 3] Testando conectar instância: {connect_url}")
        try:
            response = requests.get(connect_url, headers=self.headers, timeout=10)
            result = {
                "test": "connect_instance",
                "url": connect_url,
                "status_code": response.status_code,
                "response": response.text,
                "success": response.status_code == 200
            }
            results.append(result)
            print(f"[TEST 3] Status: {response.status_code}")
        except Exception as e:
            results.append({
                "test": "connect_instance",
                "url": connect_url,
                "error": str(e),
                "success": False
            })
            print(f"[TEST 3] Erro: {e}")
        
        # Teste 4: Endpoint de envio (teste de existência)
        print(f"[TEST 4] Testando endpoint de envio: {self.api_url}")
        fake_payload = {"number": "5511999999999", "text": "test"}
        try:
            response = requests.post(self.api_url, headers=self.headers, json=fake_payload, timeout=10)
            result = {
                "test": "send_endpoint",
                "url": self.api_url,
                "status_code": response.status_code,
                "response": response.text,
                "success": response.status_code != 404
            }
            results.append(result)
            print(f"[TEST 4] Status: {response.status_code}")
        except Exception as e:
            results.append({
                "test": "send_endpoint",
                "url": self.api_url,
                "error": str(e),
                "success": False
            })
            print(f"[TEST 4] Erro: {e}")
        
        # Resumo
        successful_tests = sum(1 for r in results if r['success'])
        total_tests = len(results)
        
        return {
            "success": successful_tests > 0,
            "message": f"{successful_tests}/{total_tests} testes passaram",
            "tests": results,
            "summary": {
                "successful": successful_tests,
                "total": total_tests,
                "instance_name": self.instance_name,
                "token_preview": self.token[:20] + "..."
            }
        }
    
    def format_report_message(self, client_name, platform, start_date, end_date, 
                            campaigns_data=None, conversion_type='leads'):
        """
        Formata mensagem personalizada baseada no tipo de conversão
        
        Args:
            client_name (str): Nome do cliente
            platform (str): Plataforma (facebook/google)
            start_date (str): Data de início
            end_date (str): Data de fim
            campaigns_data (list): Dados das campanhas (NOVO)
            conversion_type (str): Tipo de conversão ('leads' ou 'compras')
            
        Returns:
            str: Mensagem formatada
        """
        if campaigns_data:
            # Usa o formatador personalizado com dados reais
            return self.message_formatter.format_report_message(
                client_name, platform, start_date, end_date, 
                campaigns_data, conversion_type
            )
        else:
            # Fallback para mensagem simples (mantém compatibilidade)
            timestamp = datetime.now().strftime("%d/%m/%Y às %H:%M")
            
            message = f"""🔄 *RELATÓRIO GERADO*

👤 *Cliente:* {client_name}
📱 *Plataforma:* {platform.title()}
📅 *Período:* {start_date} a {end_date}"""

            message += f"""

✅ O relatório foi gerado e salvo no sistema.
🕒 *Gerado em:* {timestamp}

---
_Sistema de Relatórios Facebook_"""
            
            return message
    
    def format_google_ads_message(self, client_name, start_date, end_date, campaigns_data):
        """
        Formata mensagem personalizada para Google Ads
        
        Args:
            client_name (str): Nome do cliente
            start_date (str): Data de início
            end_date (str): Data de fim
            campaigns_data (list): Dados das campanhas Google Ads
            
        Returns:
            str: Mensagem formatada
        """
        if campaigns_data:
            # Usa o formatador personalizado com dados reais do Google Ads
            return self.message_formatter.format_google_ads_message(
                client_name, start_date, end_date, campaigns_data
            )
        else:
            # Fallback para mensagem simples
            timestamp = datetime.now().strftime("%d/%m/%Y às %H:%M")
            
            message = f"""🔄 *RELATÓRIO GOOGLE ADS GERADO*

👤 *Cliente:* {client_name}
📊 *Plataforma:* Google Ads
📅 *Período:* {start_date} a {end_date}

✅ O relatório foi gerado e salvo no sistema.
🕒 *Gerado em:* {timestamp}

---
_Sistema de Relatórios Google Ads_"""
            
            return message

# Teste simples se executado diretamente
if __name__ == "__main__":
    evolution = EvolutionAPI()
    
    # Teste de conexão
    print("=== TESTE DE CONEXÃO ===")
    result = evolution.test_connection()
    print(f"Resultado: {result}")
    
    print("\n=== TESTE DE FORMATAÇÃO ===")
    test_numbers = ["48999319622", "5548999319622"]
    for num in test_numbers:
        formatted = evolution._format_brazilian_number(num)
        print(f"{num} -> {formatted}")
    
    # Teste de envio (descomente para testar)
    print("\n=== TESTE DE ENVIO (DESABILITADO) ===")
    print("Para testar envio, descomente as linhas abaixo")
    
    # Descomente para testar envio real
    # test_message = f"🔄 TESTE DA EVOLUTION API\n\n✅ Teste realizado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
    # send_result = evolution.send_message("48999319622", test_message)
    # print(f"Envio: {send_result}")
