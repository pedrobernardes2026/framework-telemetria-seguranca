import subprocess
import logging
import psutil
import time
import sys
import os

def executar_reset_total_rede():
    """
    Contra-ataque massivo de infraestrutura. Limpa o buffer do Firewall,
    purgas cache DNS do Wi-Fi e restaura o catalogo Winsock e a pilha IP.
    """
    logging.info("[!] Gatilho do Watchdog ativado: Executando reset total de rede e limpeza forense...")
    
    comandos_pipeline = [
        ("Purga de Regras Customizadas", "powershell -Command \"Remove-NetFirewallRule -Name 'SistemaAnalise_Block_*' -ErrorAction SilentlyContinue\""),
        ("Delecao Massiva de Regras Netsh", "netsh advfirewall firewall delete rule name=all"),
        ("Flush DNS (Limpeza de Cache)", "ipconfig /flushdns"),
        ("Reset de Fabrica do Firewall", "netsh advfirewall reset"),
        ("Reset da Pilha de Protocolos IP", "netsh int ip reset"),
        ("Reset do Catalogo Winsock (Sockets)", "netsh winsock reset")
    ]
    
    for identificador, comando in comandos_pipeline:
        try:
            subprocess.run(comando, shell=True, capture_output=True, text=True, check=True)
            logging.info(f"[+] Limpeza concluida: {identificador}")
        except subprocess.CalledProcessError:
            continue

def monitorar_e_proteger_wow():
    logging.info("[*] Watchdog Sênior Unificado Ativado. Monitorando com clock de 2s e Reset total...")
    
    processos_alvo = ["Wow.exe", "Battle.net.exe"]
    wow_rodando_ultimo_estado = False
    
    # 🎯 CONTRA-ATAQUE INICIAL: Executa o reset completo logo no boot do script
    # para garantir que o launcher da Battle.net abra em um ambiente 100% esteril e limpo
    executar_reset_total_rede()
    
    while True:
        wow_ativo = False
        pids_detectados = []
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] in processos_alvo:
                    wow_ativo = True
                    pids_detectados.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
        # Detecção de encerramento abrupto do jogo por ataque dos crackers
        if wow_rodando_ultimo_estado and not wow_ativo:
            logging.critical("[!] ANOMALIA ENCONTRADA: O cliente do WoW foi fechado de forma inesperada!")
            executar_reset_total_rede()
            
            # Injeta vacina de persistência de portas para asfixiar novos scripts automatizados dos crackers
            subprocess.run("netsh advfirewall firewall add rule name='Bloqueio_Persistente_Borda' dir=in action=block protocol=tcp localport=1119,3724", shell=True, capture_output=True)
            logging.info("[+] Vacina de persistência cravada nas portas da Blizzard (1119/3724).")
            wow_rodando_ultimo_estado = False
            
        elif wow_ativo:
            if not wow_rodando_ultimo_estado:
                logging.info(f"[+] Canal seguro com Azeroth estabelecido. PIDs ativos: {pids_detectados}")
            wow_rodando_ultimo_estado = True
            
            for pid in pids_detectados:
                try:
                    p = psutil.Process(pid)
                    conexoes = p.net_connections(kind='tcp')
                    estados_anormais = [c.status for c in conexoes if c.status in ['TIME_WAIT', 'CLOSE_WAIT']]
                    
                    # Se eles tentarem inundar a rede silenciosamente enquanto você joga
                    if len(estados_anormais) > 10:
                        logging.warning(f"[!] Inundação de sockets detectada no PID {pid}. Forçando purga preventiva de DNS.")
                        subprocess.run("ipconfig /flushdns", shell=True, capture_output=True)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        time.sleep(2) # Clock agressivo de 2 segundos para interceptar os scripts inimigos na raiz

if __name__ == "__main__":
    # Configuração do barramento de logs salvando direto na pasta oficial do projeto
    diretorio_atual = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pasta_logs = os.path.join(diretorio_atual, "Logs")
    if not os.path.exists(pasta_logs):
        os.makedirs(pasta_logs)
        
    caminho_log_final = os.path.join(pasta_logs, "auditoria_redes.txt")

    log_format = '%(asctime)s - [%(levelname)s] - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(caminho_log_final, encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    monitorar_e_proteger_wow()
