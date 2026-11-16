"""
Histórico de conexões de rede durante a sessão.

Coleta periodicamente as conexões ativas e mantém um registro
do que foi observado enquanto o programa está aberto.
Útil para ver o que aconteceu durante a ausência do usuário.
"""

from datetime import datetime
from collections import defaultdict


# ------------------------------------------------------------
# Estado global da sessão
# ------------------------------------------------------------

_inicio_sessao = datetime.now()
_ultima_coleta = None

# ip -> dados agregados
_ips = {}

# processo -> contagem de vezes visto com rede
_processos = defaultdict(int)

# total de coletas feitas
_coletas = 0


def _eh_privado(ip: str) -> bool:
    if not ip:
        return True
    try:
        p = [int(x) for x in ip.split(".")]
        if len(p) != 4:
            return True
        if p[0] == 127:
            return True
        if p[0] == 10:
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


def registrar_conexoes(detalhes_conexoes):
    """
    Recebe a lista de detalhes de conexões (mesmo formato de
    obter_conexoes()["detalhes"]) e atualiza o histórico da sessão.

    Deve ser chamado periodicamente pelo dashboard.
    """
    global _ultima_coleta, _coletas

    agora = datetime.now()
    _ultima_coleta = agora
    _coletas += 1

    for item in detalhes_conexoes:
        ip = item.get("ip_remoto") or ""
        if not ip or _eh_privado(ip):
            continue

        processo = item.get("processo") or "Desconhecido"
        porta = item.get("porta_remota")
        estado = item.get("estado") or ""

        _processos[processo] += 1

        if ip not in _ips:
            _ips[ip] = {
                "ip": ip,
                "primeira_vez": agora,
                "ultima_vez": agora,
                "vezes_visto": 1,
                "portas": set(),
                "processos": set(),
                "estados": set(),
            }
        else:
            _ips[ip]["ultima_vez"] = agora
            _ips[ip]["vezes_visto"] += 1

        if porta:
            try:
                _ips[ip]["portas"].add(int(porta))
            except Exception:
                pass

        _ips[ip]["processos"].add(processo)
        if estado:
            _ips[ip]["estados"].add(estado)


def obter_historico_conexoes():
    """
    Retorna o resumo completo do histórico da sessão.
    """
    agora = datetime.now()
    duracao = agora - _inicio_sessao
    horas = int(duracao.total_seconds() // 3600)
    minutos = int((duracao.total_seconds() % 3600) // 60)

    # Ordena IPs pelos mais observados
    lista_ips = []
    for ip, dados in _ips.items():
        lista_ips.append({
            "ip": ip,
            "vezes_visto": dados["vezes_visto"],
            "primeira_vez": dados["primeira_vez"].strftime("%H:%M:%S"),
            "ultima_vez": dados["ultima_vez"].strftime("%H:%M:%S"),
            "portas": sorted(dados["portas"]),
            "processos": sorted(dados["processos"]),
            "estados": sorted(dados["estados"]),
        })

    lista_ips.sort(key=lambda x: -x["vezes_visto"])

    # Top processos por atividade de rede observada
    top_processos = sorted(
        [{"processo": k, "ocorrencias": v} for k, v in _processos.items()],
        key=lambda x: -x["ocorrencias"]
    )[:20]

    return {
        "inicio_sessao": _inicio_sessao.strftime("%d/%m/%Y %H:%M:%S"),
        "ultima_coleta": (
            _ultima_coleta.strftime("%d/%m/%Y %H:%M:%S")
            if _ultima_coleta else "Nenhuma"
        ),
        "duracao": f"{horas}h {minutos}min",
        "duracao_segundos": int(duracao.total_seconds()),
        "total_coletas": _coletas,
        "total_ips_unicos": len(lista_ips),
        "ips": lista_ips,
        "top_processos": top_processos,
    }


def limpar_historico_conexoes():
    """Reinicia o histórico da sessão (opcional)."""
    global _inicio_sessao, _ultima_coleta, _coletas
    _inicio_sessao = datetime.now()
    _ultima_coleta = None
    _coletas = 0
    _ips.clear()
    _processos.clear()
