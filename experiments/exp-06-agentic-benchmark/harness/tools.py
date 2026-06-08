"""ToolExecutor — implementa os 3 tools que o LLM pode chamar."""

import os
import subprocess
import threading
from collections import defaultdict
from pathlib import Path

from .terminal import shell_args

# Comandos que iniciam servidores e rodam indefinidamente — bloqueados no tool
_BLOCKED_COMMANDS = ("spring-boot:run", "spring-boot:start")
# Timeout padrão para comandos normais (mvn compile, mvn test, ls, etc.)
_DEFAULT_TIMEOUT = 300


class ToolExecutor:
    def __init__(self, impl_dir: str, terminal: str):
        self.impl_dir = Path(impl_dir)
        self.terminal = terminal

        # Métricas de uso
        self.tool_calls: list[dict] = []          # histórico completo [{tool, ...}]
        self.call_count: dict[str, int] = defaultdict(int)
        self.command_count: dict[str, int] = defaultdict(int)

        # Marcos para agent_behavior
        self.first_build_success_at: int | None = None
        self.first_test_success_at: int | None = None
        self._total_calls = 0

        # Contadores de falha para limites por fase
        self.build_failures = 0
        self.test_failures = 0

        # Output da última falha (para análise post-mortem)
        self.last_build_failure_output: str | None = None
        self.last_test_failure_output: str | None = None

    # ------------------------------------------------------------------
    # TOOL: run_command
    # ------------------------------------------------------------------

    def run_command(self, command: str, cwd: str | None = None) -> dict:
        self._total_calls += 1
        call_n = self._total_calls
        self.call_count["run_command"] += 1

        cmd_lower = command.strip().lower()

        # Bloquear comandos que iniciam servidores — causam hang infinito
        for blocked in _BLOCKED_COMMANDS:
            if blocked in cmd_lower:
                msg = (
                    f"BLOCKED: '{blocked}' starts a long-running server and is not allowed "
                    "during the benchmark. The harness starts the server automatically for "
                    "E2E testing. Focus on compiling and running unit tests only."
                )
                print(f"    \033[31m[BLOCKED]\033[0m {command}", flush=True)
                self.tool_calls.append({"call": call_n, "tool": "run_command", "command": command})
                return {"stdout": "", "stderr": msg, "exit_code": -1}

        # Categorizar para command_breakdown
        if cmd_lower.startswith("mvn compile") or cmd_lower.startswith("mvn clean compile"):
            self.command_count["mvn compile"] += 1
        elif cmd_lower.startswith("mvn test"):
            self.command_count["mvn test"] += 1
        elif cmd_lower.startswith("mvn"):
            self.command_count["mvn other"] += 1
        else:
            self.command_count["other"] += 1

        # cwd override: relativo ao impl_dir base se não for absoluto
        if cwd:
            effective_cwd = Path(cwd) if Path(cwd).is_absolute() else self.impl_dir / cwd
        else:
            effective_cwd = self.impl_dir

        args, use_shell = shell_args(command, self.terminal)
        stdout, stderr, exit_code = self._run_streaming(args, use_shell, effective_cwd, _DEFAULT_TIMEOUT)

        # Detectar marcos e contar falhas por fase
        combined = stdout + stderr
        is_compile = cmd_lower.startswith("mvn compile") or cmd_lower.startswith("mvn clean compile")
        is_test    = cmd_lower.startswith("mvn test")

        if is_compile:
            if exit_code == 0 and "BUILD SUCCESS" in combined:
                if self.first_build_success_at is None:
                    self.first_build_success_at = call_n
            else:
                self.build_failures += 1
                self.last_build_failure_output = combined[-3000:]

        if is_test:
            if exit_code == 0 and "BUILD SUCCESS" in combined and "Failures: 0" in combined and "Errors: 0" in combined:
                if self.first_test_success_at is None:
                    self.first_test_success_at = call_n
            else:
                self.test_failures += 1
                self.last_test_failure_output = combined[-3000:]

        self.tool_calls.append({"call": call_n, "tool": "run_command", "command": command})
        return {"stdout": stdout[-3000:], "stderr": stderr[-3000:], "exit_code": exit_code}

    def _run_streaming(
        self, args: str | list, use_shell: bool, cwd: Path, timeout: int
    ) -> tuple[str, str, int]:
        """Executa um subprocesso com streaming em tempo real para o terminal.

        Imprime cada linha com prefixo '  |' conforme chega, e acumula o
        output completo para retornar ao LLM ao final.
        """
        stdout_buf: list[str] = []
        stderr_buf: list[str] = []

        try:
            proc = subprocess.Popen(
                args,
                shell=use_shell,
                cwd=str(cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                errors="replace",
            )
        except Exception as exc:
            return "", f"ERROR starting process: {exc}", -1

        def _drain(stream, buf: list[str]):
            try:
                for line in stream:
                    buf.append(line)
                    print(f"    \033[90m|\033[0m {line}", end="", flush=True)
            except Exception:
                pass

        t_out = threading.Thread(target=_drain, args=(proc.stdout, stdout_buf), daemon=True)
        t_err = threading.Thread(target=_drain, args=(proc.stderr, stderr_buf), daemon=True)
        t_out.start()
        t_err.start()

        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            stderr_buf.append(f"\nTIMEOUT: command exceeded {timeout}s\n")
            print(f"    \033[31m[TIMEOUT {timeout}s]\033[0m", flush=True)

        t_out.join(timeout=5)
        t_err.join(timeout=5)

        return "".join(stdout_buf), "".join(stderr_buf), proc.returncode

    # ------------------------------------------------------------------
    # TOOL: write_file
    # ------------------------------------------------------------------

    def write_file(self, path: str, content: str) -> dict:
        self._total_calls += 1
        self.call_count["write_file"] += 1
        self.tool_calls.append({"call": self._total_calls, "tool": "write_file", "path": path})

        # Normalizar separadores e resolver caminho relativo ao impl_dir
        clean_path = path.replace("\\", "/").lstrip("/")
        target = self.impl_dir / clean_path

        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return {"written": str(target), "bytes": len(content.encode("utf-8"))}
        except Exception as exc:
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    # TOOL: read_file
    # ------------------------------------------------------------------

    def read_file(self, path: str) -> dict:
        self._total_calls += 1
        self.call_count["read_file"] += 1
        self.tool_calls.append({"call": self._total_calls, "tool": "read_file", "path": path})

        clean_path = path.replace("\\", "/").lstrip("/")
        target = self.impl_dir / clean_path

        try:
            content = target.read_text(encoding="utf-8", errors="replace")
            return {"content": content, "path": str(target)}
        except FileNotFoundError:
            return {"error": f"File not found: {target}"}
        except Exception as exc:
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    # Dispatch por nome
    # ------------------------------------------------------------------

    def dispatch(self, tool_name: str, arguments: dict) -> dict:
        if tool_name == "run_command":
            return self.run_command(arguments.get("command", ""), arguments.get("cwd"))
        if tool_name == "write_file":
            return self.write_file(arguments.get("path", ""), arguments.get("content", ""))
        if tool_name == "read_file":
            return self.read_file(arguments.get("path", ""))
        return {"error": f"Unknown tool: {tool_name}"}

    # ------------------------------------------------------------------
    # Resumo de métricas
    # ------------------------------------------------------------------

    def agent_behavior_summary(
        self,
        convergence_reason: str,
        completion_attempts: int = 0,
        e2e_attempts: int = 0,
        e2e_fail_streak: int = 0,
    ) -> dict:
        return {
            "total_tool_calls": self._total_calls,
            "tool_breakdown": dict(self.call_count),
            "command_breakdown": dict(self.command_count),
            "convergence_reason": convergence_reason,
            "completion_attempts": completion_attempts,
            "e2e_attempts": e2e_attempts,
            "e2e_fail_streak_at_end": e2e_fail_streak,
            "build_failures": self.build_failures,
            "test_failures": self.test_failures,
            "first_build_success_at_call": self.first_build_success_at,
            "first_test_success_at_call": self.first_test_success_at,
            "last_build_failure_output": self.last_build_failure_output,
            "last_test_failure_output": self.last_test_failure_output,
        }


# ------------------------------------------------------------------
# Schemas dos tools para a API OpenRouter (formato OpenAI function calling)
# ------------------------------------------------------------------

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": (
                "Execute a shell command in the implementation directory. "
                "Use to compile (mvn compile), run tests (mvn test), list files, etc. "
                "Returns stdout, stderr, and exit_code."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute (e.g. 'mvn compile', 'ls src/main')",
                    },
                    "cwd": {
                        "type": "string",
                        "description": "Optional working directory, relative to base dir (e.g. 'implementations/deepseek-v3/mvc'). Omit to use the default.",
                    },
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Create or overwrite a file. Provide the relative path from the "
                "implementation directory root and the complete file content. "
                "Parent directories are created automatically."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative file path (e.g. 'src/main/java/com/benchmark/taskmanager/controller/TaskController.java')",
                    },
                    "content": {
                        "type": "string",
                        "description": "Complete file content (do NOT use placeholders)",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read an existing file. Useful for inspecting pom.xml, "
                "existing Java files, or checking what has been written."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative file path from implementation directory root",
                    }
                },
                "required": ["path"],
            },
        },
    },
]
