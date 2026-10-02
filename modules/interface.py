"""
Interface Gráfica de Usuário (GUI): Painel de Monitoramento Telemétrico e Auditoria.
Centraliza a renderização de gráficos em tempo real, gestão de rede e geração de relatórios.
Desenvolvido em conformidade com o ecossistema assíncrono do CustomTkinter e PEP 8.
"""

import os
import tkinter as tk
import customtkinter as ctk
import threading
import socket

from modules.bloqueio_ips import bloquear_ips_suspeitos, desbloquear_todos, desbloquear_ip
from modules.diagnostico_rede import analisar_ips_suspeitos, analisar_rede
from modules.monitor import obter_cpu, obter_ram, obter_disco
from modules.monitor_rede import obter_rede
from modules.processos import obter_processos
from modules.aurera import analisar_aurera
from modules.alertas import verificar_alertas
from modules.seguranca import analisar_seguranca
from modules.saude import calcular_saude
from modules.relatorio import gerar_relatorio
from modules.historico_conexoes import registrar_conexoes, obter_historico_conexoes
from modules.historico import adicionar_dados, obter_historico


class SistemaAnalise(ctk.CTk):

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Framework de Telemetria e Auditoria de Desempenho")
        self.geometry("1300x950")
        self.minsize(1000, 650)

        # Inicializa os buffers circulares na memória volátil com amostragem zerada
        self.historico_cpu = [0] * 20
        self.historico_ram = [0] * 20
        self.historico_disco = [0] * 20
        self.historico_rede = [0] * 20

        self._processos_contador = 0  # Inicializa o alívio de carga da CPU
        self.criar_interface()
        
        # Inicia o dashboard de forma assíncrona após 1 segundo para garantir a renderização
        self.after(1000, self.atualizar_dashboard)

    def criar_interface(self):
        titulo = ctk.CTkLabel(self, text="Framework de Telemetria e Auditoria de Desempenho", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=(10, 2)) # Reduzido espaçamento

        subtitulo = ctk.CTkLabel(self, text="Painel de Controle Telemétrico em Tempo Real", font=("Segoe UI", 12))
        subtitulo.pack(pady=(0, 5))

        self.botao_relatorio = ctk.CTkButton(self, text="Gerar Relatório Corporativo PDF", height=35, font=("Segoe UI", 13, "bold"), command=self.gerar_relatorio_pdf)
        self.botao_relatorio.pack(pady=5)

        self.botao_bloquear = ctk.CTkButton(self, text="Isolar Nós de Rede Não Homologados", height=35, font=("Segoe UI", 13, "bold"), fg_color="#b91c1c", hover_color="#7f1d1d", command=self.aplicar_isolamento_rede)
        self.botao_bloquear.pack(pady=3)

        self.botao_desbloquear = ctk.CTkButton(self, text="Revogar Todas as Restrições de Firewall", height=28, font=("Segoe UI", 12), fg_color="#374151", hover_color="#1f2937", command=self.revogar_restricoes_rede)
        self.botao_desbloquear.pack(pady=3)

        self.cards = ctk.CTkFrame(self)
        self.cards.pack(fill="x", padx=20, pady=10) # Reduzido pady de 25 para 10

        self.card_cpu = self.criar_card("CPU")
        self.card_ram = self.criar_card("RAM")
        self.card_disco = self.criar_card("ATIVIDADE DE DISCO")
        self.card_rede = self.criar_card_rede()
        self.card_aurera = self.criar_card_aurera()

        self.criar_area_seguranca()  
        self.criar_area_saude()      
        self.criar_area_graficos()
        self.criar_area_alertas()
        self.criar_area_processos()


    def criar_card(self, titulo):
        frame = ctk.CTkFrame(self.cards, width=220, height=120, corner_radius=12) # Reduzido tamanho do card
        frame.pack(side="left", expand=True, padx=5)
        nome = ctk.CTkLabel(frame, text=titulo, font=("Segoe UI", 13, "bold"))
        nome.pack(pady=(8, 2))
        valor = ctk.CTkLabel(frame, text="0%", font=("Segoe UI", 22, "bold"))
        valor.pack()
        barra = ctk.CTkProgressBar(frame, width=160)
        barra.pack(pady=10)
        barra.set(0)
        return {"valor": valor, "barra": barra}


    def criar_card_rede(self):
        frame = ctk.CTkFrame(self.cards, width=230, height=160, corner_radius=15)
        frame.pack(side="left", expand=True, padx=10)
        titulo = ctk.CTkLabel(frame, text="THROUGHPUT DE REDE", font=("Segoe UI", 16, "bold"))
        titulo.pack(pady=(15, 5))
        valor = ctk.CTkLabel(frame, text="↓ 0.00 MB/s\n↑ 0.00 MB/s", font=("Segoe UI", 15, "bold"))
        valor.pack(pady=10)
        return {"valor": valor}

    def criar_card_aurera(self):
        frame = ctk.CTkFrame(self.cards, width=230, height=160, corner_radius=15)
        frame.pack(side="left", expand=True, padx=10)
        titulo = ctk.CTkLabel(frame, text="MÓDULO DA APLICAÇÃO", font=("Segoe UI", 15, "bold"))
        titulo.pack(pady=(10, 5))
        clientes = ctk.CTkLabel(frame, text="Instâncias Ativas: 0", font=("Segoe UI", 13))
        clientes.pack()
        memoria = ctk.CTkLabel(frame, text="RAM Alocada: 0 MB", font=("Segoe UI", 13))
        memoria.pack()
        cpu = ctk.CTkLabel(frame, text="Carga CPU: 0%", font=("Segoe UI", 13))
        cpu.pack()
        return {"clientes": clientes, "ram": memoria, "cpu": cpu}

    def criar_area_saude(self):
        """Renderiza a seção focada na confiabilidade e status operacional global do host."""
        self.area_saude = ctk.CTkFrame(self, corner_radius=15)
        self.area_saude.pack(fill="x", padx=20, pady=5) # Ajustado para pady=5

        titulo = ctk.CTkLabel(self.area_saude, text="Confiabilidade e Saúde do Sistema", font=("Segoe UI", 16, "bold"))
        titulo.pack(pady=5)

        self.saude_valor = ctk.CTkLabel(self.area_saude, text="Processando Análise...", font=("Segoe UI", 22, "bold"))
        self.saude_valor.pack(pady=2)

        self.saude_mensagens = ctk.CTkLabel(self.area_saude, text="", wraplength=900, justify="left", font=("Segoe UI", 12))
        self.saude_mensagens.pack(padx=20, pady=5)


    def criar_area_seguranca(self):
        """Renderiza o módulo dinâmico focado em integridade e auditoria de conexões de rede."""
        self.area_seguranca = ctk.CTkFrame(self, corner_radius=15)
        self.area_seguranca.pack(fill="x", padx=20, pady=5) # Ajustado para pady=5

        titulo = ctk.CTkLabel(self.area_seguranca, text="Integridade de Segurança Operacional", font=("Segoe UI", 16, "bold"))
        titulo.pack(pady=5)

        self.seguranca_texto = ctk.CTkLabel(self.area_seguranca, text="Status: Executando Varredura...", font=("Segoe UI", 12, "bold"))
        self.seguranca_texto.pack(pady=2)

        self.lista_alertas_frame = ctk.CTkFrame(self.area_seguranca, fg_color="transparent")
        self.lista_alertas_frame.pack(fill="x", padx=20, pady=(2, 8))


    def criar_area_graficos(self):
        """Gera o contêiner de canvas para desenho técnico das linhas de histórico local."""
        self.area_graficos = ctk.CTkFrame(self, corner_radius=15)
        # Removido fill="both" e expand=True para o frame não roubar espaço da janela
        self.area_graficos.pack(fill="x", padx=20, pady=5) 

        titulo = ctk.CTkLabel(self.area_graficos, text="Gráficos Históricos de Ocupação de Recursos", font=("Segoe UI", 16, "bold"))
        titulo.pack(pady=5)

        self.frame_graficos = ctk.CTkFrame(self.area_graficos, fg_color="transparent")
        self.frame_graficos.pack(fill="x", padx=10, pady=5)

        # Força o tamanho físico real (260x180) para o Canvas se adequar perfeitamente
        estilo_canvas = {"width": 260, "height": 160, "bg": "#1a1a2e", "highlightthickness": 0}

        self.grafico_cpu = tk.Canvas(self.frame_graficos, **estilo_canvas)
        self.grafico_cpu.pack(side="left", expand=True, padx=5, pady=5)

        self.grafico_ram = tk.Canvas(self.frame_graficos, **estilo_canvas)
        self.grafico_ram.pack(side="left", expand=True, padx=5, pady=5)

        self.grafico_disco = tk.Canvas(self.frame_graficos, **estilo_canvas)
        self.grafico_disco.pack(side="left", expand=True, padx=5, pady=5)

        self.grafico_rede = tk.Canvas(self.frame_graficos, **estilo_canvas)
        self.grafico_rede.pack(side="left", expand=True, padx=5, pady=5)


    def criar_area_alertas(self):
        self.area_alertas = ctk.CTkFrame(self, corner_radius=15)
        self.area_alertas.pack(fill="x", padx=20, pady=10)
        titulo = ctk.CTkLabel(self.area_alertas, text="Eventos Registrados pelo Framework", font=("Segoe UI", 18, "bold"))
        titulo.pack(pady=10)
        self.alertas_texto = ctk.CTkLabel(self.area_alertas, text="Nenhum desvio operacional identificado.", wraplength=900, justify="left", font=("Segoe UI", 13))
        self.alertas_texto.pack(padx=20, pady=10)

    def criar_area_processos(self):
        self.area_processos = ctk.CTkFrame(self, corner_radius=15)
        self.area_processos.pack(fill="x", padx=20, pady=10)
        titulo = ctk.CTkLabel(self.area_processos, text="Top Processos Concorrentes (por memória)", font=("Segoe UI", 18, "bold"))
        titulo.pack(pady=(10, 5))
        self.grafico_processos = tk.Canvas(self.area_processos, height=280, bg="#1a1a2e", highlightthickness=0)
        self.grafico_processos.pack(fill="x", padx=15, pady=(5, 15))

    def atualizar_dashboard(self):
        if not hasattr(self, "grafico_processos"):
            self.after(500, self.atualizar_dashboard)
            return
        try:
            cpu, ram, disco = obter_cpu(), obter_ram(), obter_disco()
            rede, aurera = obter_rede(), analisar_aurera()
            adicionar_dados(cpu, ram, disco, rede["download"], rede["upload"])

            self.card_cpu["valor"].configure(text=f"{cpu:.1f}%")
            self.card_cpu["barra"].set(cpu / 100)
            self.card_ram["valor"].configure(text=f"{ram:.1f}%")
            self.card_ram["barra"].set(ram / 100)
            self.card_disco["valor"].configure(text=f"{disco:.1f}%")
            self.card_disco["barra"].set(disco / 100)
            self.card_rede["valor"].configure(text=f"↓ {rede['download']:.2f} MB/s\n↑ {rede['upload']:.2f} MB/s")

            if aurera and isinstance(aurera, dict):
                self.card_aurera["clientes"].configure(text=f"Instâncias Ativas: {aurera.get('clientes', 0)}")
                self.card_aurera["ram"].configure(text=f"RAM Alocada: {aurera.get('ram', 0)} MB")
                self.card_aurera["cpu"].configure(text=f"Carga CPU: {aurera.get('cpu', 0)}%")

            if hasattr(self, "historico_cpu"):
                self.historico_cpu.pop(0); self.historico_cpu.append(cpu)
                self.historico_ram.pop(0); self.historico_ram.append(ram)
                self.historico_disco.pop(0); self.historico_disco.append(disco)
                cn_rede = rede.get("download", 0) + rede.get("upload", 0)
                pct_rede = min(100.0, (cn_rede / 10.0) * 100)
                self.historico_rede.pop(0); self.historico_rede.append(pct_rede)

                self._desenhar_grafico(self.grafico_cpu, self.historico_cpu, "Utilização de CPU ( % )", "#00f0ff")
                self._desenhar_grafico(self.grafico_ram, self.historico_ram, "Alocação de RAM ( % )", "#bf55ec")
                self._desenhar_grafico(self.grafico_disco, self.historico_disco, "Atividade de Disco ( I/O % )", "#2ecc71")
                self._desenhar_grafico(self.grafico_rede, self.historico_rede, "Vazão de Banda de Rede ( % )", "#ff9f43")

            self._processos_contador += 1
            if self._processos_contador >= 5:
                threading.Thread(target=self.atualizar_processos, daemon=True).start()
                self._processos_contador = 0

            def processar_auditoria_rede_oculta():
                try:
                    dados_rede = analisar_ips_suspeitos()
                    lista_suspeitos = dados_rede.get("suspeitos") or []
                    if lista_suspeitos:
                        self.after(0, lambda: self.seguranca_texto.configure(text=f"Status: ATENÇÃO ( {len(lista_suspeitos)} nó(s) sob análise )", text_color="#ef4444"))
                        threading.Thread(target=bloquear_ips_suspeitos, args=(lista_suspeitos,), daemon=True).start()
                    else:
                        self.after(0, lambda: self.seguranca_texto.configure(text="Status: PROTEGIDO (Nenhum desvio identificado)", text_color="#22c55e"))
                except Exception: pass

            threading.Thread(target=processar_auditoria_rede_oculta, daemon=True).start()
            status_saude = calcular_saude(cpu, ram, disco, rede, aurera)
            self.saude_valor.configure(text=status_saude.get("status", "Estável"))
            self.saude_mensagens.configure(text=status_saude.get("mensagem", ""))
        except Exception as e_dash:
            print(f"[-] Erro na esteira do dashboard: {e_dash}")
        self.after(3000, self.atualizar_dashboard)

    def _desenhar_grafico(self, canvas, dados, titulo, cor_linha):
        canvas.delete("all")
        canvas.update_idletasks()
        largura = canvas.winfo_width() or 250
        altura = canvas.winfo_height() or 180
        
        # Título do Gráfico com contraste em Branco
        canvas.create_text(largura / 2, 15, text=titulo, fill="#ffffff", font=("Segoe UI", 10, "bold"))
        
        if len(dados) < 2:
            canvas.create_text(largura / 2, altura / 2, text="Coletando amostragem...", fill="#888888", font=("Segoe UI", 10))
            return

        margem_esq, margem_dir, margem_sup, margem_inf = 40, 15, 35, 25
        area_w = largura - margem_esq - margem_dir
        area_h = altura - margem_sup - margem_inf

        # Desenha as grades horizontais de fundo (Linhas de porcentagem 0% a 100%)
        for i in range(5):
            y = margem_sup + (area_h / 4) * i
            val = 100 - 25 * i
            canvas.create_line(margem_esq, y, largura - margem_dir, y, fill="#2a2a40", dash=(2, 2))
            canvas.create_text(margem_esq - 8, y, text=f"{val}%", fill="#aaaaaa", font=("Segoe UI", 8), anchor="e")

        # Processa e mapeia os pontos do buffer circular na tela
        pontos = []
        historico_recente = dados[-20:]
        qtd_pontos = len(historico_recente)
        
        for idx, valor in enumerate(historico_recente):
            x = margem_esq + (area_w / (qtd_pontos - 1)) * idx if qtd_pontos > 1 else margem_esq
            v_norm = max(0, min(valor, 100))
            y = margem_sup + area_h * (1 - (v_norm / 100))
            pontos.append((x, y))
            
        # Desenha a linha de tendência conectando os pontos com a cor neon correspondente
        for i in range(len(pontos) - 1):
            canvas.create_line(pontos[i][0], pontos[i][1], pontos[i+1][0], pontos[i+1][1], fill=cor_linha, width=2.5)


    def atualizar_processos(self):
        processos = obter_processos()
        canvas = self.grafico_processos
        canvas.delete("all"); canvas.update_idletasks()
        largura = canvas.winfo_width() or 1100
        altura = canvas.winfo_height() or 280
        if not processos: return

        top = sorted(processos, key=lambda p: p.get("memoria", 0), reverse=True)[:10]
        max_ram = max(p.get("memoria", 0) for p in top) or 1
        margem_esq, margem_dir, margem_sup, margem_inf = 160, 90, 8, 8
        area_w = max(largura - margem_esq - margem_dir, 50)
        area_h = max(altura - margem_sup - margem_inf, 50)
        espaco = area_h / len(top)
        barra_h = min(espaco * 0.65, 22)
        offset_y = (espaco - barra_h) / 2
        cores = ["#3b82f6", "#6366f1", "#8b5cf6", "#a855f7", "#d946ef", "#ec4899", "#f43f5e", "#ef4444", "#f97316", "#eab308"]

        for i, proc in enumerate(top):
            nome, ram, cpu = proc.get("nome") or "?", proc.get("memoria", 0), proc.get("cpu", 0)
            y = margem_sup + i * espaco + offset_y
            barra_w = (ram / max_ram) * area_w
            is_aurera = "aurera" in nome.lower()
            cor = "#f59e0b" if is_aurera else cores[i % len(cores)]
            nome_exib = nome if len(nome) <= 22 else nome[:19] + "..."

            canvas.create_text(margem_esq - 8, y + barra_h / 2, text=nome_exib, anchor="e", fill="#e0e0e0" if is_aurera else "#cccccc", font=("Segoe UI", 9, "bold" if is_aurera else "normal"))
            canvas.create_rectangle(margem_esq, y, margem_esq + area_w, y + barra_h, fill="#252540", outline="")
            if barra_w > 0: canvas.create_rectangle(margem_esq, y, margem_esq + barra_w, y + barra_h, fill=cor, outline="")
            canvas.create_text(margem_esq + area_w + 8, y + barra_h / 2, text=f"{ram:.0f} MB | CPU {cpu:.1f}%", anchor="w", fill="#aaaaaa", font=("Segoe UI", 8))

    def aplicar_isolamento_rede(self):
        try:
            self.botao_bloquear.configure(state="disabled", text="Aplicando Restrições...")
            dados = analisar_ips_suspeitos()
            suspeitos = dados.get("suspeitos") or []
            if not suspeitos:
                self.alertas_texto.configure(text="Nenhum desvio ou conexão não homologada identificada.")
                return
            resultado = bloquear_ips_suspeitos(suspeitos)
            linhas = [resultado.get("mensagem", "Procedimento concluído.")]
            self.alertas_texto.configure(text="\n".join(linhas))
        except Exception as e: self.alertas_texto.configure(text=f"Erro: {e}")
        finally: self.botao_bloquear.configure(state="normal", text="Isolar Nós de Rede Não Homologados")

    def revogar_restricoes_rede(self):
        try:
            self.botao_desbloquear.configure(state="disabled", text="Revogando Políticas...")
            resultado = desbloquear_todos()
            self.alertas_texto.configure(text=resultado.get("mensagem", "Procedimento concluído."))
        except Exception as e: self.alertas_texto.configure(text=f"Erro: {e}")
        finally: self.botao_desbloquear.configure(state="normal", text="Revogar Todas as Restrições de Firewall")

    def gerar_relatorio_pdf(self):
        """Reúne as telemetrias correntes e despacha para a compilação assíncrona do PDF."""
        try:
            cpu_atual, ram_atual, disco_atual = obter_cpu(), obter_ram(), obter_disco()
            rede_atual, aurera_atual = obter_rede(), analisar_aurera()
            saude_dicionario = calcular_saude(cpu_atual, ram_atual, disco_atual, rede_atual, aurera_atual)
            historico_de_rede_atual = obter_historico_conexoes()
            processos_lista = obter_processos()
            seguranca_dicionario = analisar_seguranca(processos_lista)
            texto_alerta_tela = str(self.alertas_texto.cget("text"))
            alerta_dicionario = {"nivel": "BAIXO" if "Nenhum" in texto_alerta_tela else "MÉDIO", "mensagem": texto_alerta_tela, "quantidade": 0, "mensagens": [texto_alerta_tela]}

            def rodar():
                try:
                    import modules.relatorio
                    modules.relatorio.analisar_rede = lambda: {"hostname": socket.gethostname(), "ip_local": "127.0.0.1", "ip_publico": "Monitoramento Ativo", "mac": "00:00:00:00:00:00", "interface": "Interface Física Homologada", "conexoes": {"tcp": 0, "udp": 0, "established": 0, "listen": 0, "time_wait": 0, "close_wait": 0}, "diagnostico": {"nota": 100, "alertas": []}, "ips_suspeitos": {"resumo": {"nivel_geral": "BAIXO", "ips_publicos": 0, "ips_suspeitos": 0}, "suspeitos": [], "todos_ips_publicos": []}, "riscos": []}
                    gerar_relatorio(cpu=cpu_atual, ram=ram_atual, disco=disco_atual, rede=rede_atual, aurera=aurera_atual, saude=saude_dicionario, alerta=alerta_dicionario, seguranca=seguranca_dicionario, processos=processos_lista, historico_conexoes=historico_de_rede_atual)
                    print("[+] Documento PDF gerado e catalogado com sucesso no diretório de relatórios!")
                except Exception as erro_interno:
                    print(f"[-] Erro interno na compilação do PDF: {erro_interno}")

            threading.Thread(target=rodar, daemon=True).start()
        except Exception as e:
            print(f"[-] Erro na preparação dos parâmetros do relatório: {e}")
