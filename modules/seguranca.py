from modules.rede import obter_conexoes


# Processos considerados conhecidos (nome exato, em minúsculo)
PROCESSOS_CONHECIDOS = {
    "explorer.exe",
    "firefox.exe",
    "chrome.exe",
    "msedge.exe",
    "msedgewebview2.exe",
    "brave.exe",
    "opera.exe",
    "discord.exe",
    "steam.exe",
    "steamwebhelper.exe",
    "code.exe",
    "python.exe",
    "pythonw.exe",
    "taskmgr.exe",
    "memcompression",
    "dwm.exe",
    "svchost.exe",
    "runtimebroker.exe",
    "searchhost.exe",
    "searchindexer.exe",
    "ctfmon.exe",
    "fontdrvhost.exe",
    "sihost.exe",
    "wininit.exe",
    "winlogon.exe",
    "services.exe",
    "lsass.exe",
    "csrss.exe",
    "registry",
    "system",
    "system idle process",
    "onedrive.exe",
    "onedrive.sync.service.exe",
    "gcloud.exe",
    "msmpeng.exe",
    "nissrv.exe",
    "securityhealthservice.exe",
    "spoolsv.exe",
    "conhost.exe",
    "cmd.exe",
    "powershell.exe",
    "applicationframehost.exe",
    "shellexperiencehost.exe",
    "startmenuexperiencehost.exe",
    "textinputhost.exe",
    "widgetservice.exe",
    "widgets.exe",
}


# Portas comuns / esperadas (incluindo Aurera)
PORTAS_COMUNS = {
    80,
    443,
    53,
    123,
    3389,
    7171,
    7172,
    # Portas do cliente Aurera
    7152,
    7154,
    7155,
    8080,
    8443,
}


def _eh_aurera(nome: str) -> bool:
    """Qualquer processo do cliente Aurera (nome dinâmico)."""
    if not nome:
        return False
    n = nome.lower()
    return n.startswith("aurera") or "aurera_gl" in n


def _eh_conhecido(nome: str) -> bool:
    """Processo conhecido ou whitelist (Aurera)."""
    if not nome:
        return False
    n = nome.lower().strip()
    if n in PROCESSOS_CONHECIDOS:
        return True
    if _eh_aurera(n):
        return True
    return False


def analisar_seguranca(processos):

    alertas = []
    score = 100

    conexoes = obter_conexoes()

    # ------------------------
    # Processos desconhecidos
    # ------------------------

    for processo in processos:
        nome = (processo.get("nome") or "").lower()

        if not _eh_conhecido(nome):
            alertas.append({
                "nivel": "MÉDIO",
                "tipo": "Processo desconhecido",
                "descricao": nome
            })
            score -= 2

    # ------------------------
    # Muitas conexões
    # (ignora Aurera — normal ter dezenas de conexões)
    # ------------------------

    contador = {}

    for conexao in conexoes:
        nome = (conexao.get("processo") or "").lower()
        contador[nome] = contador.get(nome, 0) + 1

    for nome, quantidade in contador.items():
        if _eh_aurera(nome):
            continue

        if quantidade > 50:
            alertas.append({
                "nivel": "ALTO",
                "tipo": "Muitas conexões",
                "descricao": f"{nome} possui {quantidade} conexões."
            })
            score -= 10

    # ------------------------
    # Portas incomuns
    # (ignora Aurera nas portas do jogo)
    # ------------------------

    for conexao in conexoes:
        porta = conexao.get("porta_remota")
        nome = (conexao.get("processo") or "")

        if not porta:
            continue

        if porta in PORTAS_COMUNS:
            continue

        # Aurera em porta do jogo já está em PORTAS_COMUNS;
        # se aparecer outra porta do Aurera, não penaliza forte
        if _eh_aurera(nome):
            continue

        alertas.append({
            "nivel": "BAIXO",
            "tipo": "Porta incomum",
            "descricao": (
                f"{nome} conectado na porta {porta}"
            )
        })
        score -= 1

    # ------------------------
    # Status das conexões
    # (ignora Aurera — SYN_SENT é comum ao conectar)
    # ------------------------

    for conexao in conexoes:
        status = conexao.get("status")
        nome = (conexao.get("processo") or "")

        if status not in ("SYN_SENT", "CLOSE_WAIT"):
            continue

        if _eh_aurera(nome):
            continue

        alertas.append({
            "nivel": "MÉDIO",
            "tipo": "Conexão incomum",
            "descricao": f"{nome} está em {status}"
        })
        score -= 5

    score = max(score, 0)

    if score >= 90:
        status = "SEGURO"
    elif score >= 70:
        status = "ATENÇÃO"
    else:
        status = "RISCO"

    if not alertas:
        mensagem = "Nenhum alerta encontrado."
    else:
        mensagem = f"{len(alertas)} alerta(s) encontrado(s)."

    return {
        "status": status,
        "score": score,
        "mensagem": mensagem,
        "total_alertas": len(alertas),
        "alertas": alertas,
    }
