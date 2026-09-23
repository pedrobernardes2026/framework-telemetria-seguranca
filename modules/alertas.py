def verificar_alertas(cpu, ram, disco, aurera=None):
    """
    Retorna dicionário padronizado de alertas.
    {
        "nivel": "BAIXO" | "MÉDIO" | "ALTO" | "CRÍTICO",
        "mensagens": [str, ...]
    }
    """
    mensagens = []
    nivel = "BAIXO"

    if cpu >= 95:
        mensagens.append("CPU em estado crítico (≥ 95%)")
        nivel = "CRÍTICO"
    elif cpu >= 85:
        mensagens.append("CPU com carga muito elevada (≥ 85%)")
        if nivel != "CRÍTICO":
            nivel = "ALTO"
    elif cpu >= 75:
        mensagens.append("CPU com carga elevada (≥ 75%)")
        if nivel == "BAIXO":
            nivel = "MÉDIO"

    if ram >= 95:
        mensagens.append("Memória RAM em estado crítico (≥ 95%)")
        nivel = "CRÍTICO"
    elif ram >= 90:
        mensagens.append("Memória RAM muito elevada (≥ 90%)")
        if nivel not in ("CRÍTICO",):
            nivel = "ALTO"
    elif ram >= 80:
        mensagens.append("Memória RAM elevada (≥ 80%)")
        if nivel == "BAIXO":
            nivel = "MÉDIO"

    if disco >= 95:
        mensagens.append("Disco em uso crítico (≥ 95%)")
        nivel = "CRÍTICO"
    elif disco >= 90:
        mensagens.append("Disco com uso muito elevado (≥ 90%)")
        if nivel not in ("CRÍTICO",):
            nivel = "ALTO"
    elif disco >= 80:
        mensagens.append("Disco com uso elevado (≥ 80%)")
        if nivel == "BAIXO":
            nivel = "MÉDIO"

    if aurera is not None:
        memoria_aurera = aurera.get("ram", 0)
        cpu_aurera = aurera.get("cpu", 0)
        clientes = aurera.get("clientes", 0)

        if memoria_aurera >= 6000:
            mensagens.append(f"Aurera consumindo muita memória ({memoria_aurera:.0f} MB)")
            if nivel not in ("CRÍTICO",):
                nivel = "ALTO"
        elif memoria_aurera >= 3500:
            mensagens.append(f"Aurera com consumo elevado de memória ({memoria_aurera:.0f} MB)")
            if nivel == "BAIXO":
                nivel = "MÉDIO"

        if cpu_aurera >= 80:
            mensagens.append(f"Aurera usando CPU excessiva ({cpu_aurera:.1f}%)")
            if nivel not in ("CRÍTICO",):
                nivel = "ALTO"
        elif cpu_aurera >= 60:
            mensagens.append(f"Aurera usando muita CPU ({cpu_aurera:.1f}%)")
            if nivel == "BAIXO":
                nivel = "MÉDIO"

        if clientes >= 5:
            mensagens.append(f"Muitos clientes Aurera abertos ({clientes})")
            if nivel == "BAIXO":
                nivel = "MÉDIO"

    if not mensagens:
        mensagens.append("Nenhum alerta no momento.")

    return {
        "nivel": nivel,
        "mensagens": mensagens
    }
