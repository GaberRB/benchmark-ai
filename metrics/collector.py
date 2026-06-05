"""
collector.py — Extrai métricas de tokens de uma sessão Claude Code.

Fonte de dados: ~/.claude/projects/<projeto>/<session_id>.jsonl
(cada mensagem do assistente contém usage com tokens reais)

Uso:
  python metrics/collector.py --session-id <UUID> --language java
  python metrics/collector.py --session-id <UUID> --language kotlin

Saída:
  metrics/reports/<language>_<timestamp>.json
"""

import argparse
import json
import os
import re
import glob
from datetime import datetime, timezone

CLAUDE_DIR  = os.path.join(os.path.expanduser("~"), ".claude")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")

# Preço por milhão de tokens — claude-sonnet-4-6
PRICING = {
    "input":            3.00 / 1_000_000,
    "output":          15.00 / 1_000_000,
    "cache_creation":   3.75 / 1_000_000,
    "cache_read":       0.30 / 1_000_000,
}


# ─── localização do arquivo de sessão ────────────────────────────────────────

def _cwd_to_project_dir(cwd: str) -> str:
    """Converte caminho absoluto no nome do diretório de projeto do Claude Code.

    Ex: C:\\Users\\grios\\OneDrive\\Desktop\\benchmark
     →  C--Users-grios-OneDrive-Desktop-benchmark
    """
    result = cwd.replace(":\\", "--").replace("\\", "-").replace("/", "-").replace(":", "-")
    return result


def find_session_jsonl(session_id: str) -> str | None:
    """Localiza o .jsonl de uma sessão procurando em todos os projetos."""
    projects_dir = os.path.join(CLAUDE_DIR, "projects")
    if not os.path.isdir(projects_dir):
        return None

    # Busca direta pelo session_id em todos os projetos
    pattern = os.path.join(projects_dir, "*", f"{session_id}.jsonl")
    matches = glob.glob(pattern)
    if matches:
        return matches[0]

    # Fallback: procura dentro de cada projeto
    for proj in os.listdir(projects_dir):
        candidate = os.path.join(projects_dir, proj, f"{session_id}.jsonl")
        if os.path.isfile(candidate):
            return candidate

    return None


def get_session_info(session_id: str) -> dict:
    """Lê metadados da sessão em ~/.claude/sessions/."""
    sessions_dir = os.path.join(CLAUDE_DIR, "sessions")
    if not os.path.isdir(sessions_dir):
        return {}
    for fname in os.listdir(sessions_dir):
        fpath = os.path.join(sessions_dir, fname)
        try:
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
            if data.get("sessionId") == session_id:
                return data
        except Exception:
            pass
    return {}


# ─── parsing do jsonl ─────────────────────────────────────────────────────────

def load_messages(jsonl_path: str) -> list[dict]:
    messages = []
    with open(jsonl_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                messages.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return messages


# ─── métricas ─────────────────────────────────────────────────────────────────

def collect_token_metrics(messages: list[dict]) -> dict:
    input_tokens    = 0
    output_tokens   = 0
    cache_creation  = 0
    cache_read      = 0

    assistant_msgs = [m for m in messages if m.get("type") == "assistant"]

    # Deduplica por uuid — o Claude Code pode gravar a mesma mensagem 2x
    seen = set()
    unique = []
    for m in assistant_msgs:
        uid = m.get("uuid") or m.get("messageId") or id(m)
        if uid not in seen:
            seen.add(uid)
            unique.append(m)

    for m in unique:
        usage = (m.get("message") or {}).get("usage") or {}
        input_tokens   += usage.get("input_tokens", 0)
        output_tokens  += usage.get("output_tokens", 0)
        cache_creation += usage.get("cache_creation_input_tokens", 0)
        cache_read     += usage.get("cache_read_input_tokens", 0)

    cost_usd = (
        input_tokens   * PRICING["input"]
        + output_tokens  * PRICING["output"]
        + cache_creation * PRICING["cache_creation"]
        + cache_read     * PRICING["cache_read"]
    )

    total = input_tokens + output_tokens
    cache_total = cache_creation + cache_read
    cache_hit_rate = round(cache_read / cache_total * 100, 2) if cache_total else 0.0

    return {
        "input_tokens_total":    input_tokens,
        "output_tokens_total":   output_tokens,
        "cache_creation_tokens": cache_creation,
        "cache_read_tokens":     cache_read,
        "cache_hit_rate_pct":    cache_hit_rate,
        "cost_usd":              round(cost_usd, 6),
        "tokens_per_endpoint":   round(total / 5, 1),
        "cost_per_endpoint_usd": round(cost_usd / 5, 6),
        "api_calls_count":       len(unique),
    }


def collect_speed_metrics(messages: list[dict], session_info: dict) -> dict:
    timestamps = []
    for m in messages:
        ts_str = m.get("timestamp")
        if ts_str:
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                timestamps.append(ts)
            except ValueError:
                pass

    # Complementa com startedAt do arquivo de sessão
    started_at = session_info.get("startedAt")
    if started_at:
        try:
            ts = datetime.fromtimestamp(started_at / 1000, tz=timezone.utc)
            timestamps.append(ts)
        except Exception:
            pass

    if not timestamps:
        return {"session_duration_min": None, "time_per_endpoint_min": None,
                "throughput_endpoints_per_hour": None}

    timestamps.sort()
    duration_min = round((timestamps[-1] - timestamps[0]).total_seconds() / 60, 2)

    return {
        "session_duration_min":          duration_min,
        "time_per_endpoint_min":         round(duration_min / 5, 2) if duration_min else None,
        "throughput_endpoints_per_hour": round(5 / (duration_min / 60), 2) if duration_min else None,
        "session_start_utc":             timestamps[0].isoformat(),
        "session_end_utc":               timestamps[-1].isoformat(),
    }


def collect_iteration_metrics(messages: list[dict]) -> dict:
    user_msgs      = [m for m in messages if m.get("type") == "user"]
    assistant_msgs = [m for m in messages if m.get("type") == "assistant"]

    # Deduplica assistants por uuid
    seen = set()
    unique_asst = []
    for m in assistant_msgs:
        uid = m.get("uuid") or id(m)
        if uid not in seen:
            seen.add(uid)
            unique_asst.append(m)

    tool_calls = 0
    for m in unique_asst:
        content = (m.get("message") or {}).get("content") or []
        if isinstance(content, list):
            tool_calls += sum(1 for c in content if isinstance(c, dict) and c.get("type") == "tool_use")

    total_turns = len(user_msgs)

    return {
        "total_turns":           total_turns,
        "turns_per_endpoint":    round(total_turns / 5, 1),
        "tool_calls_total":      tool_calls,
        "assistant_messages":    len(unique_asst),
    }


def collect_model_metrics(messages: list[dict]) -> dict:
    """Extrai detalhes do modelo usado na sessão."""
    model_counts    = {}
    stop_reasons    = {}
    cc_versions     = {}
    entrypoints     = {}

    seen_uuids = set()
    for m in messages:
        if m.get("type") != "assistant":
            continue
        uid = m.get("uuid") or id(m)
        if uid in seen_uuids:
            continue
        seen_uuids.add(uid)

        msg = m.get("message") or {}
        model      = msg.get("model", "")
        stop       = msg.get("stop_reason", "")
        cc_version = m.get("version", "")
        entry      = m.get("entrypoint", "")

        if model:
            model_counts[model] = model_counts.get(model, 0) + 1
        if stop:
            stop_reasons[stop] = stop_reasons.get(stop, 0) + 1
        if cc_version:
            cc_versions[cc_version] = cc_versions.get(cc_version, 0) + 1
        if entry:
            entrypoints[entry] = entrypoints.get(entry, 0) + 1

    # modelo principal = o mais usado
    primary_model = max(model_counts, key=model_counts.get) if model_counts else "unknown"
    primary_cc    = max(cc_versions,  key=cc_versions.get)  if cc_versions  else "unknown"
    primary_entry = max(entrypoints,  key=entrypoints.get)  if entrypoints  else "unknown"

    total_calls = sum(stop_reasons.values()) or 1

    return {
        "primary_model":             primary_model,
        "claude_code_version":       primary_cc,
        "entrypoint":                primary_entry,
        "models_used":               model_counts,
        "stop_reason_end_turn":      stop_reasons.get("end_turn", 0),
        "stop_reason_tool_use":      stop_reasons.get("tool_use", 0),
        "stop_reason_max_tokens":    stop_reasons.get("max_tokens", 0),
        "stop_reason_end_turn_pct":  round(stop_reasons.get("end_turn", 0) / total_calls * 100, 1),
        "stop_reason_tool_use_pct":  round(stop_reasons.get("tool_use", 0) / total_calls * 100, 1),
        "stop_reason_max_tokens_pct": round(stop_reasons.get("max_tokens", 0) / total_calls * 100, 1),
        "_note_max_tokens": "stop_reason_max_tokens > 0 indica respostas truncadas — risco de código incompleto",
    }


def collect_error_metrics(messages: list[dict]) -> dict:
    compile_errors = 0
    runtime_errors = 0
    test_failures  = 0

    compile_pat  = re.compile(r"\[ERROR\]|BUILD FAILURE|error: ", re.IGNORECASE)
    runtime_pat  = re.compile(r"Exception in thread|Caused by:|\.java:\d+\)|\.kt:\d+\)", re.IGNORECASE)
    test_fail_pat = re.compile(r"Failures: [1-9]|Errors: [1-9]|FAILED\b|tests failed", re.IGNORECASE)

    for m in messages:
        # Tool results ficam nas mensagens de usuário como tool_result
        content = m.get("message", {}).get("content") or []
        if not isinstance(content, list):
            content = []
        for block in content:
            if not isinstance(block, dict):
                continue
            text = ""
            if block.get("type") == "tool_result":
                inner = block.get("content") or ""
                if isinstance(inner, list):
                    text = " ".join(c.get("text", "") for c in inner if isinstance(c, dict))
                else:
                    text = str(inner)
            elif block.get("type") == "text":
                text = block.get("text", "")

            if compile_pat.search(text):
                compile_errors += 1
            if runtime_pat.search(text):
                runtime_errors += 1
            if test_fail_pat.search(text):
                test_failures += 1

    return {
        "compile_errors": compile_errors,
        "runtime_errors": runtime_errors,
        "test_failures":  test_failures,
        "total_errors":   compile_errors + runtime_errors + test_failures,
    }


# ─── main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Coleta métricas de uma sessão de benchmark")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--language",   required=True)
    args = parser.parse_args()

    print(f"[collector] Procurando sessão: {args.session_id}")

    jsonl_path = find_session_jsonl(args.session_id)
    if not jsonl_path:
        print(f"[collector] ERRO: arquivo .jsonl não encontrado para session {args.session_id}")
        print(f"[collector] Procurado em: {os.path.join(CLAUDE_DIR, 'projects', '*', args.session_id + '.jsonl')}")
        return

    print(f"[collector] Lendo: {jsonl_path}")
    messages     = load_messages(jsonl_path)
    session_info = get_session_info(args.session_id)
    print(f"[collector] {len(messages)} mensagens encontradas.")

    model_metrics = collect_model_metrics(messages)

    report = {
        "meta": {
            "session_id":       args.session_id,
            "language":         args.language,
            "collected_at_utc": datetime.now(timezone.utc).isoformat(),
            "jsonl_source":     jsonl_path,
            "message_count":    len(messages),
            "cwd":              session_info.get("cwd", ""),
        },
        "model":      model_metrics,
        "tokens":     collect_token_metrics(messages),
        "speed":      collect_speed_metrics(messages, session_info),
        "iterations": collect_iteration_metrics(messages),
        "errors":     collect_error_metrics(messages),
    }

    os.makedirs(REPORTS_DIR, exist_ok=True)
    ts       = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{args.language}_{ts}.json"
    path     = os.path.join(REPORTS_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    t = report["tokens"]
    s = report["speed"]
    e = report["errors"]
    mo = report["model"]
    print(f"\n[collector] Relatório salvo em: {path}")
    print(f"  Modelo:          {mo['primary_model']}  (Claude Code {mo['claude_code_version']}  via {mo['entrypoint']})")
    print(f"  Tokens input:    {t['input_tokens_total']:,}")
    print(f"  Tokens output:   {t['output_tokens_total']:,}")
    print(f"  Cache read:      {t['cache_read_tokens']:,}  ({t['cache_hit_rate_pct']}%)")
    print(f"  Custo estimado:  ${t['cost_usd']:.4f} USD")
    print(f"  Duração sessão:  {s['session_duration_min']} min")
    print(f"  Turns:           {report['iterations']['total_turns']}")
    print(f"  Stop reasons:    end_turn={mo['stop_reason_end_turn']}  tool_use={mo['stop_reason_tool_use']}  max_tokens={mo['stop_reason_max_tokens']}")
    if mo["stop_reason_max_tokens"] > 0:
        print(f"  ⚠️  ATENÇÃO: {mo['stop_reason_max_tokens']} chamada(s) truncada(s) por max_tokens — pode haver código incompleto")
    print(f"  Erros (build+test): {e['total_errors']}")


if __name__ == "__main__":
    main()
