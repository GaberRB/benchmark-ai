"""BenchmarkHarness — loop principal de tool use via OpenRouter API."""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from string import Template

from openai import OpenAI

from .terminal import detect_terminal, terminal_env_description
from .tools import ToolExecutor, TOOL_SCHEMAS
from . import metrics as m


COMPLETION_SIGNAL = "IMPLEMENTATION COMPLETE"


class BenchmarkHarness:
    def __init__(self, config, model: dict, arch_idx: int):
        self.cfg = config
        self.model_name = model["name"]
        self.arch_name  = config.architectures[arch_idx - 1]
        self.model_dir  = model["dir"]

        self.terminal = detect_terminal()
        self.impl_dir = (
            Path(config.exp_dir) / "implementations" / self.model_dir / self.arch_name
        )
        self.results_dir = Path(config.exp_dir) / "results"
        self.pkg_path = config.base_package.replace(".", "/")
        self.src_base = f"src/main/java/{self.pkg_path}"
        self.test_base = f"src/test/java/{self.pkg_path}"

        self._ensure_impl_dir()
        self.executor = ToolExecutor(str(self.impl_dir), self.terminal)
        self.client = OpenAI(
            api_key=os.environ["OPENROUTER_API_KEY"],
            base_url="https://openrouter.ai/api/v1",
        )

    # ------------------------------------------------------------------

    def run(self) -> tuple[Path, dict]:
        started_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        def p(msg="", **kw):
            print(msg, **kw, flush=True)

        p(f"\n{'='*60}")
        p(f"  Modelo   : {self.model_name}")
        p(f"  Arch     : {self.arch_name}")
        p(f"  Guia     : {self._guide_path()}")
        p(f"  Dir      : {self.impl_dir}")
        p(f"  Terminal : {self.terminal}")
        p(f"{'='*60}\n")

        self._clean_java_files()

        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user",   "content": self._load_guide()},
        ]

        convergence_reason = "gave_up"
        total_calls = 0
        completion_attempts  = 0   # quantas vezes LLM declarou IMPLEMENTATION COMPLETE
        e2e_attempts         = 0   # quantas vezes o harness chegou a rodar o E2E
        e2e_fail_streak      = 0   # falhas consecutivas de E2E (reset se outro critério falha antes)
        # Resultados em cache quando verificados dentro do loop (evita rerun duplo)
        _cached_build = _cached_tests = _cached_e2e = None

        p(f"[INFO] Iniciando loop agentico "
          f"(build max={self.cfg.max_build_failures} falhas | test max={self.cfg.max_test_failures} falhas)...")

        while True:
            p(f"  → aguardando API ({self.model_name})...", end="\r")
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    tools=TOOL_SCHEMAS,
                    tool_choice="auto",
                    max_tokens=self.cfg.max_tokens_per_turn,
                    timeout=180,
                    extra_headers={
                        "HTTP-Referer": "https://github.com/GaberRB/benchmark",
                        "X-Title": "AI Coding Benchmark exp-06",
                    },
                )
            except Exception as exc:
                exc_str = str(exc)
                p(f"[ERRO] API: {exc_str[:300]}")
                if "401" in exc_str or "403" in exc_str:
                    p("[ERRO] Verifique a OPENROUTER_API_KEY no arquivo .env")
                    convergence_reason = "auth_error"
                    break
                if "404" in exc_str:
                    p("[ERRO] Modelo não suporta tool use neste provider. Troque de modelo.")
                    convergence_reason = "no_tool_support"
                    break
                time.sleep(5)
                continue

            choice = response.choices[0]
            assistant_msg = choice.message
            messages.append(assistant_msg)

            text_content = assistant_msg.content or ""
            tool_calls = assistant_msg.tool_calls or []

            if text_content.strip():
                p(f"\n\033[36m{self.model_dir}:\033[0m {text_content.strip()}\n")

            # ------------------------------------------------------------------
            # LLM declarou conclusão — verificar de forma independente
            # ------------------------------------------------------------------
            if COMPLETION_SIGNAL in text_content:
                completion_attempts += 1
                p(f"\n[CHECK #{completion_attempts}] LLM declarou conclusao "
                  f"(tool calls totais={self.executor._total_calls}). Verificando criterios...")

                chk_build = m.eval_build(self.impl_dir)
                p(f"  Build     : {'OK' if chk_build['success'] else 'FAIL'}")

                if not chk_build["success"]:
                    err = (chk_build.get("stderr") or chk_build.get("stdout") or "")[-2000:].strip()
                    if err:
                        p(f"\033[31m{'─'*60}\033[0m")
                        p(f"\033[31m  BUILD ERROR\033[0m")
                        p(f"\033[31m{'─'*60}\033[0m")
                        p(err)
                        p(f"\033[31m{'─'*60}\033[0m")
                    feedback = (
                        "Harness verification FAILED after your IMPLEMENTATION COMPLETE claim.\n\n"
                        f"Build: FAIL\n{err}\n\n"
                        "Fix the compilation errors and try again. "
                        f"Do NOT declare {COMPLETION_SIGNAL} until all criteria pass."
                    )
                    messages.append({"role": "user", "content": feedback})
                    p("  [FEEDBACK] Build falhou — continuando loop.")
                    continue

                chk_tests = m.eval_tests(self.impl_dir)
                p(f"  Tests     : {chk_tests['tests_passed']}/{chk_tests['tests_total']} "
                  f"({'PASS' if chk_tests['tests_pass'] else 'FAIL'}) | "
                  f"Coverage: {chk_tests['coverage_line_pct']}% "
                  f"({'OK' if chk_tests['coverage_ok'] else 'ABAIXO 80%'})")
                if not chk_tests.get("tests_pass", True):
                    test_err = (chk_tests.get("stderr") or chk_tests.get("stdout") or "")[-2000:].strip()
                    if test_err:
                        p(f"\033[33m{'─'*60}\033[0m")
                        p(f"\033[33m  TEST OUTPUT\033[0m")
                        p(f"\033[33m{'─'*60}\033[0m")
                        p(test_err)
                        p(f"\033[33m{'─'*60}\033[0m")

                e2e_attempts += 1
                chk_e2e = m.eval_e2e(self.impl_dir)
                p(f"  E2E       : {chk_e2e['passed']}/12  (tentativa E2E #{e2e_attempts})")

                all_ok = (
                    chk_tests.get("tests_pass", False)
                    and chk_tests.get("coverage_ok", False)
                    and chk_e2e.get("all_passed", False)
                )

                if all_ok:
                    p(f"\n[OK] Todos os criterios atendidos!")
                    _cached_build = chk_build
                    _cached_tests = chk_tests
                    _cached_e2e   = chk_e2e
                    convergence_reason = "success"
                    break

                # Construir feedback detalhado com o que faltou
                issues = []
                if not chk_tests.get("tests_pass", False):
                    e2e_fail_streak = 0
                    issues.append(
                        f"Unit tests: {chk_tests['tests_passed']}/{chk_tests['tests_total']} passed "
                        f"({chk_tests['tests_failed']} failing). Fix the failing tests."
                    )
                if not chk_tests.get("coverage_ok", False):
                    e2e_fail_streak = 0
                    issues.append(
                        f"Coverage: {chk_tests['coverage_line_pct']}% — need ≥80%. "
                        "Add more test cases to cover uncovered code paths."
                    )
                if not chk_e2e.get("all_passed", False):
                    e2e_fail_streak += 1
                    fails = "\n".join(f"  - {f}" for f in chk_e2e.get("failures", []))
                    issues.append(
                        f"E2E scenarios: {chk_e2e['passed']}/12 passed "
                        f"(E2E falhou {e2e_fail_streak}x consecutivas). Failing:\n{fails}"
                    )

                feedback = (
                    "Harness verification FAILED after your IMPLEMENTATION COMPLETE claim.\n\n"
                    + "\n\n".join(issues)
                    + f"\n\nFix all issues above, then declare {COMPLETION_SIGNAL} again."
                )
                messages.append({"role": "user", "content": feedback})
                p(f"  [FEEDBACK] {len(issues)} criterio(s) nao atendido(s) — continuando loop.")
                continue

            if not tool_calls and choice.finish_reason in ("stop", "end_turn"):
                p(f"\n[INFO] LLM parou sem usar tools (finish_reason={choice.finish_reason}).")
                convergence_reason = "gave_up"
                break

            for call in tool_calls:
                total_calls += 1
                fn_name = call.function.name
                try:
                    fn_args = json.loads(call.function.arguments)
                except json.JSONDecodeError:
                    fn_args = {}

                p(f"  [{total_calls:3d}] {fn_name}", end="")
                if fn_name == "run_command":
                    cwd = fn_args.get("cwd", "")
                    cwd_str = f" ({cwd})" if cwd else ""
                    p(f"  ${cwd_str} {fn_args.get('command','')[:80]}")
                elif fn_name == "write_file":
                    p(f"  >> {fn_args.get('path','')}")
                elif fn_name == "read_file":
                    p(f"  << {fn_args.get('path','')}")
                else:
                    p()

                result = self.executor.dispatch(fn_name, fn_args)

                # O streaming em _run_streaming já imprime tudo em tempo real.
                # Apenas marca o resultado final com ✓ ou ✗ para referência rápida.
                if fn_name == "run_command":
                    ec = result.get("exit_code", 0)
                    mark = "\033[32m✓\033[0m" if ec == 0 else f"\033[31m✗ (exit {ec})\033[0m"
                    p(f"    {mark}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result, ensure_ascii=False),
                })

            # Verificar limites de falha por fase
            if self.executor.build_failures >= self.cfg.max_build_failures:
                p(f"\n[AVISO] Limite de {self.cfg.max_build_failures} falhas de build atingido.")
                convergence_reason = "max_build_failures"
                break
            if self.executor.test_failures >= self.cfg.max_test_failures:
                p(f"\n[AVISO] Limite de {self.cfg.max_test_failures} falhas de teste atingido.")
                convergence_reason = "max_test_failures"
                break


        # ------------------------------------------------------------------
        # Avaliação final — usa cache se já verificado no loop
        # ------------------------------------------------------------------
        p("\n[EVAL] Avaliando resultado final...")

        if _cached_build is not None:
            build = _cached_build
            tests = _cached_tests
            e2e   = _cached_e2e
            p(f"  (usando resultados da verificacao in-loop)")
        else:
            p("  mvn compile...")
            build = m.eval_build(self.impl_dir)
            p(f"  Build: {'OK' if build['success'] else 'FAIL'}")

            if build["success"]:
                p("  mvn test + JaCoCo...")
                tests = m.eval_tests(self.impl_dir)
                p(f"  Tests: {tests['tests_passed']}/{tests['tests_total']} | "
                  f"Coverage: {tests['coverage_line_pct']}%")

                p("  E2E 12 cenarios...")
                e2e = m.eval_e2e(self.impl_dir)
                p(f"  E2E: {e2e['passed']}/12")
            else:
                tests = {"tests_pass": False, "tests_total": 0, "tests_passed": 0,
                         "tests_failed": 0, "coverage_line_pct": 0.0,
                         "coverage_branch_pct": 0.0, "coverage_ok": False,
                         "build_success": False}
                e2e = {"app_started": False, "passed": 0, "failed": 12,
                       "all_passed": False, "failures": ["Build failed"]}

        p("  Verificacao arquitetural...")
        arch = m.eval_architecture(self.impl_dir, self.arch_name, self.pkg_path)
        p(f"  Arch: {'OK' if arch['ok'] else str(len(arch['violations'])) + ' violacoes'}")

        agent_behavior = self.executor.agent_behavior_summary(
            convergence_reason,
            completion_attempts=completion_attempts,
            e2e_attempts=e2e_attempts,
            e2e_fail_streak=e2e_fail_streak,
        )

        out_path = m.save_result(
            results_dir=self.results_dir,
            model_name=self.model_name,
            arch_name=self.arch_name,
            impl_dir=self.impl_dir,
            started_at=started_at,
            build=build,
            tests=tests,
            e2e=e2e,
            arch=arch,
            agent_behavior=agent_behavior,
            pkg_path=self.pkg_path,
        )

        self._print_summary(build, tests, e2e, arch, agent_behavior)
        p(f"\n[JSON] {out_path}")

        results = {
            "model":    self.model_name,
            "arch":     self.arch_name,
            "build":    build,
            "tests":    tests,
            "e2e":      e2e,
            "arch_check": arch,
            "agent":    agent_behavior,
            "json_path": str(out_path),
        }
        return out_path, results

    # ------------------------------------------------------------------
    # System prompt — descreve apenas o ambiente e as tools
    # ------------------------------------------------------------------

    def _build_system_prompt(self) -> str:
        env_desc = terminal_env_description(self.terminal)
        return f"""You are an expert software engineer executing a coding benchmark.

## Execution Environment (READ CAREFULLY)
{env_desc}

## Working Directory
{self.impl_dir}
All relative paths in write_file and read_file start from this directory.
The Maven project (pom.xml) is pre-configured — do NOT modify it.

## Tools
You have exactly 3 tools:

**run_command(command)** — execute a shell command in the working directory.
Returns: stdout, stderr, exit_code.
Examples: "mvn compile", "mvn test", "dir src\\main\\java" (Windows) or "ls src/main/java" (Unix)

**write_file(path, content)** — create or overwrite a file.
- path: relative to working directory (e.g. "src/main/java/com/benchmark/taskmanager/model/Task.java")
- content: COMPLETE file content, never use placeholders or "// ... rest of file"
- Parent directories are created automatically.
- Always use forward slashes in paths passed to write_file, even on Windows.

**read_file(path)** — read an existing file.
Returns its content as a string.

## Rules
- Never ask questions — act immediately.
- Never use placeholders in code — always write complete, compilable files.
- When all tasks in the guide are done, say exactly: {COMPLETION_SIGNAL}

## How to handle build failures (CRITICAL)
When `mvn compile` returns exit_code != 0, the failure is ALWAYS a Java code error.
It is NEVER a shell, WSL, environment, OS, or Maven installation issue.
The harness guarantees that Maven is installed and configured correctly.
The correct response to a build failure is:
1. Read `stderr` carefully — find the exact file name and line number of the error.
2. Call `write_file` to fix ONLY that file with the correct, complete Java code.
3. Run `mvn compile` again to verify the fix.
NEVER try: `cmd /c mvn`, `wsl mvn`, alternative Maven paths, or any shell variations.
NEVER diagnose "WSL issue", "environment problem", or "shell not found" — just fix the Java code.

## Forbidden commands
NEVER run `mvn spring-boot:run` or `mvn spring-boot:start` — they start a server that runs
forever and will hang the benchmark. The harness handles server startup for E2E testing.
Your job is compile + unit tests only. Use only: `mvn compile`, `mvn test`, `mvn clean`, `ls`/`dir`.
"""

    # ------------------------------------------------------------------
    # Carregar e renderizar o guia .md
    # ------------------------------------------------------------------

    def _guide_path(self) -> Path:
        guides_dir = Path(self.cfg.guides_dir)
        return guides_dir / f"benchmark-arch-{self.arch_name}.md"

    def _load_guide(self) -> str:
        guide_file = self._guide_path()
        if not guide_file.exists():
            raise FileNotFoundError(
                f"Guia não encontrado: {guide_file}\n"
                f"Crie o arquivo para a arquitetura '{self.arch_name}'."
            )
        raw = guide_file.read_text(encoding="utf-8")

        # Preencher variáveis $nome com Template (safe_substitute ignora $vars ausentes)
        task_def = ""
        task_def_path = Path(self.cfg.task_definition_path)
        if task_def_path.exists():
            task_def = task_def_path.read_text(encoding="utf-8", errors="replace")

        variables = {
            "arch_name":          self.arch_name,
            "src_base":           self.src_base,
            "test_base":          self.test_base,
            "impl_dir":           str(self.impl_dir),
            "tech_stack":         self.cfg.tech_stack,
            "base_package":       self.cfg.base_package,
            "test_framework":     self.cfg.test_framework,
            "storage_desc":       self.cfg.storage_desc,
            "coverage_target":    str(self.cfg.coverage_target),
            "endpoints_desc":     self.cfg.endpoints_desc,
            "validation_rules":   self.cfg.validation_rules,
            "build_fix_rules":    self.cfg.build_fix_rules,
            "partial_update_rules": self.cfg.partial_update_rules,
            "e2e_rules":          self.cfg.e2e_rules,
            "prod_files":         self.cfg.arch_prod_files.get(self.arch_name, ""),
            "test_file":          self.cfg.arch_test_file.get(self.arch_name, ""),
            "task_definition":    task_def,
            "completion_signal":  COMPLETION_SIGNAL,
        }
        return Template(raw).safe_substitute(variables)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _ensure_impl_dir(self):
        """Garante que impl_dir existe com pom.xml. Se não existir, copia de um template."""
        if (self.impl_dir / "pom.xml").exists():
            return
        # Usar pom.xml de um modelo local como template
        impl_root = Path(self.cfg.exp_dir) / "implementations"
        template_pom = None
        for candidate in impl_root.rglob("pom.xml"):
            template_pom = candidate
            break
        if template_pom is None:
            raise FileNotFoundError(
                f"Nenhum pom.xml template encontrado em {impl_root}. "
                "Verifique se implementations/ foi inicializado corretamente."
            )
        self.impl_dir.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy2(str(template_pom), str(self.impl_dir / "pom.xml"))

    def _clean_java_files(self):
        for java_file in self.impl_dir.rglob("*.java"):
            try:
                java_file.unlink()
            except Exception:
                pass
        target = self.impl_dir / "target"
        if target.exists():
            import shutil
            try:
                shutil.rmtree(str(target))
            except Exception:
                pass

    def _print_summary(self, build, tests, e2e, arch, agent):
        print(f"""
{'='*60}
  RESULTADO FINAL
{'='*60}
  [F1] Build       : {'PASS' if build['success'] else 'FAIL'}
  [F2] Tests       : {'PASS' if tests.get('tests_pass') else 'FAIL'} ({tests.get('tests_passed',0)}/{tests.get('tests_total',0)})
  [F2] Coverage    : {tests.get('coverage_line_pct',0.0)}% ({'OK' if tests.get('coverage_ok') else 'ABAIXO 80%'})
  [F3] E2E         : {e2e.get('passed',0)}/12 {'PASS' if e2e.get('all_passed') else 'FAIL'}
  [F4] Arch        : {'OK' if arch.get('ok') else str(len(arch.get('violations',[]))) + ' violacoes'}
  [AG] Tool calls  : {agent['total_tool_calls']} ({agent['convergence_reason']})
  [AG] Breakdown   : {agent['tool_breakdown']}
  [AG] Conclusoes  : {agent['completion_attempts']}x declaradas | E2E verificado {agent['e2e_attempts']}x | streak final={agent['e2e_fail_streak_at_end']}
{'='*60}""", flush=True)
