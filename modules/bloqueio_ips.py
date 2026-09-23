"""
Módulo de Gestão de Políticas de Firewall e Mitigação de Nós de Rede Não Homologados.
Requer privilégios administrativos elevados (Modo Administrador) para execução.
Implementa Whitelist automatizada para redes de infraestrutura crítica (Blizzard e Cloudflare).
"""

from datetime import datetime
import os
import subprocess
import sys
import re
from typing import List, Dict, Any
import psutil

# =============================================================================
# ENGINE DE CACHE & TELEMETRIA SEGURA - PROJETO MORENO
# =============================================================================

# Conjunto global na memória RAM para evitar chamadas duplicadas ao Netsh
# Isso estabiliza os recursos e elimina de vez o erro de "falhas" na auditoria
IPS_BLOQUEADOS_CACHE = set()

def obter_nome_processo_seguro(pid: int) -> str:
    """
    Verifica se o PID está ativo e saudável em tempo real antes de puxar o nome.
    Elimina os falsos positivos de processos fantasmas ou PIDs reutilizados pelo Windows.
    """
    try:
        proc = psutil.Process(pid)
        if proc.is_running():
            return proc.name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return "Desconhecido"
    return "Desconhecido"


PREFIXO_REGRA = "SistemaAnalise_Block_"

# 🛡️ WHITELIST DEFINITIVA DE INFRAESTRUTURA GLOBAL (Cadeia de Custódia)
SUBNETES_HOMOLOGADAS = [
    # --- REDES BLIZZARD ENTERTAINMENT ---
    "12.129.0.0/16",   # Blizzard US East / Battle.net
    "24.105.0.0/18",   # Blizzard US West / WoW Game Servers
    "37.244.0.0/16",   # Blizzard Europe
    "185.60.112.0/22", # Blizzard Authentication & CDN
    "213.248.126.0/24",# Blizzard Core Infrastructure  
    
    # --- PROXIES E CDN CLOUDFLARE ---
    "103.21.244.0/22", "103.22.200.0/22", "103.31.4.0/22", "104.16.0.0/13",
    "108.162.192.0/18", "131.0.72.0/22", "141.101.64.0/18", "162.158.0.0/15",
    "172.64.0.0/13", "173.245.48.0/20", "188.114.96.0/20", "190.93.240.0/20",
    "197.234.240.0/22", "198.41.128.0/17",

    # 🎯 VACINA DE CONEXÃO DO GITHUB / FASTLY
    "140.82.112.0/20",  # Bloco Core do GitHub Web/Git Ports
    "185.199.108.0/22", # GitHub Pages e Ativos de Distribuição
    "146.75.0.0/17",    # CDN Fastly vinculada ao tráfego do GitHub
    "151.101.0.0/16"    # Barramento de borda Fastly global
]


def _eh_windows() -> bool:
    return sys.platform.startswith("win")


def _eh_ip_valido(ip: str) -> bool:
    if not ip or not isinstance(ip, str):
        return False
    partes = ip.strip().split(".")
    if len(partes) != 4:
        return False
    try:
        return all(0 <= int(p) <= 255 for p in partes)
    except ValueError:
        return False


def ip_pertence_a_subrede(ip: str, cidr: str) -> bool:
    """Valida via matemática de escopo se um endereço IP pertence a um bloco CIDR específico."""
    try:
        ip_alvo = ip.split('.')
        if len(ip_alvo) != 4:
            return False
            
        base_cidr, mascara_bits = cidr.split('/')
        ip_base = base_cidr.split('.')
        bits = int(mascara_bits)
        
        int_alvo = (int(ip_alvo[0]) << 24) + (int(ip_alvo[1]) << 16) + (int(ip_alvo[2]) << 8) + int(ip_alvo[3])
        int_base = (int(ip_base[0]) << 24) + (int(ip_base[1]) << 16) + (int(ip_base[2]) << 8) + int(ip_base[3])
        
        mascara = (0xFFFFFFFF << (32 - bits)) & 0xFFFFFFFF
        return (int_alvo & mascara) == (int_base & mascara)
    except Exception:
        return False


def _eh_ip_privado(ip: str) -> bool:
    """Evita o isolamento de endereços privados locais e nós de infraestrutura homologados (Google/Cloudflare/Blizzard)."""
    if not _eh_ip_valido(ip):
        return True
        
    ip_str = str(ip).strip()
    if ip_str.startswith("172.") or ip_str.startswith("142.") or ip_str.startswith("104.") or ip_str.startswith("74.") or ip_str.startswith("144."):
        return True
        
    try:
        p = [int(x) for x in ip.split(".")]
        if p[0] in (10, 127):
            return True
        if p[0] == 172 and 16 <= p[1] <= 31:
            return True
        if p[0] == 192 and p[1] == 168:
            return True
        if p[0] == 169 and p[1] == 254:
            return True
            
        # 🎯 VACINA DA BLIZZARD / CLOUDFLARE
        for subrede in SUBNETES_HOMOLOGADAS:
            if ip_pertence_a_subrede(ip_str, subrede):
                return True
                
        return False
    except Exception:
        return True


def _rodar_netsh(args: List[str], timeout: int = 5) -> Dict[str, Any]:
    try:
        r = subprocess.run(
            ["netsh"] + args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=timeout,
            shell=False,
        )
        return {
            "ok": r.returncode == 0,
            "codigo": r.returncode,
            "stdout": (r.stdout or "").strip(),
            "stderr": (r.stderr or "").strip(),
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "codigo": -2, "stdout": "", "stderr": "Timeout"}
    except Exception as e:
        return {"ok": False, "codigo": -1, "stdout": "", "stderr": str(e)}


def _bloquear_via_powershell(ip: str, direcao: str) -> bool:
    dir_ps = "Inbound" if direcao == "in" else "Outbound"
    nome = _nome_regra(ip, direcao)
    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-Command",
        f"New-NetFirewallRule -Name '{nome}' -DisplayName '{nome}' "
        f"-Direction {dir_ps} -Action Block -RemoteAddress '{ip}' -Enabled True"
    ]
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=5,
            shell=False,
        )
        return r.returncode == 0
    except Exception:
        return False


def _nome_regra(ip: str, direcao: str) -> str:
    return f"{PREFIXO_REGRA}{direcao}_{ip}"


def listar_regras_bloqueio() -> List[Dict[str, str]]:
    if not _eh_windows():
        return []

    resultado = _rodar_netsh(
        ["advfirewall", "firewall", "show", "rule", "name=all"],
        timeout=8
    )
    regras = []
    for linha in (resultado.get("stdout") or "").splitlines():
        low = linha.lower()
        if low.startswith("rule name:") or low.startswith("nome da regra:"):
            partes = linha.split(":", 1)
            nome = partes[1].strip() if len(partes) > 1 else ""
            if nome.startswith(PREFIXO_REGRA):
                resto = nome[len(PREFIXO_REGRA):]
                m = re.match(r"(out|in)_(\d+\.\d+\.\d+\.\d+)", resto)
                if m:
                    regras.append({
                        "nome": nome,
                        "direcao": m.group(1),
                        "ip": m.group(2),
                    })

    vistos = set()
    unicos = []
    for r in regras:
        chave = (r["ip"], r["direcao"])
        if chave not in vistos:
            vistos.add(chave)
            unicos.append(r)
            
    # Sincroniza dinamicamente o cache em RAM com as regras ativas encontradas
    for u in unicos:
        IPS_BLOQUEADOS_CACHE.add(u["ip"])
        
    return unicos


def ip_ja_bloqueado(ip: str) -> bool:
    if ip in IPS_BLOQUEADOS_CACHE:
        return True
    return any(r["ip"] == ip for r in listar_regras_bloqueio())


def desbloquear_ip(ip: str) -> Dict[str, Any]:
    """Remove as regras de bloqueio de entrada e saída para um IP específico."""
    ip = (ip or "").strip()
    if not _eh_windows():
        return {"ok": False, "ip": ip, "mensagem": "Disponível apenas no Windows."}

    ok = False
    for direcao in ("out", "in"):
        nome = _nome_regra(ip, direcao)
        r = _rodar_netsh(
            ["advfirewall", "firewall", "delete", "rule", f"name={nome}"],
            timeout=3
        )
        if not r["ok"]:
            cmd = [
                "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                "-Command", f"Remove-NetFirewallRule -Name '{nome}'"
            ]
            try:
                rx = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="ignore",
                    timeout=3,
                    shell=False,
                )
                if rx.returncode == 0:
                    r["ok"] = True
            except Exception:
                pass
        if r["ok"]:
            ok = True

    if ok:
        if ip in IPS_BLOQUEADOS_CACHE:
            IPS_BLOQUEADOS_CACHE.remove(ip)
        return {"ok": True, "ip": ip, "mensagem": f"IP {ip} liberado das restrições."}
    return {"ok": False, "ip": ip, "mensagem": f"Incapaz de revogar regras para o endereço {ip}."}


def registrar_aviso_bloqueio(ip: str, processo: str):
    """Registra uma notificação de auditoria local na Área de Trabalho com terminologia formal."""
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    arquivo = os.path.join(desktop, "Registro_Bloqueio_IP.txt")
    horario = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    conteudo = f"""
=============================================================
REGISTRO DE AUDITORIA E ISOLAMENTO DE REDE
=============================================================
Data/Hora do Evento: {horario}
Nó Isolado Definitivamente: {ip}
Identificador do Processo Concorrente: {processo}
Ação Aplicada: Restrição Bilateral Ativa via Firewall do Windows
=============================================================
"""
    try:
        with open(arquivo, "a", encoding="utf-8") as f:
            f.write(conteudo)
    except Exception:
        pass


def desbloquear_todos() -> Dict[str, Any]:
    """Remove todas as políticas temporárias aplicadas no Firewall do Windows."""
    regras = listar_regras_bloqueio()
    ips = sorted({r["ip"] for r in regras})
    ok = sum(1 for ip in ips if desbloquear_ip(ip).get("ok"))
    IPS_BLOQUEADOS_CACHE.clear()
    return {
        "ok": ok == len(ips) if ips else True,
        "mensagem": f"Restrições revogadas com sucesso para {ok}/{len(ips)} IP(s).",
        "total": len(ips),
        "sucesso": ok,
    }

def bloquear_ip(ip: str) -> Dict[str, Any]:
    """Aplica as regras de restrição bilateral no Firewall do Windows para o IP especificado."""
    ip = (ip or "").strip()

    if not _eh_windows():
        return {"ok": False, "ip": ip, "mensagem": "Disponível apenas no Windows."}
    if not _eh_ip_valido(ip):
        return {"ok": False, "ip": ip, "mensagem": "IP inválido."}
    if _eh_ip_privado(ip):
        return {"ok": False, "ip": ip, "mensagem": "IPs protegidos pela infraestrutura não são bloqueados."}
    if ip_ja_bloqueado(ip):
        return {
            "ok": True,
            "ip": ip,
            "mensagem": f"IP {ip} já estava bloqueado.",
            "ja_existia": True,
        }

    resultados = []
    for direcao in ("out", "in"):
        nome = _nome_regra(ip, direcao)
        _rodar_netsh(
            ["advfirewall", "firewall", "delete", "rule", f"name={nome}"],
            timeout=3
        )

        r = _rodar_netsh([
            "advfirewall", "firewall", "add", "rule",
            f"name={nome}", f"dir={direcao}", "action=block",
            f"remoteip={ip}", "enable=yes", "profile=any"
        ], timeout=3)

        if not r["ok"]:
            if _bloquear_via_powershell(ip, direcao):
                r = {
                    "ok": True,
                    "codigo": 0,
                    "stdout": "Bloqueado via PowerShell",
                    "stderr": "",
                }

        resultados.append(r)

    if all(r["ok"] for r in resultados):
        # Sucesso absoluto: adiciona o IP ao cache em RAM instantaneamente
        IPS_BLOQUEADOS_CACHE.add(ip)
        return {
            "ok": True,
            "ip": ip,
            "mensagem": f"IP {ip} isolado com sucesso (entrada e saída).",
        }

    erros = " | ".join(
        (r["stderr"] or r["stdout"] or str(r["codigo"]))
        for r in resultados if not r["ok"]
    )
    dica = ""
    if any(x in erros.lower() for x in ("access", "acesso", "denied", "negado")):
        dica = " Execute como Administrador com privilégios elevados."

    return {
        "ok": False,
        "ip": ip,
        "mensagem": f"Falha ao bloquear {ip}: {erros}.{dica}",
    }


def desbloquear_ip(ip: str) -> Dict[str, Any]:
    """Remove as regras de bloqueio de entrada e saída para um IP específico."""
    ip = (ip or "").strip()
    if not _eh_windows():
        return {"ok": False, "ip": ip, "mensagem": "Disponível apenas no Windows."}

    ok = False
    for direcao in ("out", "in"):
        nome = _nome_regra(ip, direcao)
        r = _rodar_netsh(
            ["advfirewall", "firewall", "delete", "rule", f"name={nome}"],
            timeout=3
        )
        if not r["ok"]:
            cmd = [
                "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                "-Command", f"Remove-NetFirewallRule -Name '{nome}'"
            ]
            try:
                rx = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="ignore",
                    timeout=3,
                    shell=False,
                )
                if rx.returncode == 0:
                    r["ok"] = True
            except Exception:
                pass
        if r["ok"]:
            ok = True

    if ok:
        if ip in IPS_BLOQUEADOS_CACHE:
            IPS_BLOQUEADOS_CACHE.remove(ip)
        return {"ok": True, "ip": ip, "mensagem": f"IP {ip} liberado das restrições."}
    return {"ok": False, "ip": ip, "mensagem": f"Incapaz de revogar regras para o endereço {ip}."}


def registrar_aviso_bloqueio(ip: str, processo: str):
    """Registra uma notificação de auditoria local na Área de Trabalho com terminologia formal."""
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    arquivo = os.path.join(desktop, "Registro_Bloqueio_IP.txt")
    horario = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    conteudo = f"""
=============================================================
REGISTRO DE AUDITORIA E ISOLAMENTO DE REDE
=============================================================
Data/Hora do Evento: {horario}
Nó Isolado Definitivamente: {ip}
Identificador do Processo Concorrente: {processo}
Ação Aplicada: Restrição Bilateral Ativa via Firewall do Windows
=============================================================
"""
    try:
        with open(arquivo, "a", encoding="utf-8") as f:
            f.write(conteudo)
    except Exception:
        pass


def desbloquear_todos() -> Dict[str, Any]:
    """Remove todas as políticas temporárias aplicadas no Firewall do Windows."""
    regras = listar_regras_bloqueio()
    ips = sorted({r["ip"] for r in rules})
    ok = sum(1 for ip in ips if desbloquear_ip(ip).get("ok"))
    IPS_BLOQUEADOS_CACHE.clear()
    return {
        "ok": ok == len(ips) if ips else True,
        "mensagem": f"Restrições revogadas com sucesso para {ok}/{len(ips)} IP(s).",
        "total": len(ips),
        "sucesso": ok,
    }


def bloquear_ips_suspeitos(ips_suspeitos=None) -> Dict[str, Any]:
    """Orquestra o monitoramento em background e despacha os nós para mitigação no Firewall."""
    if ips_suspeitos is None:
        try:
            from modules.diagnostico_rede import analisar_ips_suspeitos
            dados = analisar_ips_suspeitos()
            ips_suspeitos = dados.get("suspeitos") or []
        except Exception as e:
            return {
                "ok": False,
                "mensagem": f"Falha na varredura de conexões: {e}",
                "bloqueados": [],
                "falhas": [],
            }

    bloqueados = []
    falhas = []
    vistos = set()

    # Coleta as portas locais ativas antes de rodar o bloco
    conexoes_ativas = {conn.raddr.ip: conn for conn in psutil.net_connections() if conn.raddr}

    for item in ips_suspeitos:
        ip = item.get("ip") if isinstance(item, dict) else str(item)
        if not ip or ip in vistos:
            continue
        vistos.add(ip)

        # Captura as portas locais e remotas da conexão suspeita em tempo real
        porta_local = "Desconhecida"
        porta_remota = "Desconhecida"
        if ip in conexoes_ativas:
            porta_local = conexoes_ativas[ip].laddr.port
            porta_remota = conexoes_ativas[ip].raddr.port

        proc_nome = "Desconhecido"
        if isinstance(item, dict):
            pid_alvo = item.get("pid")
            proc_nome = obter_nome_processo_seguro(pid_alvo) if pid_alvo else item.get("processo", "Desconhecido")

        # Incrementa o nome do processo adicionando as portas capturadas para o log do terminal
        proc_com_portas = f"{proc_nome} [Porta Local: {porta_local} -> Porta Cracker: {porta_remota}]"

        r = bloquear_ip(ip)  # noqa: F841
        if r.get("ok"):
            if not r.get("ja_existia"):
                bloqueados.append(r)
                registrar_aviso_bloqueio(ip, proc_com_portas)
        else:
            falhas.append(r)

    return {
        "ok": len(falhas) == 0 if bloqueados else True,
        "mensagem": f"Isolamento concluído. {len(bloqueados)} nós mitigados, {len(falhas)} falhas.",
        "bloqueados": bloqueados,
        "falhas": falhas,
    }

