#!/usr/bin/env python3
"""
Execução Manual do Sistema de Atualização Diária
Permite executar a coleta de dados de ontem manualmente para teste

Uso:
    python run_daily_manual.py
    python run_daily_manual.py --date 2025-07-21  # Data específica
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# Adiciona diretório do projeto
sys.path.append(str(Path(__file__).parent))

def main():
    """Função principal para execução manual"""
    
    parser = argparse.ArgumentParser(description='Executa atualização diária manual')
    parser.add_argument('--date', help='Data específica (YYYY-MM-DD), padrão: ontem')
    parser.add_argument('--dry-run', action='store_true', help='Simula execução sem salvar dados')
    
    args = parser.parse_args()
    
    # Determina data
    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d').strftime('%Y-%m-%d')
        except ValueError:
            print("❌ Formato de data inválido. Use: YYYY-MM-DD")
            return 1
    else:
        target_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')  # Ontem
    
    print("🔧 EXECUÇÃO MANUAL DA ATUALIZAÇÃO DIÁRIA")
    print("="*50)
    print(f"📅 Data alvo: {target_date}")
    print(f"🧪 Modo: {'Simulação (dry-run)' if args.dry_run else 'Execução real'}")
    print("="*50)
    
    try:
        if args.dry_run:
            return execute_dry_run(target_date)
        else:
            return execute_real_run(target_date)
            
    except KeyboardInterrupt:
        print("\n⚠️ Execução interrompida pelo usuário")
        return 130
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        return 1

def execute_dry_run(target_date):
    """Executa simulação sem salvar dados"""
    
    print("🔍 MODO SIMULAÇÃO (nenhum dado será salvo)")
    print("-"*40)
    
    try:
        from database import Database
        from facebook_api import FacebookAPI
        from google_ads_api import GoogleAdsAPI
        
        # Inicializa
        db = Database()
        fb_api = FacebookAPI()
        google_ads_api = GoogleAdsAPI()
        
        # Busca clientes
        facebook_clients = db.get_active_facebook_clients()
        google_clients = db.get_active_google_clients()
        
        total_clients = len(facebook_clients) + len(google_clients)
        print(f"👥 {total_clients} clientes encontrados")
        print(f"   🔵 Facebook: {len(facebook_clients)}")
        print(f"   🟡 Google: {len(google_clients)}")
        
        if total_clients == 0:
            print("⚠️ Nenhum cliente ativo encontrado!")
            return 1
        
        print(f"\n📊 SIMULAÇÃO DE PROCESSAMENTO para {target_date}:")
        print("-"*40)
        
        # Simula Facebook
        if facebook_clients:
            print("🔵 Facebook:")
            for client in facebook_clients:
                name = client.get('name', 'N/A')
                account_id = client.get('act_fb', 'N/A')
                print(f"   📊 {name} ({account_id})")
                
                try:
                    # Testa API (sem salvar)
                    campaigns_data = fb_api.get_campaigns_report(account_id, target_date, target_date)
                    if campaigns_data:
                        print(f"      ✅ {len(campaigns_data)} campanhas encontradas")
                    else:
                        print(f"      ℹ️ Nenhuma campanha no período")
                except Exception as e:
                    print(f"      ❌ Erro: {str(e)[:60]}...")
        
        # Simula Google
        if google_clients:
            print("🟡 Google:")
            for client in google_clients:
                name = client.get('name', 'N/A')
                customer_id = client.get('id_google', 'N/A')
                print(f"   📊 {name} ({customer_id})")
                
                try:
                    # Testa API (sem salvar)
                    campaigns_data = google_ads_api.get_campaigns_report(customer_id, target_date, target_date)
                    if campaigns_data:
                        print(f"      ✅ {len(campaigns_data)} campanhas encontradas")
                    else:
                        print(f"      ℹ️ Nenhuma campanha no período")
                except Exception as e:
                    print(f"      ❌ Erro: {str(e)[:60]}...")
        
        print("\n✅ Simulação concluída!")
        print("💡 Execute sem --dry-run para salvar os dados")
        return 0
        
    except Exception as e:
        print(f"❌ Erro na simulação: {e}")
        return 1

def execute_real_run(target_date):
    """Executa coleta real com salvamento"""
    
    print("🚀 MODO EXECUÇÃO REAL (dados serão salvos)")
    print("-"*40)
    
    try:
        # Importa e executa o script principal
        from daily_auto_update import execute_daily_update
        from database import Database
        from facebook_api import FacebookAPI
        from google_ads_api import GoogleAdsAPI
        
        # Inicializa APIs
        db = Database()
        fb_api = FacebookAPI()
        google_ads_api = GoogleAdsAPI()
        
        # Modifica temporariamente a data (hack para teste manual)
        original_now = datetime.now
        
        def mock_now():
            # Retorna "amanhã" da data alvo, para que ontem seja a data alvo
            return datetime.strptime(target_date, '%Y-%m-%d') + timedelta(days=1)
        
        # Aplica mock
        import daily_auto_update
        datetime.now = mock_now
        
        print(f"📅 Executando para data: {target_date}")
        
        # Executa
        result = execute_daily_update(db, fb_api, google_ads_api)
        
        # Restaura datetime
        datetime.now = original_now
        
        # Mostra resultado
        print("\n📊 RESULTADO:")
        print("-"*20)
        print(f"✅ {result['message']}")
        print(f"📈 Facebook: {result['results']['facebook']['success']}/{result['results']['facebook']['total']}")
        print(f"📈 Google: {result['results']['google']['success']}/{result['results']['google']['total']}")
        
        if result.get('total_errors', 0) > 0:
            print(f"⚠️ {result['total_errors']} erros ocorreram")
        
        return 0 if result['success'] else 1
        
    except Exception as e:
        print(f"❌ Erro na execução: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
