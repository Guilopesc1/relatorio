import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import List, Dict, Optional
from datetime import datetime

# Carrega variáveis de ambiente
load_dotenv()

class Database:
    def __init__(self):
        """Inicializa conexão com Supabase"""
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(self.url, self.key)
    
    def get_active_facebook_clients(self) -> List[Dict]:
        """
        Busca clientes ativos no Facebook
        """
        try:
            # Busca todos os registros primeiro para debug
            response = self.supabase.table('relatorio_cadastro_clientes') \
                .select('*') \
                .execute()
            
            if not response.data:
                print("Debug: Nenhum cliente encontrado na tabela")
                return []
            
            # Filtra localmente para garantir o controle
            active_clients = []
            print(f"Debug: Total clientes na base: {len(response.data)}")
            
            for client in response.data:
                # Verifica diferentes formatos possíveis para o campo boolean
                roda_fb = client.get('roda_facebook')
                client_name = client.get('name', 'N/A')
                
                print(f"Debug: Cliente '{client_name}' - roda_facebook: {roda_fb} (tipo: {type(roda_fb)})")
                
                # Aceita True, true, 1, "true", "1" como valores válidos
                if roda_fb in [True, 1, "true", "True", "1", 1.0]:
                    active_clients.append(client)
                    print(f"  -> Adicionado como ativo")
                else:
                    print(f"  -> Ignorado (inativo)")
            
            print(f"Debug: Clientes Facebook ativos encontrados: {len(active_clients)}")
            
            return active_clients
            
        except Exception as e:
            print(f"Erro ao buscar clientes Facebook: {e}")
            return []
    
    def get_active_google_clients(self) -> List[Dict]:
        """
        Busca clientes ativos no Google
        """
        try:
            # Busca todos os registros primeiro para debug
            response = self.supabase.table('relatorio_cadastro_clientes') \
                .select('*') \
                .execute()
            
            if not response.data:
                print("Debug: Nenhum cliente encontrado na tabela")
                return []
            
            # Filtra localmente para garantir o controle
            active_clients = []
            print(f"Debug: Total clientes na base: {len(response.data)}")
            
            for client in response.data:
                # Verifica diferentes formatos possíveis para o campo boolean
                roda_google = client.get('roda_google')
                client_name = client.get('name', 'N/A')
                
                print(f"Debug: Cliente '{client_name}' - roda_google: {roda_google} (tipo: {type(roda_google)})")
                
                # Aceita True, true, 1, "true", "1" como valores válidos
                if roda_google in [True, 1, "true", "True", "1", 1.0]:
                    active_clients.append(client)
                    print(f"  -> Adicionado como ativo")
                else:
                    print(f"  -> Ignorado (inativo)")
            
            print(f"Debug: Clientes Google ativos encontrados: {len(active_clients)}")
            
            return active_clients
            
        except Exception as e:
            print(f"Erro ao buscar clientes Google: {e}")
            return []


    



    def get_client_by_id(self, client_id: int) -> Optional[Dict]:
        """
        Busca cliente específico por ID
        """
        try:
            response = self.supabase.table('relatorio_cadastro_clientes') \
                .select('*') \
                .eq('id', client_id) \
                .single() \
                .execute()
            
            return response.data if response.data else None
        except Exception as e:
            print(f"Erro ao buscar cliente {client_id}: {e}")
            return None
            
    # =============================================
    # MÉTODOS PARA USUÁRIOS ESPECÍFICOS
    # =============================================
    
    def get_user_facebook_clients(self, user_id: str) -> List[Dict]:
        """
        Busca clientes Facebook que o usuário tem acesso
        """
        try:
            # Query para buscar clientes do usuário via JOIN
            response = self.supabase.table('user_clients') \
                .select('*, relatorio_cadastro_clientes(*)') \
                .eq('user_id', user_id) \
                .eq('platform', 'facebook') \
                .eq('is_active', True) \
                .execute()
            
            facebook_clients = []
            for user_client in response.data:
                if user_client.get('relatorio_cadastro_clientes'):
                    client = user_client['relatorio_cadastro_clientes']
                    # Verificar se cliente ainda está ativo no Facebook
                    if client.get('roda_facebook', False):
                        facebook_clients.append(client)
            
            print(f"Debug: {len(facebook_clients)} clientes Facebook encontrados para usuário {user_id}")
            return facebook_clients
            
        except Exception as e:
            print(f"Erro ao buscar clientes Facebook do usuário: {e}")
            return []
    
    def get_user_google_clients(self, user_id: str) -> List[Dict]:
        """
        Busca clientes Google Ads que o usuário tem acesso
        """
        try:
            # Query para buscar clientes do usuário via JOIN
            response = self.supabase.table('user_clients') \
                .select('*, relatorio_cadastro_clientes(*)') \
                .eq('user_id', user_id) \
                .eq('platform', 'google') \
                .eq('is_active', True) \
                .execute()
            
            google_clients = []
            for user_client in response.data:
                if user_client.get('relatorio_cadastro_clientes'):
                    client = user_client['relatorio_cadastro_clientes']
                    # Verificar se cliente ainda está ativo no Google
                    if client.get('roda_google', False):
                        google_clients.append(client)
            
            print(f"Debug: {len(google_clients)} clientes Google encontrados para usuário {user_id}")
            return google_clients
            
        except Exception as e:
            print(f"Erro ao buscar clientes Google do usuário: {e}")
            return []
    
    def grant_user_access_to_client(self, user_id: str, client_id: int, platform: str) -> bool:
        """
        Concede acesso de um usuário a um cliente específico
        """
        try:
            response = self.supabase.table('user_clients').insert({
                'user_id': user_id,
                'client_id': client_id,
                'platform': platform,
                'is_active': True
            }).execute()
            
            return bool(response.data)
            
        except Exception as e:
            print(f"Erro ao conceder acesso: {e}")
            return False
    
    def revoke_user_access_to_client(self, user_id: str, client_id: int, platform: str) -> bool:
        """
        Remove acesso de um usuário a um cliente específico
        """
        try:
            response = self.supabase.table('user_clients') \
                .update({'is_active': False}) \
                .eq('user_id', user_id) \
                .eq('client_id', client_id) \
                .eq('platform', platform) \
                .execute()
            
            return bool(response.data)
            
        except Exception as e:
            print(f"Erro ao revogar acesso: {e}")
            return False
    
    def update_last_facebook_report(self, client_id: int, report_date: str):
        """
        Atualiza data do último relatório Facebook
        """
        try:
            self.supabase.table('relatorio_cadastro_clientes') \
                .update({'ultimo_relatorio_fb': report_date}) \
                .eq('id', client_id) \
                .execute()
        except Exception as e:
            print(f"Erro ao atualizar último relatório FB: {e}")


    
    def update_last_google_report(self, client_id: int, report_date: str):
        """
        Atualiza data do último relatório Google
        """
        try:
            self.supabase.table('relatorio_cadastro_clientes') \
                .update({'ultimo_relatorio_google': report_date}) \
                .eq('id', client_id) \
                .execute()
        except Exception as e:
            print(f"Erro ao atualizar último relatório Google: {e}")
    
   
    def check_existing_campaign_data(self, account_id: str, campaign_id: str, date: str) -> bool:
        """
        Verifica se já existem dados para esta campanha nesta data
        
        Args:
            account_id: ID da conta Facebook
            campaign_id: ID da campanha
            date: Data no formato YYYY-MM-DD
            
        Returns:
            bool: True se dados já existem, False caso contrário
        """
        try:
            response = self.supabase.table('relatorio_fb_campaigns') \
                .select('id') \
                .eq('account_id', account_id) \
                .eq('campaign_id', campaign_id) \
                .eq('date_start', date) \
                .execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            print(f"Erro ao verificar dados existentes: {e}")
            # Em caso de erro, assume que não existem dados para evitar perda
            return False
    
    def save_campaign_data(self, campaign_data: List[Dict]) -> Dict:
        """
        Salva dados de campanhas na tabela relatorio_fb_campaigns
        Retorna estatísticas do salvamento
        
        Args:
            campaign_data: Lista de dados de campanhas
            
        Returns:
            Dict: Estatísticas do salvamento (novos, ignorados, erros)
        """
        stats = {
            'total_enviados': len(campaign_data),
            'novos_salvos': 0,
            'duplicados_ignorados': 0,
            'erros': 0,
            'detalhes_erros': []
        }
        
        for campaign in campaign_data:
            try:
                account_id = campaign.get('account_id')
                campaign_id = campaign.get('campaign_id')
                date_start = campaign.get('date_start')
                
                if not all([account_id, campaign_id, date_start]):
                    stats['erros'] += 1
                    stats['detalhes_erros'].append(f"Dados incompletos: {campaign}")
                    continue
                
                # Verifica se já existe
                if self.check_existing_campaign_data(account_id, campaign_id, date_start):
                    stats['duplicados_ignorados'] += 1
                    print(f"Dados já existem - Ignorando: Account {account_id}, Campaign {campaign_id}, Data {date_start}")
                    continue
                
                # Adiciona dados para salvamento (SEM created_at)
                # campaign['created_at'] = datetime.now().isoformat()  # REMOVIDO
                
                # Salva no banco
                campaign.pop('id', None)
                response = self.supabase.table('relatorio_fb_campaigns') \
                    .insert(campaign) \
                    .execute()
                
                if response.data:
                    stats['novos_salvos'] += 1
                    print(f"Dados salvos: Account {account_id}, Campaign {campaign_id}, Data {date_start}")
                else:
                    stats['erros'] += 1
                    stats['detalhes_erros'].append(f"Falha ao salvar: {campaign}")
                    
            except Exception as e:
                stats['erros'] += 1
                error_msg = f"Erro ao processar campanha {campaign.get('campaign_id', 'N/A')}: {str(e)}"
                stats['detalhes_erros'].append(error_msg)
                print(error_msg)
        
        return stats
    
    def filter_new_campaigns(self, campaign_data: List[Dict], account_id: str) -> List[Dict]:
        """
        Filtra apenas campanhas que ainda não existem no banco
        
        Args:
            campaign_data: Lista de dados de campanhas
            account_id: ID da conta Facebook
            
        Returns:
            List[Dict]: Lista apenas com campanhas novas
        """
        if not campaign_data:
            return []
        
        new_campaigns = []
        
        for campaign in campaign_data:
            campaign_id = campaign.get('campaign_id')
            date_start = campaign.get('date_start')
            
            if not campaign_id or not date_start:
                continue
            
            # Verifica se já existe
            if not self.check_existing_campaign_data(account_id, campaign_id, date_start):
                new_campaigns.append(campaign)
            else:
                print(f"Filtrado (já existe): Campaign {campaign_id}, Data {date_start}")
        
        return new_campaigns
    
    def get_existing_campaigns_for_period(self, account_id: str, start_date: str, end_date: str) -> List[Dict]:
        """
        Busca campanhas já existentes no período para um account_id
        
        Args:
            account_id: ID da conta Facebook
            start_date: Data início (YYYY-MM-DD)
            end_date: Data fim (YYYY-MM-DD)
            
        Returns:
            List[Dict]: Lista de registros existentes
        """
        try:
            response = self.supabase.table('relatorio_fb_campaigns') \
                .select('*') \
                .eq('account_id', account_id) \
                .gte('date_start', start_date) \
                .lte('date_start', end_date) \
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"Erro ao buscar campanhas existentes: {e}")
            return []
    
    def get_client_link_grupo_by_name(self, client_name: str) -> Optional[str]:
        """
        Busca o link_grupo de um cliente pelo nome
        
        Args:
            client_name: Nome do cliente
            
        Returns:
            Optional[str]: Link do grupo WhatsApp ou None se não encontrado
        """
        try:
            response = self.supabase.table('relatorio_cadastro_clientes') \
                .select('link_grupo') \
                .eq('name', client_name) \
                .single() \
                .execute()
            
            if response.data and response.data.get('link_grupo'):
                return response.data['link_grupo']
            else:
                print(f"Link grupo não encontrado para cliente: {client_name}")
                return None
                
        except Exception as e:
            print(f"Erro ao buscar link_grupo para cliente {client_name}: {e}")
            return None
    
    def get_client_link_grupo_by_facebook_id(self, facebook_id: str) -> Optional[str]:
        """
        Busca o link_grupo de um cliente pelo ID do Facebook
        
        Args:
            facebook_id: ID do Facebook do cliente
            
        Returns:
            Optional[str]: Link do grupo WhatsApp ou None se não encontrado
        """
        try:
            response = self.supabase.table('relatorio_cadastro_clientes') \
                .select('link_grupo, name, id, tipo_conversao') \
                .eq('id_facebook', facebook_id) \
                .single() \
                .execute()
            
            print(f"[DEBUG] Facebook ID {facebook_id} - Dados encontrados: {bool(response.data)}")
            
            if response.data:
                link_grupo = response.data.get('link_grupo')
                client_name = response.data.get('name', 'N/A')
                client_id = response.data.get('id', 'N/A')
                
                print(f"[DEBUG] Cliente: {client_name} (ID: {client_id}, FB ID: {facebook_id})")
                print(f"[DEBUG] Link grupo: {repr(link_grupo)}")
                
                if link_grupo:
                    return str(link_grupo).strip()
                else:
                    print(f"[DEBUG] Link grupo não configurado para {client_name} (FB ID: {facebook_id})")
                    return None
            else:
                print(f"[DEBUG] Cliente com Facebook ID {facebook_id} não encontrado na tabela")
                return None
                
        except Exception as e:
            print(f"[DEBUG] Erro ao buscar link_grupo para Facebook ID {facebook_id}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_client_conversion_type_by_facebook_id(self, facebook_id: str) -> Optional[str]:
        """
        Busca o tipo de conversão de um cliente pelo ID do Facebook
        
        Args:
            facebook_id: ID do Facebook do cliente
            
        Returns:
            Optional[str]: Tipo de conversão ('leads' ou 'compras') ou None
        """
        try:
            response = self.supabase.table('relatorio_cadastro_clientes') \
                .select('tipo_conversao, name') \
                .eq('id_facebook', facebook_id) \
                .single() \
                .execute()
            
            if response.data:
                tipo_conversao = response.data.get('tipo_conversao', '').lower()
                client_name = response.data.get('name', 'N/A')
                
                print(f"[DEBUG] Tipo de conversão para {client_name}: {tipo_conversao}")
                
                # Normaliza os valores possíveis
                if tipo_conversao in ['leads', 'lead', 'leadgen']:
                    return 'leads'
                elif tipo_conversao in ['compras', 'compra', 'purchase', 'ecommerce']:
                    return 'compras'
                else:
                    print(f"[DEBUG] Tipo de conversão não reconhecido: {tipo_conversao}. Usando 'leads' como padrão")
                    return 'leads'  # Padrão
            else:
                print(f"[DEBUG] Cliente com Facebook ID {facebook_id} não encontrado")
                return 'leads'  # Padrão
                
        except Exception as e:
            print(f"[DEBUG] Erro ao buscar tipo de conversão para Facebook ID {facebook_id}: {e}")
            return 'leads'  # Padrão em caso de erro
    
    def check_existing_google_ads_data(self, customer_id: str, campaign_id: str, date: str) -> bool:
        """
        Verifica se já existem dados para esta campanha Google Ads nesta data
        
        Args:
            customer_id: ID do cliente Google Ads  
            campaign_id: ID da campanha Google
            date: Data no formato YYYY-MM-DD
            
        Returns:
            bool: True se dados já existem, False caso contrário
        """
        try:
            response = self.supabase.table('relatorio_google_ads') \
                .select('id') \
                .eq('customer_id', customer_id) \
                .eq('campaign_id', campaign_id) \
                .eq('dia', date) \
                .execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            print(f"Erro ao verificar dados Google Ads existentes: {e}")
            # Em caso de erro, assume que não existem dados para evitar perda
            return False
    
    def save_google_ads_data(self, campaign_data: List[Dict]) -> Dict:
        """
        Salva dados de campanhas Google Ads na tabela relatorio_google_ads
        Retorna estatísticas do salvamento
        
        Args:
            campaign_data: Lista de dados de campanhas Google Ads
            
        Returns:
            Dict: Estatísticas do salvamento (novos, ignorados, erros)
        """
        stats = {
            'total_enviados': len(campaign_data),
            'novos_salvos': 0,
            'duplicados_ignorados': 0,
            'erros': 0,
            'detalhes_erros': []
        }
        
        for campaign in campaign_data:
            try:
                customer_id = campaign.get('customer_id')
                campaign_id = campaign.get('campaign_id')
                date = campaign.get('dia')
                
                if not all([customer_id, campaign_id, date]):
                    stats['erros'] += 1
                    stats['detalhes_erros'].append(f"Dados incompletos: {campaign}")
                    continue
                
                # Verifica se já existe
                if self.check_existing_google_ads_data(customer_id, campaign_id, date):
                    stats['duplicados_ignorados'] += 1
                    print(f"Dados já existem - Ignorando: Customer {customer_id}, Campaign {campaign_id}, Data {date}")
                    continue
                
                # Remove campos que não existem na tabela
                campaign.pop('id', None)
                campaign.pop('created_at', None)
                
                # Salva no banco
                response = self.supabase.table('relatorio_google_ads') \
                    .insert(campaign) \
                    .execute()
                
                if response.data:
                    stats['novos_salvos'] += 1
                    print(f"Dados Google Ads salvos: Customer {customer_id}, Campaign {campaign_id}, Data {date}")
                else:
                    stats['erros'] += 1
                    stats['detalhes_erros'].append(f"Falha ao salvar: {campaign}")
                    
            except Exception as e:
                stats['erros'] += 1
                error_msg = f"Erro ao processar campanha Google {campaign.get('customer_id', 'N/A')}: {str(e)}"
                stats['detalhes_erros'].append(error_msg)
                print(error_msg)
        
        return stats
    
    def filter_new_google_ads_campaigns(self, campaign_data: List[Dict], customer_id: str) -> List[Dict]:
        """
        Filtra apenas campanhas Google Ads que ainda não existem no banco
        
        Args:
            campaign_data: Lista de dados de campanhas Google Ads
            customer_id: ID do cliente Google Ads
            
        Returns:
            List[Dict]: Lista apenas com campanhas novas
        """
        if not campaign_data:
            return []
        
        new_campaigns = []
        
        for campaign in campaign_data:
            campaign_id = campaign.get('campaign_id')
            date = campaign.get('dia')
            
            if not campaign_id or not date:
                continue
            
            # Verifica se já existe
            if not self.check_existing_google_ads_data(customer_id, campaign_id, date):
                new_campaigns.append(campaign)
            else:
                print(f"Filtrado Google Ads (já existe): Campaign {campaign_id}, Data {date}")
        
        return new_campaigns
    
    def get_existing_google_ads_for_period(self, customer_id: str, start_date: str, end_date: str) -> List[Dict]:
        """
        Busca campanhas Google Ads já existentes no período para um customer_id
        
        Args:
            customer_id: ID do cliente Google Ads
            start_date: Data início (YYYY-MM-DD)
            end_date: Data fim (YYYY-MM-DD)
            
        Returns:
            List[Dict]: Lista de registros existentes
        """
        try:
            response = self.supabase.table('relatorio_google_ads') \
                .select('*') \
                .eq('customer_id', customer_id) \
                .gte('dia', start_date) \
                .lte('dia', end_date) \
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"Erro ao buscar campanhas Google Ads existentes: {e}")
            return []
    
    def get_client_link_grupo_by_google_id(self, google_id: str) -> Optional[str]:
        """
        Busca o link_grupo de um cliente pelo ID do Google
        
        Args:
            google_id: ID do Google do cliente
            
        Returns:
            Optional[str]: Link do grupo WhatsApp ou None se não encontrado
        """
        try:
            # Sanitiza o google_id
            google_id_clean = str(google_id).strip().replace('\n', '').replace('\r', '')
            
            response = self.supabase.table('relatorio_cadastro_clientes') \
                .select('link_grupo, name, id') \
                .eq('id_google', google_id_clean) \
                .single() \
                .execute()
            
            print(f"[DEBUG] Google ID {google_id} (limpo: {google_id_clean}) - Dados encontrados: {bool(response.data)}")
            
            if response.data:
                link_grupo = response.data.get('link_grupo')
                client_name = response.data.get('name', 'N/A')
                client_id = response.data.get('id', 'N/A')
                
                print(f"[DEBUG] Cliente: {client_name} (ID: {client_id}, Google ID: {google_id_clean})")
                print(f"[DEBUG] Link grupo: {repr(link_grupo)}")
                
                if link_grupo:
                    return str(link_grupo).strip()
                else:
                    print(f"[DEBUG] Link grupo não configurado para {client_name} (Google ID: {google_id_clean})")
                    return None
            else:
                print(f"[DEBUG] Cliente com Google ID {google_id_clean} não encontrado na tabela")
                return None
                
        except Exception as e:
            print(f"[DEBUG] Erro ao buscar link_grupo para Google ID {google_id}: {e}")
            import traceback
            traceback.print_exc()
            return None
            
   