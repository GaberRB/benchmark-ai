"""
compare.py — Gera relatório comparativo Java vs Kotlin a partir dos JSONs coletados.

Uso:
  python metrics/compare.py \
    --java    metrics/reports/java_20260604_120000.json \
    --kotlin  metrics/reports/kotlin_20260604_140000.json

Saída:
  metrics/reports/comparison_<timestamp>.md
"""

import argparse
import json
import os
from datetime import datetime, timezone

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def delta(java_val, kotlin_val) -> str:
    """Calcula delta percentual Kotlin vs Java (negativo = Kotlin melhor em custo)."""
    try:
        java_f   = float(java_val)
        kotlin_f = float(kotlin_val)
        if java_f == 0:
            return "N/A"
        pct = (kotlin_f - java_f) / java_f * 100
        sign = "+" if pct >= 0 else ""
        return f"{sign}{pct:.1f}%"
    except (TypeError, ValueError):
        return "N/A"


def row(metric: str, java_val, kotlin_val, unit: str = "") -> str:
    j = f"{java_val}{unit}" if java_val is not None else "—"
    k = f"{kotlin_val}{unit}" if kotlin_val is not None else "—"
    d = delta(java_val, kotlin_val) if java_val is not None and kotlin_val is not None else "—"
    return f"| {metric:<40} | {j:>15} | {k:>15} | {d:>12} |"


def header(title: str) -> str:
    return f"\n## {title}\n\n| {'Métrica':<40} | {'Java':>15} | {'Kotlin':>15} | {'Delta (K vs J)':>12} |\n|{'-'*42}|{'-'*17}|{'-'*17}|{'-'*14}|"


def generate_report(java: dict, kotlin: dict) -> str:
    jt = java["tokens"]
    kt = kotlin["tokens"]
    js = java["speed"]
    ks = kotlin["speed"]
    ji = java["iterations"]
    ki = kotlin["iterations"]
    je = java["errors"]
    ke = kotlin["errors"]

    lines = [
        "# Benchmark: Java vs Kotlin — AI Coding Metrics",
        "",
        f"**Gerado em**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Java session**:   `{java['meta']['session_id']}`",
        f"**Kotlin session**: `{kotlin['meta']['session_id']}`",
        "",
        "> Delta (K vs J): valor positivo = Kotlin consumiu mais; negativo = Kotlin consumiu menos.",
        "",
        header("1. Tokens"),
        row("input_tokens_total",    jt["input_tokens_total"],    kt["input_tokens_total"]),
        row("output_tokens_total",   jt["output_tokens_total"],   kt["output_tokens_total"]),
        row("cached_tokens",         jt["cached_tokens"],         kt["cached_tokens"]),
        row("uncached_tokens",       jt["uncached_tokens"],       kt["uncached_tokens"]),
        row("cache_hit_rate",        jt["cache_hit_rate_pct"],    kt["cache_hit_rate_pct"],    "%"),
        row("cost_usd",              jt["cost_usd"],              kt["cost_usd"],              " USD"),
        row("tokens_per_endpoint",   jt["tokens_per_endpoint"],   kt["tokens_per_endpoint"]),
        row("cost_per_endpoint_usd", jt["cost_per_endpoint_usd"], kt["cost_per_endpoint_usd"], " USD"),
        "",
        header("2. Erros"),
        row("compile_errors",   je["compile_errors"],  ke["compile_errors"]),
        row("runtime_errors",   je["runtime_errors"],  ke["runtime_errors"]),
        row("test_failures",    je["test_failures"],   ke["test_failures"]),
        row("total_errors",     je["total_errors"],    ke["total_errors"]),
        "",
        header("3. Velocidade de Entrega"),
        row("session_duration_min",          js["session_duration_min"],          ks["session_duration_min"],          " min"),
        row("time_per_endpoint_min",         js["time_per_endpoint_min"],         ks["time_per_endpoint_min"],         " min"),
        row("throughput_endpoints_per_hour", js["throughput_endpoints_per_hour"], ks["throughput_endpoints_per_hour"], " ep/h"),
        row("avg_api_latency_ms",            js["avg_api_latency_ms"],            ks["avg_api_latency_ms"],            " ms"),
        "",
        header("4. Iterações"),
        row("api_calls_count",        ji["api_calls_count"],        ki["api_calls_count"]),
        row("total_turns",            ji["total_turns"],            ki["total_turns"]),
        row("turns_per_endpoint",     ji["turns_per_endpoint"],     ki["turns_per_endpoint"]),
        row("tool_calls_total",       ji["tool_calls_total"],       ki["tool_calls_total"]),
        row("file_operations_total",  ji["file_operations_total"],  ki["file_operations_total"]),
        row("max_query_depth",        ji["max_query_depth"],        ki["max_query_depth"]),
        row("stop_reason_max_tokens", ji["stop_reason_max_tokens"], ki["stop_reason_max_tokens"]),
        "",
        "## 5. Qualidade de Código",
        "",
        "> Preencher manualmente após executar `cloc` e JaCoCo/Kover:",
        "",
        "| Métrica                    | Java | Kotlin | Delta |",
        "|----------------------------|------|--------|-------|",
        "| lines_of_code              |      |        |       |",
        "| test_lines_of_code         |      |        |       |",
        "| test_coverage_pct          |      |        |       |",
        "| tokens_per_loc             |      |        |       |",
        "| cost_per_loc_usd           |      |        |       |",
        "",
        "## 6. Conclusão",
        "",
        "<!-- Preencher após análise dos dados acima -->",
        "",
        "| Dimensão | Vencedor | Resumo |",
        "|----------|---------|--------|",
        "| Custo de tokens | | |",
        "| Menor taxa de erros | | |",
        "| Velocidade de entrega | | |",
        "| Eficiência (tokens/LOC) | | |",
        "| Cache hit rate | | |",
        "",
    ]

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Comparação Java vs Kotlin")
    parser.add_argument("--java",   required=True, help="JSON de métricas Java")
    parser.add_argument("--kotlin", required=True, help="JSON de métricas Kotlin")
    args = parser.parse_args()

    java   = load(args.java)
    kotlin = load(args.kotlin)

    report = generate_report(java, kotlin)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    ts       = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"comparison_{ts}.md"
    path     = os.path.join(REPORTS_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"[compare] Relatório comparativo salvo em: {path}")


if __name__ == "__main__":
    main()
