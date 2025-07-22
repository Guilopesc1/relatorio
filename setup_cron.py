#!/usr/bin/env python3
"""
Configurador de Cron Job para Atualização Diária Automática
Configura o sistema para executar a coleta de dados automaticamente todos os dias

Uso:
    python setup_cron.py

Este script irá:
1. Verificar se é possível configurar cron jobs
2. Criar o comando cron correto para o seu sistema
3. Fornecer instruções de como configurar manualmente
"""

import os
import sys
import platform
from pathlib import Path
from datetime import datetime

def main():
    """Função principal para configurar o cron job"""
    
    print("🤖 CONFIGURADOR DE ATUALIZAÇÃO AUTOMÁTICA DIÁRIA")
    print("="*60)
    
    # Detecta sistema operacional
    os_name = platform.system()
    print(f"🖥️  Sistema detectado: {os_name}")
    
    # Caminho do projeto
    project_path = Path(__file__).parent.absolute()
    script_path = project_path / "daily_auto_update.py"
    log_path = project_path / "logs" / "daily_update.log"
    
    print(f"📂 Diretório do projeto: {project_path}")
    print(f"📄 Script de atualização: {script_path}")
    
    # Verifica se o script existe
    if not script_path.exists():
        print(f"❌ Erro: Script {script_path} não encontrado!")
        return 1
    
    # Cria diretório de logs se não existir
    log_path.parent.mkdir(exist_ok=True)
    print(f"📋 Logs serão salvos em: {log_path}")
    
    if os_name == "Windows":
        setup_windows_task(project_path, script_path)
    elif os_name in ["Linux", "Darwin"]:  # Linux ou macOS
        setup_unix_cron(project_path, script_path, log_path)
    else:
        print(f"⚠️  Sistema {os_name} não suportado automaticamente.")
        print("Por favor, configure manualmente usando o método apropriado para seu sistema.")
    
    return 0

def setup_windows_task(project_path, script_path):
    """Configura Task Scheduler no Windows"""
    
    print(f"\n🪟 CONFIGURAÇÃO PARA WINDOWS")
    print("="*40)
    
    # Comando para criar task no Windows
    task_name = "FacebookReportsDaily"
    python_exe = sys.executable
    
    # Comando XML para criar a tarefa
    xml_content = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2025-01-01T06:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Actions>
    <Exec>
      <Command>{python_exe}</Command>
      <Arguments>"{script_path}"</Arguments>
      <WorkingDirectory>{project_path}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''
    
    # Salva arquivo XML
    xml_path = project_path / "daily_task.xml"
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"📄 Arquivo de configuração criado: {xml_path}")
    print(f"\n🔧 INSTRUÇÕES PARA CONFIGURAR NO WINDOWS:")
    print(f"1. Abra o Prompt de Comando como Administrador")
    print(f"2. Execute o comando:")
    print(f'   schtasks /create /tn "{task_name}" /xml "{xml_path}"')
    print(f"")
    print(f"OU configure manualmente no Task Scheduler:")
    print(f"1. Abra 'Agendador de Tarefas' (Task Scheduler)")
    print(f"2. Criar Tarefa Básica -> '{task_name}'")
    print(f"3. Disparador: Diário às 06:00")
    print(f"4. Ação: Iniciar programa")
    print(f"   - Programa: {python_exe}")
    print(f"   - Argumentos: \"{script_path}\"")
    print(f"   - Iniciar em: {project_path}")
    print(f"")
    print(f"📋 Para testar manualmente:")
    print(f'   cd "{project_path}"')
    print(f'   python daily_auto_update.py')

def setup_unix_cron(project_path, script_path, log_path):
    """Configura cron job no Linux/macOS"""
    
    print(f"\n🐧 CONFIGURAÇÃO PARA LINUX/MACOS")
    print("="*40)
    
    # Detecta Python
    python_exe = sys.executable
    
    # Linha do cron job
    cron_line = f"0 6 * * * cd {project_path} && {python_exe} {script_path} >> {log_path} 2>&1"
    
    print(f"🕐 Agendamento: Todos os dias às 06:00")
    print(f"🐍 Python: {python_exe}")
    print(f"📄 Script: {script_path}")
    print(f"📋 Logs: {log_path}")
    print(f"")
    print(f"🔧 INSTRUÇÕES PARA CONFIGURAR:")
    print(f"1. Abra o terminal")
    print(f"2. Execute: crontab -e")
    print(f"3. Adicione a linha abaixo:")
    print(f"")
    print(f"   {cron_line}")
    print(f"")
    print(f"4. Salve e saia do editor")
    print(f"")
    print(f"🔍 Para verificar se foi configurado:")
    print(f"   crontab -l")
    print(f"")
    print(f"📋 Para testar manualmente:")
    print(f"   cd {project_path}")
    print(f"   python daily_auto_update.py")
    
    # Cria script de conveniência
    setup_script_path = project_path / "setup_daily_cron.sh"
    with open(setup_script_path, 'w') as f:
        f.write(f'''#!/bin/bash
# Script para configurar cron job automaticamente

echo "Configurando cron job para atualização diária..."
echo "Linha do cron:"
echo "{cron_line}"
echo ""

# Adiciona ao crontab
(crontab -l 2>/dev/null; echo "{cron_line}") | crontab -

echo "✅ Cron job configurado com sucesso!"
echo "Para verificar: crontab -l"
echo "Para testar: cd {project_path} && python daily_auto_update.py"
''')
    
    os.chmod(setup_script_path, 0o755)
    print(f"📄 Script de configuração automática criado: {setup_script_path}")
    print(f"   Execute: bash {setup_script_path}")

def show_additional_info():
    """Mostra informações adicionais sobre o sistema"""
    
    print(f"\n📊 INFORMAÇÕES ADICIONAIS")
    print("="*30)
    print(f"🕐 Horário configurado: 06:00 (todos os dias)")
    print(f"📅 Dados coletados: Apenas de ONTEM")
    print(f"🔄 Filtro: Apenas dados novos (não duplica)")
    print(f"📋 Logs: Salvos automaticamente")
    print(f"📊 Histórico: JSON salvo diariamente")
    print(f"")
    print(f"💡 DICAS:")
    print(f"- Escolha um horário onde as APIs têm menos tráfego")
    print(f"- Monitore os logs regularmente")
    print(f"- Teste manualmente antes de automatizar")
    print(f"- Verifique se o .env está configurado corretamente")

if __name__ == "__main__":
    try:
        exit_code = main()
        show_additional_info()
        
        print(f"\n✅ Configuração concluída!")
        print(f"Siga as instruções acima para ativar a atualização automática.")
        
    except Exception as e:
        print(f"\n❌ Erro durante configuração: {e}")
        exit_code = 1
    
    sys.exit(exit_code)
