"""
exp-07 Aider Benchmark — TUI para execução do benchmark de arquiteturas com Aider CLI.

Uso:
    python main.py

Pré-requisito:
    - aider instalado (uv tool install aider-chat ou pip install aider-chat)
    - OPENROUTER_API_KEY no .env ou na variável de ambiente
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from benchmark_config import ARCHITECTURES, JAVA_PACKAGE, MODELS

# Resolve caminhos relativos ao projeto
SCRIPT_DIR   = Path(__file__).parent
REPO_ROOT    = SCRIPT_DIR.parent.parent
RESULTS_DIR  = SCRIPT_DIR / "results"
GUIDES_DIR   = SCRIPT_DIR / "guides"
IMPL_DIR     = SCRIPT_DIR / "implementations"
TASK_DEF     = REPO_ROOT / "shared" / "task-definition.md"
EXP06_IMPLS  = REPO_ROOT / "experiments" / "exp-06-agentic-benchmark" / "implementations"

# Pasta de referência para copiar pom.xml do exp-06
EXP06_REF_MODEL = "claude-sonnet"

console = Console()

# ---------------------------------------------------------------------------
# Carrega .env (tenta o .env do exp-06 como fallback)
# ---------------------------------------------------------------------------

def _load_env():
    local_env = SCRIPT_DIR / ".env"
    exp06_env = REPO_ROOT / "experiments" / "exp-06-agentic-benchmark" / ".env"
    if local_env.exists():
        load_dotenv(local_env)
    elif exp06_env.exists():
        load_dotenv(exp06_env)
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        console.print("[red]OPENROUTER_API_KEY não encontrado.[/red]")
        console.print(f"Crie {local_env} com OPENROUTER_API_KEY=sk-or-...")
        sys.exit(1)
    return key


# ---------------------------------------------------------------------------
# Seleção de modelo via TUI
# ---------------------------------------------------------------------------

def _select_model() -> dict:
    table = Table(title="Modelos disponíveis", box=box.ROUNDED)
    table.add_column("#", style="bold cyan", width=3)
    table.add_column("Modelo", style="bold")
    table.add_column("Aider ID", style="dim")
    table.add_column("In $/M", justify="right")
    table.add_column("Out $/M", justify="right")

    for i, m in enumerate(MODELS, 1):
        table.add_row(str(i), m["label"], m["aider_model"], f"${m['price_in']:.3f}", f"${m['price_out']:.2f}")

    console.print(table)
    idx = Prompt.ask("Selecione o modelo", choices=[str(i) for i in range(1, len(MODELS) + 1)])
    return MODELS[int(idx) - 1]


def _select_arch() -> str:
    table = Table(title="Arquiteturas disponíveis", box=box.ROUNDED)
    table.add_column("#", style="bold cyan", width=3)
    table.add_column("Arquitetura")

    for i, a in enumerate(ARCHITECTURES, 1):
        table.add_row(str(i), a)

    console.print(table)
    idx = Prompt.ask("Selecione a arquitetura", choices=[str(i) for i in range(1, len(ARCHITECTURES) + 1)])
    return ARCHITECTURES[int(idx) - 1]


# ---------------------------------------------------------------------------
# Setup do projeto
# ---------------------------------------------------------------------------

def _setup_project(model: dict, arch: str) -> Path:
    impl_dir = IMPL_DIR / model["dir"] / arch
    impl_dir.mkdir(parents=True, exist_ok=True)

    pom_dest = impl_dir / "pom.xml"
    if not pom_dest.exists():
        pom_src = EXP06_IMPLS / EXP06_REF_MODEL / arch / "pom.xml"
        if pom_src.exists():
            shutil.copy2(pom_src, pom_dest)
            console.print(f"[green]✓[/green] pom.xml copiado de exp-06/{arch}")
        else:
            console.print(f"[yellow]⚠ pom.xml não encontrado em exp-06/{arch} — crie manualmente[/yellow]")

    return impl_dir


# ---------------------------------------------------------------------------
# Execução do Aider
# ---------------------------------------------------------------------------

def _run_aider(model: dict, arch: str, impl_dir: Path, api_key: str) -> tuple:
    """Lança Aider como subprocess. Retorna (custo_usd, stdout_completo)."""
    guide = GUIDES_DIR / f"benchmark-aider-{arch}.md"
    if not guide.exists():
        console.print(f"[red]Guia não encontrado: {guide}[/red]")
        return 0.0, ""

    cmd = [
        "aider",
        "--model", model["aider_model"],
        "--test-cmd", "mvn compile && mvn test",
        "--auto-test",
        "--yes-always",
        "--no-auto-commits",
        "--read", str(guide.absolute()),
        "--read", str(TASK_DEF.absolute()),
        "--message",
        (
            "Implement the Task Manager REST API as described in the guide. "
            "Write all production files first, then write the test file. "
            "After all files are ready, mvn compile && mvn test will run automatically. "
            "Fix any build or test failures. "
            "When mvn test shows BUILD SUCCESS with 0 failures, output exactly: "
            "IMPLEMENTATION COMPLETE"
        ),
    ]

    console.print(Panel(
        f"[bold cyan]Iniciando Aider[/bold cyan]\n"
        f"Modelo: [yellow]{model['aider_model']}[/yellow]\n"
        f"Arquitetura: [yellow]{arch}[/yellow]\n"
        f"Diretório: [dim]{impl_dir}[/dim]",
        title="exp-07",
    ))

    env = os.environ.copy()
    env["OPENROUTER_API_KEY"] = api_key

    start = time.time()
    result = subprocess.run(
        cmd,
        cwd=str(impl_dir),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    duration = (time.time() - start) / 60.0

    # Stream output para o terminal
    if result.stdout:
        console.print(result.stdout)
    if result.stderr:
        console.print(result.stderr)

    # Extrair custo do output (formato: "Cost: $X.XX USD" ou "Tokens: X sent, Y received. Cost: $Z")
    cost = _parse_aider_cost(result.stdout + result.stderr)

    return duration, cost, result.stdout + result.stderr


def _parse_aider_cost(output: str) -> float:
    """Extrai custo do output do Aider."""
    patterns = [
        r"[Cc]ost[:\s]+\$([0-9]+\.[0-9]+)",
        r"\$([0-9]+\.[0-9]+)\s*USD",
    ]
    for pat in patterns:
        m = re.search(pat, output)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                pass
    return 0.0


# ---------------------------------------------------------------------------
# Verificação pós-Aider (build + test + E2E)
# ---------------------------------------------------------------------------

def _verify(impl_dir: Path) -> dict:
    """Roda verificação independente: build, tests, E2E."""
    sys.path.insert(0, str(SCRIPT_DIR / "tools"))
    try:
        from collector import eval_build, eval_tests, eval_e2e, eval_architecture, count_loc
        build  = eval_build(impl_dir)
        tests  = eval_tests(impl_dir) if build["success"] else {"tests_pass": False, "tests_total": 0, "tests_passed": 0, "tests_failed": 0, "coverage_line_pct": 0.0, "coverage_branch_pct": 0.0, "coverage_ok": False}
        e2e    = eval_e2e(impl_dir)   if (build["success"] and tests.get("tests_pass")) else {"app_started": False, "passed": 0, "failed": 12, "all_passed": False, "failures": ["Skipped — build or tests failed"]}

        pkg    = impl_dir / "src" / "main" / "java" / JAVA_PACKAGE
        test_p = impl_dir / "src" / "test" / "java" / JAVA_PACKAGE
        loc    = {"prod": count_loc(pkg), "test": count_loc(test_p)}
        return {"build": build, "tests": tests, "e2e": e2e, "loc": loc}
    except ImportError as e:
        console.print(f"[red]Erro importando collector: {e}[/red]")
        return {}
    finally:
        sys.path.pop(0)


# ---------------------------------------------------------------------------
# Salvar resultado
# ---------------------------------------------------------------------------

def _save_result(model: dict, arch: str, impl_dir: Path, duration: float, cost: float, verification: dict):
    RESULTS_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = RESULTS_DIR / f"exp07_{model['dir']}_{arch}_{ts}.json"

    report = {
        "experiment": "exp-07-aider-benchmark",
        "meta": {
            "aider_model": model["aider_model"],
            "model_label": model["label"],
            "architecture": arch,
            "collected_at_utc": datetime.now(timezone.utc).isoformat(),
            "impl_dir": str(impl_dir),
        },
        "speed": {
            "duration_min": round(duration, 2),
        },
        "cost": {
            "total_usd": round(cost, 4),
            "price_in_per_m": model["price_in"],
            "price_out_per_m": model["price_out"],
        },
        **verification,
    }

    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    console.print(f"\n[green]✓ Resultado salvo:[/green] {out}")
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    _load_env()
    api_key = os.environ["OPENROUTER_API_KEY"]

    console.print(Panel("[bold]exp-07 — Aider Benchmark de Arquiteturas[/bold]", style="blue"))

    model = _select_model()
    arch  = _select_arch()

    console.print(f"\n[bold]Configuração:[/bold] {model['label']} × {arch}")
    if not Confirm.ask("Iniciar benchmark?"):
        return

    impl_dir = _setup_project(model, arch)
    duration, cost, raw_output = _run_aider(model, arch, impl_dir, api_key)

    console.print(f"\n[bold]Aider concluído.[/bold] Duração: {duration:.1f} min · Custo detectado: ${cost:.4f}")

    console.print("\n[bold cyan]Rodando verificação independente...[/bold cyan]")
    verification = _verify(impl_dir)

    _save_result(model, arch, impl_dir, duration, cost, verification)

    # Sumário
    if verification:
        b = verification.get("build", {})
        t = verification.get("tests", {})
        e = verification.get("e2e", {})
        console.print(Panel(
            f"Build: {'✅' if b.get('success') else '❌'}\n"
            f"Testes: {t.get('tests_passed', 0)}/{t.get('tests_total', 0)} · "
            f"Cobertura linha: {t.get('coverage_line_pct', 0):.1f}%\n"
            f"E2E: {e.get('passed', 0)}/12",
            title="Resultado",
        ))


if __name__ == "__main__":
    main()
