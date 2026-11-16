import psutil
import time


ultimo = psutil.net_io_counters()
ultimo_tempo = time.time()


def obter_rede():

    global ultimo
    global ultimo_tempo

    atual = psutil.net_io_counters()
    tempo = time.time()

    intervalo = tempo - ultimo_tempo

    if intervalo == 0:
        intervalo = 1

    download = (atual.bytes_recv - ultimo.bytes_recv) / intervalo
    upload = (atual.bytes_sent - ultimo.bytes_sent) / intervalo

    ultimo = atual
    ultimo_tempo = tempo

    return {
        "download": download / 1024 / 1024,
        "upload": upload / 1024 / 1024,
        "recebido": atual.bytes_recv / 1024 / 1024 / 1024,
        "enviado": atual.bytes_sent / 1024 / 1024 / 1024
    }