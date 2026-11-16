"""
Módulo de Telemetria de Hardware: Monitoramento de CPU, RAM e Atividade de Disco.
"""
import psutil

def obter_cpu():
    """Retorna o percentual instantâneo utilizando intervalo zero para não bloquear a interface visual."""
    try:
        # O valor 0.0 desliga a retenção de tempo, puxando o dado direto do barramento
        return psutil.cpu_percent(interval=0.0)
    except Exception:
        return 0.0

def obter_ram():
    """Retorna o percentual instantâneo de alocação de Memória RAM global."""
    try:
        return psutil.virtual_memory().percent
    except Exception:
        return 0.0

def obter_disco():
    """Retorna o percentual de armazenamento ocupado no diretório raiz do sistema."""
    try:
        return psutil.disk_usage("C:\\").percent
    except Exception:
        return 0.0
