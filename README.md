\# Residential and Enterprise Telemetry \& Defensive Security Framework



An advanced, high-performance Python framework for real-time hardware telemetry and active network perimeter auditing/mitigation with native Windows Defender Firewall integration. This software operates as a resident security shield designed to detect, log, and isolate unauthorized connection attempts and logical intrusions at Ring 0.



\## 🛡️ Core Engineering Highlights \& Innovations



\*   \*\*Anti-PID Shadowing Resolution:\*\* Implements multi-threaded state validation via `proc.is\_running()` to prevent zombie processes or process hijacking from blinding the security loop.

\*   \*\*In-Memory Mitigation Cache Engine:\*\* Utilizes continuous hash-set matching arrays (`IPS\_BLOQUEADOS\_CACHE`) to execute microsecond-level perimeter lookups, preventing redundancy in Windows API rules and optimizing CPU resources.

\*   \*\*Active Vector \& Socket Mapping:\*\* Audits detailed telemetric socket attributes (`.laddr.port` and `.raddr.port`) to track unauthorized cross-network scans and structural perimeter violations in real time.

\*   \*\*Live Neon Forensic Console:\*\* Direct, thread-safe asynchronous integration between the background orchestration loop (`main.py`) and the CustomTkinter GUI panel, rendering instant mitigation logs on the display without UI lock.



\---



\## 🗂️ Architectural Directory Structure



Below is the complete structural blueprint mapping the exact files and directories operating within the `ProjetoPythonbackupatt` ecosystem:





\# Residential and Enterprise Telemetry \& Defensive Security Framework



An advanced Python-based framework for real-time hardware telemetry and network perimeter auditing/mitigation, featuring integration with Windows Defender Firewall. ## 🗂️ Updated Directory Structure



The complete architectural tree for the `ProjetoPythonbackupatt` project, including the `seguranca.py` module, properly positioned:



```text

ProjetoPythonbackupatt/

│

├── ambiente\_estavel/          # Isolated virtual environment

│   ├── Include/

│   ├── Lib/site-packages/     # Dependencies (CustomTkinter, Psutil, etc.)

│   └── Scripts/               # Activation scripts

│

├── modules/                   # Analysis and security subsystems

│   ├── \_\_pycache\_\_/

│   ├── alertas.py

│   ├── aurera.py

│   ├── auditoria\_global.py

│   ├── bloqueio\_ips.py

│   ├── diagnostico\_rede.py

│   ├── historico.py

│   ├── historico\_conexoes.py

│   ├── integridade.py

│   ├── interface.py

│   ├── monitor.py

│   ├── monitor\_rede.py

│   ├── notificacao\_email.py

│   ├── process\_watchdog.py

│   ├── processos.py

│   ├── rede.py

│   ├── relatorio.py

│   ├── saude.py

│   ├── seguranca.py           # Integrity analyzer and security inspector

│   └── system\_services.py

│

├── Logs/

│   └── monitoramento.txt

│

├── .gitignore

├── icone\_guardiao.ico

├── main.py

└── README.md

```



\## 🚀 Quick Start \& Deployment Guide



\### Prerequisites

\*   \*\*Operating System:\*\* Windows 10 or Windows 11 (Required for Advanced Windows Defender API bindings).

\*   \*\*Interpreter:\*\* Python 3.10 or higher.

\*   \*\*Privileges:\*\* Prompt must be launched with \*\*Elevated Administrator Permissions\*\*.



\### Execution via Command Line

Open your \*\*CMD as Administrator\*\* and execute the sequential lines below:

```cmd

cd "C:\\Users\\moreno\\Desktop\\ProjetoPythonbackupatt"

.\\ambiente\_estavel\\Scripts\\activate

python main.py

```



Developed with honors by \*\*Moreno - Pedro Bernardes\*\* © 2026.



