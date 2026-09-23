"""
Framework Core: Módulo de Inicialização, Orquestração Assíncrona e Gestão de Sessões.
Gerencia as rotinas cíclicas de segundo plano e inicializa a interface do usuário.
Requer execução com privilégios administrativos elevados (Administrador).
"""

import sys
import os
import time
import threading
from modules.interface import SistemaAnalise

# Interface dinâmica com o ecossistema de segurança de redes local
try:
    from modules.bloqueio_ips import bloquear_ips_suspeitos
except ImportError:
    pass


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
    """
    print("\n" + "=" * 60)
    print("    SERVIÇO DE MONITORAMENTO OPERACIONAL EM SEGUNDO PLANO ATIVADO")
    print(f"    Auditoria de tráfego de interface a cada {intervalo_segundos} segundos...")
    print("=" * 60 + "\n")

    while True:
        try:
            # Invoca o motor de análise de conexões e mitigação ativa do Firewall
            resultado = bloquear_ips_suspeitos()

            # Registra se houve a aplicação de políticas de isolamento de rede com sucesso
            if resultado.get("ok") and resultado.get("bloqueados"):
                print(f"\n[!] EVENTO DE SEGURANÇA: Requisições não autorizadas mitigadas.")
                for bloco in resultado["bloqueados"]:
                    print(f"    --> [POLÍTICA APLICADA VIA SUBSISTEMA] Endereço IP: {bloco.get('ip')}")
                print(f"[+] Status: {resultado.get('mensagem')} | Alocação de recursos estabilizada.\n")

            elif resultado.get("falhas"):
                print(f"[-] Alerta na rotina de auditoria: {resultado.get('mensagem')}")

        except Exception:
            pass

        # Mantém a cadência do ciclo operacional de auditoria
        time.sleep(intervalo_segundos)


# =============================================================================
# PONTO DE ENTRADA PRINCIPAL DO FRAMEWORK (APPLICATION BOOT)
# =============================================================================
if __name__ == "__main__":
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
    # Roda DEPOIS da criação do objeto da janela para evitar o congelamento da interface visual (UI Lock)
    thread_seguranca = threading.Thread(
        target=loop_monitoramento_automatico, args=(5,), daemon=True
    )
    thread_seguranca.start()

    # 5. Inicia o loop contínuo de renderização gráfica do CustomTkinter
    app.mainloop()
