import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class FacebookAPI:
    def __init__(self):
        """Inicializa API do Facebook"""
        self.app_id = os.getenv("FACEBOOK_APP_ID")
        self.app_secret = os.getenv("FACEBOOK_APP_SECRET")
        self.access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def validate_date_range(self, start_date: str, end_date: str) -> bool:
        """
        Valida se o período não excede 90 dias
        """
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Verifica se não excede 90 dias
            if (end - start).days > 60:
                return False
            
            # Verifica se as datas são válidas
            if start > end or end > datetime.now():
                return False
                
            return True
        except ValueError:
            return False
    
    def get_campaigns_report(self, account_id: str, start_date: str, end_date: str) -> List[Dict]:
        """
        Busca relatório de campanhas do Facebook
        
        Args:
            account_id: ID da conta Facebook (formato: act_123456789)
            start_date: Data início (YYYY-MM-DD)
            end_date: Data fim (YYYY-MM-DD)
        """
        
        if not self.validate_date_range(start_date, end_date):
            raise ValueError("Período inválido. Máximo de 90 dias e datas válidas.")
        
        # Campos baseados no CSV fornecido
        fields = [
            'account_id',
            'campaign_id', 
            'campaign_name',
            'date_start',
            'reach',
            'impressions',
            'spend',
            'inline_link_clicks',
            'actions',  # Para capturar conversões
            'cost_per_action_type'
        ]
        
        # Ações específicas que queremos capturar
        action_breakdowns = [
            'link_click',
            'landing_page_view',
            'offsite_conversion.fb_pixel_add_to_cart',
            'offsite_conversion.fb_pixel_initiate_checkout',
            'offsite_conversion.fb_pixel_lead',
            'onsite_conversion.messaging_conversation_started_7d',
            'offsite_conversion.fb_pixel_purchase',
            'offsite_conversion.fb_pixel_custom',
            'offsite_conversion.fb_pixel_complete_registration',
            'onsite_conversion.lead_grouped'
        ]
        
        params = {
            'fields': ','.join(fields),
            'time_range': f'{{"since":"{start_date}","until":"{end_date}"}}',
            'time_increment': 1,  # Daily breakdown
            'access_token': self.access_token,
            'level': 'campaign',
            'limit': 1000
        }
        
        try:
            url = f"{self.base_url}/{account_id}/insights"
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            campaigns = []
            
            if 'data' in data:
                for item in data['data']:
                    campaign = self._process_campaign_data(item)
                    campaigns.append(campaign)
            
            return campaigns
            
        except requests.exceptions.RequestException as e:
            print(f"Erro na API do Facebook: {e}")
            raise Exception(f"Erro ao buscar dados do Facebook: {str(e)}")
    
    def _process_campaign_data(self, raw_data: Dict) -> Dict:
        """
        Processa dados brutos da API para formato do CSV
        """
        campaign = {
            'account_id': raw_data.get('account_id', ''),
            'campaign_id': raw_data.get('campaign_id', ''),
            'campaign_name': raw_data.get('campaign_name', ''),
            'date_start': raw_data.get('date_start', ''),
            'reach': int(raw_data.get('reach', 0)),
            'impressions': int(raw_data.get('impressions', 0)),
            'spend': float(raw_data.get('spend', 0)),
            'inline_link_clicks': int(raw_data.get('inline_link_clicks', 0)),
            'link_click': 0,
            'landing_page_view': 0,
            'offsite_conversion_fb_pixel_add_to_cart': 0,
            'offsite_conversion_fb_pixel_initiate_checkout': 0,
            'offsite_conversion_fb_pixel_lead': 0,
            'onsite_conversion_messaging_conversation_started_7d': 0,
            'offsite_conversion_fb_pixel_purchase': 0,
            'offsite_conversion_fb_pixel_custom': 0,
            'offsite_conversion_fb_pixel_complete_registration': 0,
            'onsite_conversion_lead_grouped': 0,
            'id': raw_data.get('campaign_id', '')
        }
        
        # Processa ações (conversões)
        if 'actions' in raw_data:
            for action in raw_data['actions']:
                action_type = action.get('action_type', '')
                value = int(float(action.get('value', 0)))
                
                # Mapeia ações para campos do CSV
                if action_type == 'link_click':
                    campaign['link_click'] = value
                elif action_type == 'landing_page_view':
                    campaign['landing_page_view'] = value
                elif action_type == 'offsite_conversion.fb_pixel_add_to_cart':
                    campaign['offsite_conversion_fb_pixel_add_to_cart'] = value
                elif action_type == 'offsite_conversion.fb_pixel_initiate_checkout':
                    campaign['offsite_conversion_fb_pixel_initiate_checkout'] = value
                elif action_type == 'offsite_conversion.fb_pixel_lead':
                    campaign['offsite_conversion_fb_pixel_lead'] = value
                elif action_type == 'onsite_conversion.messaging_conversation_started_7d':
                    campaign['onsite_conversion_messaging_conversation_started_7d'] = value
                elif action_type == 'offsite_conversion.fb_pixel_purchase':
                    campaign['offsite_conversion_fb_pixel_purchase'] = value
                elif action_type == 'offsite_conversion.fb_pixel_custom':
                    campaign['offsite_conversion_fb_pixel_custom'] = value
                elif action_type == 'offsite_conversion.fb_pixel_complete_registration':
                    campaign['offsite_conversion_fb_pixel_complete_registration'] = value
                elif action_type == 'onsite_conversion.lead_grouped':
                    campaign['onsite_conversion_lead_grouped'] = value
        
        return campaign
    
    def test_connection(self) -> bool:
        """
        Testa conexão com a API do Facebook
        """
        try:
            url = f"{self.base_url}/me"
            params = {'access_token': self.access_token}
            
            response = requests.get(url, params=params)
            return response.status_code == 200
        except:
            return False
