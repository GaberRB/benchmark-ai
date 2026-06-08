"""
snapshot.py — Registra o estado da telemetria antes e após uma sessão de benchmark.

Uso:
  python metrics/snapshot.py --pre  --language java
  python metrics/snapshot.py --post --language java --session-id <UUID>
"""

import argparse
import json
import os
import glob
from datetime import datetime, timezone

TELEMETRY_DIR = os.path.join(os.path.expanduser("~"), ".claude", "telemetry")
SESSIONS_DIR  = os.path.join(os.path.expanduser("~"), ".claude", "sessions")
REPORTS_DIR   = os.path.join(os.path.dirname(__file__), "reports")


def get_telemetry_snapshot():
    files = glob.glob(os.path.join(TELEMETRY_DIR, "*.json"))
    return {
        os.path.basename(f): {
            "size_bytes": os.path.getsize(f),
            "mtime": os.path.getmtime(f),
        }
        for f in files
    }


def get_active_sessions():
    sessions = {}
    for f in glob.glob(os.path.join(SESSIONS_DIR, "*.json")):
        try:
            with open(f, encoding="utf-8") as fh:
                data = json.load(fh)
            sessions[data.get("sessionId", os.path.basename(f))] = {
                "cwd": data.get("cwd"),
                "startedAt": data.get("startedAt"),
                "status": data.get("status"),
            }
        except Exception:
            pass
    return sessions


def save_snapshot(language: str, phase: str, session_id: str | None = None):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"snapshot_{language}_{phase}_{ts}.json"
    path = os.path.join(REPORTS_DIR, filename)

    payload = {
        "phase": phase,
        "language": language,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "telemetry_files": get_telemetry_snapshot(),
        "active_sessions": get_active_sessions(),
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"[snapshot] Salvo em: {path}")
    if session_id:
        print(f"[snapshot] Session ID registrado: {session_id}")
    else:
        print("[snapshot] AVISO: nenhum --session-id fornecido no snapshot --post")
        print("[snapshot] Execute 'python metrics/collector.py' imediatamente após a sessão")

    return path


def main():
    parser = argparse.ArgumentParser(description="Snapshot de telemetria para benchmark")
    parser.add_argument("--pre",  action="store_true", help="Snapshot pré-sessão")
    parser.add_argument("--post", action="store_true", help="Snapshot pós-sessão")
    parser.add_argument("--language",   required=True,
                        choices=["java", "kotlin", "java-gradle", "kotlin-gradle", "arch-hexagonal", "arch-clean",
                                 "arch-cqrs", "arch-mvc", "arch-vertical-slice"])
    parser.add_argument("--session-id", default=None,  help="UUID da sessão Claude Code")
    args = parser.parse_args()

    if args.pre:
        save_snapshot(args.language, "pre", args.session_id)
    elif args.post:
        save_snapshot(args.language, "post", args.session_id)
    else:
        parser.error("Informe --pre ou --post")


if __name__ == "__main__":
    main()
