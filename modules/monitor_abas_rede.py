import psutil, time, threading

def auditar_firefox_e_rede(limite_ram_ff_mb=1500, limite_ram_global=80.0):
    total_mb = 0.0
    qtd_processos = 0
    conexoes_ativas = 0

    for proc in psutil.process_iter(['name', 'memory_info']):
        try:
            if proc.info['name'] and 'firefox' in proc.info['name'].lower():
                qtd_processos += 1
                total_mb += proc.info['memory_info'].rss / (1024 * 1024)
                for conn in proc.net_connections(kind='inet'):
                    if conn.status == 'ESTABLISHED':
                        conexoes_ativas += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    ram_global = psutil.virtual_memory().percent
    status = 'ESTAVEL'
    if total_mb > limite_ram_ff_mb or ram_global > limite_ram_global:
        status = 'ALERTA_RAM_ALTA'

    return {
        'status': status,
        'processos_firefox': qtd_processos,
        'ram_firefox_mb': round(total_mb, 1),
        'ram_global_pct': ram_global,
        'conexoes_firefox': conexoes_ativas
    }

def loop_monitor_abas(intervalo=10):
    print('[+] Monitor de abas e memoria do Firefox iniciado...')
    while True:
        dados = auditar_firefox_e_rede()
        if dados['processos_firefox'] > 0 and dados['status'] == 'ALERTA_RAM_ALTA':
            print(f"[ALERTA FF] RAM Firefox: {dados['ram_firefox_mb']} MB ({dados['processos_firefox']} procs) | RAM PC: {dados['ram_global_pct']}% | Conexoes: {dados['conexoes_firefox']}")
        time.sleep(intervalo)

def iniciar_monitor_abas_background(intervalo=10):
    t = threading.Thread(target=loop_monitor_abas, args=(intervalo,), daemon=True)
    t.start()
    return t

if __name__ == "__main__":
    print(auditar_firefox_e_rede())
