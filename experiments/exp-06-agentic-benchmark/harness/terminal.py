"""Detecção do ambiente de terminal em execução."""

import os
from pathlib import Path


def detect_terminal() -> str:
    """Retorna: 'wsl2' | 'git_bash' | 'powershell' | 'unix'"""
    if Path("/mnt/c/Users").exists():
        return "wsl2"
    if "MSYSTEM" in os.environ:  # MINGW64, MINGW32, MSYS
        return "git_bash"
    if os.name == "nt":
        return "powershell"
    return "unix"


def shell_args(command: str, terminal: str) -> tuple[list[str] | str, bool]:
    """Retorna (args, use_shell) para subprocess.run com o terminal detectado."""
    if terminal in ("wsl2", "unix"):
        return command, True
    if terminal == "git_bash":
        return ["bash", "-c", command], False
    # powershell / cmd
    return command, True


TERMINAL_NOTE = {
    "wsl2":       "WSL2 (Ubuntu) — bash disponível, caminho /mnt/c/...",
    "git_bash":   "Git Bash (Windows/MINGW64) — bash disponível, caminhos /c/... ou C:\\...",
    "powershell": "Windows PowerShell — use comandos Windows",
    "unix":       "Unix/Linux — bash disponível",
}
