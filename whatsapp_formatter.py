from datetime import datetime
from typing import Dict, List, Optional

class WhatsAppMessageFormatter:
    """
    Classe para formatar mensagens personalizadas do WhatsApp
    baseadas no tipo de conversão (leads ou compras)
    """
    
    def __init__(self):
        pass
    
    def format_date_br(self, date_str: str) -> str:
        """
        Converte data de YYYY-MM-DD para DD/MM/YYYY
        """
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%d/%m/%Y')
        except:
            return date_str
    
    def format_currency(self, value: float) -> str:
        """
        Formata valor para moeda brasileira
        """
        if value == 0:
            return "R$ 0,00"
        return f"R$ {value:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
    
    def format_number(self, value: int) -> str:
        """
        Formata números com separador de milhares
        """
        return f"{value:,}".replace(',', '.')
    
    def calculate_metrics(self, campaigns_data: List[Dict], conversion_type: str) -> Dict:
        """
        Calcula métricas baseadas no tipo de conversão
        """
        metrics = {
            'impressions': 0,
            'clicks': 0,
            'spend': 0.0,
            'landing_page_views': 0,
            'cpc': 0.0,
            'total_conversions': 0,
            'cost_per_conversion': 0.0,
            'has_followers_campaign': False,
            'link_clicks': 0  # Para campanhas de seguidores
        }
        
        # Métricas específicas por tipo
        if conversion_type == 'leads':
            metrics.update({
                'leads': 0,
                'messaging_conversations': 0,
                'registrations': 0
            })
        else:  # compras
            metrics.update({
                'purchases': 0,
                'add_to_cart': 0,
                'initiate_checkout': 0,
                'leads_received': 0
            })
        
        # Verifica se há campanhas de seguidores
        for campaign in campaigns_data:
            campaign_name = campaign.get('campaign_name', '').lower()
            if 'seguidores' in campaign_name or 'seguidor' in campaign_name:
                metrics['has_followers_campaign'] = True
                break
        
        # Soma os valores de todas as campanhas
        for campaign in campaigns_data:
            try:
                metrics['impressions'] += int(campaign.get('impressions', 0) or 0)
                metrics['clicks'] += int(campaign.get('inline_link_clicks', 0) or 0)
                metrics['spend'] += float(campaign.get('spend', 0) or 0)
                metrics['landing_page_views'] += int(campaign.get('landing_page_view', 0) or 0)
                
                # Para campanhas de seguidores, usa link_click
                if metrics['has_followers_campaign']:
                    metrics['link_clicks'] += int(campaign.get('link_click', 0) or 0)
                
                if conversion_type == 'leads':
                    metrics['leads'] += int(campaign.get('offsite_conversion_fb_pixel_lead', 0) or 0)
                    metrics['messaging_conversations'] += int(campaign.get('onsite_conversion_messaging_conversation_started_7d', 0) or 0)
                    metrics['registrations'] += int(campaign.get('offsite_conversion_fb_pixel_complete_registration', 0) or 0)
                    
                    # Total de conversões para leads
                    metrics['total_conversions'] = (metrics['leads'] + 
                                                   metrics['messaging_conversations'] + 
                                                   metrics['registrations'])
                else:  # compras
                    metrics['purchases'] += int(campaign.get('offsite_conversion_fb_pixel_purchase', 0) or 0)
                    metrics['add_to_cart'] += int(campaign.get('offsite_conversion_fb_pixel_add_to_cart', 0) or 0)
                    metrics['initiate_checkout'] += int(campaign.get('offsite_conversion_fb_pixel_initiate_checkout', 0) or 0)
                    metrics['leads_received'] += int(campaign.get('offsite_conversion_fb_pixel_lead', 0) or 0)
                    
                    # Total de conversões para compras (só as compras efetivas)
                    metrics['total_conversions'] = metrics['purchases']
                    
            except (ValueError, TypeError) as e:
                print(f"[WARNING] Erro ao processar dados da campanha {campaign.get('campaign_name', 'N/A')}: {e}")
                continue
        
        # Calcula CPC
        if metrics['clicks'] > 0:
            metrics['cpc'] = metrics['spend'] / metrics['clicks']
        
        # Calcula custo por conversão
        if metrics['total_conversions'] > 0:
            metrics['cost_per_conversion'] = metrics['spend'] / metrics['total_conversions']
        
        return metrics
    
    def format_leads_message(self, client_name: str, start_date: str, end_date: str, 
                           campaigns_data: List[Dict]) -> str:
        """
        Formata mensagem para campanhas de leads
        """
        metrics = self.calculate_metrics(campaigns_data, 'leads')
        
        start_date_br = self.format_date_br(start_date)
        end_date_br = self.format_date_br(end_date)
        
        # Determina se tem CPC ou N/A
        cpc_text = self.format_currency(metrics['cpc']) if metrics['cpc'] > 0 else "N/A"
        
        # Determina custo por lead
        cost_per_lead_text = self.format_currency(metrics['cost_per_conversion']) if metrics['cost_per_conversion'] > 0 else "N/A"
        
        message = f"""📊 *{client_name}*
🎯 *Meta Ads*
📅 *Período de análise:* {start_date_br} à {end_date_br}

*Desempenho Geral:*
👁️ Total de Impressões: {self.format_number(metrics['impressions'])}
🖱️ Cliques nos anúncios: {self.format_number(metrics['clicks'])}
🌐 Visitas ao Site: {self.format_number(metrics['landing_page_views'])}
💰 Total Investido: {self.format_currency(metrics['spend'])}
💸 Custo por Clique: {cpc_text}
📋 Total de Leads Gerados: {self.format_number(metrics['total_conversions'])}
💵 Custo por Lead: {cost_per_lead_text}"""
        
        # Se houver campanhas de seguidores, adiciona métrica específica
        if metrics['has_followers_campaign']:
            message += f"\n👥 Novos Seguidores: {self.format_number(metrics['link_clicks'])}"
        
        # # Adiciona detalhamento se houver dados específicos
        # if metrics['leads'] > 0 or metrics['messaging_conversations'] > 0 or metrics['registrations'] > 0:
        #     message += f"\n\n*Detalhamento dos Leads:*"
        #     if metrics['leads'] > 0:
        #         message += f"\n📝 Formulários Preenchidos: {self.format_number(metrics['leads'])}"
        #     if metrics['messaging_conversations'] > 0:
        #         message += f"\n💬 Conversas Iniciadas: {self.format_number(metrics['messaging_conversations'])}"
        #     if metrics['registrations'] > 0:
        #         message += f"\n✅ Registros Concluídos: {self.format_number(metrics['registrations'])}"
        
        return message
    
    def format_compras_message(self, client_name: str, start_date: str, end_date: str, 
                             campaigns_data: List[Dict]) -> str:
        """
        Formata mensagem para campanhas de compras
        """
        metrics = self.calculate_metrics(campaigns_data, 'compras')
        
        start_date_br = self.format_date_br(start_date)
        end_date_br = self.format_date_br(end_date)
        
        # Determina custo por compra
        cost_per_purchase_text = self.format_currency(metrics['cost_per_conversion']) if metrics['cost_per_conversion'] > 0 else "–"
        
        message = f"""📊 *{client_name}*
🎯 *Meta Ads*
📅 *Período de análise:* {start_date_br} a {end_date_br}

*Desempenho Geral:*
👀 Impressões: {self.format_number(metrics['impressions'])}
📈 Cliques nos anúncios: {self.format_number(metrics['clicks'])}
📊 Custo por Clique: {self.format_currency(metrics['cpc'])}
💵 Total Investido: {self.format_currency(metrics['spend'])}
🙋 Compras: {self.format_number(metrics['purchases'])}
👉🏻 Custo por Compra: {cost_per_purchase_text}
🛒 Carrinhos Abandonados: {self.format_number(metrics['add_to_cart'])}
🪪 Checkout Iniciados: {self.format_number(metrics['initiate_checkout'])}
🙋 Leads Recebidos: {self.format_number(metrics['leads_received'])}"""
        
        return message
    
    def format_report_message(self, client_name: str, platform: str, start_date: str, 
                            end_date: str, campaigns_data: List[Dict], 
                            conversion_type: str = 'leads') -> str:
        """
        Formata mensagem baseada no tipo de conversão
        
        Args:
            client_name: Nome do cliente
            platform: Plataforma (facebook/google)
            start_date: Data de início
            end_date: Data de fim
            campaigns_data: Dados das campanhas
            conversion_type: 'leads' ou 'compras'
            
        Returns:
            str: Mensagem formatada
        """
        if not campaigns_data:
            return f"""📊 *{client_name}*
🎯 *{platform.title()} Ads*
📅 *Período:* {self.format_date_br(start_date)} a {self.format_date_br(end_date)}

❌ *Nenhum dado encontrado para este período*"""
        
        print(f"[DEBUG] Formatando mensagem para {client_name} - Tipo: {conversion_type}")
        
        if conversion_type == 'compras':
            return self.format_compras_message(client_name, start_date, end_date, campaigns_data)
        else:
            return self.format_leads_message(client_name, start_date, end_date, campaigns_data)
    
    def calculate_google_ads_metrics(self, campaigns_data: List[Dict]) -> Dict:
        """
        Calcula métricas para campanhas do Google Ads
        """
        metrics = {
            'impressions': 0,
            'clicks': 0,
            'cost': 0.0,
            'conversions': 0,
            'conversions_value': 0.0,
            'ctr': 0.0,
            'average_cpc': 0.0,
            'cost_per_conversion': 0.0
        }
        
        total_campaigns = len(campaigns_data)
        total_ctr = 0.0
        total_cpc = 0.0
        
        for campaign in campaigns_data:
            try:
                metrics['impressions'] += int(campaign.get('impressions', 0) or 0)
                metrics['clicks'] += int(campaign.get('clicks', 0) or 0)
                metrics['cost'] += float(campaign.get('cost', 0) or 0)
                metrics['conversions'] += int(campaign.get('conversions', 0) or 0)
                metrics['conversions_value'] += float(campaign.get('conversions_value', 0) or 0)
                
                # Soma CTR e CPC para cálculo da média
                total_ctr += float(campaign.get('ctr', 0) or 0)
                total_cpc += float(campaign.get('average_cpc', 0) or 0)
                
            except (ValueError, TypeError) as e:
                print(f"[WARNING] Erro ao processar dados da campanha Google Ads {campaign.get('nome_campanha', 'N/A')}: {e}")
                continue
        
        # Calcula médias
        if total_campaigns > 0:
            metrics['ctr'] = total_ctr / total_campaigns
            metrics['average_cpc'] = total_cpc / total_campaigns
        
        # Calcula custo por conversão
        if metrics['conversions'] > 0:
            metrics['cost_per_conversion'] = metrics['cost'] / metrics['conversions']
        
        return metrics
    
    def format_google_ads_message(self, client_name: str, start_date: str, end_date: str, 
                                campaigns_data: List[Dict]) -> str:
        """
        Formata mensagem para campanhas do Google Ads
        """
        if not campaigns_data:
            return f"""📊 *{client_name}*
🎯 *Google Ads*
📅 *Período:* {self.format_date_br(start_date)} a {self.format_date_br(end_date)}

❌ *Nenhum dado encontrado para este período*"""
        
        metrics = self.calculate_google_ads_metrics(campaigns_data)
        
        start_date_br = self.format_date_br(start_date)
        end_date_br = self.format_date_br(end_date)
        
        # Formata valores
        ctr_text = f"{metrics['ctr']:.2f}%" if metrics['ctr'] > 0 else "N/A"
        cpc_text = self.format_currency(metrics['average_cpc']) if metrics['average_cpc'] > 0 else "N/A"
        cost_per_conversion_text = self.format_currency(metrics['cost_per_conversion']) if metrics['cost_per_conversion'] > 0 else "N/A"
        conversions_value_text = self.format_currency(metrics['conversions_value']) if metrics['conversions_value'] > 0 else "N/A"
        
        message = f"""📊 *{client_name}*
🎯 *Google Ads*
📅 *Período de análise:* {start_date_br} à {end_date_br}

*Desempenho Geral:*
👁️ Total de Impressões: {self.format_number(metrics['impressions'])}
🖱️ Cliques nos anúncios: {self.format_number(metrics['clicks'])}
📊 Taxa de Cliques (CTR): {ctr_text}
💰 Total Investido: {self.format_currency(metrics['cost'])}
💸 Custo por Clique (CPC): {cpc_text}
🎯 Total de Conversões: {self.format_number(metrics['conversions'])}
💵 Custo por Conversão: {cost_per_conversion_text}
💎 Valor das Conversões: {conversions_value_text}"""
        
        return message
