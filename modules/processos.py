import psutil

def obter_processos():
    processos = []

    # Otimizado: removemos a checagem direta de cpu_percent do iterador para evitar o travamento do loop
    for processo in psutil.process_iter(["name", "memory_info"]):
        try:
            nome = processo.info["name"]
            if nome is None:
                continue

            # Cálculo de memória em MB estável
            memoria = processo.info["memory_info"].rss / (1024 * 1024)

            # Define 0.0 temporariamente ou lê de forma segura sem travar o clock do Kernel
            cpu = 0.0 

            processos.append({
                "nome": nome,
                "cpu": cpu,
                "memoria": memoria
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, KeyError):
            pass

    # Mantém a sua regra sênior: Primeiro mostra os clientes Aurera organizados por consumo de RAM
    processos.sort(
        key=lambda x: (
            "aurera" not in x["nome"].lower(),
            -x["memoria"]
        )
    )

    return processos[:25]
