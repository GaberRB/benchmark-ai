"""Avaliação final independente do LLM + escrita do JSON de resultado."""

import csv
import json
import os
import re
import subprocess
import threading
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import requests


BASE_URL = "http://localhost:8080"
APP_PORT = 8080
APP_STARTUP_TIMEOUT = 90  # segundos

# No Windows, mvn é mvn.cmd — subprocess precisa de shell=True para encontrá-lo
_SHELL = os.name == "nt"
_MVN   = "mvn"


# ======================================================================
# BUILD
# ======================================================================

def eval_build(impl_dir: Path) -> dict:
    result = subprocess.run(
        f"{_MVN} compile -q" if _SHELL else [_MVN, "compile", "-q"],
        shell=_SHELL,
        cwd=str(impl_dir),
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    success = result.returncode == 0 and "BUILD FAILURE" not in (result.stdout + result.stderr)
    return {
        "success": success,
        "stdout": result.stdout[-3000:],
        "stderr": result.stderr[-3000:],
    }


# ======================================================================
# TEST + COVERAGE (JaCoCo)
# ======================================================================

def eval_tests(impl_dir: Path) -> dict:
    result = subprocess.run(
        f"{_MVN} test" if _SHELL else [_MVN, "test"],
        shell=_SHELL,
        cwd=str(impl_dir),
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    combined = result.stdout + result.stderr

    # Parse via XMLs do Surefire (mais confiável que parsear stdout no Windows)
    total, failures, errors = _parse_surefire_xml(impl_dir)
    if total == 0:
        # Fallback: regex no stdout (formato: "Tests run: X, Failures: Y, Errors: Z")
        summary_match = re.findall(
            r"Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+)", combined
        )
        if summary_match:
            last = summary_match[-1]
            total, failures, errors = int(last[0]), int(last[1]), int(last[2])

    passed = max(0, total - failures - errors)
    tests_pass = failures == 0 and errors == 0 and total > 0

    build_success = result.returncode == 0 or "BUILD SUCCESS" in combined

    line_pct, branch_pct = _read_jacoco(impl_dir)
    coverage_ok = line_pct >= 80.0

    return {
        "build_success": build_success,
        "tests_pass": tests_pass,
        "tests_total": total,
        "tests_passed": passed,
        "tests_failed": failures + errors,
        "coverage_line_pct": line_pct,
        "coverage_branch_pct": branch_pct,
        "coverage_ok": coverage_ok,
        "stdout": result.stdout[-3000:],
        "stderr": result.stderr[-3000:],
    }


def _parse_surefire_xml(impl_dir: Path) -> tuple[int, int, int]:
    """Lê os XMLs gerados pelo Surefire em target/surefire-reports/TEST-*.xml.
    Retorna (total, failures, errors) somados de todos os arquivos."""
    reports_dir = impl_dir / "target" / "surefire-reports"
    if not reports_dir.exists():
        return 0, 0, 0
    total = failures = errors = 0
    for xml_file in reports_dir.glob("TEST-*.xml"):
        try:
            root = ET.parse(xml_file).getroot()
            total    += int(root.get("tests",    0))
            failures += int(root.get("failures", 0))
            errors   += int(root.get("errors",   0))
        except Exception:
            pass
    return total, failures, errors


def _read_jacoco(impl_dir: Path) -> tuple[float, float]:
    csv_path = impl_dir / "target" / "site" / "jacoco" / "jacoco.csv"
    if not csv_path.exists():
        return 0.0, 0.0
    try:
        line_c = line_m = branch_c = branch_m = 0
        with csv_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                line_c   += int(row.get("LINE_COVERED",   0))
                line_m   += int(row.get("LINE_MISSED",    0))
                branch_c += int(row.get("BRANCH_COVERED", 0))
                branch_m += int(row.get("BRANCH_MISSED",  0))
        line_pct   = line_c   / (line_c + line_m)   * 100 if (line_c + line_m)   > 0 else 0.0
        branch_pct = branch_c / (branch_c + branch_m) * 100 if (branch_c + branch_m) > 0 else 0.0
        return round(line_pct, 1), round(branch_pct, 1)
    except Exception:
        return 0.0, 0.0


# ======================================================================
# E2E (12 cenários HTTP)
# ======================================================================

def eval_e2e(impl_dir: Path) -> dict:
    """Sobe Spring Boot, roda os 12 cenários, para o app. Retorna dict de resultados."""
    proc = _start_app(impl_dir)
    if proc is None:
        return {
            "app_started": False,
            "passed": 0,
            "failed": 12,
            "all_passed": False,
            "failures": ["App failed to start"],
        }

    try:
        results = _run_e2e_scenarios()
    finally:
        _stop_app(proc)

    passed = sum(1 for r in results if r["pass"])
    failed = sum(1 for r in results if not r["pass"])
    failures = [
        f"E2E-{r['id']}: {r['desc']}  expected={r['want']}  got={r['got']}"
        + (f"  body={r['body']}" if r.get("body") else "")
        for r in results if not r["pass"]
    ]
    return {
        "app_started": True,
        "passed": passed,
        "failed": failed,
        "all_passed": passed == 12,
        "failures": failures,
        "results": results,   # lista completa para print detalhado no harness
    }


def _start_app(impl_dir: Path):
    """Inicia Spring Boot e aguarda até estar pronto. Retorna Popen ou None."""
    proc = subprocess.Popen(
        f"{_MVN} spring-boot:run" if _SHELL else [_MVN, "spring-boot:run"],
        shell=_SHELL,
        cwd=str(impl_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        errors="replace",
    )

    started = threading.Event()
    output_lines: list[str] = []

    def _tail():
        for line in proc.stdout:
            output_lines.append(line)
            if "Started " in line and "seconds" in line:
                started.set()

    threading.Thread(target=_tail, daemon=True).start()

    if not started.wait(timeout=APP_STARTUP_TIMEOUT):
        # Fallback: tentar conectar de qualquer forma
        deadline = time.time() + 15
        while time.time() < deadline:
            try:
                requests.get(f"{BASE_URL}/tasks", timeout=2)
                return proc
            except Exception:
                time.sleep(2)
        proc.terminate()
        return None

    time.sleep(1)  # buffer para o app ficar 100% pronto
    return proc


def _stop_app(proc):
    try:
        proc.terminate()
        proc.wait(timeout=15)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def _http(method: str, url: str, body=None) -> tuple[int, dict | None]:
    """Faz requisição HTTP e retorna (status_code, body_dict). Em erro: (-1, None)."""
    try:
        resp = getattr(requests, method.lower())(
            url,
            json=body,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        try:
            body_json = resp.json()
        except Exception:
            body_json = None
        return resp.status_code, body_json
    except Exception:
        return -1, None


def _run_e2e_scenarios() -> list[dict]:
    results = []
    task_id = "unknown"

    def chk(id: str, desc: str, got: int, want: int, body=None) -> dict:
        body_str = ""
        if body is not None:
            try:
                import json as _json
                body_str = _json.dumps(body, ensure_ascii=False)[:300]
            except Exception:
                body_str = str(body)[:300]
        return {"id": id, "desc": desc, "got": got, "want": want,
                "pass": got == want, "body": body_str}

    # 01 — GET /tasks vazia
    code, body = _http("GET", f"{BASE_URL}/tasks")
    results.append(chk("01", "GET /tasks vazia", code, 200, body))

    # 02 — POST /tasks com título → 201
    code, body = _http("POST", f"{BASE_URL}/tasks", {"title": "Test Task", "description": "Desc"})
    results.append(chk("02", "POST /tasks 201", code, 201, body))
    if body and isinstance(body, dict):
        task_id = body.get("id", "unknown")

    # 03 — POST sem body → 400
    code, body = _http("POST", f"{BASE_URL}/tasks", {})
    results.append(chk("03", "POST sem title 400", code, 400, body))

    # 04 — POST title vazio → 400
    code, body = _http("POST", f"{BASE_URL}/tasks", {"title": ""})
    results.append(chk("04", "POST title='' 400", code, 400, body))

    # 05 — GET /tasks lista (deve conter a tarefa criada)
    code, body = _http("GET", f"{BASE_URL}/tasks")
    results.append(chk("05", "GET /tasks lista", code, 200, body))

    # 06 — GET /tasks/{id} existente → 200
    code, body = _http("GET", f"{BASE_URL}/tasks/{task_id}")
    results.append(chk("06", "GET /tasks/{id} existente", code, 200, body))

    # 07 — GET /tasks/{id} inválido → 404
    code, body = _http("GET", f"{BASE_URL}/tasks/id-invalido-xyz")
    results.append(chk("07", "GET invalido 404", code, 404, body))

    # 08 — PUT /tasks/{id} → 200
    code, body = _http("PUT", f"{BASE_URL}/tasks/{task_id}", {"title": "Updated", "completed": True})
    results.append(chk("08", "PUT /tasks/{id} existente", code, 200, body))

    # 09 — PUT /tasks/{id} inválido → 404
    code, body = _http("PUT", f"{BASE_URL}/tasks/id-invalido-xyz", {"title": "X"})
    results.append(chk("09", "PUT invalido 404", code, 404, body))

    # 10 — DELETE /tasks/{id} → 204
    code, body = _http("DELETE", f"{BASE_URL}/tasks/{task_id}")
    results.append(chk("10", "DELETE /tasks/{id} existente", code, 204, body))

    # 11 — DELETE inválido → 404
    code, body = _http("DELETE", f"{BASE_URL}/tasks/id-invalido-xyz")
    results.append(chk("11", "DELETE invalido 404", code, 404, body))

    # 12 — GET após DELETE → 404
    code, body = _http("GET", f"{BASE_URL}/tasks/{task_id}")
    results.append(chk("12", "GET apos DELETE 404", code, 404, body))

    return results


# ======================================================================
# ARQUITETURA
# ======================================================================

def eval_architecture(impl_dir: Path, arch_name: str, pkg_path: str) -> dict:
    src = impl_dir / "src" / "main" / "java" / pkg_path
    violations = _check_arch(src, arch_name, pkg_path.replace("/", "."))
    supported = arch_name in ("mvc", "clean-architecture", "hexagonal", "ddd", "cqrs")
    return {
        "supported": supported,
        "violations": violations,
        "ok": len(violations) == 0,
    }


def _check_arch(src: Path, arch: str, base_pkg: str) -> list[str]:
    viols = []

    def _grep(directory: Path, pattern: str) -> list[Path]:
        if not directory.exists():
            return []
        return list(directory.rglob("*.java"))

    def _contains(f: Path, pattern: str) -> bool:
        try:
            return bool(re.search(pattern, f.read_text(encoding="utf-8", errors="replace")))
        except Exception:
            return False

    if arch == "mvc":
        for f in (src / "controller").rglob("*.java") if (src / "controller").exists() else []:
            if _contains(f, rf"import {re.escape(base_pkg)}\.repository\."):
                viols.append(f"MVC: '{f.name}' importa repository diretamente")
        for f in (src / "service").rglob("*.java") if (src / "service").exists() else []:
            if _contains(f, rf"import {re.escape(base_pkg)}\.controller\."):
                viols.append(f"MVC: '{f.name}' service importa controller")

    elif arch == "clean-architecture":
        for f in (src / "domain").rglob("*.java") if (src / "domain").exists() else []:
            if _contains(f, r"import org\.springframework"):
                viols.append(f"Clean Arch: domain '{f.name}' importa Spring")
            if _contains(f, rf"import {re.escape(base_pkg)}\.infrastructure"):
                viols.append(f"Clean Arch: domain '{f.name}' importa infrastructure")

    elif arch == "hexagonal":
        for sub in ("domain", "core"):
            d = src / sub
            if not d.exists():
                continue
            for f in d.rglob("*.java"):
                if _contains(f, r"import org\.springframework"):
                    viols.append(f"Hexagonal: '{f.name}' no núcleo importa Spring")
                if _contains(f, rf"import {re.escape(base_pkg)}\.adapter"):
                    viols.append(f"Hexagonal: '{f.name}' no núcleo importa adapter")

    elif arch == "ddd":
        for f in (src / "domain").rglob("*.java") if (src / "domain").exists() else []:
            if _contains(f, r"import org\.springframework\.web"):
                viols.append(f"DDD: domain '{f.name}' importa spring.web")
            if _contains(f, rf"import {re.escape(base_pkg)}\.infrastructure"):
                viols.append(f"DDD: domain '{f.name}' importa infrastructure")

    elif arch == "cqrs":
        for f in (src / "command").rglob("*.java") if (src / "command").exists() else []:
            if _contains(f, rf"import {re.escape(base_pkg)}\.query\."):
                viols.append(f"CQRS: '{f.name}' em command importa query")
        for f in (src / "query").rglob("*.java") if (src / "query").exists() else []:
            if _contains(f, rf"import {re.escape(base_pkg)}\.command\."):
                viols.append(f"CQRS: '{f.name}' em query importa command")

    return viols


# ======================================================================
# LOC
# ======================================================================

def count_loc(directory: Path) -> int:
    if not directory.exists():
        return 0
    total = 0
    for f in directory.rglob("*.java"):
        try:
            for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
                stripped = line.strip()
                if stripped and not stripped.startswith("//"):
                    total += 1
        except Exception:
            pass
    return total


# ======================================================================
# SALVAR JSON
# ======================================================================

def save_result(
    results_dir: Path,
    model_name: str,
    arch_name: str,
    impl_dir: Path,
    started_at: str,
    build: dict,
    tests: dict,
    e2e: dict,
    arch: dict,
    agent_behavior: dict,
    pkg_path: str,
) -> Path:
    ended_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_model = model_name.replace("/", "--").replace(":", "--")
    out_path = results_dir / f"exp06_{safe_model}_{arch_name}_{ts}.json"

    src_dir = impl_dir / "src" / "main" / "java" / pkg_path
    test_dir = impl_dir / "src" / "test" / "java" / pkg_path

    all_criteria = (
        build.get("success", False)
        and tests.get("tests_pass", False)
        and tests.get("coverage_ok", False)
        and e2e.get("all_passed", False)
        and arch.get("ok", True)
    )

    report = {
        "experiment": "exp-06-agentic-benchmark",
        "meta": {
            "provider": "openrouter",
            "model": model_name,
            "architecture": arch_name,
            "collected_at_utc": ended_at,
            "impl_dir": str(impl_dir),
        },
        "speed": {
            "session_start_utc": started_at,
            "session_end_utc": ended_at,
        },
        "code_quality": {
            "lines_of_code": count_loc(src_dir),
            "test_lines_of_code": count_loc(test_dir),
            "test_coverage_line_pct": tests.get("coverage_line_pct", 0.0),
            "test_coverage_branch_pct": tests.get("coverage_branch_pct", 0.0),
            "coverage_meets_80pct": tests.get("coverage_ok", False),
        },
        "build": {
            "success": build.get("success", False),
        },
        "unit_tests": {
            "pass": tests.get("tests_pass", False),
            "total": tests.get("tests_total", 0),
            "passed": tests.get("tests_passed", 0),
            "failed": tests.get("tests_failed", 0),
        },
        "e2e": {
            "total_scenarios": 12,
            "passed": e2e.get("passed", 0),
            "failed": e2e.get("failed", 12),
            "all_passed": e2e.get("all_passed", False),
            "app_started": e2e.get("app_started", False),
            "failure_details": e2e.get("failures", []),
        },
        "architecture": {
            "violations": arch.get("violations", []),
            "violations_count": len(arch.get("violations", [])),
            "ok": arch.get("ok", True),
            "auto_check_supported": arch.get("supported", False),
        },
        "agent_behavior": agent_behavior,
        "criteria_met": {
            "build_success": build.get("success", False),
            "tests_pass": tests.get("tests_pass", False),
            "coverage_80pct": tests.get("coverage_ok", False),
            "e2e_all_pass": e2e.get("all_passed", False),
            "arch_no_violations": arch.get("ok", True),
            "all_criteria_met": all_criteria,
        },
    }

    results_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path
