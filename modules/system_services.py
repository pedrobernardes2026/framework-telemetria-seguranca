#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Resposta Ativa e Governança de Infraestrutura de Rede.
Responsável pelo gerenciamento, purga e reset do perímetro de segurança (Firewall)
e resolução de exaustão de conexões DNS/Wi-Fi sob cenários de estresse e ataques DDoS.
"""

import subprocess
import logging
import sys
import os

# Configuração robusta de logs estruturados (Console e Arquivo de Auditoria)
log_format = '%(asctime)s - [%(levelname)s] - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.FileHandler("auditoria_redes.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

def verificar_privilegios():
    """
    Valida se o interpretador Python está rodando com privilégios de Administrador.
    Crucial para chamadas de alteração de estado no Netsh e PowerShell API.
    """
    try:
        # No Windows, verifica se o usuário atual pertence ao grupo de administradores
        return os.getuid() == 0 if hasattr(os, 'getuid') else subprocess.os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def purgar_e_resetar_firewall():
    """
    Executa a purga sequencial de tabelas acumuladas, remove regras dinâmicas
    geradas por scripts de bloco, limpa o buffer DNS e restaura as políticas de fábrica do Firewall.
    """
    logging.info("[!] Iniciando protocolo de purga forense e reset de perímetro de rede...")
    
    if not verificar_privilegios():
        logging.critical("[-] ERRO DE SEGURANÇA: Permissão negada. O script precisa ser executado como ADMINISTRADOR.")
        print("[-] Execução abortada devido à falta de privilégios elevados.")
        return False

    # Pipeline sequencial de comandos administrativos estruturados
    comandos_pipeline = [
        (
            "Purga de Regras Dinâmicas Customizadas",
            "powershell -Command \"Remove-NetFirewallRule -Name 'SistemaAnalise_Block_*' -ErrorAction SilentlyContinue\""
        ),
        (
            "Deleção Massiva de Regras Acumuladas via Netsh",
            "netsh advfirewall firewall delete rule name=all"
        ),
        (
            "Flush DNS (Limpeza e Purga de Cache de Resolução Wi-Fi)",
            "ipconfig /flushdns"
        ),
        (
            "Reset de Fábrica do Windows Defender Firewall (Zero-State)",
            "netsh advfirewall reset"
        )
    ]
    
    sucesso_global = True

    for identificador, comando_bruto in comandos_pipeline:
        try:
            logging.info(f"[*] Subprocesso ativo: Executando {identificador}...")
            
            # Execução isolada com capture_output para evitar injeção de lixo na UI do main.py
            resultado = subprocess.run(
                comando_bruto,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            
            logging.info(f"[+] Subprocesso concluído com sucesso: {identificador}")
            if resultado.stdout:
                logging.debug(f"[OUTPUT]: {resultado.stdout.strip()}")
                
        except subprocess.CalledProcessError as e:
            # Captura se o comando falhar de forma segura (ex: se o Firewall já estava limpo)
            logging.warning(f"[-] Nota de execução em [{identificador}]: O sistema retornou um status de atenção.")
            if e.stderr:
                logging.debug(f"[DETALHE]: {e.stderr.strip()}")
            # Não quebra o loop para garantir que o Flush DNS e o Reset final sejam executados de qualquer forma
            sucesso_global = False

    if sucesso_global:
        logging.info("[+] PROTOCOLO CONCLUÍDO: Perímetro de rede higienizado e Firewall resetado com sucesso total.")
    else:
        logging.warning("[!] PROTOCOLO FINALIZADO: Operação concluída, mas alguns comandos retornaram avisos do Windows.")
        
    return sucesso_global

if __name__ == "__main__":
    print("="*70)
    print(" SUBSISTEMA DE MITIGAÇÃO E MANUTENÇÃO DE REDE - MODO ISOLADO ")
    print("="*70)
    
    # Aciona a purga imediatamente se executado de forma direta pelo console administrativo
    purgar_e_resetar_firewall()


def otimizar_ambiente_point_blank() -> dict:
    """
    Varre o Kernel para localizar o Point Blank. Ajusta a prioridade do jogo 
    para Alta e altera a frequência de varredura do Watchdog 
    para eliminar gargalos de FPS e garantir conexão total.
    """
    import psutil
    jogo_nome = "PointBlank.exe"
    jogo_encontrado = False
    
    try:
        # Varre os processos ativos na memória RAM para achar o jogo
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == jogo_nome:
                p = psutil.Process(proc.info['pid'])
                
                # 1. Aloca prioridade alta para o jogo não perder ciclos da CPU
                p.nice(psutil.HIGH_PRIORITY_CLASS)
                
                # 2. Garante afinidade total de threads (usa os 6 núcleos / 12 threads)
                p.cpu_affinity(list(range(psutil.cpu_count())))
                jogo_encontrado = True
                break
                
        if jogo_encontrado:
            return {
                "ativo": True,
                "mensagem": "[+] Point Blank Otimizado: Prioridade Elevada & Afinidade Total de Threads.",
                "ajustar_clock_inspecao": 10
            }
            
    except Exception as e:
        return {"ativo": False, "mensagem": f"[-] Falha ao calibrar ambiente do jogo: {e}", "ajustar_clock_inspecao": 2}
        
    return {"ativo": False, "mensagem": "[*] Point Blank inativo. Mantendo clock padrão do Watchdog.", "ajustar_clock_inspecao": 2}
