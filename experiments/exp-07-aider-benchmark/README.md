# Experimento 7 — Aider Benchmark de Arquiteturas

> **Variável:** LLM + Arquitetura · **Constante:** tarefa (Task Manager API), build tool (Maven), avaliação (12 E2E + JaCoCo ≥ 80%)  
> **Pergunta:** qual combinação de LLM × arquitetura produz o melhor código com menor custo usando o Aider CLI?

---

## O que é diferente do exp-02

| | exp-02 | exp-07 |
|---|---|---|
| Agente | Claude Code CLI | **Aider CLI** |
| LLM | claude-sonnet-4-6 (fixo) | **Configurável via OpenRouter** |
| Modo | Humano executa guia | **Autônomo** (`--yes-always --auto-test`) |
| Build loop | Manual | **Aider roda `mvn compile && mvn test` automaticamente** |
| API key | Claude Code (local) | **OpenRouter** (exp-06 .env) |

### Como o Aider executa o benchmark

```
aider --model openrouter/<model>
      --test-cmd "mvn compile && mvn test"
      --auto-test          ← roda após cada mudança, resultado vai de volta para a LLM
      --yes-always         ← aceita diffs sem confirmação
      --read benchmark-aider-<arch>.md
      --read task-definition.md
      --message "Implement the Task Manager REST API..."
```

A LLM escreve os arquivos Java via diffs. Aider os aplica, roda `mvn compile && mvn test`, e se falhar, devolve o output para a LLM corrigir. Ciclo totalmente autônomo.

---

## Modelos testados

| Modelo | OpenRouter ID | In ($/M) | Out ($/M) |
|--------|--------------|---------|---------|
| Claude Sonnet 4.5 | `openrouter/anthropic/claude-sonnet-4.5` | $3.00 | $15.00 |
| Claude Sonnet 4.6 | `openrouter/anthropic/claude-sonnet-4.6` | $3.00 | $15.00 |
| DeepSeek V3 | `openrouter/deepseek/deepseek-chat` | $0.14 | $0.28 |
| DeepSeek V3.2 | `openrouter/deepseek/deepseek-v3.2` | $0.14 | $0.28 |
| Gemini 2.5 Flash | `openrouter/google/gemini-2.5-flash` | $0.075 | $0.30 |
| Devstral 25/12 | `openrouter/mistralai/devstral-2512` | ~$0.10 | ~$0.30 |

Todos são confirmados na lista oficial do Aider para OpenRouter (`aider --list-models openrouter`).

---

## Arquiteturas testadas

As mesmas 7 do exp-02: **MVC · Vertical Slice · Clean Architecture · Hexagonal · DDD · Event-Driven · CQRS**

---

## Como usar

```powershell
# 1. Setup (ver guides/setup.md para detalhes)
pip install -r requirements.txt

# 2. Rodar benchmark
python main.py
```

O script exibe a TUI de seleção, lança o Aider, e ao final roda a verificação independente e salva o JSON em `results/`.

---

## Resultados

> A preencher após as runs.

| LLM | Arquitetura | Custo | Duração | Build | Testes | Cob. Linha | E2E |
|-----|------------|-------|---------|-------|--------|-----------|-----|
| — | — | — | — | — | — | — | — |

---

## Estrutura

```
exp-07-aider-benchmark/
├── main.py                # TUI + launcher do Aider + verificação
├── benchmark_config.py    # Lista de modelos e arquiteturas
├── requirements.txt
├── guides/
│   ├── setup.md           # Como configurar o ambiente
│   └── benchmark-aider-*.md  # Um guia por arquitetura
├── implementations/       # Código gerado (gitignored)
│   └── <model>/<arch>/
│       └── pom.xml        # Copiado de exp-06
├── tools/
│   └── collector.py       # Verificação: build + tests + E2E
└── results/               # JSONs de resultado (gitignored)
```
