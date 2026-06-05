# AI Coding Benchmark — Java vs Kotlin

Benchmark controlado para medir o custo, velocidade e qualidade de uma IA (Claude Code) ao
implementar a mesma API REST CRUD em **Java** e **Kotlin**, em dois modos de execução:

| Modo | Descrição |
|------|-----------|
| **Modo 1** | Agente único implementa tudo sequencialmente |
| **Modo 2** | Orquestrador decompõe o trabalho em tasks paralelas (subagentes) |

A tarefa é sempre a mesma: uma **Task Manager API** com 5 endpoints CRUD, armazenamento
in-memory, validação, testes unitários e cobertura ≥ 80%.

---

## Métricas coletadas

| Categoria | O que mede |
|-----------|-----------|
| **Tokens & Custo** | Input/output tokens, cache hit rate, custo USD por sessão e por endpoint |
| **Velocidade** | Duração da sessão, tempo por endpoint, throughput |
| **Erros** | Erros de compilação, runtime e falhas de teste |
| **Iterações** | Total de turns, tool calls, chamadas de API |
| **Qualidade** | LOC, cobertura JaCoCo (linha + branch), proporção testes/produção |
| **E2E** | 12 cenários curl contra o app em execução |
| **Modelo** | Modelo usado, versão do Claude Code, stop reasons |

---

## Pré-requisitos

```bash
java -version      # Java 21+
mvn -version       # Maven 3.9+  →  https://maven.apache.org/download.cgi
python --version   # Python 3.10+
claude --version   # Claude Code CLI  →  npm install -g @anthropic-ai/claude-code
cloc               # Opcional, para contar LOC  →  npm install -g cloc
```

> **Windows**: adicione `mvn` ao PATH antes de rodar os benchmarks.  
> O `mvnw.cmd` de cada projeto detecta automaticamente o Maven via PATH ou `MAVEN_HOME`.

---

## Estrutura do projeto

```
benchmark/
├── benchmark-java-modo-1.md          ← instruções completas para o agente (Execução #1)
├── benchmark-kotlin-modo-1.md        ← instruções completas para o agente (Execução #2)
├── benchmark-java-modo-2.md          ← instruções completas para o orquestrador (Execução #3)
├── benchmark-kotlin-modo-2.md        ← instruções completas para o orquestrador (Execução #4)
│
├── java-implementation/              ← Modo 1 Java  (src/ gerado pelo agente)
│   ├── pom.xml                       ← Spring Boot 3.2 + JaCoCo (pré-configurado)
│   └── mvnw.cmd                      ← wrapper Maven (Windows)
├── kotlin-implementation/            ← Modo 1 Kotlin
│   ├── pom.xml                       ← Spring Boot 3.2 + kotlin-maven-plugin + JaCoCo
│   └── mvnw.cmd
├── java-implementation-mode2/        ← Modo 2 Java
│   ├── pom.xml
│   └── mvnw.cmd
├── kotlin-implementation-mode2/      ← Modo 2 Kotlin
│   ├── pom.xml
│   └── mvnw.cmd
│
├── .claude/spec/
│   ├── prd-ai-benchmark-java-vs-kotlin.md   ← framework de métricas (referência)
│   ├── prd-java-task-manager-api.md          ← PRD Java com mandatos do agente
│   └── prd-kotlin-task-manager-api.md        ← PRD Kotlin com mandatos do agente
├── spec/
│   └── task-definition.md                    ← especificação CRUD idêntica para ambos
│
└── metrics/
    ├── collector.py    ← extrai métricas do JSONL da sessão Claude Code
    ├── snapshot.py     ← snapshot pré/pós sessão
    ├── compare.py      ← tabela comparativa em Markdown
    ├── report.py       ← relatório HTML interativo (Chart.js)
    └── reports/        ← JSONs e HTMLs gerados (não commitados)
```

---

## Como executar

Cada benchmark é um arquivo `.md` auto-suficiente. Abra o Claude Code na pasta `benchmark/`
e peça ao agente para executar o arquivo desejado.

### Execução #1 — Java, Modo 1

```
Abra o Claude Code na pasta benchmark/ com o modelo claude-sonnet-4-6 e peça:
"execute o benchmark-java-modo-1.md"
```

O agente vai:
1. Capturar o session ID da sessão atual
2. Implementar a API Java completa com testes
3. Rodar os 12 cenários E2E
4. Coletar métricas e salvar em `metrics/reports/java_<timestamp>.json`

### Execução #2 — Kotlin, Modo 1

```
"execute o benchmark-kotlin-modo-1.md"
```

### Execução #3 — Java, Modo 2 (subagentes)

```
"execute o benchmark-java-modo-2.md"
```

O orquestrador vai decompor o trabalho em 7 subagentes paralelos (T0–T6) e coletar
métricas individuais de cada um.

### Execução #4 — Kotlin, Modo 2

```
"execute o benchmark-kotlin-modo-2.md"
```

---

## Gerar o relatório HTML

Após qualquer execução, gere o relatório visual interativo:

```bash
python metrics/report.py
# Saída: metrics/reports/benchmark_report_<timestamp>.html
```

O HTML contém gráficos comparativos de tokens, custo, velocidade, erros, cobertura e E2E,
além de uma tabela com todos os 28 indicadores e indicação de qual linguagem venceu em cada um.

Para especificar arquivos:

```bash
python metrics/report.py --java metrics/reports/java_X.json --kotlin metrics/reports/kotlin_Y.json
```

---

## Dados das sessões

O `collector.py` lê diretamente os arquivos JSONL que o Claude Code grava em:

```
~/.claude/projects/<project-dir>/<session-id>.jsonl
```

Cada mensagem do assistente contém `message.usage` com os tokens reais consumidos.
Não é necessário configurar telemetria adicional.

---

## Resultados de exemplo

Execução realizada com **claude-sonnet-4-6** (Claude Code 2.1.163), Task Manager API
com 5 endpoints CRUD, Spring Boot 3.2, Maven:

| Métrica | ☕ Java | 🟣 Kotlin | Vencedor |
|---------|--------|---------|---------|
| Duração | 5,4 min | 10,7 min | Java (2x mais rápido) |
| Custo total | $1,46 | $3,50 | Java (2,4x mais barato) |
| Output tokens | 29.393 | 94.748 | Java (3,2x menos) |
| Chamadas API | 50 | 83 | Java |
| Erros totais | 2 | 3 | Java |
| LOC produção | 198 | 132 | Kotlin (33% mais conciso) |
| Cobertura linha | 89,1% | 94,3% | Kotlin |
| Cobertura branch | 81,2% | 85,7% | Kotlin |
| E2E (12 cenários) | 12/12 ✅ | 12/12 ✅ | Empate |

**Conclusão**: Java foi mais produtivo para a IA (mais rápido e barato) por ter maior
representação nos dados de treinamento dos LLMs. Kotlin gerou código mais conciso e
com melhor cobertura de testes — a linguagem mostrou sua expressividade mesmo quando
o caminho foi mais longo.

---

## Contribuindo

Para rodar em outros modelos ou linguagens, adapte os arquivos `benchmark-*.md` e
os `pom.xml` correspondentes. O `collector.py` funciona com qualquer sessão Claude Code
que produza arquivos JSONL em `~/.claude/projects/`.

---

## Licença

MIT
