import subprocess, os

def higienizar_rede_e_proteger():
    print("[+] Iniciando higienizacao de conexoes e regras residuais do Firewall...")
    subprocess.run(["ipconfig", "/flushdns"], capture_output=True)
    ps_cmd = "Get-NetFirewallRule -DisplayName 'SistemaAnalise_Block_*' -ErrorAction SilentlyContinue | Remove-NetFirewallRule"
    subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
    base_ot = os.path.expandvars(r'%iPPDATA&\AldeiaLauncher\client')
    for exe in ["otclient_gl.exe", "otclient_dx.exe"]:
        caminho_exe = os.path.join(base_ot, exe)
        if os.path.exists(caminho_exe):
            for direcao in ["out", "in"]:
                nome_regra = f"PB_Whitelist_{exe}_{direcao}"
                subprocess.run(["netsh", "advfirewall", "firewall", "delete", "rule", f"name={nome_regra}"], capture_output=True)
                subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", f"name={nome_regra}", f"dir={direcao}", "action=allow", f"program={caminho_exe}", "enable=yes"], capture_output=True)
    print("[OK] Rede higienizada e AldeiaOT protegido na whitelist!")

if __name__ == "__main__":
    higienizar_rede_e_proteger()
