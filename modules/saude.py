def calcular_saude(cpu, ram, disco, rede, aurera):

    nota = 100
    mensagens = []

    # ==========================
    # CPU
    # ==========================

    if cpu >= 95:
        nota -= 30
        mensagens.append("CPU em estado crítico")

    elif cpu >= 80:
        nota -= 15
        mensagens.append("CPU com carga elevada")


    # ==========================
    # RAM
    # ==========================

    if ram >= 95:
        nota -= 30
        mensagens.append("Memória RAM crítica")

    elif ram >= 85:
        nota -= 15
        mensagens.append("Memória RAM elevada")


    # ==========================
    # DISCO
    # ==========================

    if disco >= 95:
        nota -= 25
        mensagens.append("Disco em uso crítico")

    elif disco >= 80:
        nota -= 10
        mensagens.append("Disco com uso elevado")


    # ==========================
    # REDE
    # ==========================

    download = rede.get("download", 0)
    upload = rede.get("upload", 0)

    if download > 80:
        nota -= 5
        mensagens.append("Download elevado")

    if upload > 40:
        nota -= 5
        mensagens.append("Upload elevado")


    # ==========================
    # AURERA
    # ==========================

    memoria_aurera = aurera.get("ram", 0)
    cpu_aurera = aurera.get("cpu", 0)


    if memoria_aurera >= 6000:
        nota -= 20
        mensagens.append("Aurera consumindo muita memória")

    elif memoria_aurera >= 3000:
        nota -= 10
        mensagens.append("Aurera com consumo elevado")


    if cpu_aurera >= 80:
        nota -= 15
        mensagens.append("Aurera usando CPU excessiva")

    elif cpu_aurera >= 60:
        nota -= 10
        mensagens.append("Aurera usando muita CPU")


    # ==========================
    # Limite da nota
    # ==========================

    if nota < 0:
        nota = 0


    # ==========================
    # Classificação
    # ==========================

    if nota >= 90:
        status = "Excelente"

    elif nota >= 70:
        status = "Bom"

    elif nota >= 50:
        status = "Atenção"

    else:
        status = "Crítico"


    # ==========================
    # Retorno
    # ==========================

    return {
        "nota": nota,
        "status": status,
        "mensagens": mensagens
    }