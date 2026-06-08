"""
Verificação independente pós-Aider: build, testes, E2E, LOC.
Pode ser usado como módulo (importado pelo main.py) ou como CLI para re-rodar.

CLI:
    python tools/collector.py \\
        --model deepseek-v3 \\
        --arch mvc \\
        --cost 0.23 \\
        --duration 8.5 \\
        --project-dir implementations/deepseek-v3/mvc
"""

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import threading
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import requests

E2E_SPEC = {
    "01": 'GET /tasks → 200. Lista vazia [] quando não há tarefas (nunca null)',
    "02": 'POST /tasks → 201: { "id": "uuid", "title": "...", "completed": false, ... }',
    "03": 'POST /tasks sem title → 400: { "error": "title is required" }',
    "04": 'POST /tasks title="" → 400: { "error": "title is required" }',
    "05": 'GET /tasks → 200: lista com tarefas criadas',
    "06": 'GET /tasks/{id} existente → 200: objeto da tarefa',
    "07": (
        'GET /tasks/id-invalido-xyz → 404: { "error": "Task not found" }. '
        'IDs são UUIDs — use @PathVariable String id com UUID.fromString() em try/catch, '
        'não @PathVariable UUID id (que retornaria 400).'
    ),
    "08": 'PUT /tasks/{id} → 200: tarefa atualizada. updatedAt deve ser atualizado.',
    "09": 'PUT /tasks/id-invalido-xyz → 404. Mesma regra do E2E-07.',
    "10": 'DELETE /tasks/{id} existente → 204 (sem body)',
    "11": 'DELETE /tasks/id-invalido-xyz → 404. Mesma regra do E2E-07.',
    "12": 'GET /tasks/{id} após DELETE → 404: tarefa não existe mais.',
}

BASE_URL = "http://localhost:8080"
APP_STARTUP_TIMEOUT = 90
_SHELL = os.name == "nt"
_MVN   = "mvn"


# ---------------------------------------------------------------------------
# BUILD
# ---------------------------------------------------------------------------

def eval_build(impl_dir: Path) -> dict:
    r = subprocess.run(
        f"{_MVN} compile -q" if _SHELL else [_MVN, "compile", "-q"],
        shell=_SHELL, cwd=str(impl_dir),
        capture_output=True, encoding="utf-8", errors="replace", timeout=120,
    )
    ok = r.returncode == 0 and "BUILD FAILURE" not in (r.stdout + r.stderr)
    return {"success": ok, "stdout": r.stdout[-3000:], "stderr": r.stderr[-3000:]}


# ---------------------------------------------------------------------------
# TEST + JACOCO
# ---------------------------------------------------------------------------

def eval_tests(impl_dir: Path) -> dict:
    r = subprocess.run(
        f"{_MVN} test" if _SHELL else [_MVN, "test"],
        shell=_SHELL, cwd=str(impl_dir),
        capture_output=True, encoding="utf-8", errors="replace", timeout=180,
    )
    combined = r.stdout + r.stderr
    total, failures, errors = _parse_surefire(impl_dir)
    if total == 0:
        m = re.findall(r"Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+)", combined)
        if m:
            total, failures, errors = int(m[-1][0]), int(m[-1][1]), int(m[-1][2])

    passed = max(0, total - failures - errors)
    line_pct, branch_pct = _read_jacoco(impl_dir)
    return {
        "build_success": r.returncode == 0 or "BUILD SUCCESS" in combined,
        "tests_pass": failures == 0 and errors == 0 and total > 0,
        "tests_total": total,
        "tests_passed": passed,
        "tests_failed": failures + errors,
        "coverage_line_pct": line_pct,
        "coverage_branch_pct": branch_pct,
        "coverage_ok": line_pct >= 80.0,
        "stdout": combined[-3000:],
    }


def _parse_surefire(impl_dir: Path) -> tuple:
    d = impl_dir / "target" / "surefire-reports"
    if not d.exists():
        return 0, 0, 0
    total = failures = errors = 0
    for f in d.glob("TEST-*.xml"):
        try:
            root = ET.parse(f).getroot()
            total    += int(root.get("tests",    0))
            failures += int(root.get("failures", 0))
            errors   += int(root.get("errors",   0))
        except Exception:
            pass
    return total, failures, errors


def _read_jacoco(impl_dir: Path) -> tuple:
    csv_path = impl_dir / "target" / "site" / "jacoco" / "jacoco.csv"
    if not csv_path.exists():
        return 0.0, 0.0
    try:
        lc = lm = bc = bm = 0
        with csv_path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                lc += int(row.get("LINE_COVERED",   0))
                lm += int(row.get("LINE_MISSED",    0))
                bc += int(row.get("BRANCH_COVERED", 0))
                bm += int(row.get("BRANCH_MISSED",  0))
        lp = lc / (lc + lm) * 100 if (lc + lm) > 0 else 0.0
        bp = bc / (bc + bm) * 100 if (bc + bm) > 0 else 0.0
        return round(lp, 1), round(bp, 1)
    except Exception:
        return 0.0, 0.0


# ---------------------------------------------------------------------------
# E2E (12 cenários)
# ---------------------------------------------------------------------------

def eval_e2e(impl_dir: Path) -> dict:
    proc = _start_app(impl_dir)
    if proc is None:
        return {"app_started": False, "passed": 0, "failed": 12, "all_passed": False, "failures": ["App não iniciou"]}
    try:
        results = _run_scenarios()
    finally:
        _stop_app(proc)

    passed  = sum(1 for r in results if r["pass"])
    failed  = sum(1 for r in results if not r["pass"])
    details = []
    for r in results:
        if not r["pass"]:
            line = f"E2E-{r['id']}: expected={r['want']} got={r['got']}"
            if r.get("body"):
                line += f" | body: {r['body']}"
            if r.get("spec"):
                line += f"\n  spec: {r['spec']}"
            details.append(line)
    return {
        "app_started": True,
        "passed": passed,
        "failed": failed,
        "all_passed": passed == 12,
        "failures": details,
        "results": results,
    }


def _start_app(impl_dir: Path):
    proc = subprocess.Popen(
        f"{_MVN} spring-boot:run" if _SHELL else [_MVN, "spring-boot:run"],
        shell=_SHELL, cwd=str(impl_dir),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        encoding="utf-8", errors="replace",
    )
    started = threading.Event()

    def _tail():
        for line in proc.stdout:
            if "Started " in line and "seconds" in line:
                started.set()

    threading.Thread(target=_tail, daemon=True).start()
    if not started.wait(timeout=APP_STARTUP_TIMEOUT):
        deadline = time.time() + 15
        while time.time() < deadline:
            try:
                requests.get(f"{BASE_URL}/tasks", timeout=2)
                return proc
            except Exception:
                time.sleep(2)
        proc.terminate()
        return None
    time.sleep(1)
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


def _http(method: str, url: str, body=None) -> tuple:
    try:
        resp = getattr(requests, method.lower())(url, json=body, headers={"Content-Type": "application/json"}, timeout=10)
        try:
            b = resp.json()
        except Exception:
            b = None
        return resp.status_code, b
    except Exception:
        return -1, None


def _run_scenarios() -> list:
    results = []
    task_id = "unknown"

    def chk(id, desc, got, want, body=None):
        bs = ""
        if body is not None:
            try:
                bs = json.dumps(body, ensure_ascii=False)[:300]
            except Exception:
                bs = str(body)[:300]
        return {"id": id, "desc": desc, "got": got, "want": want, "pass": got == want, "body": bs, "spec": E2E_SPEC.get(id, "")}

    code, body = _http("GET", f"{BASE_URL}/tasks")
    results.append(chk("01", "GET /tasks vazia", code, 200, body))

    code, body = _http("POST", f"{BASE_URL}/tasks", {"title": "Test Task", "description": "Desc"})
    results.append(chk("02", "POST 201", code, 201, body))
    if body and isinstance(body, dict):
        task_id = body.get("id", "unknown")

    code, body = _http("POST", f"{BASE_URL}/tasks", {})
    results.append(chk("03", "POST sem title 400", code, 400, body))

    code, body = _http("POST", f"{BASE_URL}/tasks", {"title": ""})
    results.append(chk("04", "POST title='' 400", code, 400, body))

    code, body = _http("GET", f"{BASE_URL}/tasks")
    results.append(chk("05", "GET /tasks lista", code, 200, body))

    code, body = _http("GET", f"{BASE_URL}/tasks/{task_id}")
    results.append(chk("06", "GET by id 200", code, 200, body))

    code, body = _http("GET", f"{BASE_URL}/tasks/id-invalido-xyz")
    results.append(chk("07", "GET invalido 404", code, 404, body))

    code, body = _http("PUT", f"{BASE_URL}/tasks/{task_id}", {"title": "Updated", "completed": True})
    results.append(chk("08", "PUT 200", code, 200, body))

    code, body = _http("PUT", f"{BASE_URL}/tasks/id-invalido-xyz", {"title": "X"})
    results.append(chk("09", "PUT invalido 404", code, 404, body))

    code, body = _http("DELETE", f"{BASE_URL}/tasks/{task_id}")
    results.append(chk("10", "DELETE 204", code, 204, body))

    code, body = _http("DELETE", f"{BASE_URL}/tasks/id-invalido-xyz")
    results.append(chk("11", "DELETE invalido 404", code, 404, body))

    code, body = _http("GET", f"{BASE_URL}/tasks/{task_id}")
    results.append(chk("12", "GET apos DELETE 404", code, 404, body))

    return results


# ---------------------------------------------------------------------------
# LOC
# ---------------------------------------------------------------------------

def count_loc(directory: Path) -> int:
    if not directory.exists():
        return 0
    total = 0
    for f in directory.rglob("*.java"):
        try:
            for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
                s = line.strip()
                if s and not s.startswith("//"):
                    total += 1
        except Exception:
            pass
    return total


# ---------------------------------------------------------------------------
# CLI standalone
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Verificação pós-Aider para exp-07")
    parser.add_argument("--model",       required=True, help="dir do modelo (ex: deepseek-v3)")
    parser.add_argument("--arch",        required=True, help="arquitetura (ex: mvc)")
    parser.add_argument("--cost",        type=float, default=0.0, help="custo USD extraído do Aider")
    parser.add_argument("--duration",    type=float, default=0.0, help="duração em minutos")
    parser.add_argument("--project-dir", required=True, help="caminho para o diretório do projeto Maven")
    args = parser.parse_args()

    impl_dir = Path(args.project_dir).resolve()
    if not impl_dir.exists():
        print(f"Diretório não encontrado: {impl_dir}")
        sys.exit(1)

    print(f"Build...")
    build = eval_build(impl_dir)
    print(f"  success: {build['success']}")

    print(f"Tests...")
    tests = eval_tests(impl_dir)
    print(f"  {tests['tests_passed']}/{tests['tests_total']} · cobertura: {tests['coverage_line_pct']:.1f}%")

    print(f"E2E...")
    e2e = eval_e2e(impl_dir)
    print(f"  {e2e['passed']}/12 passaram")

    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = results_dir / f"exp07_{args.model}_{args.arch}_{ts}.json"

    pkg   = impl_dir / "src" / "main" / "java" / "com" / "benchmark" / "taskmanager"
    tpkg  = impl_dir / "src" / "test" / "java" / "com" / "benchmark" / "taskmanager"
    report = {
        "experiment": "exp-07-aider-benchmark",
        "meta": {"model": args.model, "architecture": args.arch, "collected_at_utc": datetime.now(timezone.utc).isoformat()},
        "speed":  {"duration_min": args.duration},
        "cost":   {"total_usd": args.cost},
        "build":  build,
        "tests":  tests,
        "e2e":    e2e,
        "loc":    {"prod": count_loc(pkg), "test": count_loc(tpkg)},
    }
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSalvo em: {out}")


if __name__ == "__main__":
    main()
