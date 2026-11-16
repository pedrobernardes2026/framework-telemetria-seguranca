from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.platypus import Table, TableStyle

from reportlab.lib import colors

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import navy
from reportlab.lib.units import cm

from reportlab.pdfbase import pdfmetrics

import os

from datetime import datetime

from modules.diagnostico_rede import analisar_rede


def gerar_relatorio(
    cpu,
    ram,
    disco,
    rede,
    aurera,
    saude,
    alerta,
    seguranca,
    processos,
    historico_conexoes=None
):

    os.makedirs(
        "Relatorios",
        exist_ok=True
    )

    agora = datetime.now()

    diagnostico_rede = analisar_rede()

    nome_pdf = (
        f"Relatorios/Relatorio_"
        f"{agora.strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
    )

    documento = SimpleDocTemplate(
        nome_pdf,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm
    )

    estilos = getSampleStyleSheet()

    titulo = estilos["Heading1"]
    titulo.alignment = TA_CENTER
    titulo.textColor = navy

    subtitulo = estilos["Heading2"]

    normal = estilos["BodyText"]

    elementos = []

    elementos.append(
        Paragraph(
            "Sistema de Análise de Desempenho",
            titulo
        )
    )

    elementos.append(
        Paragraph(
            "Relatório de Diagnóstico",
            subtitulo
        )
    )

    elementos.append(
        Spacer(
            1,
            0.5 * cm
        )
    )

    elementos.append(
        Paragraph(
            f"Data: {agora.strftime('%d/%m/%Y')}",
            normal
        )
    )

    elementos.append(
        Paragraph(
            f"Hora: {agora.strftime('%H:%M:%S')}",
            normal
        )
    )

    elementos.append(
        Spacer(
            1,
            0.8 * cm
        )
    )

    # ==================================================
    # RESUMO
    # ==================================================

    elementos.append(
        Paragraph(
            "<b>RESUMO DO SISTEMA</b>",
            subtitulo
        )
    )

    elementos.append(
        Paragraph(
            f"Nota Geral: <b>{saude['nota']}/100</b>",
            normal
        )
    )

    elementos.append(
        Paragraph(
            f"Status: <b>{saude['status']}</b>",
            normal
        )
    )

    elementos.append(
        Spacer(
            1,
            0.4 * cm
        )
    )


    # ==================================================
    # USO DOS RECURSOS
    # ==================================================

    elementos.append(
        Paragraph(
            "<b>USO DOS RECURSOS</b>",
            subtitulo
        )
    )

    elementos.append(
        Paragraph(
            f"CPU: {cpu:.1f}%",
            normal
        )
    )

    elementos.append(
        Paragraph(
            f"Memória RAM: {ram:.1f}%",
            normal
        )
    )

    elementos.append(
        Paragraph(
            f"Disco: {disco:.1f}%",
            normal
        )
    )

    elementos.append(
        Paragraph(
            f"Download: {rede['download']:.2f} MB/s",
            normal
        )
    )

    elementos.append(
        Paragraph(
            f"Upload: {rede['upload']:.2f} MB/s",
            normal
        )
    )

    elementos.append(
        Spacer(
            1,
            0.4 * cm
        )
    )

    # ==================================================
    # AURERA GLOBAL
    # ==================================================

    elementos.append(
        Paragraph(
            "<b>AURERA GLOBAL</b>",
            subtitulo
        )
    )

    elementos.append(
        Paragraph(
            f"Clientes abertos: {aurera['clientes']}",
            normal
        )
    )

    elementos.append(
        Paragraph(
            f"RAM utilizada: {aurera['ram']:.0f} MB",
            normal
        )
    )

    elementos.append(
        Paragraph(
            f"CPU utilizada: {aurera['cpu']:.1f}%",
            normal
        )
    )

    elementos.append(
        Spacer(
            1,
            0.5 * cm
        )
    )


    # ==================================================
    # ANÁLISE DA SAÚDE
    # ==================================================

    elementos.append(
        Paragraph(
            "<b>ANÁLISE DA SAÚDE</b>",
            subtitulo
        )
    )

    if saude["mensagens"]:

        for mensagem in saude["mensagens"]:

            elementos.append(
                Paragraph(
                    f"• {mensagem}",
                    normal
                )
            )

    else:

        elementos.append(
            Paragraph(
                "• Sistema funcionando normalmente.",
                normal
            )
        )


    elementos.append(
        Spacer(
            1,
            0.4 * cm
        )
    )


    # ==================================================
    # ALERTAS
    # ==================================================

    elementos.append(
        Paragraph(
            "<b>ALERTAS</b>",
            subtitulo
        )
    )

    elementos.append(
        Paragraph(
            f"Nível: <b>{alerta['nivel']}</b>",
            normal
        )
    )


    for mensagem in alerta["mensagens"]:

        elementos.append(
            Paragraph(
                f"• {mensagem}",
                normal
            )
        )


    elementos.append(
        Spacer(
            1,
            0.4 * cm
        )
    )


    # ==================================================
    # SEGURANÇA
    # ==================================================

    elementos.append(
        Paragraph(
            "<b>SEGURANÇA</b>",
            subtitulo
        )
    )

    elementos.append(
        Paragraph(
            f"Status: <b>{seguranca['status']}</b>",
            normal
        )
    )

    elementos.append(
        Paragraph(
            seguranca["mensagem"],
            normal
        )
    )

    elementos.append(
        Spacer(
            1,
            0.5 * cm
        )
    )

    # ==================================================
    # DIAGNÓSTICO DE REDE
    # ==================================================

    elementos.append(
        Paragraph(
            "<b>DIAGNÓSTICO DE REDE</b>",
            subtitulo
        )
    )

    elementos.append(
        Paragraph(
            f"Hostname: {diagnostico_rede['hostname']}",
            normal
        )
    )

    elementos.append(
        Paragraph(
            f"IP Local: {diagnostico_rede['ip_local']}",
            normal
        )
    )

    elementos.append(
        Paragraph(
            f"IP Público: {diagnostico_rede['ip_publico']}",
            normal
        )
    )

    elementos.append(
        Paragraph(
            f"MAC: {diagnostico_rede['mac']}",
            normal
        )
    )

    elementos.append(
        Paragraph(
            f"Interface: {diagnostico_rede['interface']}",
            normal
        )
    )

    # Estatísticas rápidas de conexão
    con = diagnostico_rede.get("conexoes", {})
    elementos.append(Spacer(1, 0.3 * cm))
    elementos.append(
        Paragraph(
            f"Conexões — TCP: {con.get('tcp', 0)}  |  UDP: {con.get('udp', 0)}  |  "
            f"ESTABLISHED: {con.get('established', 0)}  |  LISTEN: {con.get('listen', 0)}  |  "
            f"TIME_WAIT: {con.get('time_wait', 0)}  |  CLOSE_WAIT: {con.get('close_wait', 0)}",
            normal
        )
    )

    diag = diagnostico_rede.get("diagnostico", {})
    elementos.append(
        Paragraph(
            f"Nota da rede: <b>{diag.get('nota', '-')}/100</b>",
            normal
        )
    )
    if diag.get("alertas"):
        for a in diag["alertas"]:
            elementos.append(Paragraph(f"• {a}", normal))

    elementos.append(Spacer(1, 0.5 * cm))

    # ==================================================
    # IPs SUSPEITOS (ANÁLISE DETALHADA)
    # ==================================================

    elementos.append(
        Paragraph(
            "<b>IPs SUSPEITOS — ANÁLISE DETALHADA</b>",
            subtitulo
        )
    )

    ips_data = diagnostico_rede.get("ips_suspeitos") or {}
    resumo_ips = ips_data.get("resumo") or {}
    lista_suspeitos = ips_data.get("suspeitos") or []
    todos_publicos = ips_data.get("todos_ips_publicos") or []

    nivel_geral = resumo_ips.get("nivel_geral", "BAIXO")
    cor_nivel = {
        "ALTO": colors.Color(0.75, 0.1, 0.1),
        "MÉDIO": colors.Color(0.85, 0.45, 0.05),
        "BAIXO": colors.Color(0.1, 0.55, 0.2),
    }.get(nivel_geral, colors.grey)

    elementos.append(
        Paragraph(
            f"Nível geral de risco: <b>{nivel_geral}</b>",
            normal
        )
    )
    elementos.append(
        Paragraph(
            f"IPs públicos observados agora: <b>{resumo_ips.get('ips_publicos', len(todos_publicos))}</b>  |  "
            f"IPs classificados como suspeitos: <b>{resumo_ips.get('ips_suspeitos', len(lista_suspeitos))}</b>",
            normal
        )
    )
    elementos.append(Spacer(1, 0.35 * cm))

    if lista_suspeitos:
        # --- Tabela resumo (todos os suspeitos) ---
        elementos.append(
            Paragraph(
                "<b>Resumo dos IPs suspeitos (ordenados por risco e volume)</b>",
                normal
            )
        )
        elementos.append(Spacer(1, 0.2 * cm))

        tabela_sus = [["Nível", "IP", "Conexões", "Portas", "Processos", "Motivos"]]

        for item in lista_suspeitos:
            portas_str = ", ".join(str(p) for p in item.get("portas", [])[:8])
            if len(item.get("portas", [])) > 8:
                portas_str += "..."
            procs_str = ", ".join(item.get("processos", [])[:4])
            if len(item.get("processos", [])) > 4:
                procs_str += "..."
            motivos_str = "; ".join(item.get("motivos", [])[:3])
            if len(motivos_str) > 70:
                motivos_str = motivos_str[:67] + "..."

            tabela_sus.append([
                item.get("nivel", "-"),
                item.get("ip", "-"),
                str(item.get("quantidade", 0)),
                portas_str or "-",
                procs_str or "-",
                motivos_str or "-",
            ])

        tabela_sus_pdf = Table(
            tabela_sus,
            colWidths=[1.6 * cm, 3.2 * cm, 1.7 * cm, 2.8 * cm, 3.2 * cm, 4.0 * cm]
        )

        estilo_sus = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.45, 0.05, 0.05)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("ALIGN", (0, 0), (2, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ]

        # Colorir linhas por nível de risco
        for idx, item in enumerate(lista_suspeitos, start=1):
            nivel = item.get("nivel", "")
            if nivel == "ALTO":
                estilo_sus.append(
                    ("BACKGROUND", (0, idx), (-1, idx), colors.Color(1.0, 0.85, 0.85))
                )
            elif nivel == "MÉDIO":
                estilo_sus.append(
                    ("BACKGROUND", (0, idx), (-1, idx), colors.Color(1.0, 0.94, 0.80))
                )
            else:
                estilo_sus.append(
                    ("BACKGROUND", (0, idx), (-1, idx), colors.Color(0.92, 0.95, 0.92))
                )

        tabela_sus_pdf.setStyle(TableStyle(estilo_sus))
        elementos.append(tabela_sus_pdf)
        elementos.append(Spacer(1, 0.45 * cm))

        # --- Detalhamento individual de cada IP suspeito ---
        elementos.append(
            Paragraph(
                "<b>Detalhamento individual de cada IP suspeito</b>",
                normal
            )
        )
        elementos.append(Spacer(1, 0.25 * cm))

        for i, item in enumerate(lista_suspeitos, start=1):
            nivel = item.get("nivel", "-")
            ip = item.get("ip", "-")
            qtd = item.get("quantidade", 0)
            portas = item.get("portas", [])
            processos = item.get("processos", [])
            motivos = item.get("motivos", [])

            elementos.append(
                Paragraph(
                    f"<b>{i}. [{nivel}] {ip}</b> — {qtd} conexão(ões) ativa(s)",
                    normal
                )
            )
            elementos.append(
                Paragraph(
                    f"Portas remotas: {', '.join(str(p) for p in portas) if portas else 'nenhuma identificada'}",
                    normal
                )
            )
            elementos.append(
                Paragraph(
                    f"Processos envolvidos: {', '.join(processos) if processos else 'desconhecido'}",
                    normal
                )
            )
            if motivos:
                elementos.append(
                    Paragraph(
                        "Motivos da classificação:",
                        normal
                    )
                )
                for m in motivos:
                    elementos.append(
                        Paragraph(f"&nbsp;&nbsp;• {m}", normal)
                    )
            else:
                elementos.append(
                    Paragraph("Motivos: não especificados.", normal)
                )
            elementos.append(Spacer(1, 0.25 * cm))

    else:
        elementos.append(
            Paragraph(
                "Nenhum IP suspeito detectado no momento. "
                "As conexões públicas observadas não apresentaram indícios de risco "
                "(portas sensíveis, processos desconhecidos ou volume anormal).",
                normal
            )
        )
        if todos_publicos:
            elementos.append(Spacer(1, 0.2 * cm))
            elementos.append(
                Paragraph(
                    f"IPs públicos observados (sem suspeita): {', '.join(todos_publicos[:30])}"
                    + ("..." if len(todos_publicos) > 30 else ""),
                    normal
                )
            )

    # Riscos por processo (se houver)
    riscos = diagnostico_rede.get("riscos") or []
    if riscos:
        elementos.append(Spacer(1, 0.35 * cm))
        elementos.append(
            Paragraph(
                "<b>Processos com risco de rede</b>",
                normal
            )
        )
        elementos.append(Spacer(1, 0.15 * cm))

        tabela_riscos = [["Processo", "Nível", "Conexões", "Motivos"]]
        for r in riscos[:15]:
            motivos_r = "; ".join(r.get("motivos", [])[:3])
            if len(motivos_r) > 60:
                motivos_r = motivos_r[:57] + "..."
            tabela_riscos.append([
                r.get("processo", "-"),
                r.get("nivel", "-"),
                str(r.get("quantidade", 0)),
                motivos_r or "-",
            ])

        tabela_riscos_pdf = Table(
            tabela_riscos,
            colWidths=[5.0 * cm, 1.8 * cm, 2.0 * cm, 7.7 * cm]
        )
        estilo_riscos = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.15, 0.15, 0.35)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("ALIGN", (1, 0), (2, -1), "CENTER"),
            ("BACKGROUND", (0, 1), (-1, -1), colors.Color(0.95, 0.95, 0.98)),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]
        for idx, r in enumerate(riscos[:15], start=1):
            if r.get("nivel") == "ALTO":
                estilo_riscos.append(
                    ("BACKGROUND", (0, idx), (-1, idx), colors.Color(1.0, 0.88, 0.88))
                )
            elif r.get("nivel") == "MÉDIO":
                estilo_riscos.append(
                    ("BACKGROUND", (0, idx), (-1, idx), colors.Color(1.0, 0.95, 0.85))
                )
        tabela_riscos_pdf.setStyle(TableStyle(estilo_riscos))
        elementos.append(tabela_riscos_pdf)

    elementos.append(Spacer(1, 0.5 * cm))

    # ==================================================
    # HISTÓRICO DE CONEXÕES DA SESSÃO
    # ==================================================

    elementos.append(
        Paragraph(
            "<b>HISTÓRICO DE CONEXÕES DA SESSÃO</b>",
            subtitulo
        )
    )

    if historico_conexoes:
        elementos.append(
            Paragraph(
                f"Início da sessão: {historico_conexoes.get('inicio_sessao', '-')}",
                normal
            )
        )
        elementos.append(
            Paragraph(
                f"Última coleta: {historico_conexoes.get('ultima_coleta', '-')}",
                normal
            )
        )
        elementos.append(
            Paragraph(
                f"Duração: {historico_conexoes.get('duracao', '-')}  |  "
                f"Coletas: {historico_conexoes.get('total_coletas', 0)}  |  "
                f"IPs públicos únicos: {historico_conexoes.get('total_ips_unicos', 0)}",
                normal
            )
        )
        elementos.append(Spacer(1, 0.3 * cm))

        ips_hist = historico_conexoes.get("ips", [])
        if ips_hist:
            elementos.append(
                Paragraph(
                    "<b>IPs públicos observados (mais vistos primeiro)</b>",
                    normal
                )
            )
            elementos.append(Spacer(1, 0.2 * cm))

            tabela_hist = [["IP", "Vezes", "Primeira", "Última", "Portas / Processos"]]

            for item in ips_hist[:25]:
                portas = ", ".join(str(p) for p in item.get("portas", [])[:6])
                procs = ", ".join(item.get("processos", [])[:3])
                detalhe = f"{portas} | {procs}"
                if len(detalhe) > 55:
                    detalhe = detalhe[:52] + "..."

                tabela_hist.append([
                    item.get("ip", ""),
                    str(item.get("vezes_visto", 0)),
                    item.get("primeira_vez", ""),
                    item.get("ultima_vez", ""),
                    detalhe,
                ])

            tabela_hist_pdf = Table(
                tabela_hist,
                colWidths=[3.8 * cm, 1.5 * cm, 2.0 * cm, 2.0 * cm, 5.8 * cm]
            )
            tabela_hist_pdf.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.navy),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("ALIGN", (1, 1), (3, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 2),
            ]))
            elementos.append(tabela_hist_pdf)
        else:
            elementos.append(
                Paragraph(
                    "Nenhum IP público registrado ainda nesta sessão.",
                    normal
                )
            )
    else:
        elementos.append(
            Paragraph(
                "Histórico de conexões não disponível.",
                normal
            )
        )

    elementos.append(Spacer(1, 0.5 * cm))


    # ==================================================
    # TOP PROCESSOS
    # ==================================================

    elementos.append(
        Paragraph(
            "<b>TOP PROCESSOS</b>",
            subtitulo
        )
    )


    tabela = [

        [
            "Processo",
            "CPU (%)",
            "RAM (MB)"
        ]

    ]


    for processo in processos:

        tabela.append(
            [
                processo["nome"],
                f"{processo['cpu']:.1f}",
                f"{processo['memoria']:.1f}"
            ]
        )


    tabela_pdf = Table(
        tabela,
        colWidths=[
            9 * cm,
            3 * cm,
            3 * cm
        ]
    )


    tabela_pdf.setStyle(
        TableStyle(
            [

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.navy
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),

                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, -1),
                    colors.beige
                ),

                (
                    "ALIGN",
                    (1, 1),
                    (-1, -1),
                    "CENTER"
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, 0),
                    8
                )

            ]
        )
    )


    elementos.append(
        tabela_pdf
    )


    elementos.append(
        Spacer(
            1,
            0.5 * cm
        )
    )


    documento.build(
        elementos
    )


    return nome_pdf