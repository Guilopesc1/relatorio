"""
Sistema para descobrir automaticamente clientes através das conexões OAuth
e conceder acesso aos usuários
"""

import os
from google_oauth import GoogleAdsOAuth
from database import Database
from auth_manager import AuthManager
import requests
from typing import List, Dict

class ClientDiscovery:
    def __init__(self):
        self.db = Database()
        self.auth_manager = AuthManager()
        self.google_oauth = GoogleAdsOAuth(self.auth_manager)
    
    def discover_google_clients(self, user_id: str) -> Dict:
        """
        Descobre clientes Google Ads através do OAuth do usuário
        Inclui verificação de MCC e hierarquia de contas
        """
        try:
            # Obter token válido do usuário
            access_token = self.google_oauth.get_valid_access_token(user_id)
            if not access_token:
                return {'success': False, 'message': 'Token de acesso não disponível'}
            
            # Primeiro, listar contas acessíveis
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'developer-token': os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN')
            }
            
            url = 'https://googleads.googleapis.com/v18/customers:listAccessibleCustomers'
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                return {'success': False, 'message': f'Erro na API: {response.status_code}'}
            
            data = response.json()
            accessible_customers = data.get('resourceNames', [])
            
            if not accessible_customers:
                return {'success': False, 'message': 'Nenhuma conta Google Ads encontrada'}
            
            # Processar cada conta e verificar hierarquia
            discovered_clients = []
            manager_accounts = []
            
            for customer_resource in accessible_customers:
                customer_id = customer_resource.split('/')[-1]
                
                # Buscar informações detalhadas do cliente
                client_info = self._get_google_client_info(customer_id, access_token)
                
                # Verificar se é MCC (Manager Account)
                is_manager = client_info.get('manager', False)
                
                # Verificar se usuário já tem acesso
                has_access = self._user_has_access_to_client(user_id, customer_id)
                
                client_data = {
                    'customer_id': customer_id,
                    'name': client_info.get('name', f'Cliente {customer_id}'),
                    'status': client_info.get('status', 'UNKNOWN'),
                    'currency': client_info.get('currency', 'USD'),
                    'time_zone': client_info.get('time_zone', ''),
                    'is_manager': is_manager,
                    'has_access': has_access,
                    'type': 'MCC (Conta Gerenciadora)' if is_manager else 'Conta Regular'
                }
                
                if is_manager:
                    # Buscar contas filhas do MCC
                    child_accounts = self._get_mcc_child_accounts(customer_id, access_token)
                    client_data['child_accounts'] = child_accounts
                    manager_accounts.append(client_data)
                else:
                    discovered_clients.append(client_data)
            
            # Combinar contas regulares e MCCs
            all_clients = discovered_clients + manager_accounts
            
            return {
                'success': True,
                'message': f'{len(all_clients)} contas descobertas ({len(manager_accounts)} MCCs, {len(discovered_clients)} contas regulares)',
                'clients': all_clients,
                'has_mcc': len(manager_accounts) > 0
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Erro ao descobrir clientes: {str(e)}'}
    
    def _find_or_create_google_client(self, customer_id: str) -> Dict:
        """
        Busca cliente Google existente ou cria um novo se não existir
        """
        try:
            # Buscar cliente existente pelo google_id
            response = self.db.supabase.table('relatorio_cadastro_clientes') \
                .select('*') \
                .eq('id_google', customer_id) \
                .execute()
            
            if response.data:
                return response.data[0]
            
            # Se não existe, criar novo cliente
            new_client = {
                'name': f'Cliente Google {customer_id}',
                'id_google': customer_id,
                'roda_google': True,
                'roda_facebook': False,
                'tipo_conversao': 'lead',
                'created_at': 'now()'
            }
            
            response = self.db.supabase.table('relatorio_cadastro_clientes') \
                .insert(new_client) \
                .execute()
            
            if response.data:
                print(f"Novo cliente Google criado: {customer_id}")
                return response.data[0]
            
            return None
            
        except Exception as e:
            print(f"Erro ao buscar/criar cliente Google {customer_id}: {e}")
            return None
    
    def _get_google_client_info(self, customer_id: str, access_token: str) -> Dict:
        """
        Busca informações detalhadas de um cliente Google Ads
        """
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'developer-token': os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN')
            }
            
            # Query para buscar informações do cliente incluindo se é manager
            query = "SELECT customer.descriptive_name, customer.currency_code, customer.time_zone, customer.status, customer.manager FROM customer"
            
            url = f'https://googleads.googleapis.com/v18/customers/{customer_id}/googleAds:search'
            data = {'query': query}
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('results'):
                    customer_data = result['results'][0]['customer']
                    return {
                        'name': customer_data.get('descriptiveName', f'Cliente {customer_id}'),
                        'currency': customer_data.get('currencyCode', 'USD'),
                        'time_zone': customer_data.get('timeZone', ''),
                        'status': customer_data.get('status', 'UNKNOWN'),
                        'manager': customer_data.get('manager', False)
                    }
            
            return {'name': f'Cliente {customer_id}', 'manager': False}
            
        except Exception as e:
            print(f"Erro ao buscar informações do cliente {customer_id}: {e}")
            return {'name': f'Cliente {customer_id}', 'manager': False}
    
    def _get_mcc_child_accounts(self, mcc_customer_id: str, access_token: str) -> List[Dict]:
        """
        Busca contas filhas de um MCC (Manager Account)
        """
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'developer-token': os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN')
            }
            
            # Query para buscar contas gerenciadas
            query = """
                SELECT 
                    customer_client.client_customer,
                    customer_client.descriptive_name,
                    customer_client.currency_code,
                    customer_client.level,
                    customer_client.manager
                FROM customer_client 
                WHERE customer_client.level = 1
            """
            
            url = f'https://googleads.googleapis.com/v18/customers/{mcc_customer_id}/googleAds:search'
            data = {'query': query}
            
            response = requests.post(url, headers=headers, json=data)
            
            child_accounts = []
            
            if response.status_code == 200:
                result = response.json()
                for row in result.get('results', []):
                    customer_client = row.get('customerClient', {})
                    # Extrair customer ID do resource name
                    client_customer = customer_client.get('clientCustomer', '')
                    customer_id = client_customer.split('/')[-1] if client_customer else ''
                    
                    if customer_id:
                        child_accounts.append({
                            'customer_id': customer_id,
                            'name': customer_client.get('descriptiveName', f'Conta {customer_id}'),
                            'currency': customer_client.get('currencyCode', 'USD'),
                            'is_manager': customer_client.get('manager', False)
                        })
            
            return child_accounts
            
        except Exception as e:
            print(f"Erro ao buscar contas filhas do MCC {mcc_customer_id}: {e}")
            return []
    
    def _user_has_access_to_client(self, user_id: str, customer_id: str) -> bool:
        """
        Verifica se usuário já tem acesso a um cliente Google
        """
        try:
            # Buscar na tabela user_clients
            response = self.db.supabase.table('user_clients') \
                .select('*, relatorio_cadastro_clientes(id_google)') \
                .eq('user_id', user_id) \
                .eq('platform', 'google') \
                .eq('is_active', True) \
                .execute()
            
            for user_client in response.data:
                if user_client.get('relatorio_cadastro_clientes', {}).get('id_google') == customer_id:
                    return True
            
            return False
            
        except Exception as e:
            print(f"Erro ao verificar acesso: {e}")
            return False
    
    def grant_access_to_selected_clients(self, user_id: str, selected_customers: List[str]) -> Dict:
        """
        Concede acesso aos clientes selecionados pelo usuário
        """
        try:
            granted_count = 0
            
            for customer_id in selected_customers:
                # Buscar ou criar cliente
                existing_client = self._find_or_create_google_client(customer_id)
                
                if existing_client:
                    # Conceder acesso
                    success = self.db.grant_user_access_to_client(
                        user_id=user_id,
                        client_id=existing_client['id'],
                        platform='google'
                    )
                    
                    if success:
                        granted_count += 1
                        print(f"Acesso concedido para cliente {customer_id}")
            
            return {
                'success': True,
                'message': f'Acesso concedido a {granted_count} clientes',
                'granted_count': granted_count
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Erro ao conceder acesso: {str(e)}'}
    
    def discover_facebook_clients(self, user_id: str) -> Dict:
        """
        Descobre clientes Facebook através do OAuth do usuário
        TODO: Implementar quando Facebook OAuth estiver pronto
        """
        return {
            'success': False, 
            'message': 'Descoberta automática do Facebook será implementada no próximo passo'
        }
