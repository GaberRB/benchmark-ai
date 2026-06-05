# PRD — AI Coding Benchmark: Java vs Kotlin

**Versão**: 2.0  
**Data**: 2026-06-04  
**Status**: Aprovado

---

## 1. Problema

Não existe medição objetiva e controlada sobre quanto a IA consome em tokens, comete erros e
demora para entregar código em **Java vs Kotlin** para o mesmo problema. Decisões de stack são
tomadas com base em opiniões; este benchmark fornece dados.

---

## 2. Objetivo

Quantificar, de forma reproduzível, o custo e a produtividade da IA ao implementar uma API REST
CRUD nas duas linguagens, em **dois modos de execução distintos**:

| Modo | Descrição |
|------|-----------|
| **Modo 1 — Sequencial** | Agente único implementa o PRD do início ao fim |
| **Modo 2 — Subagentes Paralelos** | Orquestrador decompõe em tasks independentes; subagentes as executam em paralelo |

Métricas capturadas em ambos os modos:

- Custo de tokens (input, output, cache)
- Volume e tipo de erros gerados
- Velocidade de entrega
- Qualidade do código produzido
- Comportamento da IA durante a sessão

Métricas exclusivas do Modo 2:

- Overhead de orquestração e duplicação de contexto
- Speedup real de wall clock vs. tempo sequencial equivalente
- Taxa de falhas por task e custo de integração entre subagentes

---

## 3. Tarefa Benchmark

A mesma especificação funcional é implementada pela IA nas duas linguagens.

**Aplicação**: Task Manager API  
**Spec completa**: `spec/task-definition.md`

### Endpoints obrigatórios

| Método | Rota           | Descrição                    |
|--------|----------------|------------------------------|
| GET    | /tasks         | Listar todas as tarefas      |
| POST   | /tasks         | Criar nova tarefa            |
| GET    | /tasks/{id}    | Buscar tarefa por ID         |
| PUT    | /tasks/{id}    | Atualizar tarefa             |
| DELETE | /tasks/{id}    | Remover tarefa               |

### Restrições do benchmark

- Storage in-memory (sem banco de dados externo)
- Validação básica de input (campos obrigatórios, tipos)
- Suite de testes unitários com ≥ 80% de cobertura
- Retornos HTTP corretos (200, 201, 400, 404, 204)
- Nenhuma dependência externa além do framework HTTP escolhido
- **Java**: Spring Boot 3.x
- **Kotlin**: Spring Boot 3.x (mesma stack — elimina variável de framework)

---

## 4. Framework de Métricas

### 4.1 Tokens

> Fonte: `~/.claude/telemetry/1p_failed_events.*.json` — eventos `tengu_api_success`

| Métrica | Campo Telemetria | Unidade | Como Calcular |
|---|---|---|---|
| `input_tokens_total` | `inputTokens` | tokens | Soma de todos os eventos da sessão |
| `output_tokens_total` | `outputTokens` | tokens | Soma de todos os eventos da sessão |
| `cached_tokens` | `cachedInputTokens` | tokens | Soma — tokens servidos do cache |
| `uncached_tokens` | `uncachedInputTokens` | tokens | Soma — tokens processados sem cache |
| `cost_usd` | `costUSD` | USD | Soma de todos os eventos |
| `cache_hit_rate` | calculado | % | `cached / (cached + uncached) × 100` |
| `tokens_per_endpoint` | calculado | tokens | `(input + output) / 5` |
| `cost_per_endpoint` | calculado | USD | `cost_usd / 5` |

**Por que é importante**: token total determina custo direto; cache_hit_rate revela se a IA
repete contexto desnecessário; tokens_per_endpoint normaliza para comparação justa.

---

### 4.2 Erros

> Fonte: parsing dos outputs de ferramentas (Bash, compilador, test runner) durante a sessão

| Métrica | Fonte | Unidade | Definição |
|---|---|---|---|
| `compile_errors` | saída mvn/gradle | count | Linhas contendo `ERROR` no build |
| `runtime_errors` | stack traces em Bash output | count | Exceções não tratadas em runtime |
| `test_failures` | output JUnit/Kotest | count | `Tests run: X, Failures: Y, Errors: Z` |
| `error_recovery_turns` | turns após erro até próximo sucesso | count | Quantos turns a IA levou para resolver cada erro |
| `self_correction_rate` | calculado | % | `(erros resolvidos sem intervenção humana / total erros) × 100` |
| `avg_turns_per_error` | calculado | turns | `error_recovery_turns / total_errors` |

**Como registrar**: o `snapshot.py` (pré/pós sessão) coleta a saída bruta; o `collector.py`
faz o parsing com regex para extrair contagens.

---

### 4.3 Velocidade de Entrega

> Fonte: `client_timestamp` dos eventos de telemetria + arquivos de sessão `~/.claude/sessions/`

| Métrica | Fonte | Unidade | Definição |
|---|---|---|---|
| `session_duration_min` | `startedAt` / último `client_timestamp` | minutos | Tempo total da sessão |
| `time_to_first_build_min` | primeiro evento após build ok | minutos | Do início até primeiro `BUILD SUCCESS` |
| `time_to_passing_tests_min` | primeiro evento após tests verdes | minutos | Do início até suite 100% verde |
| `time_per_endpoint_min` | calculado | minutos | `session_duration / 5` |
| `throughput_endpoints_per_hour` | calculado | endpoints/h | `5 / (session_duration_min / 60)` |

---

### 4.4 Iterações

> Fonte: contagem de eventos e campo `messageCount` na telemetria

| Métrica | Fonte | Unidade | Definição |
|---|---|---|---|
| `total_turns` | `messageCount` (último evento) | count | Total de turns conversa IA-humano |
| `api_calls_count` | count de eventos `tengu_api_success` | count | Total de chamadas à API Anthropic |
| `turns_per_endpoint` | calculado | turns | `total_turns / 5` |
| `max_query_depth` | `queryDepth` (máximo) | nível | Profundidade máxima de raciocínio encadeado |
| `tool_calls_total` | count de eventos `tengu_tool_use_success` | count | Total de ferramentas executadas |
| `file_operations_total` | count de eventos `tengu_file_operation` | count | Arquivos criados/modificados |

---

### 4.5 Qualidade de Código

> Fonte: análise estática executada após a sessão

| Métrica | Ferramenta | Unidade | Definição |
|---|---|---|---|
| `lines_of_code` | `cloc` | linhas | LOC apenas de código de produção (excl. testes) |
| `test_lines_of_code` | `cloc` | linhas | LOC de código de testes |
| `test_coverage_pct` | JaCoCo (Java) / Kover (Kotlin) | % | Cobertura de linhas pelos testes |
| `tokens_per_loc` | calculado | tokens/linha | `(input + output) / lines_of_code` |
| `cost_per_loc` | calculado | USD/linha | `cost_usd / lines_of_code` |
| `test_ratio` | calculado | % | `test_loc / (prod_loc + test_loc) × 100` |

---

### 4.6 Comportamento da IA

> Fonte: telemetria — campos `stop_reason`, eventos de ferramentas

| Métrica | Campo | Definição |
|---|---|---|
| `stop_reason_end_turn` | `stop_reason == "end_turn"` | Calls que terminaram naturalmente |
| `stop_reason_tool_use` | `stop_reason == "tool_use"` | Calls que acionaram ferramentas |
| `stop_reason_max_tokens` | `stop_reason == "max_tokens"` | Calls que atingiram limite (sinal de risco) |
| `avg_latency_ms` | `durationMs` (média) | Latência média por chamada de API |
| `avg_ttft_ms` | `ttftMs` (média) | Time-to-first-token médio |
| `total_cost_usd` | `costUSD` (soma) | Custo total da sessão |

**Alerta**: `stop_reason_max_tokens > 0` indica que a IA foi interrompida antes de terminar
a resposta — pode gerar código truncado e erros subsequentes.

---

### 4.7 Métricas Exclusivas do Modo 2 (Subagentes Paralelos)

> Estas métricas só existem quando a execução usa decomposição em tasks e subagentes.
> A comparação Modo 1 vs Modo 2 para a mesma linguagem é uma dimensão separada de análise.

#### A. Orquestração

| Métrica | Fonte | Unidade | Definição |
|---|---|---|---|
| `orchestration_tokens` | session do orquestrador | tokens | Tokens gastos para analisar o PRD e gerar as tasks |
| `orchestration_cost_usd` | session do orquestrador | USD | Custo isolado da orquestração |
| `task_count` | contagem de tasks geradas | count | Número total de tasks decompostas |
| `parallelizable_tasks` | contagem de tasks sem deps | count | Tasks que rodaram realmente em paralelo |
| `sequential_tasks` | contagem de tasks com deps | count | Tasks que precisaram aguardar outras |
| `parallelizable_pct` | calculado | % | `parallelizable / task_count × 100` |

#### B. Tempo e Paralelismo

| Métrica | Fonte | Unidade | Definição |
|---|---|---|---|
| `wall_clock_time_min` | timestamp início / fim da sessão total | min | Tempo real decorrido (com paralelismo) |
| `cpu_equivalent_time_min` | soma dos tempos individuais das tasks | min | Quanto levaria se fossem sequenciais |
| `speedup_ratio` | calculado | x | `cpu_equivalent / wall_clock` — fator de aceleração |
| `max_parallel_agents` | pico simultâneo de subagentes ativos | count | Maior número de subagentes ao mesmo tempo |
| `avg_parallel_agents` | média de subagentes ativos | count | Grau médio de paralelismo durante a execução |

> `speedup_ratio > 1` significa que o paralelismo foi benéfico.
> `speedup_ratio < 1` indica que o overhead de orquestração/contexto superou o ganho.

#### C. Tokens por Subagente e Overhead de Contexto

| Métrica | Fonte | Unidade | Definição |
|---|---|---|---|
| `tokens_per_task[n]` | session_id de cada subagente | tokens | Tokens gastos por cada task individual |
| `cost_per_task[n]` | session_id de cada subagente | USD | Custo de cada task individual |
| `context_duplication_tokens` | calculado | tokens | Tokens de contexto repetidos entre subagentes (cada um relê spec + arquivos base) |
| `mode2_total_tokens` | soma de todos os subagentes + orquestrador | tokens | Total real do Modo 2 |
| `orchestration_overhead_pct` | calculado | % | `orchestration_tokens / mode2_total_tokens × 100` |
| `context_overhead_pct` | calculado | % | `context_duplication_tokens / mode2_total_tokens × 100` |
| `mode2_vs_mode1_token_delta_pct` | calculado | % | `(mode2_total - mode1_total) / mode1_total × 100` |

> **Hipótese a testar**: Modo 2 consome mais tokens totais (contexto duplicado por subagente)
> mas entrega mais rápido (wall clock). A tradeoff custo × velocidade é o dado central.

#### D. Falhas por Task

| Métrica | Fonte | Unidade | Definição |
|---|---|---|---|
| `task_failure_count` | tasks que retornaram build/test com erro | count | Tasks que falharam na primeira tentativa |
| `task_retry_count` | total de retentas somadas | count | Soma de todas as tentativas extras |
| `failed_task_ids` | IDs das tasks com falha | lista | Quais tasks específicas falharam |
| `avg_turns_per_task` | calculado | turns | Média de turns por task para completar |
| `max_turns_single_task` | task com mais turns | turns | Task mais custosa em iterações |

#### E. Integração entre Subagentes

| Métrica | Fonte | Unidade | Definição |
|---|---|---|---|
| `integration_conflicts` | erros pós-integração (imports, interfaces) | count | Conflitos ao juntar código de subagentes diferentes |
| `integration_fix_turns` | turns do orquestrador após integração | count | Turns extras para corrigir incompatibilidades |
| `api_contract_violations` | divergências de interface detectadas | count | Subagente A esperou interface X, subagente B gerou Y |
| `rework_after_integration_tokens` | tokens gastos na fase de integração | tokens | Custo de corrigir o código após juntar tudo |
| `tasks_requiring_rework` | tasks editadas pós-integração | count | Tasks cujo código precisou ser alterado depois |

#### F. Comparação Direta Modo 1 vs Modo 2 (por linguagem)

| Dimensão | Modo 1 | Modo 2 | Delta | Vencedor |
|---|---|---|---|---|
| `total_tokens` | | | | |
| `total_cost_usd` | | | | |
| `wall_clock_time_min` | | | | |
| `total_errors` | | | | |
| `e2e_failures` | | | | |
| `test_coverage_pct` | | | | |
| `lines_of_code` | | | | |
| `tokens_per_loc` | | | | |

---

## 5. Estratégia de Captura de Dados

### 5.1 Fluxo por Sessão

```
ANTES DA SESSÃO                     DURANTE A SESSÃO              APÓS A SESSÃO
─────────────────                   ────────────────              ─────────────
python metrics/snapshot.py          Claude Code executa           python metrics/snapshot.py
  --pre --language java               a implementação               --post --language java
                                                                                │
                                                                  python metrics/collector.py
                                                                    --session-id <UUID>
                                                                    --language java
                                                                                │
                                                                  metrics/reports/java_<ts>.json
```

### 5.2 Como Obter o Session ID

O Session ID aparece no terminal do Claude Code ao iniciar uma sessão. Alternativamente:

```powershell
# Listar sessions recentes
Get-ChildItem "$env:USERPROFILE\.claude\sessions\" | Sort-Object LastWriteTime -Descending | Select-Object -First 5

# Ver conteúdo do session file mais recente
Get-Content (Get-ChildItem "$env:USERPROFILE\.claude\sessions\" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName | ConvertFrom-Json | Select sessionId, cwd, startedAt
```

### 5.3 Checklist de Não-Perda de Dados

Execute **obrigatoriamente** antes e após cada sessão:

- [ ] `python metrics/snapshot.py --pre --language java` (ou kotlin)
- [ ] Não fechar/apagar `~/.claude/telemetry/` durante o benchmark
- [ ] Ao fim da sessão, anotar o session_id do terminal
- [ ] `python metrics/snapshot.py --post --language java --session-id <UUID>`
- [ ] `python metrics/collector.py --session-id <UUID> --language java`
- [ ] Salvar `metrics/reports/java_<timestamp>.json` em local seguro

### 5.4 Isolamento entre Sessões

- Cada linguagem = sessão separada em diretório separado
- Java: abrir Claude Code em `java-implementation/`
- Kotlin: abrir Claude Code em `kotlin-implementation/`
- O campo `cwd` na telemetria confirma o isolamento

---

## 6. Scripts de Coleta

### `metrics/snapshot.py`

Registra o estado da telemetria antes e após a sessão para definir o delta de dados.

```
Uso:
  python metrics/snapshot.py --pre  --language java
  python metrics/snapshot.py --post --language java --session-id <UUID>

Saída:
  metrics/reports/snapshot_java_pre_<timestamp>.json
  metrics/reports/snapshot_java_post_<timestamp>.json
```

### `metrics/collector.py`

Extrai todas as métricas de tokens e comportamento da telemetria do Claude Code.

```
Uso:
  python metrics/collector.py --session-id <UUID> --language java

Saída:
  metrics/reports/java_<timestamp>.json
```

### `metrics/compare.py`

Gera relatório comparativo entre Java e Kotlin a partir dos JSONs coletados.

```
Uso:
  python metrics/compare.py \
    --java    metrics/reports/java_<timestamp>.json \
    --kotlin  metrics/reports/kotlin_<timestamp>.json

Saída:
  metrics/reports/comparison_<timestamp>.md
```

---

## 7. Estrutura de Diretórios

```
benchmark/
├── .claude/
│   ├── settings.local.json
│   └── spec/
│       └── prd-ai-benchmark-java-vs-kotlin.md   ← este documento
├── spec/
│   └── task-definition.md                        ← spec CRUD compartilhada
├── java-implementation/                           ← sessão IA: Java
├── kotlin-implementation/                         ← sessão IA: Kotlin
├── metrics/
│   ├── snapshot.py
│   ├── collector.py
│   ├── compare.py
│   └── reports/
│       ├── snapshot_java_pre_*.json
│       ├── snapshot_java_post_*.json
│       ├── java_*.json
│       ├── kotlin_*.json
│       └── comparison_*.md
└── CLAUDE.md
```

---

## 8. Formato do Relatório Final

`metrics/reports/comparison_<timestamp>.md` terá a seguinte estrutura:

```markdown
# Benchmark: Java vs Kotlin — AI Coding Metrics

## Tokens
| Métrica                | Java      | Kotlin    | Delta (%)  |
|------------------------|-----------|-----------|------------|
| input_tokens_total     | X         | Y         | +/-Z%      |
| output_tokens_total    | X         | Y         | +/-Z%      |
| cached_tokens          | X         | Y         | +/-Z%      |
| cache_hit_rate         | X%        | Y%        | +/-Z pp    |
| cost_usd               | $X        | $Y        | +/-Z%      |
| tokens_per_endpoint    | X         | Y         | +/-Z%      |

## Erros
| ...                    | ...       | ...       | ...        |

## Velocidade
| ...                    | ...       | ...       | ...        |

## Iterações
| ...                    | ...       | ...       | ...        |

## Qualidade de Código
| ...                    | ...       | ...       | ...        |

## Comportamento da IA
| ...                    | ...       | ...       | ...        |

## Conclusão
[Síntese dos dados — qual linguagem teve menor custo, menor erro, maior velocidade]
```

---

## 9. Critérios de Sucesso

| Critério | Definição de "Completo" |
|---|---|
| Dados capturados | JSONs de coleta gerados para Java e Kotlin sem gaps |
| Comparação gerada | `comparison_*.md` com todas as 6 categorias preenchidas |
| Implementações funcionais | Suite de testes ≥ 80% cobertura passando nas 2 linguagens |
| Métricas normalizadas | Valores por endpoint e por LOC calculados (comparação justa) |
| Rastreabilidade | Cada métrica tem fonte de dados documentada |

---

## 10. Fora de Escopo

- Banco de dados externo (PostgreSQL, MySQL, etc.)
- Deploy em produção ou containerização
- Outras linguagens além de Java e Kotlin
- Outros modelos de IA além de Claude Code (claude-sonnet-4-6)
- Front-end ou cliente HTTP
- Autenticação / autorização
