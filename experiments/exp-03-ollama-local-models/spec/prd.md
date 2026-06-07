# PRD — Experimento 3: Modelos Locais (Ollama + Aider)

## Objetivo

Comparar a qualidade de código gerado por 4 modelos open-source locais (via Ollama + Aider) nas mesmas 7 arquiteturas do Experimento 2. Identificar qual modelo gratuito mais se aproxima da qualidade do Claude Sonnet.

## Hipótese

1. Modelos especializados em código (Deepseek Coder, Qwen Coder) vão superar modelos gerais (Llama 3.1) em conformidade ao PRD, cobertura de testes e erros de compilação.
2. Arquiteturas mais simples (MVC) terão maior taxa de sucesso que arquiteturas complexas (CQRS, Hexagonal) — contexto window menor dos modelos locais vai se tornar gargalo em arquiteturas com mais abstrações.
3. O melhor modelo local atingirá ≥ 80% de cobertura em pelo menos 5 das 7 arquiteturas, a custo zero.

## Ferramenta de Agente

**Aider** substitui o Claude Code como CLI de coding agent.

Aider é open source, suporta qualquer modelo via OpenAI-compatible API (incluindo Ollama), e edita arquivos de código iterativamente — o mesmo loop de desenvolvimento do Claude Code.

```bash
pip install aider-chat

# Uso com Ollama
aider --model ollama/deepseek-coder-v2:16b --no-auto-commits
```

## Modelos Testados

| Modelo Ollama | Parâmetros | Especialização | RAM ~GPU | Justificativa |
|---------------|-----------|----------------|---------|---------------|
| `deepseek-coder-v2:16b` | 16B | Código (Deepseek AI) | ~10 GB | Melhor modelo de código open-source |
| `qwen2.5-coder:7b` | 7B | Código (Alibaba) | ~5 GB | Excelente qualidade para o tamanho |
| `codellama:13b` | 13B | Código (Meta) | ~8 GB | Baseline histórico do segmento |
| `llama3.1:8b` | 8B | Geral (Meta) | ~5 GB | Controle: modelo geral sem especialização |

## Tarefa

Idêntica aos experimentos anteriores — Task Manager REST API:

- **Spec:** `shared/task-definition.md`
- **Stack:** Java 21 + Spring Boot 3.2 + Maven
- **Arquiteturas:** as mesmas 7 do Exp-02 (MVC, Vertical Slice, Clean Architecture, Hexagonal, DDD Tático, Event-Driven, CQRS)
- **Requisito mínimo:** BUILD SUCCESS + cobertura ≥ 80% + 12/12 E2E

## Matriz de Execução

28 runs (4 modelos × 7 arquiteturas). Execute incrementalmente — cada run é independente.

Ordem recomendada: comece por `mvc` com cada modelo (mais simples) antes de avançar para arquiteturas complexas.

## Métricas

### Substituições em relação ao Exp-02 (sem custo monetário)

| Exp-02 (Claude) | Exp-03 (Ollama) |
|-----------------|-----------------|
| Custo USD | ~~Custo USD~~ → R$ 0,00 |
| Cache hit rate | Tokens/segundo |
| Cache creation tokens | RAM pico (GB) |
| Cache read tokens | Tamanho do modelo (GB) |

### Métricas mantidas idênticas

- Tempo total (min)
- Erros de compilação / runtime / teste
- LOC produção e testes
- Cobertura de linha e branch (JaCoCo)
- E2E: 12 cenários com curl (scripts idênticos)
- Conformidade arquitetural (checklist 0-10)

## Schema JSON de Saída (ollama_collector.py)

```json
{
  "meta": {
    "experiment": "exp-03",
    "tool": "aider",
    "model": "deepseek-coder-v2:16b",
    "architecture": "clean-architecture",
    "collected_at_utc": "ISO8601"
  },
  "model_info": {
    "name": "deepseek-coder-v2:16b",
    "size_gb": 9.1,
    "parameters": "16B",
    "specialization": "code"
  },
  "speed": {
    "session_duration_min": 0,
    "session_start_utc": "",
    "session_end_utc": "",
    "tokens_per_sec": 0,
    "time_per_endpoint_min": 0,
    "throughput_endpoints_per_hour": 0
  },
  "hardware": {
    "ram_peak_gb": 0,
    "vram_peak_gb": 0,
    "cpu_model": "",
    "gpu_model": ""
  },
  "iterations": {
    "total_turns": 0,
    "aider_messages": 0
  },
  "errors": {
    "compile_errors": 0,
    "runtime_errors": 0,
    "test_failures": 0,
    "total_errors": 0,
    "context_window_exceeded": false
  },
  "code_quality": {
    "lines_of_code": 0,
    "test_lines_of_code": 0,
    "test_coverage_line_pct": 0,
    "test_coverage_branch_pct": 0
  },
  "arch_metrics": {
    "arch_conformance": 0,
    "dependency_violations": 0
  },
  "e2e": {
    "total_scenarios": 12,
    "passed": 0,
    "failed": 12,
    "failure_details": []
  }
}
```

## Critério de Aceite por Run

- `.\mvnw.cmd compile` → BUILD SUCCESS
- `.\mvnw.cmd test` → 0 failures, 0 errors, cobertura ≥ 80%
- 12/12 cenários E2E passando
- JSON de métricas gerado em `results/`

Run que não atingir esses critérios é registrado com `"status": "FAILED"` no JSON e não conta para o ranking final.

## Limitações Esperadas (documentar durante a execução)

- **Context window**: modelos 7-16B têm 4K-32K tokens vs 200K do Claude — PRDs longos podem ser truncados
- **Sem cache de prompt**: cada turno reprocessa o contexto completo
- **Variância**: modelos locais têm mais variância entre runs — re-runs podem ser necessários
- **Hardware dependente**: velocidade varia muito (CPU-only vs GPU)

Se um modelo exceder o context window, registrar `"context_window_exceeded": true` no JSON e tentar com um PRD simplificado (sem a seção de estrutura de pacotes detalhada).
