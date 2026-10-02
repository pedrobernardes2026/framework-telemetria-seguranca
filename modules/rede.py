import socket
import psutil


def obter_rede():
    """
    Retorna estatísticas gerais da interface de rede.
    """

    io = psutil.net_io_counters()

    return {
        "enviados": round(io.bytes_sent / (1024 * 1024), 2),
        "recebidos": round(io.bytes_recv / (1024 * 1024), 2),
        "pacotes_enviados": io.packets_sent,
        "pacotes_recebidos": io.packets_recv,
        "erros_entrada": io.errin,
        "erros_saida": io.errout,
        "descartados_entrada": io.dropin,
        "descartados_saida": io.dropout,
    }


def obter_conexoes():
    """
    Retorna todas as conexões TCP/UDP abertas associadas ao processo.
    """

    conexoes = []

    for conexao in psutil.net_connections(kind="inet"):

        try:

            pid = conexao.pid

            if pid is None:
                continue

            processo = psutil.Process(pid)

            nome = processo.name()

            ip_local = (
                conexao.laddr.ip
                if conexao.laddr else ""
            )

            porta_local = (
                conexao.laddr.port
                if conexao.laddr else ""
            )

            ip_remoto = (
                conexao.raddr.ip
                if conexao.raddr else ""
            )

            porta_remota = (
                conexao.raddr.port
                if conexao.raddr else ""
            )

            conexoes.append(
                {
                    "processo": nome,
                    "pid": pid,
                    "ip_local": ip_local,
                    "porta_local": porta_local,
                    "ip_remoto": ip_remoto,
                    "porta_remota": porta_remota,
                    "status": conexao.status,
                }
            )

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            pass

    conexoes.sort(
        key=lambda c: (
            c["processo"].lower(),
            c["ip_remoto"]
        )
    )

    return conexoes


def obter_ips_unicos():
    """
    Retorna somente IPs remotos únicos.
    """

    ips = set()

    for conexao in obter_conexoes():

        if conexao["ip_remoto"]:
            ips.add(conexao["ip_remoto"])

    return sorted(ips)


def obter_processos_rede():
    """
    Quantidade de conexões por processo.
    """

    contador = {}

    for conexao in obter_conexoes():

        nome = conexao["processo"]

        contador[nome] = contador.get(nome, 0) + 1

    lista = []

    for nome, quantidade in contador.items():

        lista.append(
            {
                "processo": nome,
                "conexoes": quantidade
            }
        )

    lista.sort(
        key=lambda x: x["conexoes"],
        reverse=True
    )

    return lista