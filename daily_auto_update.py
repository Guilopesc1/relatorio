#!/usr/bin/env python3
"""
Script de Atualização Diária Automática
Executa coleta de dados de ONTEM para todos os clientes ativos
Roda independente do Flask via Cron Job

Uso:
    python daily_auto_update.py

Cron Job (todos os dias às 06:00):
    0 6 * * * cd /path/to/project && python daily_auto_update.py >> logs/daily_update.log 2>&1
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Adiciona o diretório do projeto ao path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

# Configuração de logging
log_dir = project_dir / 'logs'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'daily_update.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Função principal do script de atualização diária"""
    
    logger.info("="*80)
    logger.info("🤖 INICIANDO ATUALIZAÇÃO AUTOMÁTICA DIÁRIA")
    logger.info("="*80)
    
    start_time = datetime.now()
    
    try:
        # Importa dependências (dentro do try para capturar erros)
        from database import Database
        from facebook_api import FacebookAPI
        from google_ads_api import GoogleAdsAPI
        from dotenv import load_dotenv
        
        # Carrega variáveis de ambiente
        load_dotenv()
        
        # Verifica se todas as dependências estão disponíveis
        logger.info("✅ Dependências carregadas com sucesso")
        
        # Inicializa classes
        db = Database()
        fb_api = FacebookAPI()
        google_ads_api = GoogleAdsAPI()
        
        logger.info("✅ APIs inicializadas com sucesso")
        
        # Executa atualização diária
        result = execute_daily_update(db, fb_api, google_ads_api)
        
        # Log do resultado
        duration = datetime.now() - start_time
        logger.info("="*80)
        logger.info("🏁 ATUALIZAÇÃO DIÁRIA CONCLUÍDA")
        logger.info("="*80)
        logger.info(f"⏱️  Duração: {duration.total_seconds():.1f} segundos")
        logger.info(f"📊 Resultado: {result['message']}")
        logger.info(f"📈 Facebook: {result['results']['facebook']['success']}/{result['results']['facebook']['total']}")
        logger.info(f"📈 Google: {result['results']['google']['success']}/{result['results']['google']['total']}")
        
        if result.get('total_errors', 0) > 0:
            logger.warning(f"⚠️  {result['total_errors']} erros ocorreram durante a atualização")
        
        # Salva resultado em arquivo JSON para histórico
        save_execution_history(result)
        
        logger.info("✅ Atualização diária finalizada com sucesso")
        return 0
        
    except Exception as e:
        duration = datetime.now() - start_time
        logger.error("="*80)
        logger.error("❌ ERRO NA ATUALIZAÇÃO DIÁRIA")
        logger.error("="*80)
        logger.error(f"⏱️  Duração até erro: {duration.total_seconds():.1f} segundos")
        logger.error(f"🚨 Erro: {str(e)}")
        logger.error("📋 Detalhes do erro:", exc_info=True)
        
        # Salva erro no histórico
        save_error_history(str(e), duration.total_seconds())
        
        return 1

def execute_daily_update(db, fb_api, google_ads_api):
    """
    Executa a atualização diária de todos os clientes ativos
    Busca apenas dados de ONTEM
    
    Args:
        db: Instância da classe Database
        fb_api: Instância da classe FacebookAPI
        google_ads_api: Instância da classe GoogleAdsAPI
        
    Returns:
        dict: Resultado da atualização
    """
    
    # Calcula data: apenas ONTEM
    ontem = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = ontem  # Apenas ontem
    end_date = ontem    # Apenas ontem
    
    logger.info(f"📅 Processando dados de: {ontem} (apenas ontem)")
    
    # Busca clientes ativos
    try:
        facebook_clients = db.get_active_facebook_clients()
        google_clients = db.get_active_google_clients()
    except Exception as e:
        logger.error(f"❌ Erro ao buscar clientes ativos: {e}")
        raise
    
    total_clients = len(facebook_clients) + len(google_clients)
    logger.info(f"👥 Clientes encontrados: {total_clients} (Facebook: {len(facebook_clients)}, Google: {len(google_clients)})")
    
    if total_clients == 0:
        logger.warning("⚠️  Nenhum cliente ativo encontrado!")
        return {
            'success': True,
            'message': 'Nenhum cliente ativo encontrado',
            'date_processed': ontem,
            'results': {
                'facebook': {'total': 0, 'success': 0, 'errors': 0},
                'google': {'total': 0, 'success': 0, 'errors': 0}
            },
            'total_errors': 0
        }
    
    # Inicializa resultados
    results = {
        'facebook': {'total': len(facebook_clients), 'success': 0, 'errors': 0, 'details': []},
        'google': {'total': len(google_clients), 'success': 0, 'errors': 0, 'details': []}
    }
    
    # Processa clientes Facebook
    if facebook_clients:
        logger.info(f"🔵 Processando {len(facebook_clients)} clientes Facebook...")
        for i, client in enumerate(facebook_clients, 1):
            client_name = client.get('name', 'N/A')
            logger.info(f"  📊 {i:2d}/{len(facebook_clients)} - Processando: {client_name}")
            
            try:
                client_result = process_facebook_client(client, start_date, end_date, fb_api, db)
                results['facebook']['details'].append(client_result)
                
                if client_result['success']:
                    results['facebook']['success'] += 1
                    new_records = client_result.get('new_records', 0)
                    if new_records > 0:
                        logger.info(f"    ✅ {new_records} novos registros salvos")
                    else:
                        logger.info(f"    ℹ️  Nenhum dado novo (já existia)")
                else:
                    results['facebook']['errors'] += 1
                    logger.warning(f"    ❌ Erro: {client_result['message']}")
                    
            except Exception as e:
                results['facebook']['errors'] += 1
                error_msg = f"Exceção durante processamento: {str(e)}"
                logger.error(f"    🚨 {error_msg}")
                results['facebook']['details'].append({
                    'client_name': client_name,
                    'success': False,
                    'message': error_msg
                })
    
    # Processa clientes Google
    if google_clients:
        logger.info(f"🟡 Processando {len(google_clients)} clientes Google...")
        for i, client in enumerate(google_clients, 1):
            client_name = client.get('name', 'N/A')
            logger.info(f"  📊 {i:2d}/{len(google_clients)} - Processando: {client_name}")
            
            try:
                client_result = process_google_client(client, start_date, end_date, google_ads_api, db)
                results['google']['details'].append(client_result)
                
                if client_result['success']:
                    results['google']['success'] += 1
                    new_records = client_result.get('new_records', 0)
                    if new_records > 0:
                        logger.info(f"    ✅ {new_records} novos registros salvos")
                    else:
                        logger.info(f"    ℹ️  Nenhum dado novo (já existia)")
                else:
                    results['google']['errors'] += 1
                    logger.warning(f"    ❌ Erro: {client_result['message']}")
                    
            except Exception as e:
                results['google']['errors'] += 1
                error_msg = f"Exceção durante processamento: {str(e)}"
                logger.error(f"    🚨 {error_msg}")
                results['google']['details'].append({
                    'client_name': client_name,
                    'success': False,
                    'message': error_msg
                })
    
    # Calcula estatísticas finais
    total_success = results['facebook']['success'] + results['google']['success']
    total_errors = results['facebook']['errors'] + results['google']['errors']
    
    return {
        'success': True,
        'message': f'Atualização diária concluída: {total_success}/{total_clients} clientes processados',
        'date_processed': ontem,
        'timestamp': datetime.now().isoformat(),
        'results': {
            'facebook': {
                'total': results['facebook']['total'],
                'success': results['facebook']['success'],
                'errors': results['facebook']['errors']
            },
            'google': {
                'total': results['google']['total'],
                'success': results['google']['success'],
                'errors': results['google']['errors']
            }
        },
        'total_errors': total_errors,
        'details': results
    }

def process_facebook_client(client, start_date, end_date, fb_api, db):
    """Processa um cliente Facebook individual"""
    
    client_name = client.get('name', 'N/A')
    account_id = client.get('act_fb')
    
    if not account_id:
        return {
            'client_name': client_name,
            'success': False,
            'message': 'Conta Facebook não configurada',
            'new_records': 0
        }
    
    try:
        # Busca dados via API
        campaigns_data = fb_api.get_campaigns_report(account_id, start_date, end_date)
        
        if not campaigns_data:
            return {
                'client_name': client_name,
                'success': True,
                'message': 'Nenhum dado encontrado para ontem',
                'new_records': 0
            }
        
        # Filtra apenas campanhas novas
        new_campaigns = db.filter_new_campaigns(campaigns_data, account_id)
        
        # Salva apenas dados novos
        new_records = 0
        if new_campaigns:
            save_stats = db.save_campaign_data(new_campaigns)
            new_records = save_stats['novos_salvos']
            
            if save_stats['erros'] > 0:
                return {
                    'client_name': client_name,
                    'success': False,
                    'message': f'Erro ao salvar {save_stats["erros"]} registros',
                    'new_records': new_records
                }
        
        # Atualiza timestamp do último relatório
        db.update_last_facebook_report(client['id'], datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        return {
            'client_name': client_name,
            'success': True,
            'message': f'{new_records} novos registros processados',
            'new_records': new_records
        }
        
    except Exception as e:
        return {
            'client_name': client_name,
            'success': False,
            'message': f'Erro na API Facebook: {str(e)}',
            'new_records': 0
        }

def process_google_client(client, start_date, end_date, google_ads_api, db):
    """Processa um cliente Google individual"""
    
    client_name = client.get('name', 'N/A')
    customer_id = client.get('id_google')
    
    if not customer_id:
        return {
            'client_name': client_name,
            'success': False,
            'message': 'Conta Google não configurada',
            'new_records': 0
        }
    
    try:
        # Busca dados via API
        campaigns_data = google_ads_api.get_campaigns_report(customer_id, start_date, end_date)
        
        if not campaigns_data:
            return {
                'client_name': client_name,
                'success': True,
                'message': 'Nenhum dado encontrado para ontem',
                'new_records': 0
            }
        
        # Filtra apenas campanhas novas
        new_campaigns = db.filter_new_google_ads_campaigns(campaigns_data, customer_id)
        
        # Salva apenas dados novos
        new_records = 0
        if new_campaigns:
            save_stats = db.save_google_ads_data(new_campaigns)
            new_records = save_stats['novos_salvos']
            
            if save_stats['erros'] > 0:
                return {
                    'client_name': client_name,
                    'success': False,
                    'message': f'Erro ao salvar {save_stats["erros"]} registros',
                    'new_records': new_records
                }
        
        # Atualiza timestamp do último relatório
        db.update_last_google_report(client['id'], datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        return {
            'client_name': client_name,
            'success': True,
            'message': f'{new_records} novos registros processados',
            'new_records': new_records
        }
        
    except Exception as e:
        return {
            'client_name': client_name,
            'success': False,
            'message': f'Erro na API Google: {str(e)}',
            'new_records': 0
        }

def save_execution_history(result):
    """Salva histórico de execução em arquivo JSON"""
    
    try:
        history_dir = Path(__file__).parent / 'logs' / 'history'
        history_dir.mkdir(exist_ok=True)
        
        # Nome do arquivo com data
        date_str = datetime.now().strftime('%Y-%m-%d')
        history_file = history_dir / f'daily_update_{date_str}.json'
        
        import json
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        logger.info(f"📄 Histórico salvo em: {history_file}")
        
    except Exception as e:
        logger.error(f"⚠️  Erro ao salvar histórico: {e}")

def save_error_history(error_msg, duration):
    """Salva histórico de erro"""
    
    try:
        history_dir = Path(__file__).parent / 'logs' / 'history'
        history_dir.mkdir(exist_ok=True)
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        error_file = history_dir / f'daily_update_ERROR_{date_str}.json'
        
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'error': error_msg,
            'duration_seconds': duration,
            'success': False
        }
        
        import json
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(error_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"📄 Erro salvo em: {error_file}")
        
    except Exception as e:
        logger.error(f"⚠️  Erro ao salvar histórico de erro: {e}")

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
