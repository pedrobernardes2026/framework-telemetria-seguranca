import os, glob, shutil, json
def otimizar_e_auditar_firefox():
    print("[+] Iniciando auditoria e otimizacao do Firefox...")
    roaming = os.path.join(os.environ["APPDATA"], "Mozilla", "Firefox", "Profiles")
    local = os.path.join(os.environ["LOCALAPPDATA"], "Mozilla", "Firefox", "Profiles")
    prefs = ['user_pref("dom.ipc.processCount", 4);', 'user_pref("dom.ipc.processCount.webIsolated", 2);', 'user_pref("browser.tabs.unloadOnLowMemory", true);', 'user_pref("network.prefetch-next", false);', 'user_pref("network.dns.disablePrefetch", true);', 'user_pref("browser.cache.disk.capacity", 256000);', 'user_pref("privacy.trackingprotection.enabled", true);']
    for p in glob.glob(os.path.join(roaming, "*")):
        if os.path.isdir(p):
            open(os.path.join(p, "user.js"), "w", encoding="utf-8").write("\n".join(prefs))
            ext = os.path.join(p, "extensions.json")
            if os.path.exists(ext):
                try:
                    d = json.load(open(ext, encoding="utf-8"))
                    ativas = [a.get("defaultLocale", {}).get("name", a.get("id")) for a in d.get("addons", []) if a.get("active")]
                    print(f"[INFO] Extensoes ativas ({os.path.basename(p)}): {ativas}")
                except Exception: pass
    for c in glob.glob(os.path.join(local, "*", "cache2")):
        shutil.rmtree(c, ignore_errors=True)
        os.makedirs(c, exist_ok=True)
    print("[OK] Perfil do Firefox otimizado e cache limpo!")
if __name__ == "__main__":
    otimizar_e_auditar_firefox()