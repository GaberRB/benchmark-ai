#!/usr/bin/env python3
"""
chat.py — Interface de chat interativa com o modelo.

O modelo tem acesso às tools (run_command, write_file, read_file) e pode
executar benchmarks autonomamente a partir das suas instruções.

Uso:
    python chat.py [model_idx]
    python chat.py 1          # DeepSeek V3
    python chat.py            # menu interativo

Exemplo de sessão:
    você: execute o benchmark-arch-mvc.md com deepseek
    deepseek-v3: Vou executar o benchmark MVC. Lendo o guia...
    [tool] read_file ← guides/benchmark-arch-mvc.md
    deepseek-v3: Guia carregado. Começando a implementação...
    [tool] write_file → implementations/deepseek-v3/mvc/src/...
    ...
"""

import json
import os
import sys
from pathlib import Path
from string import Template
from textwrap import shorten

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).parent / ".env")

from benchmark_config import config
from harness.terminal import detect_terminal, TERMINAL_NOTE
from harness.tools import ToolExecutor, TOOL_SCHEMAS

# ── Cores ANSI ──────────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[36m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
GRAY   = "\033[90m"
WHITE  = "\033[97m"


def _c(color: str, text: str) -> str:
    return f"{color}{text}{RESET}"


# ── System prompt do modo chat ────────────────────────────────────────────────

def build_system_prompt(model_name: str, terminal: str) -> str:
    terminal_desc = TERMINAL_NOTE.get(terminal, terminal)
    exp_dir = config.exp_dir

    models_list = "\n".join(
        f"  {i+1}. {m['name']} → implementations/{m['dir']}/"
        for i, m in enumerate(config.models)
    )
    archs_list = "\n".join(
        f"  {i+1}. {a}"
        for i, a in enumerate(config.architectures)
    )

    guides_list = "\n".join(
        f"  guides/benchmark-arch-{a}.md"
        for a in config.architectures
    )

    impl_map = "\n".join(
        f"  {m['name']} → implementations/{m['dir']}/<arch>/"
        for m in config.models
    )

    return f"""You are an AI coding benchmark assistant. You help run benchmarks that test LLM code generation quality.

## Your role
The user gives you instructions in natural language. You execute them using your tools, report progress, and show results.
Always respond in the same language the user writes in (Portuguese or English).
Be concise but informative — tell the user what you're doing at each step.

## Environment
- Terminal: {terminal_desc}
- Base directory: {exp_dir}
- All relative paths in tools are relative to this base directory.

## Available tools
**run_command(command, cwd?)** — runs a shell command. Use `cwd` to specify a subdirectory.
  Example: run_command("mvn compile", cwd="implementations/deepseek-v3/mvc")

**write_file(path, content)** — creates or overwrites a file (path relative to base dir).
  Example: write_file("implementations/deepseek-v3/mvc/src/.../Task.java", "...java code...")

**read_file(path)** — reads a file (path relative to base dir).
  Example: read_file("guides/benchmark-arch-mvc.md")

## Available guides (read with read_file)
{guides_list}

## Models and their implementation directories
{models_list}

## Architectures
{archs_list}

## Implementation directory map
{impl_map}

## How to run a benchmark
When the user asks to run a benchmark (e.g. "execute benchmark-arch-mvc.md with deepseek"):
1. Use read_file to load the guide: `guides/benchmark-arch-<arch>.md`
2. Fill in context: the guide uses placeholders — tell the user what you understood
3. Use write_file to create all Java files in `implementations/<model-dir>/<arch>/`
4. Use run_command with cwd="implementations/<model-dir>/<arch>" to compile: `mvn compile`
5. Fix any errors and re-compile
6. Use run_command to test: `mvn test`
7. Fix failures. Repeat until 0 failures.
8. Report the result to the user (build, tests, coverage)

## Important rules
- Always delete old Java files before starting: run_command("find src -name '*.java' -delete", cwd=<impl_dir>)
- Never modify pom.xml
- Write COMPLETE file content — no placeholders
- Keep the user informed at each major step
- If something fails after multiple attempts, explain the error and ask what to do
"""


# ── Exibição ──────────────────────────────────────────────────────────────────

def print_tool_call(fn_name: str, fn_args: dict) -> None:
    if fn_name == "run_command":
        cmd = fn_args.get("command", "")
        cwd = fn_args.get("cwd", "")
        cwd_str = f"  ({cwd})" if cwd else ""
        print(_c(GRAY, f"  [tool] run_command{cwd_str}  $ {shorten(cmd, 90)}"))
    elif fn_name == "write_file":
        print(_c(GRAY, f"  [tool] write_file  >> {fn_args.get('path','')}"))
    elif fn_name == "read_file":
        print(_c(GRAY, f"  [tool] read_file   << {fn_args.get('path','')}"))
    else:
        print(_c(GRAY, f"  [tool] {fn_name}  {json.dumps(fn_args)[:80]}"))


def print_tool_result(fn_name: str, result: dict) -> None:
    if fn_name == "run_command":
        code = result.get("exit_code", "?")
        status = _c(GREEN, "OK") if code == 0 else _c(YELLOW, f"FAIL exit={code}")
        stdout = result.get("stdout", "").strip()
        if stdout:
            # Mostrar apenas as últimas linhas relevantes
            lines = stdout.splitlines()
            summary = next(
                (l for l in reversed(lines) if "BUILD" in l or "Tests run" in l or "ERROR" in l),
                lines[-1] if lines else ""
            )
            print(_c(GRAY, f"         {status}  {shorten(summary, 80)}"))
        else:
            print(_c(GRAY, f"         {status}"))


# ── Loop principal ────────────────────────────────────────────────────────────

def chat_loop(model_idx: int) -> None:
    model_info = config.models[model_idx - 1]
    model_name = model_info["name"]
    model_label = model_info["dir"]  # ex: "deepseek-v3"

    terminal = detect_terminal()
    executor = ToolExecutor(config.exp_dir, terminal)

    client = OpenAI(
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url="https://openrouter.ai/api/v1",
    )

    system_prompt = build_system_prompt(model_name, terminal)
    messages: list[dict] = [{"role": "system", "content": system_prompt}]

    print(f"\n{_c(CYAN + BOLD, '='*60)}")
    print(_c(CYAN, f"  Benchmark Chat"))
    print(_c(CYAN, f"  Modelo : {model_name}"))
    print(_c(CYAN, f"  Terminal: {terminal}"))
    print(_c(CYAN + BOLD, '='*60))
    print(_c(GRAY, "  Digite 'sair' para encerrar.\n"))

    while True:
        # ── Input do usuário ──
        try:
            user_input = input(_c(BOLD + WHITE, "você: ")).strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{_c(GRAY, 'Encerrando.')}")
            break

        if not user_input:
            continue
        if user_input.lower() in ("sair", "exit", "quit"):
            print(_c(GRAY, "Encerrando."))
            break

        messages.append({"role": "user", "content": user_input})
        print()

        # ── Loop agentico para esta mensagem ──
        while True:
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    tools=TOOL_SCHEMAS,
                    tool_choice="auto",
                    max_tokens=config.max_tokens_per_turn,
                    extra_headers={
                        "HTTP-Referer": "https://github.com/GaberRB/benchmark",
                        "X-Title": "AI Coding Benchmark chat",
                    },
                )
            except Exception as exc:
                print(_c(YELLOW, f"[ERRO API] {exc}"))
                break

            choice = response.choices[0]
            assistant_msg = choice.message
            messages.append(assistant_msg)

            text = (assistant_msg.content or "").strip()
            tool_calls = assistant_msg.tool_calls or []

            # Exibir resposta textual do modelo
            if text:
                print(_c(CYAN + BOLD, f"{model_label}: ") + text + "\n")

            # Se não há tool calls → modelo terminou de responder
            if not tool_calls:
                break

            # Executar tool calls
            for call in tool_calls:
                fn_name = call.function.name
                try:
                    fn_args = json.loads(call.function.arguments)
                except json.JSONDecodeError:
                    fn_args = {}

                print_tool_call(fn_name, fn_args)
                result = executor.dispatch(fn_name, fn_args)
                print_tool_result(fn_name, result)

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result, ensure_ascii=False),
                })

            # Continuar o loop agentico (modelo vai processar os resultados das tools)


# ── Entry point ───────────────────────────────────────────────────────────────

def pick_model() -> int:
    print(f"\n{_c(CYAN, 'Escolha o modelo:')}")
    for i, m in enumerate(config.models, 1):
        print(f"  {i}. {m['name']}")
    print()
    while True:
        raw = input("Número: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(config.models):
            return int(raw)


def main() -> None:
    if "OPENROUTER_API_KEY" not in os.environ or \
       os.environ["OPENROUTER_API_KEY"].startswith("sk-or-coloque"):
        print("[ERRO] OPENROUTER_API_KEY não definida. Edite o arquivo .env.")
        sys.exit(1)

    model_idx = int(sys.argv[1]) if len(sys.argv) > 1 else None
    if model_idx is None:
        model_idx = pick_model()
    if model_idx not in range(1, len(config.models) + 1):
        print(f"Modelo inválido: {model_idx}")
        sys.exit(1)

    chat_loop(model_idx)


if __name__ == "__main__":
    main()
