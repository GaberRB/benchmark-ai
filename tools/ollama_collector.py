"""
ollama_collector.py — Coleta de métricas para sessões Aider + Ollama (Experimento 3)

Uso:
  python tools/ollama_collector.py --start   --model deepseek-coder-v2:16b --arch mvc
  python tools/ollama_collector.py --collect --model deepseek-coder-v2:16b --arch mvc --impl-dir <path>
  python tools/ollama_collector.py --hardware   # apenas coleta especificações da máquina
"""

import argparse
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent
RESULTS_DIR = BASE_DIR / "experiments" / "exp-03-ollama-local-models" / "results"
STATE_FILE  = BASE_DIR / "tools" / ".ollama_session_state.json"

MODEL_SIZES = {
    "deepseek-coder-v2:16b": 9.1,
    "qwen2.5-coder:7b":      4.7,
    "codellama:13b":          7.4,
    "llama3.1:8b":            4.7,
}


# ── Hardware detection ────────────────────────────────────────────────────────

def get_hardware_info() -> dict:
    hw = {
        "os":        platform.system() + " " + platform.release(),
        "cpu_model": _get_cpu_name(),
        "cpu_cores": os.cpu_count(),
        "ram_total_gb": _get_ram_total_gb(),
        "gpu_model": None,
        "vram_total_gb": None,
        "inference_device": "cpu",
    }

    gpu = _get_gpu_info()
    if gpu:
        hw["gpu_model"]      = gpu.get("name")
        hw["vram_total_gb"]  = gpu.get("vram_gb")
        hw["inference_device"] = "gpu"

    return hw


def _get_cpu_name() -> str:
    try:
        if platform.system() == "Windows":
            out = subprocess.check_output(
                ["wmic", "cpu", "get", "Name", "/value"], text=True, stderr=subprocess.DEVNULL
            )
            for line in out.splitlines():
                if line.startswith("Name="):
                    return line.split("=", 1)[1].strip()
        elif platform.system() == "Darwin":
            return subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"], text=True
            ).strip()
        else:
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return platform.processor() or "unknown"


def _get_ram_total_gb() -> float:
    try:
        import psutil
        return round(psutil.virtual_memory().total / (1024**3), 1)
    except ImportError:
        pass
    try:
        if platform.system() == "Windows":
            out = subprocess.check_output(
                ["wmic", "computersystem", "get", "TotalPhysicalMemory", "/value"],
                text=True, stderr=subprocess.DEVNULL
            )
            for line in out.splitlines():
                if line.startswith("TotalPhysicalMemory="):
                    return round(int(line.split("=", 1)[1].strip()) / (1024**3), 1)
    except Exception:
        pass
    return 0.0


def _get_gpu_info() -> dict | None:
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.total",
             "--format=csv,noheader,nounits"],
            text=True, stderr=subprocess.DEVNULL
        )
        parts = out.strip().split(",")
        if len(parts) >= 2:
            return {
                "name":    parts[0].strip(),
                "vram_gb": round(int(parts[1].strip()) / 1024, 1),
            }
    except Exception:
        pass
    # AMD / Intel via wmic (Windows)
    try:
        out = subprocess.check_output(
            ["wmic", "path", "win32_VideoController", "get",
             "Name,AdapterRAM", "/value"],
            text=True, stderr=subprocess.DEVNULL
        )
        name, vram = None, None
        for line in out.splitlines():
            if line.startswith("Name=") and line.split("=", 1)[1].strip():
                name = line.split("=", 1)[1].strip()
            if line.startswith("AdapterRAM="):
                try:
                    vram = round(int(line.split("=", 1)[1].strip()) / (1024**3), 1)
                except ValueError:
                    pass
        if name:
            return {"name": name, "vram_gb": vram}
    except Exception:
        pass
    return None


def _get_ram_usage_gb() -> float:
    try:
        import psutil
        return round(psutil.virtual_memory().used / (1024**3), 1)
    except ImportError:
        return 0.0


def _get_ollama_model_size(model: str) -> float:
    known = MODEL_SIZES.get(model)
    if known:
        return known
    try:
        out = subprocess.check_output(
            ["ollama", "show", model, "--modelinfo"],
            text=True, stderr=subprocess.DEVNULL
        )
        for line in out.splitlines():
            if "size" in line.lower():
                parts = line.split()
                for p in parts:
                    try:
                        return round(float(p) / (1024**3), 1)
                    except ValueError:
                        pass
    except Exception:
        pass
    return 0.0


# ── Session state helpers ─────────────────────────────────────────────────────

def save_state(data: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(data, indent=2))


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_hardware():
    hw = get_hardware_info()
    print(json.dumps(hw, indent=2, ensure_ascii=False))


def cmd_start(model: str, arch: str):
    hw = get_hardware_info()
    state = {
        "model":          model,
        "arch":           arch,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "ram_start_gb":   _get_ram_usage_gb(),
        "hardware":       hw,
    }
    save_state(state)
    print(f"[ollama_collector] Sessão iniciada — {model} / {arch}")
    print(f"  Hardware: {hw['cpu_model']} | RAM: {hw['ram_total_gb']} GB | GPU: {hw.get('gpu_model', 'nenhuma')}")
    print(f"  RAM em uso agora: {state['ram_start_gb']} GB")
    print(f"  Timestamp: {state['started_at_utc']}")


def cmd_collect(model: str, arch: str, impl_dir: str | None):
    state = load_state()
    if not state:
        print("[AVISO] Estado de sessão não encontrado. Execute --start primeiro.", file=sys.stderr)
        state = {}

    ended_at = datetime.now(timezone.utc)
    started_at_str = state.get("started_at_utc", ended_at.isoformat())
    started_at = datetime.fromisoformat(started_at_str)
    duration_min = round((ended_at - started_at).total_seconds() / 60, 2)

    ram_end = _get_ram_usage_gb()
    ram_start = state.get("ram_start_gb", 0.0)
    ram_peak = round(max(ram_start, ram_end), 1)

    hw = state.get("hardware") or get_hardware_info()

    model_dir = model.split(":")[0].replace("-", "_")
    ts = ended_at.strftime("%Y%m%d_%H%M%S")
    safe_model = model.replace(":", "-").replace("/", "_")
    filename = f"ollama_{safe_model}_{arch}_{ts}.json"
    output_path = RESULTS_DIR / filename

    report = {
        "meta": {
            "experiment": "exp-03",
            "tool": "aider",
            "model": model,
            "architecture": arch,
            "collected_at_utc": ended_at.isoformat(),
            "impl_dir": str(impl_dir) if impl_dir else "",
        },
        "model_info": {
            "name":           model,
            "size_gb":        _get_ollama_model_size(model),
            "parameters":     model.split(":")[-1] if ":" in model else "",
            "specialization": "code" if any(k in model for k in ["coder", "codellama"]) else "general",
        },
        "speed": {
            "session_start_utc":         started_at_str,
            "session_end_utc":           ended_at.isoformat(),
            "session_duration_min":      duration_min,
            "time_per_endpoint_min":     round(duration_min / 5, 2),
            "throughput_endpoints_per_hour": round(5 / (duration_min / 60), 1) if duration_min > 0 else 0,
            "tokens_per_sec":            0,  # preencher manualmente dos logs do Ollama
        },
        "hardware": {
            "os":            hw.get("os"),
            "cpu_model":     hw.get("cpu_model"),
            "cpu_cores":     hw.get("cpu_cores"),
            "ram_total_gb":  hw.get("ram_total_gb"),
            "ram_peak_gb":   ram_peak,
            "gpu_model":     hw.get("gpu_model"),
            "vram_total_gb": hw.get("vram_total_gb"),
            "inference_device": hw.get("inference_device", "cpu"),
        },
        "iterations": {
            "total_turns":    0,   # preencher manualmente
            "aider_messages": 0,   # preencher manualmente
        },
        "errors": {
            "compile_errors":         0,
            "runtime_errors":         0,
            "test_failures":          0,
            "total_errors":           0,
            "context_window_exceeded": False,
        },
        "code_quality": {
            "lines_of_code":          0,
            "test_lines_of_code":     0,
            "test_coverage_line_pct": 0.0,
            "test_coverage_branch_pct": 0.0,
        },
        "arch_metrics": {
            "arch_conformance":      0,
            "dependency_violations": 0,
        },
        "e2e": {
            "total_scenarios": 12,
            "passed":          0,
            "failed":          12,
            "failure_details": [],
        },
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))

    print(f"\n[ollama_collector] Métricas coletadas → {output_path}")
    print(f"  Duração: {duration_min} min")
    print(f"  RAM pico estimada: {ram_peak} GB")
    print(f"  Hardware: {hw.get('cpu_model')} | GPU: {hw.get('gpu_model', 'nenhuma')}")
    print(f"\n  Preencha manualmente no JSON:")
    print(f"    - speed.tokens_per_sec    (dos logs do Ollama)")
    print(f"    - iterations.total_turns  (contagem de interações do Aider)")
    print(f"    - errors.*                (BUILD FAILURE counts)")
    print(f"    - code_quality.*          (cloc + JaCoCo)")
    print(f"    - e2e.*                   (resultados dos 12 cenários)")
    print(f"    - arch_metrics.*          (conformidade arquitetural)")

    if STATE_FILE.exists():
        STATE_FILE.unlink()


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Coleta métricas de sessões Aider + Ollama (Experimento 3)"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--start",    action="store_true", help="Inicia sessão e registra timestamp + hardware")
    group.add_argument("--collect",  action="store_true", help="Finaliza sessão e gera JSON de métricas")
    group.add_argument("--hardware", action="store_true", help="Apenas exibe especificações da máquina")

    parser.add_argument("--model",    help="Nome do modelo Ollama (ex: deepseek-coder-v2:16b)")
    parser.add_argument("--arch",     help="Arquitetura (ex: mvc, clean-architecture)")
    parser.add_argument("--impl-dir", dest="impl_dir", help="Caminho da pasta de implementação")

    args = parser.parse_args()

    if args.hardware:
        cmd_hardware()
    elif args.start:
        if not args.model or not args.arch:
            parser.error("--start exige --model e --arch")
        cmd_start(args.model, args.arch)
    elif args.collect:
        if not args.model or not args.arch:
            parser.error("--collect exige --model e --arch")
        cmd_collect(args.model, args.arch, args.impl_dir)


if __name__ == "__main__":
    main()
