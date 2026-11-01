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





```text

ProjetoPythonbackupatt/

│

├── ambiente\_estavel/          # Isolated virtual environment (Python Executable \& Dependencies)

│   ├── Include/

│   ├── Lib/site-packages/     # CustomTkinter, Psutil, ReportLab, etc.

│   └── Scripts/               # Activation scripts (activate.bat)

│

├── modules/                   # Core Analytical \& Cybersecurity Subsystems

│   ├── \_\_pycache\_\_/           # Compiled bytecode cache files

│   ├── alertas.py             # Event verification and warning module

│   ├── aurera.py              # Application module analytics

│   ├── auditoria\_global.py    # System-wide compliance and event logging

│   ├── bloqueio\_ips.py        # Active network firewall block policy execution

│   ├── diagnostico\_rede.py    # Remote socket inspector and packet monitor

│   ├── historico.py           # In-memory circular buffer data persistent engine

│   ├── historico\_conexoes.py  # Network route persistence and history database

│   ├── integridade.py         # Module SHA-256 cryptographic signature validator

│   ├── interface.py           # CustomTkinter UI \& Live Neon Terminal implementation (368 lines)

│   ├── monitor.py             # CPU, RAM, and Disk hardware performance telemetrist

│   ├── monitor\_rede.py        # Sub-interface throughput analyst

│   ├── notificacao\_email.py   # Asynchronous SMTP alert communication dispatch

│   ├── process\_watchdog.py    # Core Kernel process scanner and father-PID watchdog

│   ├── processos.py           # Memory concurrent top process ranker

│   ├── rede.py                # Global socket network mapper

│   ├── relatorio.py           # ReportLab dynamic enterprise PDF compilation engine

│   ├── saude.py               # Host stability and health coefficient calculator

│   └── system\_services.py     # Process purger and automation services

│

├── Logs/                      # Local audit trail folder

│   └── monitoramento.txt      # Text logs recording live mitigated network vectors

│

├── .gitignore                 # Exclusion configuration file (Build, Dist, and EXE tracking shield)

├── icone\_guardiao.ico         # Custom high-resolution brand asset identity visual icon

├── main.py                    # Core Framework Orchestrator and Asynchronous Boot Loader

└── README.md                  # Project structural documentation file

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



