"""
Diagnóstico de conexões de rede e classificação de IPs suspeitos.
"""

import socket
import subprocess
from typing import Dict, Any, List

try:
    import psutil
except ImportError:
    psutil = None

PORTAS_SENSIVEIS = {
    22, 23, 135, 139, 445, 3389, 5900, 5901, 5902,
    2222, 2323, 4444, 5555, 6667, 12345, 31337, 27374,
    4899, 6129, 1604
}

PROCESSOS_CONFIAVEIS = {
    "firefox.exe", "chrome.exe", "msedge.exe", "msedgewebview2.exe",
    "brave.exe", "opera.exe", "discord.exe", "steam.exe", "steamwebhelper.exe",
    "onedrive.exe", "explorer.exe", "svchost.exe", "system", "services.exe",
    "lsass.exe", "wininit.exe", "spoolsv.exe", "code.exe", "python.exe",
    "pythonw.exe", "gcloud.exe", "searchhost.exe", "runtimebroker.exe",
}


def _eh_ip_privado(ip: str) -> bool:
    if not ip:
        return True
    try:
        p = [int(x) for x in ip.split(".")]
        if len(p) != 4:
            return True
        if p[0] in (10, 127):
            return True
        if p[0] == 172 and 16 <= p[1] <= 31:
            return True
        if p[0] == 192 and p[1] == 168:
            return True
        if p[0] == 169 and p[1] == 254:
            return True
        return False
    except Exception:
        return True


def _eh_aurera(nome: str) -> bool:
    if not nome:
        return False
    n = nome.lower()
    return n.startswith("aurera") or "aurera_gl" in n


def obter_conexoes() -> Dict[str, Any]:
    resultado = {
        "tcp": 0,
        "udp": 0,
        "established": 0,
        "listen": 0,
        "time_wait": 0,
        "close_wait": 0,
        "detalhes": []
    }

    if not psutil:
        return resultado

    try:
        for conn in psutil.net_connections(kind="inet"):
            proto = "tcp" if conn.type == 1 else "udp"
            resultado[proto] += 1

            status = (conn.status or "").upper()
            if status == "ESTABLISHED":
                resultado["established"] += 1
            elif status == "LISTEN":
                resultado["listen"] += 1
            elif status == "TIME_WAIT":
                resultado["time_wait"] += 1
            elif status == "CLOSE_WAIT":
                resultado["close_wait"] += 1

            ip_remoto = conn.raddr.ip if conn.raddr else ""
            porta_remota = conn.raddr.port if conn.raddr else 0

            nome = "Desconhecido"
            if conn.pid:
                try:
                    nome = psutil.Process(conn.pid).name()
                except Exception:
                    pass

            if ip_remoto:
                resultado["detalhes"].append({
                    "ip_remoto": ip_remoto,
                    "porta_remota": porta_remota,
                    "processo": nome,
                    "estado": status,
                })
    except Exception:
        pass

    return resultado


def analisar_ips_suspeitos() -> Dict[str, Any]:
    data = obter_conexoes()
    detalhes = data.get("detalhes", [])

    ips_info = {}
    for item in detalhes:
        ip = item.get("ip_remoto") or ""
        if not ip or _eh_ip_privado(ip):
            continue

        if ip not in ips_info:
            ips_info[ip] = {
                "ip": ip,
                "quantidade": 0,
                "portas": set(),
                "processos": set(),
                "estados": set(),
            }

        info = ips_info[ip]
        info["quantidade"] += 1

        if item.get("porta_remota"):
            try:
                info["portas"].add(int(item["porta_remota"]))
            except Exception:
                pass

        info["processos"].add(item.get("processo") or "Desconhecido")
        if item.get("estado"):
            info["estados"].add(item["estado"])

    suspeitos = []
    todos_publicos = list(ips_info.keys())

    for ip, info in ips_info.items():
        motivos = []
        nivel = "BAIXO"

        portas_sens = info["portas"] & PORTAS_SENSIVEIS
        if portas_sens:
            nivel = "ALTO"
            motivos.append(f"Portas sensíveis: {sorted(portas_sens)}")

        procs_desconhecidos = [
            p for p in info["processos"]
            if p.lower() not in PROCESSOS_CONFIAVEIS and not _eh_aurera(p)
        ]
        if procs_desconhecidos:
            if nivel != "ALTO":
                nivel = "MÉDIO"
            motivos.append(
                f"Processos não reconhecidos: {', '.join(list(procs_desconhecidos)[:3])}"
            )

        if nivel in ("ALTO", "MÉDIO"):
            suspeitos.append({
                "ip": ip,
                "quantidade": info["quantidade"],
                "portas": sorted(info["portas"]),
                "processos": sorted(info["processos"]),
                "nivel": nivel,
                "motivos": motivos,
                "processo": ", ".join(info["processos"]),
            })

    nivel_geral = "BAIXO"
    if any(s["nivel"] == "ALTO" for s in suspeitos):
        nivel_geral = "ALTO"
    elif any(s["nivel"] == "MÉDIO" for s in suspeitos):
        nivel_geral = "MÉDIO"

    return {
        "suspeitos": suspeitos,
        "todos_ips_publicos": todos_publicos,
        "resumo": {
            "nivel_geral": nivel_geral,
            "ips_publicos": len(todos_publicos),
            "ips_suspeitos": len(suspeitos),
        },
        "total_analisados": len(ips_info),
    }


def analisar_rede() -> Dict[str, Any]:
    """Retorno completo usado pelo relatório PDF."""
    conexoes = obter_conexoes()
    ips = analisar_ips_suspeitos()

    hostname = socket.gethostname()
    ip_local = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    nota = max(0, 100 - (10 * len(ips.get("suspeitos", []))))

    return {
        "hostname": hostname,
        "ip_local": ip_local,
        "ip_publico": "—",
        "mac": "—",
        "interface": "—",
        "conexoes": {
            "tcp": conexoes.get("tcp", 0),
            "udp": conexoes.get("udp", 0),
            "established": conexoes.get("established", 0),
            "listen": conexoes.get("listen", 0),
            "time_wait": conexoes.get("time_wait", 0),
            "close_wait": conexoes.get("close_wait", 0),
        },
        "diagnostico": {
            "nota": nota,
            "alertas": [
                (s.get("motivos") or [""])[0]
                for s in ips.get("suspeitos", [])[:5]
            ],
        },
        "ips_suspeitos": ips,
        "riscos": [],
    }