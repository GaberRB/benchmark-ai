#!/usr/bin/env python3
"""
main.py — TUI principal do AI Coding Benchmark (exp-06)

Uso:
    python main.py

Requer:
    pip install -r requirements.txt
    Preencher OPENROUTER_API_KEY no .env
    Java 21 + Maven no PATH
"""

import io
import os
import shutil
import sys
from pathlib import Path

import requests

# Forcar UTF-8 no stdout/stderr antes de qualquer import de rich
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
os.environ.setdefault("PYTHONUTF8", "1")

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from benchmark_config import config

console = Console()


# ═══════════════════════════════════════════════════════════════════════
# BANNER
# ═══════════════════════════════════════════════════════════════════════

BANNER = """\
 AI CODING BENCHMARK
 exp-06  |  Agentic  |  OpenRouter + Tool Use
 7 Arquiteturas  |  5 Modelos  |  12 Cenarios E2E"""

def show_banner() -> None:
    console.print()
    console.print(Panel(BANNER, style="bold cyan", padding=(1, 4)))
    console.print()


# ═══════════════════════════════════════════════════════════════════════
# HELPERS DE INPUT
# ═══════════════════════════════════════════════════════════════════════

def ask(prompt: str, default: str = "") -> str:
    default_hint = f" [{default}]" if default else ""
    try:
        val = input(f"[cyan]>[/cyan] {prompt}{default_hint}: ".replace("[cyan]", "\033[36m").replace("[/cyan]", "\033[0m")).strip()
    except (EOFError, KeyboardInterrupt):
        console.print("\n[yellow]Cancelado.[/yellow]")
        sys.exit(0)
    return val or default


def ask_int(prompt: str, default: int, min_val: int = 1, max_val: int | None = None) -> int:
    while True:
        raw = ask(prompt, str(default))
        if raw.isdigit() and int(raw) >= min_val and (max_val is None or int(raw) <= max_val):
            return int(raw)
        limit = f">= {min_val}" if max_val is None else f"entre {min_val} e {max_val}"
        console.print(f"  [red]Digite um número {limit}.[/red]")


def parse_selection(raw: str, total: int) -> list[int]:
    """Converte '1,3-5,todos' em lista de índices 1..total."""
    raw = raw.strip().lower()
    if raw in ("todos", "all", "a", "*"):
        return list(range(1, total + 1))
    result = set()
    for part in raw.replace(" ", "").split(","):
        if "-" in part:
            a, _, b = part.partition("-")
            if a.isdigit() and b.isdigit():
                result.update(range(int(a), int(b) + 1))
        elif part.isdigit():
            result.add(int(part))
    valid = sorted(x for x in result if 1 <= x <= total)
    return valid


def confirm(prompt: str) -> bool:
    raw = ask(f"{prompt} [s/N]", "N").lower()
    return raw in ("s", "sim", "y", "yes")


# ═══════════════════════════════════════════════════════════════════════
# BUSCA DE MODELOS VIA OPENROUTER API
# ═══════════════════════════════════════════════════════════════════════

def fetch_openrouter_models() -> list[dict]:
    """Busca modelos do OpenRouter que suportam tool use (campo supported_parameters contém 'tools')."""
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    try:
        resp = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=15,
        )
        resp.raise_for_status()
        all_models = resp.json().get("data", [])
    except Exception as exc:
        console.print(f"  [red]Erro ao buscar modelos: {exc}[/red]")
        return []

    result = []
    for m in all_models:
        params = m.get("supported_parameters") or []
        if "tools" not in params:
            continue
        pricing = m.get("pricing", {})
        try:
            price_in  = float(pricing.get("prompt",     0)) * 1_000_000
            price_out = float(pricing.get("completion", 0)) * 1_000_000
        except (TypeError, ValueError):
            price_in = price_out = 0.0
        result.append({
            "name":      m["id"],
            "label":     m.get("name", m["id"]),
            "price_in":  round(price_in,  4),
            "price_out": round(price_out, 4),
            "tool_use":  True,
            "dir":       m["id"].replace("/", "--"),
        })

    result.sort(key=lambda m: m["name"])
    return result


def select_models_from_openrouter() -> list[dict]:
    """Lista modelos do OpenRouter com tool use, paginados de 10 em 10. Retorna lista de dicts de modelo."""
    console.print()
    console.print(Rule("[bold cyan]Buscando modelos com tool use no OpenRouter...[/bold cyan]"))

    models = fetch_openrouter_models()
    if not models:
        console.print("  [yellow]Nenhum modelo encontrado. Usando lista local.[/yellow]\n")
        return []

    page_size = 10
    offset = 0
    selected: list[dict] = []

    while True:
        page = models[offset: offset + page_size]
        console.print()
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan", padding=(0, 1))
        table.add_column("#",      style="bold cyan", width=4,  justify="right")
        table.add_column("Modelo", style="white",     min_width=40)
        table.add_column("In",     style="green",     width=10, justify="right")
        table.add_column("Out",    style="yellow",    width=10, justify="right")

        for i, m in enumerate(page, offset + 1):
            already = "[dim] (selecionado)[/dim]" if m in selected else ""
            table.add_row(str(i), m["name"] + already, f"${m['price_in']}/M", f"${m['price_out']}/M")

        console.print(table)
        showing_end = min(offset + page_size, len(models))
        console.print(f"  Mostrando [cyan]{offset + 1}–{showing_end}[/cyan] de [cyan]{len(models)}[/cyan] modelos com tool use.")
        if selected:
            console.print(f"  Selecionados: [green]{', '.join(m['name'] for m in selected)}[/green]")
        console.print()
        console.print("  Digite os [bold]números[/bold] para selecionar  |  [bold]mais[/bold] para ver próximos 10  |  [bold]ok[/bold] para confirmar")
        console.print()

        raw = ask("Opcao").strip().lower()

        if raw in ("mais", "m", "next", "n"):
            if offset + page_size < len(models):
                offset += page_size
            else:
                console.print("  [yellow]Já está na última página.[/yellow]")
            continue

        if raw in ("ok", "confirmar", ""):
            if selected:
                return selected
            console.print("  [red]Selecione ao menos um modelo antes de confirmar.[/red]")
            continue

        # Interpretar como seleção de números (ex: "1,3" ou "2")
        idxs = parse_selection(raw, len(models))
        for idx in idxs:
            m = models[idx - 1]
            if m not in selected:
                selected.append(m)
        if idxs:
            console.print(f"  [green]Adicionado(s): {', '.join(models[i-1]['name'] for i in idxs)}[/green]")


# ═══════════════════════════════════════════════════════════════════════
# SELEÇÃO DE MODELOS
# ═══════════════════════════════════════════════════════════════════════

def select_models() -> list[int]:
    console.print(Rule("[bold cyan]Modelos disponíveis[/bold cyan]"))
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan", padding=(0, 1))
    table.add_column("#",      style="bold cyan",   width=3,  justify="right")
    table.add_column("Modelo", style="white",        min_width=30)
    table.add_column("Label",  style="dim white",    min_width=18)
    table.add_column("In",     style="green",        width=9,  justify="right")
    table.add_column("Out",    style="yellow",       width=9,  justify="right")

    for i, m in enumerate(config.models, 1):
        tag = "[bold magenta] REF[/bold magenta]" if "claude" in m["name"] else ""
        no_tools = not m.get("tool_use", True)
        name_cell = f"[dim]{m['name']}[/dim]" if no_tools else m["name"]
        label_cell = m["label"] + tag + ("[red] [sem tool use][/red]" if no_tools else "")
        table.add_row(str(i), name_cell, label_cell, f"${m['price_in']}/M", f"${m['price_out']}/M")
    console.print(table)
    console.print()

    while True:
        raw = ask("Modelos (ex: 1,3  |  1-3  |  todos)")
        selected = parse_selection(raw, len(config.models))
        if selected:
            return selected
        console.print("  [red]Selecione ao menos um modelo.[/red]")


# ═══════════════════════════════════════════════════════════════════════
# SELEÇÃO DE ARQUITETURAS
# ═══════════════════════════════════════════════════════════════════════

def select_archs() -> list[int]:
    console.print(Rule("[bold cyan]Arquiteturas disponíveis[/bold cyan]"))
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan", padding=(0, 1))
    table.add_column("#",            style="bold cyan", width=3, justify="right")
    table.add_column("Arquitetura",  style="white",     min_width=22)
    table.add_column("Guia",         style="dim white", min_width=35)

    for i, a in enumerate(config.architectures, 1):
        guide = f"guides/benchmark-arch-{a}.md"
        exists = (Path(config.guides_dir) / f"benchmark-arch-{a}.md").exists()
        status = "" if exists else " [red][sem guia][/red]"
        table.add_row(str(i), a, guide + status)
    console.print(table)
    console.print()

    while True:
        raw = ask("Arquiteturas (ex: 1,2  |  1-4  |  todos)")
        selected = parse_selection(raw, len(config.architectures))
        if selected:
            return selected
        console.print("  [red]Selecione ao menos uma arquitetura.[/red]")


# ═══════════════════════════════════════════════════════════════════════
# PLANO DE EXECUÇÃO
# ═══════════════════════════════════════════════════════════════════════

def build_plan(models: list[dict], arch_idxs: list[int]) -> list[tuple[dict, int]]:
    """Retorna lista de (model_dict, arch_idx) na ordem modelo × arch."""
    return [(m, a) for m in models for a in arch_idxs]


def show_plan(plan: list[tuple[dict, int]], max_build: int, max_test: int) -> None:
    console.print()
    console.print(Rule("[bold cyan]Plano de execução[/bold cyan]"))
    table = Table(box=box.SIMPLE_HEAD, show_header=True,
                  header_style="bold", padding=(0, 1))
    table.add_column("#",           style="cyan",   width=4,  justify="right")
    table.add_column("Modelo",      style="white",  min_width=22)
    table.add_column("Arquitetura", style="white",  min_width=20)
    table.add_column("Max build",   style="yellow", width=10, justify="right")
    table.add_column("Max test",    style="yellow", width=10, justify="right")

    for i, (model, a) in enumerate(plan, 1):
        arch = config.architectures[a - 1]
        table.add_row(str(i), model.get("label", model["name"]), arch, str(max_build), str(max_test))

    console.print(table)
    console.print(f"  Total: [bold cyan]{len(plan)} runs[/bold cyan]\n")


# ═══════════════════════════════════════════════════════════════════════
# EXECUÇÃO DO BENCHMARK
# ═══════════════════════════════════════════════════════════════════════

def _select_model_source() -> list[dict]:
    """Pergunta ao usuário a fonte dos modelos e retorna lista de dicts."""
    console.print(Rule("[bold cyan]Fonte dos modelos[/bold cyan]"))
    console.print("  [cyan]1[/cyan]  Lista local     [dim](5 modelos pré-configurados)[/dim]")
    console.print("  [cyan]2[/cyan]  OpenRouter live [dim](busca todos com tool use na API)[/dim]")
    console.print()
    while True:
        raw = ask("Opcao", "1")
        if raw == "1":
            model_idxs = select_models()
            return [config.models[i - 1] for i in model_idxs]
        if raw == "2":
            result = select_models_from_openrouter()
            if result:
                return result
            console.print("  [yellow]Nenhum modelo selecionado. Tente novamente.[/yellow]")
        else:
            console.print("  [red]Digite 1 ou 2.[/red]")


def run_benchmark_mode() -> None:
    console.print()
    selected_models = _select_model_source()
    console.print()
    arch_idxs = select_archs()
    console.print()

    max_build = ask_int(
        "Max tentativas de build (mvn compile com falha)",
        default=config.max_build_failures,
        min_val=1,
    )
    max_test = ask_int(
        "Max tentativas de teste  (mvn test com falha)  ",
        default=config.max_test_failures,
        min_val=1,
    )
    console.print()

    plan = build_plan(selected_models, arch_idxs)
    show_plan(plan, max_build, max_test)

    if not confirm("Confirmar e iniciar o benchmark?"):
        console.print("[yellow]Cancelado.[/yellow]")
        return

    config.max_build_failures = max_build
    config.max_test_failures  = max_test

    from harness.harness import BenchmarkHarness

    all_results: list[dict] = []
    total = len(plan)

    for i, (model, a_idx) in enumerate(plan, 1):
        arch = config.architectures[a_idx - 1]

        console.print()
        console.print(Panel(
            f"[bold white]Run {i}/{total}[/bold white]  "
            f"[cyan]{model.get('label', model['name'])}[/cyan]  ×  [green]{arch}[/green]\n"
            f"[dim]build failures max={config.max_build_failures}  |  "
            f"test failures max={config.max_test_failures}  |  execução autônoma[/dim]",
            style="bold",
            padding=(0, 2),
        ))

        try:
            harness = BenchmarkHarness(config, model, a_idx)
            _, result = harness.run()
            all_results.append(result)
        except FileNotFoundError as exc:
            console.print(f"[red]{exc}[/red]")
            all_results.append({
                "model": model["name"], "arch": arch,
                "build": {"success": False}, "tests": {}, "e2e": {}, "arch_check": {},
                "agent": {"total_tool_calls": 0, "convergence_reason": "error"},
            })
        except Exception as exc:
            console.print(f"[red]Erro inesperado: {exc}[/red]")
            all_results.append({
                "model": model["name"], "arch": arch,
                "build": {"success": False}, "tests": {}, "e2e": {}, "arch_check": {},
                "agent": {"total_tool_calls": 0, "convergence_reason": "error"},
            })

        _print_run_result(i, total, all_results[-1], model, arch)

    show_final_summary(all_results)


def _print_run_result(run_n: int, total: int, r: dict, model: dict, arch: str) -> None:
    build_ok = r.get("build", {}).get("success", False)
    tests    = r.get("tests", {})
    e2e      = r.get("e2e",   {})
    arch_r   = r.get("arch_check", {})
    agent    = r.get("agent", {})

    b  = "[green]PASS[/green]" if build_ok else "[red]FAIL[/red]"
    t  = f"{tests.get('tests_passed',0)}/{tests.get('tests_total',0)}"
    cov = f"{tests.get('coverage_line_pct',0.0):.1f}%"
    e  = f"{e2e.get('passed',0)}/12"
    ac = "[green]OK[/green]" if arch_r.get("ok", True) else f"[red]{len(arch_r.get('violations',[]))} viol.[/red]"
    ag = f"{agent.get('total_tool_calls',0)} calls  ({agent.get('convergence_reason','?')})"

    console.print(
        f"  [dim]{run_n}/{total}[/dim] "
        f"[bold]{model['label']}[/bold] × [bold]{arch}[/bold]  "
        f"Build:{b}  Tests:{t}  Cov:{cov}  E2E:{e}  Arch:{ac}  [dim]{ag}[/dim]"
    )


# ═══════════════════════════════════════════════════════════════════════
# TABELA FINAL
# ═══════════════════════════════════════════════════════════════════════

def show_final_summary(results: list[dict]) -> None:
    if not results:
        return

    console.print()
    console.print(Rule("[bold cyan]Resultados Finais[/bold cyan]"))

    table = Table(box=box.ROUNDED, show_header=True,
                  header_style="bold cyan", padding=(0, 1))
    table.add_column("Modelo",      style="white",  min_width=22, no_wrap=True)
    table.add_column("Arch",        style="cyan",   min_width=18, no_wrap=True)
    table.add_column("Build",       style="white",  min_width=6,  justify="center")
    table.add_column("Tests",       style="white",  min_width=7,  justify="center")
    table.add_column("Cov",         style="white",  min_width=6,  justify="right")
    table.add_column("E2E",         style="white",  min_width=5,  justify="center")
    table.add_column("Arch",        style="white",  min_width=6,  justify="center")
    table.add_column("Calls",       style="dim",    min_width=6,  justify="right")
    table.add_column("Bld fail",    style="dim",    min_width=8,  justify="right")
    table.add_column("Tst fail",    style="dim",    min_width=8,  justify="right")
    table.add_column("Converge",    style="dim",    min_width=13)

    passed_runs = 0
    for r in results:
        build_ok = r.get("build", {}).get("success", False)
        tests    = r.get("tests", {})
        e2e      = r.get("e2e",   {})
        arch_r   = r.get("arch_check", {})
        agent    = r.get("agent", {})

        all_ok = (
            build_ok
            and tests.get("tests_pass", False)
            and tests.get("coverage_ok", False)
            and e2e.get("all_passed", False)
            and arch_r.get("ok", True)
        )
        if all_ok:
            passed_runs += 1

        # Label curto do modelo
        m_name = r.get("model", "")
        m_label = next((m["label"] for m in config.models if m["name"] == m_name), m_name)

        b   = "[green]PASS[/green]"  if build_ok                        else "[red]FAIL[/red]"
        t   = f"{tests.get('tests_passed',0)}/{tests.get('tests_total',0)}"
        cov_val = tests.get('coverage_line_pct', 0.0)
        cov = (f"[green]{cov_val:.1f}%[/green]"
               if cov_val >= 80 else f"[yellow]{cov_val:.1f}%[/yellow]")
        ep  = e2e.get("passed", 0)
        e   = f"[green]{ep}/12[/green]" if ep == 12 else f"[yellow]{ep}/12[/yellow]"
        ac  = "[green]OK[/green]" if arch_r.get("ok", True) \
              else f"[red]{len(arch_r.get('violations',[]))}[/red]"
        calls   = str(agent.get("total_tool_calls", 0))
        bf      = str(agent.get("build_failures", 0))
        tf      = str(agent.get("test_failures", 0))
        conv    = agent.get("convergence_reason", "?")

        row_style = "bold" if all_ok else ""
        table.add_row(m_label, r.get("arch",""), b, t, cov, e, ac, calls, bf, tf, conv,
                      style=row_style)

    console.print(table)
    console.print(
        f"\n  [bold cyan]{passed_runs}/{len(results)}[/bold cyan] runs com todos os critérios atendidos.\n"
    )


# ═══════════════════════════════════════════════════════════════════════
# MODO CHAT
# ═══════════════════════════════════════════════════════════════════════

def select_model_single() -> int:
    console.print(Rule("[bold cyan]Modelos disponíveis[/bold cyan]"))
    for i, m in enumerate(config.models, 1):
        tag = "  [magenta][REF][/magenta]" if "claude" in m["name"] else ""
        console.print(f"  [cyan]{i}[/cyan]  {m['label']:22s}  [dim]{m['name']}[/dim]{tag}")
    console.print()
    while True:
        raw = ask("Modelo")
        if raw.isdigit() and 1 <= int(raw) <= len(config.models):
            return int(raw)
        console.print("  [red]Número inválido.[/red]")


def run_chat_mode() -> None:
    console.print()
    model_idx = select_model_single()
    # Importar e iniciar o loop de chat
    import chat as chat_module
    chat_module.chat_loop(model_idx)


# ═══════════════════════════════════════════════════════════════════════
# LIMPEZA DE ARQUIVOS GERADOS
# ═══════════════════════════════════════════════════════════════════════

def run_clean_mode() -> None:
    console.print()
    console.print(Rule("[bold cyan]Limpar arquivos gerados[/bold cyan]"))

    exp_dir    = Path(config.exp_dir)
    impl_dir   = exp_dir / "implementations"
    results_dir = exp_dir / "results"

    java_files   = list(impl_dir.rglob("*.java"))
    target_dirs  = [d for d in impl_dir.rglob("target") if d.is_dir()]
    result_jsons = list(results_dir.rglob("*.json")) if results_dir.exists() else []

    if not java_files and not target_dirs and not result_jsons:
        console.print("  [green]Nada para limpar — já está limpo.[/green]\n")
        return

    console.print("  Serão removidos:")
    if java_files:
        console.print(f"    [yellow]{len(java_files)}[/yellow] arquivo(s) [bold].java[/bold] em implementations/")
    if target_dirs:
        console.print(f"    [yellow]{len(target_dirs)}[/yellow] pasta(s) [bold]target/[/bold]")
    if result_jsons:
        console.print(f"    [yellow]{len(result_jsons)}[/yellow] resultado(s) [bold].json[/bold] em results/")
    console.print()
    console.print("  [dim]Mantidos: pom.xml, .gitkeep, guias, harness, config[/dim]")
    console.print()

    if not confirm("Confirmar limpeza?"):
        console.print("[yellow]Cancelado.[/yellow]\n")
        return

    for f in java_files:
        try:
            f.unlink()
        except Exception:
            pass
    for d in target_dirs:
        try:
            shutil.rmtree(str(d))
        except Exception:
            pass
    for f in result_jsons:
        try:
            f.unlink()
        except Exception:
            pass

    console.print(
        f"\n  [green]Removidos:[/green] "
        f"{len(java_files)} .java  |  "
        f"{len(target_dirs)} target/  |  "
        f"{len(result_jsons)} .json\n"
    )


# ═══════════════════════════════════════════════════════════════════════
# MENU PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════

def main_menu() -> str:
    console.print(Rule("[bold cyan]Menu Principal[/bold cyan]"))
    console.print("  [cyan]1[/cyan]  Benchmark automatico  [dim](seleciona modelos + archs + roda em sequencia)[/dim]")
    console.print("  [cyan]2[/cyan]  Chat interativo       [dim](conversa com o modelo, ele executa benchmarks)[/dim]")
    console.print("  [cyan]3[/cyan]  Limpar arquivos       [dim](remove .java, target/ e resultados gerados)[/dim]")
    console.print("  [cyan]4[/cyan]  Sair")
    console.print()
    while True:
        raw = ask("Opcao")
        if raw in ("1", "2", "3", "4"):
            return raw
        console.print("  [red]Digite 1, 2, 3 ou 4.[/red]")


# ═══════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════

def main() -> None:
    if "OPENROUTER_API_KEY" not in os.environ or \
       os.environ["OPENROUTER_API_KEY"].startswith("sk-or-coloque"):
        console.print("[red][ERRO][/red] OPENROUTER_API_KEY não definida. Edite o arquivo [bold].env[/bold].")
        sys.exit(1)

    show_banner()

    while True:
        choice = main_menu()
        if choice == "1":
            run_benchmark_mode()
        elif choice == "2":
            run_chat_mode()
        elif choice == "3":
            run_clean_mode()
        else:
            console.print("\n[dim]Ate logo.[/dim]\n")
            break


if __name__ == "__main__":
    main()
