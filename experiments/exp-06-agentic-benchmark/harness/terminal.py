"""Detecção do ambiente de terminal e shell em execução."""

import os
import platform
from pathlib import Path


def detect_terminal() -> str:
    """Detecta o ambiente real de execução do processo Python.

    Lógica:
    - os.name == 'nt'  → Python Windows nativo (PowerShell, CMD ou Git Bash)
    - os.name == 'posix' + /proc/version com 'microsoft' → WSL2
    - os.name == 'posix' sem WSL → Unix/Linux/macOS

    Retorna: 'powershell' | 'git_bash' | 'wsl2' | 'unix'
    """
    if os.name == "nt":
        # Python rodando no Windows nativo.
        # Git for Windows define MSYSTEM (ex: 'MINGW64', 'MSYS').
        # Mesmo assim, subprocess com shell=True usa cmd.exe — mais seguro que chamar bash
        # explicitamente, pois 'bash' no PATH pode rotear pelo WSL quebrado.
        if "MSYSTEM" in os.environ:
            return "git_bash"
        return "powershell"

    # os.name == 'posix' — Linux, macOS ou WSL
    try:
        proc_version = Path("/proc/version").read_text(errors="replace").lower()
        if "microsoft" in proc_version or "wsl" in proc_version:
            return "wsl2"
    except Exception:
        pass

    return "unix"


def shell_args(command: str, terminal: str) -> tuple[str, bool]:
    """Retorna (command, use_shell=True) para subprocess.run.

    Sempre usa shell=True com string — o shell nativo do SO (cmd.exe no Windows,
    /bin/sh no Unix) resolve o comando sem depender de 'bash' no PATH.
    Isso evita o problema de 'bash' rotear acidentalmente pelo WSL no Windows.
    """
    return command, True


def terminal_env_description(terminal: str) -> str:
    """Descrição detalhada do ambiente para o system prompt do LLM.

    O LLM precisa saber exatamente em qual SO e shell está para:
    - Usar a sintaxe de path correta
    - Não tentar comandos bash no Windows (ou vice-versa)
    - Não assumir que erros de build são problemas de ambiente
    """
    os_name    = platform.system()   # 'Windows', 'Linux', 'Darwin'
    os_version = platform.release()  # ex: '10', '11', '22.04'

    if terminal == "powershell":
        return (
            f"OS: Windows {os_version} (Python running natively via PowerShell/CMD)\n"
            "Shell: cmd.exe (shell=True)\n"
            "Path format: C:\\Users\\... (backslash)\n"
            "Maven: mvn.cmd — invoked as 'mvn compile', 'mvn test'\n"
            "Available commands: dir, type, copy, del — NOT bash/grep/cat\n"
            "IMPORTANT: Do NOT use Unix paths (/mnt/..., /home/...) or bash syntax"
        )
    if terminal == "git_bash":
        return (
            f"OS: Windows {os_version} (Python running inside Git Bash / MINGW64)\n"
            "Shell: cmd.exe via shell=True (commands run through Windows CMD, not bash)\n"
            "Path format: use Windows paths C:\\Users\\... for Java/Maven files\n"
            "Maven: mvn.cmd — invoked as 'mvn compile', 'mvn test'\n"
            "IMPORTANT: Do NOT use WSL paths (/mnt/...) or WSL-specific commands"
        )
    if terminal == "wsl2":
        return (
            f"OS: Windows (WSL2 — Linux subsystem, kernel: {os_version})\n"
            "Shell: /bin/sh via shell=True\n"
            "Path format: Unix-style, Windows drives at /mnt/c/Users/...\n"
            "Maven: mvn — invoked as 'mvn compile', 'mvn test'\n"
            "Available commands: ls, cat, grep, find — standard Linux"
        )
    # unix / macOS / Linux
    return (
        f"OS: {os_name} {os_version} (native Unix/Linux)\n"
        "Shell: /bin/sh via shell=True\n"
        "Path format: Unix-style /home/... or /Users/...\n"
        "Maven: mvn — invoked as 'mvn compile', 'mvn test'\n"
        "Available commands: ls, cat, grep, find — standard Unix"
    )


# Mantido para compatibilidade com imports existentes
TERMINAL_NOTE = {
    "powershell": "Windows PowerShell/CMD — use comandos Windows, path com backslash",
    "git_bash":   "Git Bash (Windows/MINGW64) — Maven via cmd.exe, não use WSL",
    "wsl2":       "WSL2 (Ubuntu/Linux no Windows) — paths /mnt/c/...",
    "unix":       "Unix/Linux/macOS — bash/sh disponível, paths Unix",
}
