"""
Script de Verificação das Modificações
Verifica se todas as mudanças foram implementadas corretamente
"""

import os
import sys

def check_file_modifications():
    """Verifica se os arquivos foram modificados corretamente"""
    
    print("🔍 VERIFICAÇÃO DAS MODIFICAÇÕES")
    print("=" * 50)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Lista de verificações
    checks = []
    
    # 1. Verificar database.py
    database_path = os.path.join(base_path, 'database.py')
    if os.path.exists(database_path):
        with open(database_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verifica se os novos métodos foram adicionados
        has_by_id = 'get_client_link_grupo_by_id' in content
        has_by_name = 'get_client_link_grupo_by_name' in content
        has_link_grupo_select = "select('link_grupo')" in content
        
        checks.append({
            'file': 'database.py',
            'checks': [
                ('✅' if has_by_id else '❌', 'get_client_link_grupo_by_id() método'),
                ('✅' if has_by_name else '❌', 'get_client_link_grupo_by_name() método'),
                ('✅' if has_link_grupo_select else '❌', 'Busca por campo link_grupo')
            ]
        })
    else:
        checks.append({
            'file': 'database.py',
            'checks': [('❌', 'Arquivo não encontrado')]
        })
    
    # 2. Verificar app.py
    app_path = os.path.join(base_path, 'app.py')
    if os.path.exists(app_path):
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verifica se as modificações foram feitas
        no_fixed_number = '48999319622' not in content or 'Número fixo' not in content
        has_link_grupo_fetch = 'get_client_link_grupo_by_id' in content
        has_validation = 'não configurado para o cliente' in content
        has_logs = '[WHATSAPP]' in content
        
        checks.append({
            'file': 'app.py',
            'checks': [
                ('✅' if no_fixed_number else '❌', 'Número fixo removido'),
                ('✅' if has_link_grupo_fetch else '❌', 'Busca link_grupo implementada'),
                ('✅' if has_validation else '❌', 'Validação de cliente configurado'),
                ('✅' if has_logs else '❌', 'Logs informativos adicionados')
            ]
        })
    else:
        checks.append({
            'file': 'app.py',
            'checks': [('❌', 'Arquivo não encontrado')]
        })
    
    # 3. Verificar arquivos de documentação
    doc_files = [
        'MODIFICACOES_WHATSAPP.md',
        'test_whatsapp_update.py',
        'MODIFICACOES_WHATSAPP.py'
    ]
    
    for doc_file in doc_files:
        doc_path = os.path.join(base_path, doc_file)
        exists = os.path.exists(doc_path)
        checks.append({
            'file': doc_file,
            'checks': [('✅' if exists else '❌', 'Arquivo criado')]
        })
    
    # Exibir resultados
    for check in checks:
        print(f"\n📄 {check['file']}:")
        for status, description in check['checks']:
            print(f"   {status} {description}")
    
    # Resumo
    total_checks = sum(len(check['checks']) for check in checks)
    passed_checks = sum(1 for check in checks for status, _ in check['checks'] if status == '✅')
    
    print(f"\n📊 RESUMO:")
    print(f"   Total de verificações: {total_checks}")
    print(f"   Aprovadas: {passed_checks}")
    print(f"   Falharam: {total_checks - passed_checks}")
    
    if passed_checks == total_checks:
        print(f"\n🎉 TODAS AS MODIFICAÇÕES FORAM IMPLEMENTADAS COM SUCESSO!")
        return True
    else:
        print(f"\n⚠️  Algumas verificações falharam. Verifique os arquivos marcados com ❌")
        return False

def show_next_steps():
    """Mostra próximos passos"""
    print(f"\n📋 PRÓXIMOS PASSOS:")
    print("1. ✅ Certifique-se que o campo 'link_grupo' existe na tabela 'relatorio_cadastro_clientes'")
    print("2. ✅ Preencha o 'link_grupo' para todos os clientes ativos")
    print("3. ✅ Teste o sistema com alguns envios")
    print("4. ✅ Monitore os logs para verificar funcionamento")
    
    print(f"\n🗂️  ESTRUTURA DE DADOS NECESSÁRIA:")
    print("   Tabela: relatorio_cadastro_clientes")
    print("   Campos obrigatórios:")
    print("   - id (int): ID do cliente")
    print("   - name (string): Nome do cliente") 
    print("   - link_grupo (string): Número WhatsApp para envio")
    print("   - roda_facebook (bool): Se cliente está ativo no Facebook")
    
    print(f"\n📞 FORMATO DO NÚMERO:")
    print("   - Brasileiro: 5548999999999")
    print("   - Internacional: +5548999999999")
    print("   - Sistema formatará automaticamente")

def main():
    """Função principal"""
    print("🔧 SCRIPT DE VERIFICAÇÃO - MODIFICAÇÕES WHATSAPP")
    print("Sistema: Facebook Reports")
    print("Data: Julho 2025")
    print()
    
    success = check_file_modifications()
    
    if success:
        show_next_steps()
        
        print(f"\n✨ SISTEMA ATUALIZADO COM SUCESSO!")
        print("As mensagens agora serão enviadas para o número específico de cada cliente.")
        
    else:
        print(f"\n🚨 ATENÇÃO: Algumas modificações podem não ter sido aplicadas corretamente.")
        print("Verifique os arquivos e tente novamente.")
    
    print(f"\n📚 Para mais informações, consulte:")
    print("   - MODIFICACOES_WHATSAPP.md (documentação completa)")
    print("   - test_whatsapp_update.py (script de teste)")

if __name__ == "__main__":
    main()
