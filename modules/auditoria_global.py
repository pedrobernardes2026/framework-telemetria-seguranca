"""
Auditoria de processos e persistências do sistema.
"""

import psutil
import winreg
from typing import List, Dict, Any

PROCESSOS_PERMITIDOS = [
    "main.py",
    "sistemaanalise",
    "code.exe",
    "python.exe",
    "pythonw.exe",
    "explorer.exe",
    "firefox.exe",
    "chrome.exe",
    "msedge.exe",
]


def varrer_scripts_suspeitos() -> List[Dict[str, Any]]:
    """Identifica interpretadores e binários com comportamento suspeito."""
    suspeitos = []

    for proc in psutil.process_iter(["pid", "name", "cmdline", "memory_info", "cpu_percent"]):
        try:
            nome = (proc.info["name"] or "").lower()
            cmdline = proc.info["cmdline"] or []
            cmdline_str = " ".join(cmdline).lower()

            # Interpretadores com parâmetros suspeitos
            if nome in ("cmd.exe", "powershell.exe", "wscript.exe", "cscript.exe"):
                if len(cmdline) > 1 and not any(p in cmdline_str for p in PROCESSOS_PERMITIDOS):
                    suspeitos.append({
                        "pid": proc.info["pid"],
                        "nome": nome,
                        "tipo": "Interpretador com parâmetros suspeitos",
                        "comando": cmdline_str[:150],
                        "ram": round(proc.info["memory_info"].rss / (1024 * 1024), 2),
                        "cpu": proc.info["cpu_percent"],
                    })

            # Python fora de contextos conhecidos
            elif nome in ("python.exe", "pythonw.exe"):
                if not any(x in cmdline_str for x in ["sistemaanalise", "main.py"]):
                    if any(p in cmdline_str for p in ["appdata", "temp", "programdata"]):
                        suspeitos.append({
                            "pid": proc.info["pid"],
                            "nome": nome,
                            "tipo": "Python em diretório temporário/restrito",
                            "comando": cmdline_str[:150],
                            "ram": round(proc.info["memory_info"].rss / (1024 * 1024), 2),
                            "cpu": proc.info["cpu_percent"],
                        })

            # Binários de sistema em local inesperado
            elif nome in ("explorer.exe", "taskmgr.exe", "svchost.exe"):
                try:
                    exe = proc.exe().lower()
                    if "windows" not in exe and "system32" not in exe:
                        suspeitos.append({
                            "pid": proc.info["pid"],
                            "nome": nome,
                            "tipo": "Binário de sistema em caminho inesperado",
                            "comando": exe,
                            "ram": round(proc.info["memory_info"].rss / (1024 * 1024), 2),
                            "cpu": proc.info["cpu_percent"],
                        })
                except Exception:
                    pass

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return suspeitos


def verificar_persistencias() -> List[str]:
    """Verifica chaves de inicialização do registro."""
    alertas = []
    caminhos = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
    ]

    for hive, path in caminhos:
        try:
            chave = winreg.OpenKey(hive, path, 0, winreg.KEY_READ)
            qtd, _, _ = winreg.QueryInfoKey(chave)
            for i in range(qtd):
                nome, valor, _ = winreg.EnumValue(chave, i)
                val = str(valor).lower()
                if any(t in val for t in ["cmd", "powershell", "wscript", "temp", "appdata"]):
                    if not any(p in val for p in PROCESSOS_PERMITIDOS):
                        alertas.append(f"{nome} -> {valor}")
            winreg.CloseKey(chave)
        except Exception:
            continue

    return alertas


def obter_telemetria() -> Dict[str, Any]:
    return {
        "total_processos": len(psutil.pids()),
        "conexoes_tcp": len(psutil.net_connections(kind="tcp")),
        "cpu_percent": psutil.cpu_percent(),
        "cpu_alta": psutil.cpu_percent() > 85,
    }