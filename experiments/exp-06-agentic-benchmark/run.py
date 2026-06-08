#!/usr/bin/env python3
"""
run.py — Exp-06: Agentic Benchmark (Python harness + LLM tool use)

Uso:
    python run.py [model_idx] [arch_idx]
    python run.py 1 1       # DeepSeek V3 + MVC
    python run.py           # menu interativo

Requisitos:
    pip install -r requirements.txt
    Preencha OPENROUTER_API_KEY no arquivo .env
    Java 21 + Maven no PATH
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Carrega .env do diretório do script (se existir)
load_dotenv(Path(__file__).parent / ".env")

from benchmark_config import config
from harness.harness import BenchmarkHarness


MODELS_DISPLAY = [
    f"{i+1}. {m['name']:45s} ({m['dir']})"
    for i, m in enumerate(config.models)
]

ARCHS_DISPLAY = [
    f"{i+1}. {a}"
    for i, a in enumerate(config.architectures)
]


def pick(prompt: str, options: list[str], valid_range: range) -> int:
    print(f"\n{prompt}")
    for opt in options:
        print(f"  {opt}")
    print()
    while True:
        raw = input("Número: ").strip()
        if raw.isdigit() and int(raw) in valid_range:
            return int(raw)
        print(f"  Inválido. Digite um número entre {valid_range.start} e {valid_range.stop - 1}.")


def main():
    if "OPENROUTER_API_KEY" not in os.environ or os.environ["OPENROUTER_API_KEY"].startswith("sk-or-coloque"):
        print('[ERRO] OPENROUTER_API_KEY não definida.')
        print('Edite o arquivo .env e coloque sua chave real:')
        print('  OPENROUTER_API_KEY=sk-or-...')
        sys.exit(1)

    model_idx = int(sys.argv[1]) if len(sys.argv) > 1 else None
    arch_idx  = int(sys.argv[2]) if len(sys.argv) > 2 else None

    n_models = len(config.models)
    n_archs  = len(config.architectures)

    if model_idx is None:
        model_idx = pick("Modelo:", MODELS_DISPLAY, range(1, n_models + 1))
    if arch_idx is None:
        arch_idx = pick("Arquitetura:", ARCHS_DISPLAY, range(1, n_archs + 1))

    if model_idx not in range(1, n_models + 1):
        print(f"Modelo inválido: {model_idx}"); sys.exit(1)
    if arch_idx not in range(1, n_archs + 1):
        print(f"Arquitetura inválida: {arch_idx}"); sys.exit(1)

    harness = BenchmarkHarness(config, model_idx, arch_idx)
    harness.run()


if __name__ == "__main__":
    main()
