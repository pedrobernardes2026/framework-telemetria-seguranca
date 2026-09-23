import psutil


def obter_processos():

    processos = []


    for processo in psutil.process_iter(
        ["name", "cpu_percent", "memory_info"]
    ):

        try:

            nome = processo.info["name"]

            if nome is None:
                continue


            memoria = (
                processo.info["memory_info"].rss /
                (1024 * 1024)
            )


            cpu = processo.info["cpu_percent"]


            processos.append(
                {
                    "nome": nome,
                    "cpu": cpu,
                    "memoria": memoria
                }
            )


        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            pass



    # Primeiro mostra clientes Aurera
    processos.sort(
        key=lambda x: (
            "aurera" not in x["nome"].lower(),
            -x["memoria"]
        )
    )


    return processos[:25]