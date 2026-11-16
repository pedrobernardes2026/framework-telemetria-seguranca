"""
Monitoramento de processos do cliente Aurera e auditoria de integridade.
"""

import os
import psutil
from datetime import datetime
from modules.processos import obter_processos
from modules.auditoria_global import varrer_scripts_suspeitos, obter_telemetria

LOG_DIR = os.path.join(os.getcwd(), "Logs")
LOG_PATH = os.path.join(LOG_DIR, "monitoramento.txt")


def analisar_aurera():
    processos = obter_processos()
    clientes = [p for p in processos if "aurera" in p.get("nome", "").lower()]

    total_ram = sum(p.get("memoria", 0) for p in clientes)
    total_cpu = sum(p.get("cpu", 0) for p in clientes)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(LOG_DIR, exist_ok=True)

    scripts = varrer_scripts_suspeitos()
    telemetria = obter_telemetria()

    try:
        from modules.integridade import verificar_adulteracao
        violacoes = verificar_adulteracao()
    except ImportError:
        violacoes = []

    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}] --- MONITORAMENTO ---\n")
            f.write(f"  Clientes Aurera: {len(clientes)} | RAM: {total_ram:.1f} MB | CPU: {total_cpu:.1f}%\n")
            f.write(f"  Processos totais: {telemetria['total_processos']} | Conexões TCP: {telemetria['conexoes_tcp']}\n")

            if violacoes:
                f.write("  [ALERTA] Arquivos com integridade comprometida:\n")
                try:
                    from modules.notificacao_email import disparar_alerta_integridade
                    for item in violacoes:
                        f.write(f"    - {item['arquivo']}\n")
                        disparar_alerta_integridade(
                            item["arquivo"], item["esperado"], item["detectado"]
                        )
                except Exception as e:
                    f.write(f"    Erro ao notificar: {e}\n")
            else:
                f.write("  [OK] Integridade dos arquivos críticos verificada.\n")

            if scripts:
                f.write("  [ALERTA] Processos suspeitos detectados:\n")
                for s in scripts:
                    f.write(f"    - {s['nome']} (PID {s['pid']}) | {s['tipo']}\n")
                    try:
                        psutil.Process(s["pid"]).terminate()
                        f.write(f"      Processo {s['pid']} finalizado.\n")
                    except Exception:
                        f.write(f"      Não foi possível finalizar PID {s['pid']}.\n")
            else:
                f.write("  [OK] Nenhum processo suspeito encontrado.\n")

            f.write("=" * 60 + "\n")
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:
        print(f"[LOG] Erro ao gravar: {e}")

    return {
        "clientes": len(clientes),
        "ram": round(total_ram, 2),
        "cpu": round(total_cpu, 2),
        "ram_mb": round(total_ram, 2),
        "ram_gb": round(total_ram / 1024, 2),
        "lista_clientes": clientes,
    }