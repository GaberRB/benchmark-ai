<div align="center">

# AI Coding Benchmark

**Série de experimentos medindo custo, velocidade e qualidade de modelos de IA gerando código para a mesma tarefa controlada.**

[![Framework](https://img.shields.io/badge/Framework-Spring%20Boot%203.2-6db33f?style=flat-square)](https://spring.io/projects/spring-boot)
[![Build](https://img.shields.io/badge/Build-Maven%203.9-c71a36?style=flat-square)](https://maven.apache.org)
[![E2E](https://img.shields.io/badge/E2E%20Exp.%201%2B2-108%2F108%20✅-brightgreen?style=flat-square)](#)

</div>

---

## Tarefa Base

Todos os experimentos usam a mesma tarefa: **Task Manager REST API** — 5 endpoints CRUD, armazenamento em memória, validação de campos, cobertura ≥ 80%.

> Especificação completa: [`shared/task-definition.md`](shared/task-definition.md)

---

## Experimentos

| # | Nome | Variável | Ferramenta / Modelos | Status | Resultados |
|---|------|----------|----------------------|--------|------------|
| 01 | **Java vs Kotlin** | Linguagem | Claude Code · `claude-sonnet-4-6` | ✅ Concluído | [→ ver resultados](experiments/exp-01-java-vs-kotlin/README.md) |
| 02 | **Padrões Arquiteturais** | Arquitetura (7 padrões) | Claude Code · `claude-sonnet-4-6` | ✅ Concluído | [→ ver resultados](experiments/exp-02-arch-patterns/README.md) |
| 03 | **Modelos Locais (Ollama)** | Modelo open-source (4 modelos × 7 arquiteturas) | Aider + Ollama · **100% gratuito** | 🔄 Em andamento | [→ ver experimento](experiments/exp-03-ollama-local-models/README.md) |

---

## Destaques dos Resultados

### Experimento 1 — Java vs Kotlin

| | Java | Kotlin |
|---|---|---|
| Custo | **$1,46** 🏆 | $3,50 |
| Duração | **5,4 min** 🏆 | 10,7 min |
| Cobertura linha | 89,1% | **94,3%** 🏆 |
| E2E | 12/12 | 12/12 |

Java foi 2,4× mais barato e 2× mais rápido — mais exemplos nos dados de treinamento do modelo.

### Experimento 2 — Padrões Arquiteturais (Java + Spring Boot)

| Padrão | Custo | Duração | Erros | Cobertura | E2E |
|--------|-------|---------|-------|-----------|-----|
| MVC | $1,73 | 6,3 min | 5 | 93,0% | 12/12 |
| Vertical Slice | $3,84 | 5,4 min | 2 | 91,8% | 12/12 |
| Clean Architecture | $3,18 | 7,3 min | 1 | **97,0%** 🏆 | 12/12 |
| Hexagonal | $2,92 | 8,4 min | 6 | 93,6% | 12/12 |
| DDD Tático | $2,33 | **5,0 min** 🏆 | 1 | 88,0% | 12/12 |
| Event-Driven | **$2,22** 🏆 | 8,85 min | 5 | 90,0% | 12/12 |
| CQRS | $3,27 | 8,81 min | 2 | 95,0% | 12/12 |

---

## Estrutura do Repositório

```
benchmark/
├── experiments/
│   ├── exp-01-java-vs-kotlin/          # Experimento 1: Java vs Kotlin
│   │   ├── README.md                   # Resultados detalhados
│   │   ├── java-mode-1/                # Implementação Java (agente sequencial)
│   │   ├── java-mode-2/                # Implementação Java (orquestrador + subagentes)
│   │   ├── kotlin-mode-1/              # Implementação Kotlin (agente sequencial)
│   │   ├── kotlin-mode-2/              # Implementação Kotlin (orquestrador + subagentes)
│   │   ├── guides/                     # Guias de execução (benchmark-*.md)
│   │   └── results/                    # Métricas JSON e relatórios HTML
│   │
│   ├── exp-02-arch-patterns/           # Experimento 2: 7 padrões arquiteturais
│   │   ├── README.md                   # Resultados detalhados
│   │   ├── mvc/ vertical-slice/ ...    # Uma pasta por arquitetura
│   │   ├── guides/                     # Guias de execução (benchmark-arch-*.md)
│   │   └── results/
│   │
│   └── exp-03-ollama-local-models/     # Experimento 3: Modelos locais via Ollama
│       ├── README.md                   # Hipótese e resultados
│       ├── spec/prd.md                 # PRD do experimento
│       ├── implementations/            # deepseek-coder/ qwen2.5-coder/ codellama/ llama3.1/
│       │   └── <modelo>/<arquitetura>/ # 4 modelos × 7 arquiteturas = 28 runs
│       ├── guides/                     # setup.md + benchmark-<arch>.md (modelo como parâmetro)
│       └── results/
│
├── shared/
│   ├── task-definition.md              # Especificação CRUD compartilhada entre todos os experimentos
│   └── docs/                           # Guias teóricos de cada padrão arquitetural
│
└── tools/
    ├── collector.py                    # Extrai tokens/custo/velocidade de sessões Claude Code
    ├── snapshot.py                     # Snapshot pré/pós sessão
    ├── compare.py                      # Tabela comparativa em Markdown
    ├── report.py                       # Relatório HTML interativo (Chart.js)
    └── ollama_collector.py             # Métricas para sessões Aider + Ollama (Exp-03)
```

---

## Como Rodar

### Pré-requisitos

```bash
java -version      # Java 21+
mvn -version       # Maven 3.9+
python --version   # Python 3.10+
```

### Experimentos 1 e 2 (Claude Code)

```bash
claude --version   # Claude Code CLI
```

Abra o Claude Code na raiz do repo e peça ao agente para executar o guia:

```
"execute o experiments/exp-01-java-vs-kotlin/guides/benchmark-java-modo-1.md"
"execute o experiments/exp-02-arch-patterns/guides/benchmark-arch-clean.md"
```

### Experimento 3 (Ollama — gratuito)

```bash
ollama --version   # Ollama instalado
pip install aider-chat
```

Siga o guia de setup: [`experiments/exp-03-ollama-local-models/guides/setup.md`](experiments/exp-03-ollama-local-models/guides/setup.md)

### Gerar relatórios

```bash
python tools/report.py              # Relatório Exp-01 (Java vs Kotlin)
python tools/report.py --mode arch  # Relatório Exp-02 (Arquiteturas)
```

---

## Como Adicionar um Novo Experimento

1. Crie `experiments/exp-NN-nome/`
2. Adicione `README.md` (hipótese, metodologia, resultados)
3. Adicione `spec/prd.md` (PRD detalhado)
4. Adicione `guides/` com guias de execução no mesmo padrão dos existentes
5. Adicione `results/.gitkeep`
6. Atualize a tabela de experimentos neste README

---

## Guias Teóricos de Arquitetura

Os documentos em [`shared/docs/`](shared/docs/) explicam cada padrão com diagramas e análise dos resultados:

[MVC](shared/docs/arch-mvc.md) · [Vertical Slice](shared/docs/arch-vertical-slice.md) · [Clean Architecture](shared/docs/arch-clean.md) · [Hexagonal](shared/docs/arch-hexagonal.md) · [DDD](shared/docs/arch-ddd.md) · [Event-Driven](shared/docs/arch-event-driven.md) · [CQRS](shared/docs/arch-cqrs.md)

---

<div align="center">

Rode você mesmo e compare com os seus resultados.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

</div>
