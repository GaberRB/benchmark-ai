# Exp-06 — Agentic Benchmark

> LLMs autônomos implementando a mesma Task Manager API via tool use — sem interferência humana no loop.

---

## O que é

Nos experimentos anteriores (exp-01, exp-02), um humano fornecia um guia `.md` e o Claude Code CLI executava as instruções passo a passo. O humano ainda controlava o ritmo: definia as fases, corrigia o rumo, aprovava o resultado.

O exp-06 remove o humano do loop. O modelo recebe a especificação completa da tarefa, três ferramentas para interagir com o sistema de arquivos e o compilador, e **decide sozinho** o que escrever, quando compilar, o que corrigir e quando parar.

Isso mede uma capacidade diferente: **autonomia e raciocínio sequencial**, não só qualidade de código em tentativas guiadas.

---

## Diferença dos experimentos anteriores

| Dimensão | Exp-01 / Exp-02 | Exp-06 |
|---|---|---|
| Quem controla o loop | Humano via prompt | LLM via tool use |
| Ferramenta | Claude Code CLI | OpenRouter API |
| Fases de execução | Guiadas pelo humano | Livres — LLM escolhe a ordem |
| Como o código é escrito | Agente usa editor interno | LLM chama `write_file` explicitamente |
| Critério de término | Humano aprova | Harness verifica independentemente |
| Métrica de processo | Aider calls por fase | Tool calls totais + breakdown por tipo |

---

## O que é um harness

O termo vem da engenharia: um *harness* (arnês) é o conjunto de cabos e conectores que liga componentes de um sistema sem fazer parte da lógica deles — existe apenas para rotear sinais. No carro, o arnês elétrico conecta sensores, atuadores e a ECU sem ser nenhum deles.

No software, um *test harness* é a infraestrutura que **envolve** um sistema sob teste: fornece entradas controladas, executa as chamadas, captura saídas e avalia resultados de forma completamente independente da implementação. O sistema não sabe que está sendo avaliado; o harness observa de fora.

Aqui, o sistema sob teste é o **LLM**. O harness:
- Fornece as 3 ferramentas (`write_file`, `run_command`, `read_file`) como interface controlada
- Executa cada chamada de ferramenta de verdade — disco real, Maven real, sem simulação
- Registra todo o comportamento do modelo (quantas chamadas, quais erros, quanto tempo para compilar)
- Avalia o resultado **de forma independente**: quando o LLM declara que terminou, o harness compila, testa e roda os 12 cenários E2E por conta própria, sem confiar na palavra do modelo

O harness é o **árbitro**, não o colaborador. O LLM pode mentir ou se enganar — o harness verifica.

---

## Como o harness funciona

### Visão estrutural

```
┌─────────────────────────────── HARNESS ─────────────────────────────────┐
│                                                                          │
│  ┌──────────────────┐  tool_call (JSON)  ┌─────────────────────────┐   │
│  │                  │ ─────────────────► │                         │   │
│  │   LLM            │                    │   ToolExecutor          │   │
│  │  (OpenRouter API)│ ◄───────────────── │                         │   │
│  │                  │   result (JSON)    │  run_command()          │   │
│  └────────┬─────────┘                    │  write_file()           │   │
│           │                              │  read_file()            │   │
│           │ "IMPLEMENTATION              └──────────┬──────────────┘   │
│           │  COMPLETE"                              │                  │
│           ▼                                         │ subprocess /     │
│  ┌──────────────────┐                               │ disk I/O        │
│  │                  │                   ┌──────────▼──────────────┐   │
│  │  MetricsEvaluator│◄── mvn compile ───│                         │   │
│  │  (independente)  │◄── mvn test   ────│  File System + Maven    │   │
│  │                  │◄── 12x HTTP E2E ──│  (projeto Java real)    │   │
│  └────────┬─────────┘                   └─────────────────────────┘   │
│           │                                                             │
│           │ OK  → salva JSON + encerra loop                            │
│           │ NOK → injeta feedback → loop continua                      │
└───────────┼─────────────────────────────────────────────────────────────┘
            ▼
    results/exp06_<modelo>_<arch>_<ts>.json
```

### Fluxo de decisão

```mermaid
flowchart TD
    A[python main.py] --> B[Selecionar modelos + arquiteturas]
    B --> C[Carregar guia .md da arquitetura]
    C --> D[Enviar system prompt + guia → LLM via OpenRouter]
    D --> E{LLM decide próxima ação}
    E -->|write_file| F[Cria / sobrescreve arquivo .java]
    E -->|run_command| G[Executa mvn compile / mvn test]
    E -->|read_file| H[Lê arquivo existente]
    F & G & H --> I[Resultado retornado ao LLM]
    I --> E
    E -->|IMPLEMENTATION COMPLETE| J[Harness verifica independentemente]
    J -->|build + testes ≥80% + E2E 12/12 OK| K[✅ Salva JSON de resultado]
    J -->|algum critério falhou| L[Injeta feedback com body + regra da spec]
    L --> D
    E -->|max_build_failures ou max_test_failures| M[⛔ Limite de falhas — salva motivo]
    J -->|max_e2e_failures atingido| N[⛔ Limite E2E — salva motivo]
    E -->|stuck_threshold em build/test| O[📄 LLM analisa problema → salva .md em stuck/]
    J -->|stuck_threshold em E2E| O
```

### Troca de mensagens ao longo do tempo

```mermaid
sequenceDiagram
    participant H as Harness
    participant L as LLM (OpenRouter)
    participant FS as File System
    participant MV as Maven

    H->>L: system prompt + guia da arquitetura
    loop agentic loop
        L->>H: tool_call: write_file("Task.java", "...")
        H->>FS: escreve arquivo
        FS-->>H: ok
        H-->>L: {"written": "...", "bytes": 1240}

        L->>H: tool_call: run_command("mvn compile")
        H->>MV: mvn compile
        MV-->>H: BUILD SUCCESS / FAILURE + stderr
        H-->>L: {"exit_code": 0, "stdout": "..."}

        L->>H: "IMPLEMENTATION COMPLETE"
        H->>MV: mvn compile + test + JaCoCo
        H->>H: 12 cenários E2E via HTTP
        alt todos os critérios OK
            H-->>L: loop encerra
        else algum critério falhou
            H-->>L: feedback com body HTTP + regra da spec por cenário
        end
    end
    opt stuck_threshold atingido em qualquer etapa
        H->>L: "Analyze the problem: what did you try, root cause hypothesis, fix needed"
        L-->>H: análise estruturada (Problem / Tried / Root cause / Fix needed)
        H->>H: salva stuck/<modelo>_<arch>_<etapa>_<ts>.md
        Note over H: convergence_reason = "stuck" — loop encerra
    end
    H->>H: salva results/exp06_*.json
```

### Condições de término

O loop só termina em cinco situações:
1. **Sucesso**: harness confirma que build compila, testes passam com ≥ 80% de cobertura e os 12 cenários E2E estão corretos.
2. **Limite de build/teste**: o modelo atingiu `max_build_failures` ou `max_test_failures` falhas consecutivas.
3. **Limite de E2E**: o modelo atingiu `max_e2e_failures` verificações E2E consecutivas sem passar.
4. **Stuck**: qualquer etapa (build, test ou E2E) falhou `stuck_threshold` vezes seguidas — o harness pede ao LLM uma análise estruturada do problema, salva o resultado em `stuck/` e encerra o run (para revisão humana ou por outro modelo).
5. **Desistência**: o modelo para de usar ferramentas sem sinalizar conclusão.

---

## As 3 ferramentas

| Ferramenta | O que faz | Por que existe |
|---|---|---|
| `write_file(path, content)` | Cria ou sobrescreve um arquivo com conteúdo completo | Escrever Java via shell é frágil — aspas, `$`, `{` têm significados especiais que corrompem o arquivo silenciosamente |
| `run_command(command)` | Executa um comando no diretório do projeto | Compilar, testar, listar arquivos, verificar saída do Maven |
| `read_file(path)` | Lê um arquivo existente | O modelo precisa ver o que já escreveu antes de corrigir |

---

## Loop de verificação independente

Quando o LLM escreve `IMPLEMENTATION COMPLETE`, o harness **não confia** — roda a verificação por conta própria:

```
1. mvn compile          → build compila?
2. mvn test + JaCoCo    → todos os testes passam? cobertura de linha ≥ 80%?
3. 12 cenários E2E HTTP → todos os endpoints respondem corretamente?
```

Se qualquer critério falhar, o harness injeta no chat um feedback detalhado com o resultado exato. O feedback inclui: contador de tentativa, ✓/✗ por cenário, body HTTP da resposta e a regra exata da spec que o cenário valida:

```
Harness verification FAILED (tentativa E2E #3) after your IMPLEMENTATION COMPLETE claim.

Unit tests: 15/16 passed — fix the failing tests.
Coverage: 0.0% — need ≥80%. Add more test cases to cover uncovered code paths.
E2E scenarios: 10/12 passed. Failing:
  ✗ E2E-07: GET /tasks/{id} inválido — expected=404 got=400  body={"timestamp":"...","status":400}
     spec rule: GET /tasks/{id} → 404 se não encontrado. IDs são UUIDs v4. Uma string inválida
     não é um UUID válido — deve retornar 404 semanticamente, não 400.
     Solução: use @PathVariable String id + UUID.fromString() em try/catch.
  ✗ E2E-09: PUT /tasks/{id} inválido — expected=404 got=400  body={"timestamp":"...","status":400}
     spec rule: (mesma regra UUID acima)

Fix all issues above, then declare IMPLEMENTATION COMPLETE again.
```

O LLM só sai do loop quando todos os critérios passam simultaneamente.

---

## Sistema de análise de stuck

Quando qualquer etapa (build, test ou E2E) falha `stuck_threshold` vezes consecutivas (padrão: 3), o harness reconhece que o modelo entrou em loop sem progresso e aciona a análise:

1. **Interrompe o loop agentico normal** e envia um prompt estruturado pedindo ao LLM que documente o problema:
   - O que está tentando fazer
   - O que já tentou
   - Hipótese de causa raiz
   - O que seria necessário para corrigir

2. **Salva o resultado** em `stuck/<modelo>_<arch>_<etapa>_<ts>.md` com metadata da run (modelo, arquitetura, etapa travada, número de falhas) + a análise gerada pelo LLM.

3. **Encerra o run** com `convergence_reason = "stuck"`.

O arquivo gerado fica disponível para análise humana ou para ser enviado a outro modelo como contexto inicial de diagnóstico.

---

## Métricas salvas por run

Cada run salva um JSON em `results/` com dois blocos principais:

**Qualidade do código** (avaliação independente do harness):
```json
{
  "build":      { "success": true },
  "unit_tests": { "pass": true, "total": 16, "passed": 16, "failed": 0 },
  "e2e":        { "passed": 12, "all_passed": true },
  "architecture": { "violations": [], "ok": true }
}
```

**Comportamento do agente** (como o modelo trabalhou):
```json
{
  "agent_behavior": {
    "total_tool_calls": 47,
    "tool_breakdown":    { "run_command": 31, "write_file": 12, "read_file": 4 },
    "command_breakdown": { "mvn compile": 8, "mvn test": 6, "other": 17 },
    "convergence_reason": "success",
    "completion_attempts": 3,
    "e2e_attempts": 3,
    "e2e_fail_streak_at_end": 0,
    "build_failures": 3,
    "test_failures":  1,
    "first_build_success_at_call": 5,
    "first_test_success_at_call": 23,
    "last_build_failure_output": "...",
    "last_test_failure_output":  "..."
  }
}
```

`convergence_reason` pode ser: `success` · `gave_up` · `max_build_failures` · `max_test_failures` · `max_e2e_failures` · `stuck` · `auth_error` · `no_tool_support`

---

## Modelos avaliados

| Modelo | ID OpenRouter | In ($/M tok) | Out ($/M tok) | Tool use |
|--------|---------------|-------------|--------------|----------|
| DeepSeek V3 | `deepseek/deepseek-chat` | $0,14 | $0,28 | ✅ |
| Qwen 2.5 Coder 32B | `qwen/qwen-2.5-coder-32b-instruct` | $0,10 | $0,20 | ❌ |
| Gemini 2.0 Flash | `google/gemini-2.0-flash-001` | $0,075 | $0,30 | ✅ |
| Llama 3.3 70B | `meta-llama/llama-3.3-70b-instruct` | $0,10 | $0,20 | ✅ |
| Claude Sonnet 4.5 | `anthropic/claude-sonnet-4-5` | $3,00 | $15,00 | ✅ |

> Qwen 2.5 Coder 32B não suporta tool use nativo — o harness injeta as ferramentas via formato texto no prompt.

Cada modelo é testado nas 7 arquiteturas: `mvc`, `vertical-slice`, `clean-architecture`, `hexagonal`, `ddd`, `event-driven`, `cqrs`.

---

## Como rodar você mesmo

**Pré-requisitos:**
```bash
java -version    # Java 21+
mvn -version     # Maven 3.9+
python --version # Python 3.10+
```

**Setup:**
```bash
cd experiments/exp-06-agentic-benchmark
pip install -r requirements.txt
```

Crie o arquivo `.env` na pasta do experimento:
```
OPENROUTER_API_KEY=sk-or-...
```

**Execução:**
```bash
python main.py
```

O TUI interativo oferece três opções:
- **Benchmark automático** — seleciona modelos, arquiteturas e limites de falha; executa em sequência; exibe tabela de resultados ao final
- **Chat interativo** — conversa diretamente com o modelo; ele pode executar benchmarks como resposta
- **Limpar arquivos** — remove `.java`, `target/` e JSONs gerados

---

## Estrutura de arquivos

```
exp-06-agentic-benchmark/
│
├── main.py                 # TUI principal (Rich) — entrada do usuário
├── chat.py                 # Modo chat interativo com o modelo
├── benchmark_config.py     # Config do projeto: modelos, arquiteturas, regras de domínio
├── requirements.txt        # openai, requests, python-dotenv, rich
├── .env                    # OPENROUTER_API_KEY (não commitado)
│
├── harness/
│   ├── harness.py          # BenchmarkHarness — loop agentico principal
│   ├── tools.py            # ToolExecutor — implementa write_file, run_command, read_file
│   ├── metrics.py          # Avaliação independente: build, tests, E2E, arquitetura
│   └── terminal.py         # Detecção de ambiente: WSL2, Git Bash, PowerShell, Unix
│
├── guides/
│   ├── benchmark-arch-mvc.md
│   ├── benchmark-arch-vertical-slice.md
│   ├── benchmark-arch-clean-architecture.md
│   ├── benchmark-arch-hexagonal.md
│   ├── benchmark-arch-ddd.md
│   ├── benchmark-arch-event-driven.md
│   └── benchmark-arch-cqrs.md
│   # Cada guia descreve a arquitetura e instrui o LLM com variáveis $src_base, $prod_files, etc.
│
├── implementations/
│   └── <modelo>/<arquitetura>/   # pom.xml pré-configurado + código gerado pelo LLM
│       ├── pom.xml               # Spring Boot 3.2 + JaCoCo 0.8.11 (não modificado)
│       └── src/                  # Gerado autonomamente pelo LLM durante o benchmark
│
├── results/
│   └── exp06_<modelo>_<arch>_<ts>.json   # Um JSON por run com todas as métricas
│
└── stuck/
    └── <modelo>_<arch>_<etapa>_<ts>.md   # Análise estruturada gerada pelo LLM ao ficar preso
```
