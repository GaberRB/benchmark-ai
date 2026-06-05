<div align="center">

# 🔬 AI Coding Benchmark — Java vs Kotlin

**Qual linguagem a IA implementa melhor? Medimos tokens, custo, velocidade e qualidade.**

[![Model](https://img.shields.io/badge/Model-claude--sonnet--4--6-orange?style=flat-square)](https://anthropic.com)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-2.1.163-orange?style=flat-square)](https://claude.ai/code)
[![Framework](https://img.shields.io/badge/Framework-Spring%20Boot%203.2-6db33f?style=flat-square)](https://spring.io/projects/spring-boot)
[![Build](https://img.shields.io/badge/Build-Maven%203.9-c71a36?style=flat-square)](https://maven.apache.org)
[![Java E2E](https://img.shields.io/badge/Java%20E2E-12%2F12%20✅-brightgreen?style=flat-square)](#)
[![Kotlin E2E](https://img.shields.io/badge/Kotlin%20E2E-12%2F12%20✅-brightgreen?style=flat-square)](#)

</div>

---

## O Experimento

Mesmo agente, mesma tarefa, mesma stack — só muda a linguagem.

**Tarefa:** implementar uma Task Manager REST API com 5 endpoints CRUD, storage in-memory,
validação de input, testes unitários e cobertura ≥ 80%.

**Condições controladas:**
- Modelo: `claude-sonnet-4-6` (idêntico nas duas sessões)
- Framework: Spring Boot 3.2 + Maven (idêntico)
- Modo 1: agente único, implementação sequencial
- Métricas coletadas automaticamente via JSONL de sessão do Claude Code

---

## 🎯 Resultados — Modo 1 (Agente Sequencial)

<table>
<tr>
<td align="center" width="50%">

### ☕ Java

| | |
|---|---|
| 💰 Custo | **$1.46 USD** |
| ⏱ Duração | **5.4 min** |
| 📡 API calls | **50** |
| 🐛 Erros | **2** |
| 📏 LOC produção | **198** |
| 🎯 Cobertura linha | **89.1%** |
| ✅ E2E | **12 / 12** |

</td>
<td align="center" width="50%">

### 🟣 Kotlin

| | |
|---|---|
| 💰 Custo | **$3.50 USD** |
| ⏱ Duração | **10.7 min** |
| 📡 API calls | **83** |
| 🐛 Erros | **3** |
| 📏 LOC produção | **132** |
| 🎯 Cobertura linha | **94.3%** |
| ✅ E2E | **12 / 12** |

</td>
</tr>
</table>

---

## 🔢 Tokens & Custo

<table>
<thead>
<tr><th>Métrica</th><th>☕ Java</th><th>🟣 Kotlin</th><th>Δ</th><th>Vencedor</th></tr>
</thead>
<tbody>
<tr><td>Input tokens</td><td>56</td><td>6.719</td><td>Kotlin +11.898%</td><td>☕ Java</td></tr>
<tr><td>Output tokens</td><td>29.393</td><td>94.748</td><td>Kotlin +222%</td><td>☕ Java 🏆</td></tr>
<tr><td>Cache creation</td><td>107.782</td><td>209.024</td><td>Kotlin +94%</td><td>☕ Java</td></tr>
<tr><td>Cache read</td><td>2.057.345</td><td>4.263.879</td><td>Kotlin +107%</td><td>☕ Java</td></tr>
<tr><td>Cache hit rate</td><td>95,02%</td><td>95,33%</td><td>≈ empate</td><td>🤝 Empate</td></tr>
<tr><td><b>Custo total</b></td><td><b>$1,4624</b></td><td><b>$3,5044</b></td><td><b>Kotlin +140%</b></td><td><b>☕ Java 🏆</b></td></tr>
<tr><td>Custo por endpoint</td><td>$0,2925</td><td>$0,7009</td><td>Kotlin +140%</td><td>☕ Java</td></tr>
</tbody>
</table>

**Breakdown do custo por categoria:**

```
☕ Java  — $1,46 total
  Output tokens ████████████░░░░░░░░ $0,441  30,2%
  Cache read    █████████████████░░░ $0,617  42,2%
  Cache create  ███████████░░░░░░░░░ $0,404  27,6%
  Input tokens  ░░░░░░░░░░░░░░░░░░░░ $0,000   0,01%

🟣 Kotlin — $3,50 total
  Output tokens ████████░░░░░░░░░░░░ $1,421  40,6%
  Cache read    ███████░░░░░░░░░░░░░ $1,279  36,5%
  Cache create  ████░░░░░░░░░░░░░░░░ $0,784  22,4%
  Input tokens  ░░░░░░░░░░░░░░░░░░░░ $0,020   0,6%
```

> Kotlin gerou **3,2× mais output tokens** — a IA precisou "pensar" muito mais para implementar o mesmo código.

---

## ⚡ Velocidade & Iterações

| Métrica | ☕ Java | 🟣 Kotlin | Vencedor |
|---------|--------|---------|---------|
| Duração da sessão | **5,42 min** | **10,67 min** | ☕ Java 🏆 |
| Tempo por endpoint | 1,08 min | 2,13 min | ☕ Java |
| Throughput | 55,35 ep/h | 28,12 ep/h | ☕ Java |
| Total de turns | **28** | **45** | ☕ Java |
| Tool calls | 27 | 44 | ☕ Java |
| Chamadas de API | 50 | 83 | ☕ Java |

> Kotlin precisou de **66% mais chamadas de API** e **61% mais turns** para entregar a mesma API.

---

## 🐛 Erros de Desenvolvimento

| Tipo de erro | ☕ Java | 🟣 Kotlin |
|---|:---:|:---:|
| Erros de compilação | 1 | 2 |
| Erros de runtime | 0 | 0 |
| Falhas de teste | 1 | 1 |
| **Total** | **2** | **3** |

```
☕ Java   ██░░░░░░░░  2 erros
🟣 Kotlin ███░░░░░░░  3 erros
```

Ambas as linguagens precisaram de auto-correção durante o desenvolvimento.
Java resolveu na primeira compilação adicional; Kotlin teve um ciclo extra.

---

## ✅ Qualidade de Código

| Métrica | ☕ Java | 🟣 Kotlin | Vencedor |
|---------|:------:|:-------:|---------|
| LOC produção | 198 | **132** | 🟣 Kotlin 🏆 |
| LOC testes | 261 | **244** | 🟣 Kotlin |
| LOC total | 459 | **376** | 🟣 Kotlin |
| Proporção testes | 56,9% | **64,9%** | 🟣 Kotlin |

**Cobertura de testes:**

```
Linha  — Java    ██████████████████░░  89,1%
Linha  — Kotlin  ███████████████████░  94,3%  ← +5,2pp 🏆

Branch — Java    ████████████████░░░░  81,3%
Branch — Kotlin  █████████████████░░░  85,7%  ← +4,4pp 🏆
```

> Kotlin é naturalmente mais conciso — `data class`, null safety e extension functions
> reduzem boilerplate. A IA gerou **33% menos linhas** de código de produção para a mesma
> funcionalidade, com **cobertura 5pp superior**.

---

## 🌐 Testes E2E — 12 Cenários

Ambas as implementações passaram em todos os 12 cenários contra o app em execução na porta 8080:

| Cenário | Java | Kotlin |
|---------|:----:|:------:|
| GET /tasks (lista vazia) → 200 | ✅ | ✅ |
| POST /tasks (válido) → 201 | ✅ | ✅ |
| POST /tasks (sem title) → 400 | ✅ | ✅ |
| POST /tasks (title vazio) → 400 | ✅ | ✅ |
| GET /tasks (com itens) → 200 | ✅ | ✅ |
| GET /tasks/:id (existente) → 200 | ✅ | ✅ |
| GET /tasks/:id (inexistente) → 404 | ✅ | ✅ |
| PUT /tasks/:id (válido) → 200 | ✅ | ✅ |
| PUT /tasks/:id (inexistente) → 404 | ✅ | ✅ |
| DELETE /tasks/:id (existente) → 204 | ✅ | ✅ |
| DELETE /tasks/:id (inexistente) → 404 | ✅ | ✅ |
| GET /tasks/:id (após deletar) → 404 | ✅ | ✅ |
| **Resultado** | **12/12 ✅** | **12/12 ✅** |

---

## 🏆 Placar Final

| Categoria | ☕ Java | 🟣 Kotlin |
|-----------|:------:|:--------:|
| Custo | 🏆 **2,4× mais barato** | |
| Velocidade | 🏆 **2× mais rápido** | |
| Output tokens | 🏆 **3,2× menos** | |
| Erros | 🏆 Menos 1 erro | |
| LOC (concisão) | | 🏆 **33% menos linhas** |
| Cobertura linha | | 🏆 +5,2pp (94,3%) |
| Cobertura branch | | 🏆 +4,4pp (85,7%) |
| E2E | 🤝 Empate | 🤝 Empate |

---

## 🧠 Por Que Java Foi Mais Produtivo Para a IA?

**Hipótese: densidade de dados de treinamento.**

Spring Boot com Java está presente em dezenas de milhões de arquivos públicos — tutoriais,
Stack Overflow, documentação oficial, repositórios GitHub. O modelo reconhece os padrões
`@RestController`, `@Service`, `@SpringBootApplication` quase de memória:
- Menos tokens para "descobrir" o caminho
- Menos ciclos de compilação
- Menos tentativas erradas

Kotlin com Maven (em vez do Gradle padrão do Spring Initializr) adicionou atrito: o
`kotlin-maven-plugin` com `compilerPlugins: spring` e `kotlin-maven-allopen` aparece com
muito menos frequência nos exemplos públicos, forçando mais iterações.

**Isso não significa que Java é melhor — significa que a IA conhece Java melhor (ainda).**

Kotlin venceu nos atributos intrínsecos da linguagem: código mais conciso, melhor cobertura
gerada naturalmente, menos boilerplate. À medida que o ecossistema Kotlin cresce nos dados
de treinamento, essa diferença de produtividade deve diminuir.

---

## 🚀 Como Rodar

### Pré-requisitos

```bash
java -version      # Java 21+
mvn -version       # Maven 3.9+
python --version   # Python 3.10+
claude --version   # Claude Code CLI
cloc               # opcional, para LOC
```

### Executar um benchmark

Abra o Claude Code na pasta `benchmark/` com o modelo `claude-sonnet-4-6` e peça:

```
"execute o benchmark-java-modo-1.md"
```

O agente executa os 11 passos autonomamente: lê a spec, implementa, valida,
roda os E2E e coleta todas as métricas.

Os 4 benchmarks disponíveis:

| Arquivo | Linguagem | Modo |
|---------|-----------|------|
| `benchmark-java-modo-1.md` | Java | Agente único sequencial |
| `benchmark-kotlin-modo-1.md` | Kotlin | Agente único sequencial |
| `benchmark-java-modo-2.md` | Java | Orquestrador + 7 subagentes paralelos |
| `benchmark-kotlin-modo-2.md` | Kotlin | Orquestrador + 7 subagentes paralelos |

### Gerar relatório HTML interativo

```bash
python metrics/report.py
# → metrics/reports/benchmark_report_<timestamp>.html
```

---

## 📁 Estrutura

```
benchmark/
├── benchmark-*.md                    ← instruções auto-suficientes para o agente
├── java-implementation/
│   ├── pom.xml                       ← Spring Boot 3.2 + JaCoCo (pré-configurado)
│   └── mvnw.cmd                      ← wrapper Maven (usa PATH ou MAVEN_HOME)
├── kotlin-implementation/
│   ├── pom.xml                       ← kotlin-maven-plugin + JaCoCo
│   └── mvnw.cmd
├── java-implementation-mode2/        ← diretório isolado para o Modo 2
├── kotlin-implementation-mode2/
├── .claude/spec/                     ← PRDs detalhados com mandatos do agente
├── spec/task-definition.md           ← especificação CRUD (idêntica para ambos)
└── metrics/
    ├── collector.py    ← lê ~/.claude/projects/<proj>/<session>.jsonl
    ├── snapshot.py     ← snapshot pré/pós sessão
    ├── compare.py      ← tabela comparativa em Markdown
    └── report.py       ← relatório HTML interativo (Chart.js)
```

---

<div align="center">

**Resultados de uma única execução com `claude-sonnet-4-6` em 2026-06-05.**  
Rode você mesmo e compare com os seus resultados.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

</div>
