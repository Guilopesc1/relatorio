import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

load_dotenv()

class GoogleAdsAPI:
    def __init__(self):
        """Inicializa API do Google Ads"""
        # Configurações da API do Google Ads
        self.developer_token = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
        self.client_id = os.getenv("GOOGLE_ADS_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_ADS_CLIENT_SECRET")
        self.refresh_token = os.getenv("GOOGLE_ADS_REFRESH_TOKEN")
        self.login_customer_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID")  # Novo
        
        # Inicializa cliente do Google Ads
        self.client = self._initialize_client()
    
    def _initialize_client(self) -> GoogleAdsClient:
        """
        Inicializa o cliente da API do Google Ads
        """
        try:
            # Configuração do cliente
            google_ads_config = {
                "developer_token": self.developer_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
                "use_proto_plus": True
            }
            
            # Adiciona login_customer_id se estiver configurado
            if self.login_customer_id and self.login_customer_id.strip():
                google_ads_config["login_customer_id"] = self.login_customer_id.strip()
                print(f"[DEBUG] Usando login_customer_id: {self.login_customer_id.strip()}")
            
            return GoogleAdsClient.load_from_dict(google_ads_config)
            
        except Exception as e:
            print(f"Erro ao inicializar cliente Google Ads: {e}")
            raise Exception(f"Falha na configuração da API Google Ads: {str(e)}")
    
    def validate_date_range(self, start_date: str, end_date: str) -> bool:
        """
        Valida se o período não excede 90 dias
        """
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Verifica se não excede 90 dias
            if (end - start).days > 90:
                return False
            
            # Verifica se as datas são válidas
            if start > end or end > datetime.now():
                return False
                
            return True
        except ValueError:
            return False
    
    def get_campaigns_report(self, customer_id: str, start_date: str, end_date: str) -> List[Dict]:
        """
        Busca relatório de campanhas do Google Ads
        
        Args:
            customer_id: ID do cliente Google Ads (formato: 1234567890)
            start_date: Data início (YYYY-MM-DD)
            end_date: Data fim (YYYY-MM-DD)
        """
        
        if not self.validate_date_range(start_date, end_date):
            raise ValueError("Período inválido. Máximo de 90 dias e datas válidas.")
        
        # Sanitiza o customer_id (remove espaços, quebras de linha, etc.)
        customer_id = str(customer_id).strip().replace('\n', '').replace('\r', '')
        
        # Valida formato do customer_id
        if not customer_id.isdigit() or len(customer_id) < 9:
            raise ValueError(f"Customer ID inválido: '{customer_id}'. Deve conter apenas números e ter pelo menos 9 dígitos.")
        
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            # Query GAQL baseada nas colunas do CSV fornecido
            query = f"""
                SELECT 
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    segments.date,
                    metrics.clicks,
                    metrics.conversions,
                    metrics.conversions_value,
                    metrics.ctr,
                    metrics.average_cpc,
                    metrics.impressions,
                    metrics.cost_micros
                FROM campaign 
                WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
                ORDER BY segments.date DESC
            """
            
            print(f"[DEBUG] Executando query para customer {customer_id}: {start_date} a {end_date}")
            
            search_request = self.client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = customer_id
            search_request.query = query
            
            # Executa a query
            results = ga_service.search(request=search_request)
            
            campaigns = []
            campaign_count = 0
            for row in results:
                campaign_data = self._process_campaign_data(row, customer_id)
                campaigns.append(campaign_data)
                campaign_count += 1
                
                # Debug apenas para as primeiras campanhas
                if campaign_count <= 3:
                    print(f"[DEBUG] Campanha {campaign_count}: {campaign_data['nome_campanha']} - {campaign_data['dia']} - Clicks: {campaign_data['clicks']}")
            
            print(f"Google Ads API: {len(campaigns)} registros encontrados para o cliente {customer_id}")
            if campaign_count > 3:
                print(f"[DEBUG] ... e mais {campaign_count - 3} campanhas")
            
            return campaigns
            
        except GoogleAdsException as ex:
            print(f"Google Ads API Exception: {ex}")
            error_details = []
            for error in ex.failure.errors:
                error_details.append(f"{error.error_code.name}: {error.message}")
            raise Exception(f"Erro na API Google Ads: {'; '.join(error_details)}")
        
        except Exception as e:
            print(f"Erro geral na API Google Ads: {e}")
            raise Exception(f"Erro ao buscar dados do Google Ads: {str(e)}")
    
    def _process_campaign_data(self, row, customer_id: str) -> Dict:
        """
        Processa dados brutos da API para formato do CSV
        """
        campaign = row.campaign
        metrics = row.metrics
        segments = row.segments
        
        # Converte micros para valores reais (Google Ads usa micros para valores monetários)
        cost = metrics.cost_micros / 1_000_000 if metrics.cost_micros else 0
        average_cpc = metrics.average_cpc / 1_000_000 if metrics.average_cpc else 0
        conversions_value = metrics.conversions_value if metrics.conversions_value else 0
        
        # Converte a data para string se necessário
        if hasattr(segments.date, 'strftime'):
            date_str = segments.date.strftime('%Y-%m-%d')
        else:
            date_str = str(segments.date)
        
        return {
            'campaign_id': int(campaign.id),  # ID da campanha vai para campaign_id
            'nome_campanha': campaign.name,
            'dia': date_str,
            'clicks': int(metrics.clicks),
            'conversions': int(metrics.conversions),
            'conversions_value': float(conversions_value),
            'ctr': float(metrics.ctr),
            'average_cpc': float(average_cpc),
            'impressions': int(metrics.impressions),
            'cost': float(cost),
            # Campos do nosso sistema - id_google = customer_id
            'customer_id': customer_id  # Mantém para uso interno, será movido para id_google na hora de salvar
        }
    
    def test_connection(self, customer_id: str = None) -> bool:
        """
        Testa conexão com a API do Google Ads
        """
        try:
            if not customer_id:
                # Se não tiver customer_id, faz um teste básico de autenticação
                customer_service = self.client.get_service("CustomerService")
                # Tenta listar clientes acessíveis como teste de conexão
                accessible_customers = customer_service.list_accessible_customers()
                return bool(accessible_customers.resource_names)
            else:
                # Sanitiza o customer_id
                customer_id = str(customer_id).strip().replace('\n', '').replace('\r', '')
                
                # Valida formato
                if not customer_id.isdigit() or len(customer_id) < 9:
                    print(f"Customer ID inválido para teste: '{customer_id}'")
                    return False
                
                # Testa com customer_id específico
                ga_service = self.client.get_service("GoogleAdsService")
                
                query = """
                    SELECT campaign.id 
                    FROM campaign 
                    LIMIT 1
                """
                
                search_request = self.client.get_type("SearchGoogleAdsRequest")
                search_request.customer_id = customer_id
                search_request.query = query
                
                results = ga_service.search(request=search_request)
                # Se chegou até aqui sem erro, a conexão está ok
                return True
                
        except Exception as e:
            print(f"Erro no teste de conexão Google Ads: {e}")
            return False
    
    def get_accessible_customers(self) -> List[Dict]:
        """
        Lista clientes acessíveis via API
        """
        try:
            customer_service = self.client.get_service("CustomerService")
            accessible_customers = customer_service.list_accessible_customers()
            
            customers = []
            for customer_resource in accessible_customers.resource_names:
                # Extrai ID do resource name (formato: customers/1234567890)
                customer_id = customer_resource.split('/')[-1]
                customers.append({
                    'customer_id': customer_id,
                    'resource_name': customer_resource
                })
            
            return customers
            
        except Exception as e:
            print(f"Erro ao listar clientes acessíveis: {e}")
            return []
