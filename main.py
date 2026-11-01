"""
Framework Core: Módulo de Inicialização, Orquestração Assíncrona e Interface Gráfica.
Projeto PB Framework - Telemetria e Auditoria de Segurança Residente - Moreno
Requer privilégios administrativos elevados (Administrador).
"""

import sys
import os
import time
import threading
import subprocess
import multiprocessing  # Vacina essencial para bloquear os loops de janelas fantasmas do CMD
import psutil
from modules.interface import SistemaAnalise
from modules.system_services import otimizar_ambiente_point_blank, purgar_e_resetar_firewall

# Interface dinâmica com o ecossistema de segurança de redes local
try:
    from modules.bloqueio_ips import bloquear_ips_suspeitos
except ImportError:
    print("[-] Alerta de Dependência: Módulo de mitigação atômica bloqueio_ips não localizado.")
    def bloquear_ips_suspeitos(*args, **kwargs):
        return {"ok": False, "mensagem": "Módulo indisponível no host."}

# =============================================================================
# DIRETRIZES DE FLUXO E VARIÁVEIS DE SESSÃO CORE
# =============================================================================

def verificar_privilegios_admin() -> bool:
    """Verifica se o processo atual possui privilégios administrativos no sistema operacional."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def loop_monitoramento_automatico(intervalo_segundos: int = 5):
    """
    Executa a verificação cíclica em uma thread isolada para mapeamento
    e mitigação automatizada de requisições externas não homologadas.
    Otimiza dinamicamente o clock de amostragem, elimina árvores de processos
    fantasmas em Ring 0 e reseta o Firewall caso o Point Blank esteja ativo.
    """
    print("\n" + "=" * 60)
    print("    SERVIÇO DE MONITORAMENTO OPERACIONAL EM SEGUNDO PLANO ATIVADO")
    print(f"    Auditoria de tráfego de interface a cada {intervalo_segundos} segundos...")
    print("=" * 60 + "\n")

    # Variável de controle para evitar a execução repetida e redundante da purga
    jogo_estava_aberto = False

    while True:
        try:
            # 🎯 VACINA DINÂMICA: Verifica e otimiza as threads do Point Blank
            status_jogo = otimizar_ambiente_point_blank()
            
            if status_jogo["ativo"]:
                # 🛡️ INTERVENÇÃO ATIVA DE PROCESSO-PAI OCULTO
                # Vasculha a tabela do Kernel para capturar e ejetar relacionamentos de dependência maliciosos
                for proc in psutil.process_iter(['pid', 'name', 'ppid']):
                    try:
                        nome_proc = proc.info['name']
                        if nome_proc and ("PointBlank" in nome_proc or "Cheat" in nome_proc):
                            pid_filho = proc.info['pid']
                            pid_pai = proc.info['ppid']
                            
                            # Se for detectada uma árvore estruturada por processo-pai intruso (Ex: PPID 6456)
                            if pid_pai > 0 and pid_pai != pid_filho:
                                msg_intrusao = f"[ALERTA] Árvore oculta detectada: {nome_proc} (PID: {pid_filho}) -> Pai Oculto (PPID: {pid_pai})"
                                print(f"\n[!] {msg_intrusao}")
                                if 'app' in globals():
                                    app.logar_evento_terminal(msg_intrusao)
                                    app.logar_evento_terminal("[🔥] Executando purga brutal da raiz para liberar barramento...")
                                
                                # Aniquila o processo pai diretamente para quebrar o bloqueio de "Acesso Negado"
                                subprocess.run(f"powershell -Command \"Stop-Process -Id {pid_pai} -Force\"", shell=True, capture_output=True)
                                # Derruba a instância remanescente retida na memória RAM
                                subprocess.run(f"powershell -Command \"Stop-Process -Id {pid_filho} -Force\"", shell=True, capture_output=True)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue

                # Se o jogo acabou de abrir, dispara o protocolo automático de higienização de portas
                if not jogo_estava_aberto:
                    msg_pb = "Point Blank detectado ativo. Disparando purga automatizada do perímetro..."
                    print(f"\n[!] {msg_pb}")
                    if 'app' in globals():
                        app.logar_evento_terminal(f"[SISTEMA] {msg_pb}")
                    purgar_e_resetar_firewall()
                    jogo_estava_aberto = True
                
                # Se o jogo estiver aberto, folga o clock para 10 segundos para blindar seu ping e FPS
                cadencia_atual = status_jogo["ajustar_clock_inspecao"]
            else:
                jogo_estava_aberto = False
                # Se o jogo estiver fechado, mantém o ritmo padrão de patrulha pesada de 5 segundos
                cadencia_atual = intervalo_segundos

            # 🚀 ISOLAMENTO INTELIGNETE: Só invoca a mitigação activa de blocos se o jogo NÃO estiver aberto
            if not status_jogo["ativo"]:
                resultado = bloquear_ips_suspeitos()

                # Registra se houve a aplicação de políticas de isolamento de rede com sucesso
                if resultado.get("ok") and resultado.get("bloqueados"):
                    print(f"\n[!] EVENTO DE SEGURANÇA: Requisições não autorizadas mitigadas.")
                    for bloco in resultado["bloqueados"]:
                        ip_mitigado = bloco.get('ip')
                        print(f"    --> [POLÍTICA APLICADA VIA SUBSISTEMA] Endereço IP: {ip_mitigado}")
                        # 🎯 REDIRECIONAMENTO COMPULSÓRIO PARA O TERMINAL INTERNO DA INTERFACE
                        if 'app' in globals():
                            app.logar_evento_terminal(f"[MITIGAÇÃO] Nó não homologado isolado no Firewall: {ip_mitigado}")

                elif resultado.get("falhas"):
                    print(f"[-] Alerta na rotina de auditoria: {resultado.get('mensagem')}")
                    if 'app' in globals():
                        app.logar_evento_terminal(f"[ERRO] Falha no barramento de varredura: {resultado.get('mensagem')}")

        except Exception as e:
            print(f"[-] Erro na esteira assíncrona do loop: {e}")

        # Mantém a cadência do ciclo operacional de auditoria calculada dinamicamente
        time.sleep(cadencia_atual)


# =============================================================================
# PONTO DE ENTRADA PRINCIPAL DO FRAMEWORK (APPLICATION BOOT)
# =============================================================================
if __name__ == "__main__":
    # 🎯 FIX FORK LOOP: Linha compulsória colocada obrigatoriamente no início absoluto do boot
    multiprocessing.freeze_support()

    # 1. Validação de privilégios operacionais: impede a execução em modo restrito
    if not verificar_privilegios_admin():
        print("\n[!] ERRO OPERACIONAL: Acesso Negado.")
        print("    Para realizar a gestão de diretrizes no Firewall do Windows,")
        print("    o terminal DEVE ser executado como ADMINISTRADOR antes de iniciar o script.")
        print("    Execução abortada por segurança.\n")
        sys.exit(1)

    # 2. Inicialização da esteira de validação criptográfica de integridade de módulos (SHA-256)
    try:
        from modules.integridade import inicializar_assinaturas_projeto
        inicializar_assinaturas_projeto()
    except Exception as e_integridade:
        print(f"[-] Alerta no barramento de verificação de assinaturas: {e_integridade}")

    # 3. Inicialização da Interface Gráfica primeiro para registrar os objetos na RAM
    print("[+] Inicializando a interface visual do Sistema de Análise...")
    app = SistemaAnalise()

    # 4. Inicialização do serviço assíncrono de segundo plano EM THREAD ISOLADA (Daemon)
    # Roda DEPOIS da criação do objeto da janela para evitar o congelamento della interface visual (UI Lock)
    thread_seguranca = threading.Thread(
        target=loop_monitoramento_automatico, args=(5,), daemon=True
    )
    thread_seguranca.start()

    # 5. Inicia o loop contínuo de renderização gráfica do CustomTkinter
    app.mainloop()
