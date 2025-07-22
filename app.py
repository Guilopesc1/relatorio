from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
import csv
import io
from datetime import datetime, timedelta
from database import Database
from facebook_api import FacebookAPI
from google_ads_api import GoogleAdsAPI
from evolution_api import EvolutionAPI
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Mude para uma chave secreta segura

# Inicializa classes
db = Database()
fb_api = FacebookAPI()
google_ads_api = GoogleAdsAPI()
evolution_api = EvolutionAPI()

@app.route('/')
def index():
    """Página inicial com lista de clientes"""
    try:
        facebook_clients = db.get_active_facebook_clients()
        google_clients = db.get_active_google_clients()
        
        return render_template('index.html', 
                             facebook_clients=facebook_clients,
                             google_clients=google_clients)
    except Exception as e:
        flash(f"Erro ao carregar clientes: {str(e)}", 'error')
        return render_template('index.html', 
                             facebook_clients=[],
                             google_clients=[])

@app.route('/client/<int:client_id>/<platform>')
def client_page(client_id, platform):
    """Página do cliente para gerar relatórios"""
    try:
        client = db.get_client_by_id(client_id)
        if not client:
            flash("Cliente não encontrado", 'error')
            return redirect(url_for('index'))
        
        # Verifica se o cliente está ativo na plataforma
        if platform == 'facebook' and not client.get('roda_facebook'):
            flash("Cliente não está ativo no Facebook", 'error')
            return redirect(url_for('index'))
        
        if platform == 'google' and not client.get('roda_google'):
            flash("Cliente não está ativo no Google", 'error') 
            return redirect(url_for('index'))
        
        return render_template('client.html', 
                             client=client, 
                             platform=platform)
    except Exception as e:
        flash(f"Erro ao carregar cliente: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/generate_report', methods=['POST'])
def generate_report():
    """Gera relatório baseado nos parâmetros"""
    try:
        client_id = int(request.form.get('client_id'))
        platform = request.form.get('platform')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        # Validações básicas
        if not all([client_id, platform, start_date, end_date]):
            flash("Todos os campos são obrigatórios", 'error')
            return redirect(url_for('client_page', client_id=client_id, platform=platform))
        
        # Busca dados do cliente
        client = db.get_client_by_id(client_id)
        if not client:
            flash("Cliente não encontrado", 'error')
            return redirect(url_for('index'))
        
        if platform == 'facebook':
            return generate_facebook_report(client, start_date, end_date)
        elif platform == 'google':
            return generate_google_ads_report(client, start_date, end_date)
        else:
            flash("Plataforma inválida", 'error')
            return redirect(url_for('index'))
            
    except ValueError as e:
        flash(f"Erro nos parâmetros: {str(e)}", 'error')
        return redirect(url_for('client_page', client_id=client_id, platform=platform))
    except Exception as e:
        flash(f"Erro ao gerar relatório: {str(e)}", 'error')
        return redirect(url_for('client_page', client_id=client_id, platform=platform))

def generate_facebook_report(client, start_date, end_date):
    """Gera relatório específico do Facebook"""
    try:
        account_id = client.get('act_fb')
        if not account_id:
            flash("Cliente não possui conta Facebook configurada", 'error')
            return redirect(url_for('client_page', client_id=client['id'], platform='facebook'))
        
        # Busca dados via API
        campaigns_data = fb_api.get_campaigns_report(account_id, start_date, end_date)
        
        if not campaigns_data:
            flash("Nenhum dado encontrado para o período selecionado", 'warning')
            return redirect(url_for('client_page', client_id=client['id'], platform='facebook'))
        
        # Verifica campanhas existentes no período
        existing_campaigns = db.get_existing_campaigns_for_period(account_id, start_date, end_date)
        
        print(f"\n=== RELATÓRIO DE DUPLICATAS ===")
        print(f"Cliente: {client['name']} (Account ID: {account_id})")
        print(f"Período: {start_date} a {end_date}")
        print(f"Campanhas encontradas na API: {len(campaigns_data)}")
        print(f"Campanhas já no banco: {len(existing_campaigns)}")
        
        # Filtra apenas campanhas novas
        new_campaigns = db.filter_new_campaigns(campaigns_data, account_id)
        print(f"Campanhas novas para salvar: {len(new_campaigns)}")
        
        # Salva apenas dados novos no banco
        save_stats = None
        if new_campaigns:
            save_stats = db.save_campaign_data(new_campaigns)
            print(f"\nResultado do salvamento:")
            print(f"  - Novos salvos: {save_stats['novos_salvos']}")
            print(f"  - Duplicados ignorados: {save_stats['duplicados_ignorados']}")
            print(f"  - Erros: {save_stats['erros']}")
            
            if save_stats['erros'] > 0:
                print(f"  - Detalhes dos erros: {save_stats['detalhes_erros']}")
        else:
            print("Nenhuma campanha nova para salvar.")
        
        # Atualiza último relatório no banco
        db.update_last_facebook_report(client['id'], datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Gera mensagem informativa para o usuário
        if save_stats:
            if save_stats['novos_salvos'] > 0:
                flash(f"Relatório gerado! {save_stats['novos_salvos']} novos registros salvos no banco.", 'success')
            if save_stats['duplicados_ignorados'] > 0:
                flash(f"{save_stats['duplicados_ignorados']} registros já existiam e foram ignorados.", 'info')
            if save_stats['erros'] > 0:
                flash(f"{save_stats['erros']} erros ocorreram durante o salvamento.", 'warning')
        
        # Gera CSV para download (com todos os dados da API, independente do que foi salvo)
        return generate_csv_response(campaigns_data, client['name'], start_date, end_date)
        
    except Exception as e:
        flash(f"Erro ao gerar relatório Facebook: {str(e)}", 'error')
        return redirect(url_for('client_page', client_id=client['id'], platform='facebook'))

def generate_google_ads_report(client, start_date, end_date):
    """Gera relatório específico do Google Ads"""
    try:
        customer_id = client.get('id_google')
        if not customer_id:
            flash("Cliente não possui conta Google Ads configurada", 'error')
            return redirect(url_for('client_page', client_id=client['id'], platform='google'))
        
        # Busca dados via API
        campaigns_data = google_ads_api.get_campaigns_report(customer_id, start_date, end_date)
        
        if not campaigns_data:
            flash("Nenhum dado encontrado para o período selecionado", 'warning')
            return redirect(url_for('client_page', client_id=client['id'], platform='google'))
        
        # Verifica campanhas existentes no período
        existing_campaigns = db.get_existing_google_ads_for_period(customer_id, start_date, end_date)
        
        print(f"\n=== RELATÓRIO GOOGLE ADS ====")
        print(f"Cliente: {client['name']} (Customer ID: {customer_id})")
        print(f"Período: {start_date} a {end_date}")
        print(f"Campanhas encontradas na API: {len(campaigns_data)}")
        print(f"Campanhas já no banco: {len(existing_campaigns)}")
        
        # Filtra apenas campanhas novas
        new_campaigns = db.filter_new_google_ads_campaigns(campaigns_data, customer_id)
        print(f"Campanhas novas para salvar: {len(new_campaigns)}")
        
        # Salva apenas dados novos no banco
        save_stats = None
        if new_campaigns:
            save_stats = db.save_google_ads_data(new_campaigns)
            print(f"\nResultado do salvamento:")
            print(f"  - Novos salvos: {save_stats['novos_salvos']}")
            print(f"  - Duplicados ignorados: {save_stats['duplicados_ignorados']}")
            print(f"  - Erros: {save_stats['erros']}")
            
            if save_stats['erros'] > 0:
                print(f"  - Detalhes dos erros: {save_stats['detalhes_erros']}")
        else:
            print("Nenhuma campanha nova para salvar.")
        
        # Atualiza último relatório no banco
        db.update_last_google_report(client['id'], datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Gera mensagem informativa para o usuário
        if save_stats:
            if save_stats['novos_salvos'] > 0:
                flash(f"Relatório Google Ads gerado! {save_stats['novos_salvos']} novos registros salvos no banco.", 'success')
            if save_stats['duplicados_ignorados'] > 0:
                flash(f"{save_stats['duplicados_ignorados']} registros já existiam e foram ignorados.", 'info')
            if save_stats['erros'] > 0:
                flash(f"{save_stats['erros']} erros ocorreram durante o salvamento.", 'warning')
        
        # Gera CSV para download (com todos os dados da API, independente do que foi salvo)
        return generate_google_ads_csv_response(campaigns_data, client['name'], start_date, end_date)
        
    except Exception as e:
        flash(f"Erro ao gerar relatório Google Ads: {str(e)}", 'error')
        return redirect(url_for('client_page', client_id=client['id'], platform='google'))

def generate_csv_response(data, client_name, start_date, end_date):
    """Gera resposta CSV para download"""
    try:
        output = io.StringIO()
        
        if data:
            # Define colunas baseadas no CSV original
            fieldnames = [
                'account_id', 'campaign_id', 'campaign_name', 'date_start',
                'reach', 'impressions', 'spend', 'inline_link_clicks',
                'link_click', 'landing_page_view', 'offsite_conversion_fb_pixel_add_to_cart',
                'offsite_conversion_fb_pixel_initiate_checkout', 'offsite_conversion_fb_pixel_lead',
                'onsite_conversion_messaging_conversation_started_7d', 'offsite_conversion_fb_pixel_purchase',
                'offsite_conversion_fb_pixel_custom', 'offsite_conversion_fb_pixel_complete_registration',
                'onsite_conversion_lead_grouped', 'id'
            ]
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in data:
                writer.writerow(row)
        
        # Prepara resposta
        from flask import make_response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        
        filename = f"relatorio_facebook_{client_name}_{start_date}_{end_date}.csv"
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        flash(f"Erro ao gerar arquivo CSV: {str(e)}", 'error')
        return redirect(url_for('index'))

def generate_google_ads_csv_response(data, client_name, start_date, end_date):
    """Gera resposta CSV para download - Google Ads"""
    try:
        output = io.StringIO()
        
        if data:
            # Define colunas baseadas no CSV do Google Ads
            fieldnames = [
                'id_google', 'nome_campanha', 'dia', 'clicks', 'conversions',
                'conversions_value', 'ctr', 'average_cpc', 'impressions', 'cost'
            ]
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in data:
                # Filtra apenas os campos do CSV
                csv_row = {field: row.get(field, '') for field in fieldnames}
                writer.writerow(csv_row)
        
        # Prepara resposta
        from flask import make_response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        
        filename = f"relatorio_google_ads_{client_name}_{start_date}_{end_date}.csv"
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        flash(f"Erro ao gerar arquivo CSV Google Ads: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/api/test_connection')
def test_connection():
    """Testa conexões com APIs"""
    try:
        fb_status = fb_api.test_connection()
        evolution_status = evolution_api.test_connection()
        google_ads_status = google_ads_api.test_connection()
        
        return jsonify({
            'facebook': fb_status,
            'evolution': evolution_status,
            'google_ads': google_ads_status
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/send_whatsapp', methods=['POST'])
def send_whatsapp():
    """Envia relatório via WhatsApp usando Evolution API"""
    try:
        client_id = int(request.form.get('client_id'))
        platform = request.form.get('platform')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        # Validações básicas
        if not all([client_id, platform, start_date, end_date]):
            flash("Todos os campos são obrigatórios para envio", 'error')
            return redirect(url_for('client_page', client_id=client_id, platform=platform))
        
        # Busca dados do cliente
        client = db.get_client_by_id(client_id)
        if not client:
            flash("Cliente não encontrado", 'error')
            return redirect(url_for('index'))
        
        # Busca o link_grupo do cliente usando id_facebook
        if platform == 'facebook':
            facebook_id = client.get('id_facebook')
            if not facebook_id:
                flash(f"Cliente {client.get('name', 'N/A')} não possui ID do Facebook configurado", 'error')
                return redirect(url_for('client_page', client_id=client_id, platform=platform))
            
            phone_number = db.get_client_link_grupo_by_facebook_id(str(facebook_id))
            conversion_type = db.get_client_conversion_type_by_facebook_id(str(facebook_id))
        elif platform == 'google':
            google_id = client.get('id_google')
            if not google_id:
                flash(f"Cliente {client.get('name', 'N/A')} não possui ID do Google configurado", 'error')
                return redirect(url_for('client_page', client_id=client_id, platform=platform))
            
            phone_number = db.get_client_link_grupo_by_google_id(str(google_id))
            conversion_type = 'leads'  # Padrão para Google por enquanto
        else:
            flash("Plataforma inválida", 'error')
            return redirect(url_for('index'))
        
        if not phone_number:
            client_name = client.get('name', 'N/A')
            print(f"[WHATSAPP] Erro: Link do grupo não configurado para o cliente '{client_name}' na plataforma {platform}")
            flash(f"Link do grupo WhatsApp não configurado para o cliente {client_name} ({platform})", 'error')
            return redirect(url_for('client_page', client_id=client_id, platform=platform))
        
        print(f"[WHATSAPP] Enviando para cliente '{client.get('name', 'N/A')}' ({platform}) no número: {phone_number}")
        print(f"[WHATSAPP] Tipo de conversão: {conversion_type}")
        
        if platform == 'facebook':
            return send_facebook_whatsapp(client, start_date, end_date, phone_number, conversion_type)
        elif platform == 'google':
            return send_google_ads_whatsapp(client, start_date, end_date, phone_number, conversion_type)
            
    except ValueError as e:
        flash(f"Erro nos parâmetros: {str(e)}", 'error')
        return redirect(url_for('client_page', client_id=client_id, platform=platform))
    except Exception as e:
        flash(f"Erro ao enviar via WhatsApp: {str(e)}", 'error')
        return redirect(url_for('client_page', client_id=client_id, platform=platform))

def send_facebook_whatsapp(client, start_date, end_date, phone_number, conversion_type='leads'):
    """Envia dados do Facebook via WhatsApp com mensagem personalizada"""
    try:
        account_id = client.get('act_fb')
        if not account_id:
            flash("Cliente não possui conta Facebook configurada", 'error')
            return redirect(url_for('client_page', client_id=client['id'], platform='facebook'))
        
        # Busca dados via API para obter informações atualizadas
        campaigns_data = fb_api.get_campaigns_report(account_id, start_date, end_date)
        
        if not campaigns_data:
            flash("Nenhum dado encontrado para o período selecionado", 'warning')
            return redirect(url_for('client_page', client_id=client['id'], platform='facebook'))
        
        print(f"[WHATSAPP] Formatando mensagem personalizada - Tipo: {conversion_type}")
        print(f"[WHATSAPP] Dados de {len(campaigns_data)} campanhas encontradas")
        
        # Formata mensagem personalizada com dados reais e tipo de conversão
        message = evolution_api.format_report_message(
            client['name'], 
            'facebook', 
            start_date, 
            end_date, 
            campaigns_data,  # Passa os dados das campanhas
            conversion_type  # Passa o tipo de conversão
        )
        
        print(f"[WHATSAPP] Mensagem formatada com {len(message)} caracteres")
        
        # Envia mensagem
        result = evolution_api.send_message(phone_number, message)
        
        if result['success']:
            # Atualiza último envio no banco (assumindo que existe método no database)
            try:
                db.update_last_facebook_send(client['id'], datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            except:
                pass  # Ignora se método não existir
            flash(f"Relatório {conversion_type} enviado via WhatsApp com sucesso! ({len(campaigns_data)} campanhas)", 'success')
        else:
            flash(f"Erro ao enviar via WhatsApp: {result['message']}", 'error')
        
        return redirect(url_for('client_page', client_id=client['id'], platform='facebook'))
        
    except Exception as e:
        flash(f"Erro ao enviar relatório Facebook via WhatsApp: {str(e)}", 'error')
        return redirect(url_for('client_page', client_id=client['id'], platform='facebook'))

def send_google_ads_whatsapp(client, start_date, end_date, phone_number, conversion_type='leads'):
    """Envia dados do Google Ads via WhatsApp com mensagem personalizada
    
    NOVA IMPLEMENTAÇÃO:
    1. Primeiro consulta tabela relatorio_google_ads onde customer_id = id_google
    2. Usa dados do banco como prioridade
    3. Só busca na API se não houver dados suficientes no banco
    """
    try:
        customer_id = client.get('id_google')
        if not customer_id:
            flash("Cliente não possui conta Google Ads configurada", 'error')
            return redirect(url_for('client_page', client_id=client['id'], platform='google'))
        
        print(f"\n=== ENVIO WHATSAPP GOOGLE ADS (NOVA IMPLEMENTAÇÃO) ===")
        print(f"Cliente: {client['name']} (Customer ID: {customer_id})")
        print(f"Período: {start_date} a {end_date}")
        
        # PASSO 1: PRIMEIRO CONSULTA A TABELA relatorio_google_ads
        # Busca dados onde customer_id = id_google
        campaigns_data = db.get_existing_google_ads_for_period(customer_id, start_date, end_date)
        print(f"✅ Campanhas encontradas no banco (relatorio_google_ads): {len(campaigns_data)}")
        
        # PASSO 2: Verifica se temos dados suficientes no banco
        use_bank_data = True
        if not campaigns_data:
            print(f"⚠️ Nenhum dado encontrado no banco para o período")
            use_bank_data = False
        else:
            # Verifica se os dados são recentes o suficiente
            from datetime import datetime, timedelta
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            recent_threshold = (end_date_obj - timedelta(days=2)).strftime('%Y-%m-%d')
            
            recent_data = [c for c in campaigns_data if c.get('dia', '') >= recent_threshold]
            if len(recent_data) == 0 and len(campaigns_data) > 0:
                print(f"⚠️ Dados do banco são antigos (mais de 2 dias). Buscando API...")
                use_bank_data = False
            else:
                print(f"✅ Usando dados do banco: {len(campaigns_data)} campanhas")
                if recent_data:
                    print(f"   - {len(recent_data)} campanhas recentes (últimos 2 dias)")
        
        # PASSO 3: Busca na API apenas se necessário
        if not use_bank_data:
            print(f"🔄 Buscando dados via API Google Ads...")
            try:
                api_campaigns_data = google_ads_api.get_campaigns_report(customer_id, start_date, end_date)
                print(f"📊 API retornou: {len(api_campaigns_data)} campanhas")
                
                if api_campaigns_data:
                    campaigns_data = api_campaigns_data
                    
                    # Salva dados novos no banco para próximas consultas
                    new_campaigns = db.filter_new_google_ads_campaigns(campaigns_data, customer_id)
                    if new_campaigns:
                        save_stats = db.save_google_ads_data(new_campaigns)
                        print(f"💾 Salvos no banco: {save_stats['novos_salvos']} novos registros")
                        if save_stats['duplicados_ignorados'] > 0:
                            print(f"   - {save_stats['duplicados_ignorados']} duplicados ignorados")
                        if save_stats['erros'] > 0:
                            print(f"   - {save_stats['erros']} erros: {save_stats['detalhes_erros']}")
                    else:
                        print(f"💾 Todos os dados já existiam no banco")
                elif campaigns_data:
                    # API falhou mas temos dados antigos do banco
                    print(f"⚠️ API falhou, usando dados do banco ({len(campaigns_data)} campanhas)")
                else:
                    # Nem API nem banco têm dados
                    flash("Nenhum dado encontrado para o período selecionado", 'warning')
                    return redirect(url_for('client_page', client_id=client['id'], platform='google'))
                    
            except Exception as api_error:
                print(f"❌ Erro na API: {api_error}")
                if campaigns_data:
                    print(f"🔄 Usando dados do banco como fallback ({len(campaigns_data)} campanhas)")
                else:
                    flash(f"Erro na API e sem dados no banco: {str(api_error)}", 'error')
                    return redirect(url_for('client_page', client_id=client['id'], platform='google'))
        
        print(f"\n[WHATSAPP] Formatando mensagem Google Ads")
        print(f"[WHATSAPP] Fonte dos dados: {'Banco de dados' if use_bank_data else 'API + Banco'}")
        print(f"[WHATSAPP] Campanhas processadas: {len(campaigns_data)}")
        print(f"[WHATSAPP] Tipo de conversão: {conversion_type}")
        
        # PASSO 4: Formata mensagem personalizada
        message = evolution_api.format_google_ads_message(
            client['name'], 
            start_date, 
            end_date, 
            campaigns_data
        )
        
        print(f"[WHATSAPP] Mensagem formatada: {len(message)} caracteres")
        
        # PASSO 5: Envia via WhatsApp
        result = evolution_api.send_message(phone_number, message)
        
        if result['success']:
            # Atualiza último envio no banco
            try:
                db.update_last_google_report(client['id'], datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                print(f"✅ Último envio atualizado no banco")
            except Exception as update_error:
                print(f"⚠️ Erro ao atualizar último envio: {update_error}")
            
            flash(f"✅ Relatório Google Ads enviado via WhatsApp! ({len(campaigns_data)} campanhas)", 'success')
        else:
            flash(f"❌ Erro ao enviar via WhatsApp: {result['message']}", 'error')
        
        return redirect(url_for('client_page', client_id=client['id'], platform='google'))
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f"Erro ao enviar relatório Google Ads via WhatsApp: {str(e)}", 'error')
        return redirect(url_for('client_page', client_id=client['id'], platform='google'))

@app.route('/test_evolution')
def test_evolution():
    """Endpoint para testar Evolution API via web"""
    try:
        result = evolution_api.test_connection()
        return jsonify({
            "status": "success",
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/test_evolution_simple')
def test_evolution_simple():
    """Teste simples da Evolution API"""
    import requests
    
    BASE_URL = "https://lc-evolution-api.qy8om2.easypanel.host"
    TOKEN = "3D1F8FB65596-4C32-A0FF-7AD3C64DF81D"
    INSTANCE = "Guilherme"
    
    headers = {
        "Content-Type": "application/json",
        "apikey": TOKEN
    }
    
    tests = []
    
    # Teste 1: Endpoint raiz
    try:
        response = requests.get(BASE_URL, headers=headers, timeout=10)
        tests.append({
            "test": "root",
            "url": BASE_URL,
            "status_code": response.status_code,
            "response": response.text[:200] if response.text else None,
            "success": response.status_code == 200
        })
    except Exception as e:
        tests.append({
            "test": "root",
            "error": str(e),
            "success": False
        })
    
    # Teste 2: Envio fake
    try:
        url = f"{BASE_URL}/message/sendText/{INSTANCE}"
        payload = {"number": "5511999999999", "textMessage": {"text": "test"}}
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        tests.append({
            "test": "send_fake",
            "url": url,
            "status_code": response.status_code,
            "response": response.text[:200] if response.text else None,
            "success": response.status_code != 404
        })
    except Exception as e:
        tests.append({
            "test": "send_fake",
            "error": str(e),
            "success": False
        })
    
    return jsonify({
        "tests": tests,
        "config": {
            "base_url": BASE_URL,
            "instance": INSTANCE,
            "token_preview": TOKEN[:20] + "..."
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health_check():
    """Endpoint de saúde do sistema"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/mass_update', methods=['POST'])
def mass_update():
    """Atualiza dados de todos os clientes ativos em massa"""
    try:
        # Pega o período dos dados da requisição
        period = request.form.get('period', '7')  # padrão 7 dias
        
        # Validação do período
        if period not in ['7', '15', '30']:
            return jsonify({'success': False, 'message': 'Período inválido'}), 400
        
        # Calcula as datas baseado no período (até ontem, não hoje)
        end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')  # Ontem
        start_date = (datetime.now() - timedelta(days=int(period))).strftime('%Y-%m-%d')  # Período para trás
        
        print(f"\n=== ATUALIZAÇÃO EM MASSA ====")
        print(f"Período: {period} dias ({start_date} a {end_date})")
        
        # Busca todos os clientes ativos
        facebook_clients = db.get_active_facebook_clients()
        google_clients = db.get_active_google_clients()
        
        results = {
            'facebook': {'total': len(facebook_clients), 'success': 0, 'errors': 0, 'details': []},
            'google': {'total': len(google_clients), 'success': 0, 'errors': 0, 'details': []}
        }
        
        # Processa clientes Facebook
        for client in facebook_clients:
            try:
                client_result = process_facebook_mass_update(client, start_date, end_date)
                if client_result['success']:
                    results['facebook']['success'] += 1
                else:
                    results['facebook']['errors'] += 1
                results['facebook']['details'].append(client_result)
            except Exception as e:
                results['facebook']['errors'] += 1
                results['facebook']['details'].append({
                    'client_name': client.get('name', 'N/A'),
                    'success': False,
                    'message': str(e)
                })
        
        # Processa clientes Google
        for client in google_clients:
            try:
                client_result = process_google_mass_update(client, start_date, end_date)
                if client_result['success']:
                    results['google']['success'] += 1
                else:
                    results['google']['errors'] += 1
                results['google']['details'].append(client_result)
            except Exception as e:
                results['google']['errors'] += 1
                results['google']['details'].append({
                    'client_name': client.get('name', 'N/A'),
                    'success': False,
                    'message': str(e)
                })
        
        # Prepara resposta
        total_processed = results['facebook']['total'] + results['google']['total']
        total_success = results['facebook']['success'] + results['google']['success']
        total_errors = results['facebook']['errors'] + results['google']['errors']
        
        print(f"\n=== RESULTADO ATUALIZAÇÃO EM MASSA ====")
        print(f"Total processados: {total_processed}")
        print(f"Sucessos: {total_success}")
        print(f"Erros: {total_errors}")
        print(f"Facebook: {results['facebook']['success']}/{results['facebook']['total']}")
        print(f"Google: {results['google']['success']}/{results['google']['total']}")
        
        return jsonify({
            'success': True,
            'message': f'Atualização concluída: {total_success}/{total_processed} clientes atualizados',
            'results': results,
            'period': period,
            'date_range': f'{start_date} a {end_date}'
        })
        
    except Exception as e:
        print(f"Erro na atualização em massa: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro na atualização em massa: {str(e)}'
        }), 500

def process_facebook_mass_update(client, start_date, end_date):
    """Processa atualização de um cliente Facebook"""
    try:
        client_name = client.get('name', 'N/A')
        account_id = client.get('act_fb')
        
        if not account_id:
            return {
                'client_name': client_name,
                'success': False,
                'message': 'Conta Facebook não configurada'
            }
        
        print(f"📊 Processando Facebook: {client_name} ({account_id})")
        
        # Busca dados via API
        campaigns_data = fb_api.get_campaigns_report(account_id, start_date, end_date)
        
        if not campaigns_data:
            return {
                'client_name': client_name,
                'success': True,
                'message': 'Nenhum dado encontrado para o período',
                'new_records': 0
            }
        
        # Filtra apenas campanhas novas
        new_campaigns = db.filter_new_campaigns(campaigns_data, account_id)
        
        # Salva apenas dados novos no banco
        new_records = 0
        if new_campaigns:
            save_stats = db.save_campaign_data(new_campaigns)
            new_records = save_stats['novos_salvos']
            
            if save_stats['erros'] > 0:
                return {
                    'client_name': client_name,
                    'success': False,
                    'message': f'Erro ao salvar: {save_stats["erros"]} erros',
                    'new_records': new_records
                }
        
        # Atualiza último relatório
        db.update_last_facebook_report(client['id'], datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        print(f"✅ Facebook {client_name}: {new_records} novos registros")
        
        return {
            'client_name': client_name,
            'success': True,
            'message': f'{new_records} novos registros salvos',
            'new_records': new_records
        }
        
    except Exception as e:
        print(f"❌ Erro Facebook {client.get('name', 'N/A')}: {str(e)}")
        return {
            'client_name': client.get('name', 'N/A'),
            'success': False,
            'message': str(e)
        }

def process_google_mass_update(client, start_date, end_date):
    """Processa atualização de um cliente Google"""
    try:
        client_name = client.get('name', 'N/A')
        customer_id = client.get('id_google')
        
        if not customer_id:
            return {
                'client_name': client_name,
                'success': False,
                'message': 'Conta Google não configurada'
            }
        
        print(f"📊 Processando Google: {client_name} ({customer_id})")
        
        # Busca dados via API
        campaigns_data = google_ads_api.get_campaigns_report(customer_id, start_date, end_date)
        
        if not campaigns_data:
            return {
                'client_name': client_name,
                'success': True,
                'message': 'Nenhum dado encontrado para o período',
                'new_records': 0
            }
        
        # Filtra apenas campanhas novas
        new_campaigns = db.filter_new_google_ads_campaigns(campaigns_data, customer_id)
        
        # Salva apenas dados novos no banco
        new_records = 0
        if new_campaigns:
            save_stats = db.save_google_ads_data(new_campaigns)
            new_records = save_stats['novos_salvos']
            
            if save_stats['erros'] > 0:
                return {
                    'client_name': client_name,
                    'success': False,
                    'message': f'Erro ao salvar: {save_stats["erros"]} erros',
                    'new_records': new_records
                }
        
        # Atualiza último relatório
        db.update_last_google_report(client['id'], datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        print(f"✅ Google {client_name}: {new_records} novos registros")
        
        return {
            'client_name': client_name,
            'success': True,
            'message': f'{new_records} novos registros salvos',
            'new_records': new_records
        }
        
    except Exception as e:
        print(f"❌ Erro Google {client.get('name', 'N/A')}: {str(e)}")
        return {
            'client_name': client.get('name', 'N/A'),
            'success': False,
            'message': str(e)
        }

if __name__ == '__main__':
    # Configurações do servidor
    host = os.getenv('WEB_HOST', '127.0.0.1')
    port = int(os.getenv('WEB_PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Iniciando servidor Facebook Reports em http://{host}:{port}")
    print(f"📊 Modo debug: {debug}")
    
    app.run(host=host, port=port, debug=debug)
