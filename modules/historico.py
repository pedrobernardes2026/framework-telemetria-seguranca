from collections import deque


# Quantidade de pontos mantidos no gráfico
MAX_PONTOS = 60


cpu_historico = deque(maxlen=MAX_PONTOS)
ram_historico = deque(maxlen=MAX_PONTOS)
disco_historico = deque(maxlen=MAX_PONTOS)

download_historico = deque(maxlen=MAX_PONTOS)
upload_historico = deque(maxlen=MAX_PONTOS)



def adicionar_dados(
    cpu,
    ram,
    disco,
    download,
    upload
):

    cpu_historico.append(cpu)

    ram_historico.append(ram)

    disco_historico.append(disco)

    download_historico.append(download)

    upload_historico.append(upload)



def obter_historico():

    return {
        "cpu": list(cpu_historico),
        "ram": list(ram_historico),
        "disco": list(disco_historico),
        "download": list(download_historico),
        "upload": list(upload_historico)
    }