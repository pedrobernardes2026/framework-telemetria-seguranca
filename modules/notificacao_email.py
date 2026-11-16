"""
Módulo de notificação por e-mail.
Credenciais via variáveis de ambiente (.env).
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
SENHA_REMETENTE = os.getenv("SENHA_APP")
EMAIL_DESTINATARIO = os.getenv("EMAIL_DESTINATARIO", EMAIL_REMETENTE)


def enviar_email(assunto: str, corpo_texto: str) -> bool:
    """Envia e-mail via SMTP com TLS. Retorna True em caso de sucesso."""
    if not all([EMAIL_REMETENTE, SENHA_REMETENTE, EMAIL_DESTINATARIO]):
        print("[EMAIL] Variáveis de ambiente não configuradas.")
        return False

    try:
        mensagem = MIMEMultipart()
        mensagem["From"] = EMAIL_REMETENTE
        mensagem["To"] = EMAIL_DESTINATARIO
        mensagem["Subject"] = assunto
        mensagem.attach(MIMEText(corpo_texto, "plain", "utf-8"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as servidor:
            servidor.starttls()
            servidor.login(EMAIL_REMETENTE, SENHA_REMETENTE)
            servidor.sendmail(EMAIL_REMETENTE, EMAIL_DESTINATARIO, mensagem.as_string())

        print(f"[EMAIL] Enviado com sucesso para {EMAIL_DESTINATARIO}")
        return True
    except Exception as e:
        print(f"[EMAIL] Falha no envio: {e}")
        return False


def disparar_alerta_integridade(arquivo: str, hash_esperado: str, hash_detectado: str):
    """Alerta de violação de integridade de arquivo."""
    horario = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    assunto = "[ALERTA] Violação de Integridade Detectada"

    corpo = f"""
ALERTA DE INTEGRIDADE DE CÓDIGO
================================
Data/Hora: {horario}

Arquivo alterado: {arquivo}
Hash esperado (boot): {hash_esperado}
Hash atual:           {hash_detectado}

O arquivo foi modificado após a inicialização do sistema.
Recomenda-se investigar a origem da alteração.
"""
    enviar_email(assunto, corpo.strip())


def disparar_alerta_ips_bloqueados(ips_bloqueados: list):
    """Envia e-mail quando IPs suspeitos são bloqueados."""
    if not ips_bloqueados:
        return

    horario = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    assunto = f"[ALERTA] {len(ips_bloqueados)} IP(s) suspeito(s) bloqueado(s)"

    lista_ips = "\n".join(f"  - {ip}" for ip in ips_bloqueados)

    corpo = f"""
ALERTA DE BLOQUEIO DE IPs
=========================
Data/Hora: {horario}

Os seguintes IPs foram classificados como suspeitos e bloqueados pelo Firewall:

{lista_ips}

Ação realizada: Bloqueio de entrada e saída via Firewall do Windows.
"""
    enviar_email(assunto, corpo.strip())


def disparar_alerta_saude_critica(mensagens: list, nota: int):
    """Envia e-mail quando a saúde do sistema está crítica."""
    horario = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    assunto = f"[ALERTA] Saúde do Sistema Crítica (Nota: {nota}/100)"

    lista = "\n".join(f"  - {m}" for m in mensagens) if mensagens else "  - Sem detalhes"

    corpo = f"""
ALERTA DE SAÚDE DO SISTEMA
==========================
Data/Hora: {horario}
Nota atual: {nota}/100

Problemas detectados:
{lista}

Recomenda-se verificar o uso de CPU, memória e disco.
"""
    enviar_email(assunto, corpo.strip())