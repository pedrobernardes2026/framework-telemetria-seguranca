"""
Módulo de Integridade Criptográfica: Validação de Assinaturas SHA-256 de Códigos-Fonte.
Protege o ecossistema contra modificações e adulterações não homologadas.
"""

import hashlib
import os

# Lista de arquivos vitais monitorados pela cadeia de custódia
ARQUIVOS_CRITICOS = [
    "main.py",
    "modules/interface.py",
    "modules/aurera.py",
    "modules/bloqueio_ips import.py" if os.path.exists("modules/bloqueio_ips import.py") else "modules/bloqueio_ips.py",
    "modules/diagnostico_rede.py",
    "modules/processos.py",
    "modules/integridade.py"
]

# Armazena as assinaturas originais tiradas no instante do boot
_DNAS_ORIGINAIS = {}


def calcular_sha256(caminho_arquivo: str) -> str:
    """Calcula a assinatura criptográfica única (Hash SHA-256) de um arquivo."""
    if not os.path.exists(caminho_arquivo):
        return "ARQUIVO_INEXISTENTE"
    
    sha256_hash = hashlib.sha256()
    try:
        with open(caminho_arquivo, "rb") as f:
            for bloco in iter(lambda: f.read(4096), b""):
                sha256_hash.update(bloco)
        return sha256_hash.hexdigest()
    except Exception:
        return "ERRO_LEITURA"


def inicializar_assinaturas_projeto():
    """Tira a assinatura digital instantânea de todos os códigos no primeiro segundo do boot."""
    global _DNAS_ORIGINAIS
    diretorio_raiz = os.getcwd()
    
    for arquivo_relativo in ARQUIVOS_CRITICOS:
        caminho_absoluto = os.path.join(diretorio_raiz, arquivo_relativo)
        if os.path.exists(caminho_absolute := caminho_absoluto):
            sha_real = calcular_sha256(caminho_absolute)
            _DNAS_ORIGINAIS[arquivo_relativo] = sha_real
    
    print(f"[🛡️ INTEGRIDADE] Cadeia de custódia criptográfica inicializada para {len(_DNAS_ORIGINAIS)} arquivos vitais.")


def verificar_adulteracao_codigos():
    """Compara a assinatura em tempo real com a original do boot para detectar desvios."""
    global _DNAS_ORIGINAIS
    diretorio_raiz = os.getcwd()
    arquivos_violados = []
    
    for arquivo_relativo, sha_original in _DNAS_ORIGINAIS.items():
        caminho_absoluto = os.path.join(diretorio_raiz, arquivo_relativo)
        sha_atual = calcular_sha256(caminho_absoluto)
        
        if sha_atual != sha_original:
            arquivos_violados.append({
                "arquivo": arquivo_relativo,
                "esperado": sha_original,
                "detectado": sha_atual
            })
            
    return arquivos_violados
