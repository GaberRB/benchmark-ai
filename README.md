<div align="center">

# 🔬 AI Coding Benchmark

**Medimos custo, velocidade e qualidade da IA em dois experimentos controlados.**

[![Model](https://img.shields.io/badge/Model-claude--sonnet--4--6-orange?style=flat-square)](https://anthropic.com)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-2.1.165-orange?style=flat-square)](https://claude.ai/code)
[![Framework](https://img.shields.io/badge/Framework-Spring%20Boot%203.2-6db33f?style=flat-square)](https://spring.io/projects/spring-boot)
[![Build](https://img.shields.io/badge/Build-Maven%203.9-c71a36?style=flat-square)](https://maven.apache.org)
[![E2E](https://img.shields.io/badge/E2E-48%2F48%20✅-brightgreen?style=flat-square)](#)

</div>

---

## Os Experimentos

Mesmo agente, mesma tarefa (Task Manager REST API — 5 endpoints CRUD, storage in-memory, validação, cobertura ≥ 80%), mesmo modelo (`claude-sonnet-4-6`).

| # | Variável | Constante | Pergunta |
|---|----------|-----------|---------|
| 1 | **Linguagem** (Java vs Kotlin) | Arquitetura MVC | Qual linguagem a IA implementa melhor? |
| 2 | **Arquitetura** (MVC / Vertical Slice / Clean / Hexagonal) | Linguagem Java | Qual padrão arquitetural a IA executa melhor? |

---

# Experimento 1 — Java vs Kotlin

## 🎯 Resultados

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

**Breakdown do custo:**

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

## ⚡ Velocidade & Iterações

| Métrica | ☕ Java | 🟣 Kotlin | Vencedor |
|---------|--------|---------|---------|
| Duração da sessão | **5,42 min** | **10,67 min** | ☕ Java 🏆 |
| Tempo por endpoint | 1,08 min | 2,13 min | ☕ Java |
| Throughput | 55,35 ep/h | 28,12 ep/h | ☕ Java |
| Total de turns | **28** | **45** | ☕ Java |
| Tool calls | 27 | 44 | ☕ Java |
| Chamadas de API | 50 | 83 | ☕ Java |

## 🐛 Erros de Desenvolvimento

| Tipo | ☕ Java | 🟣 Kotlin |
|------|:------:|:--------:|
| Compilação | 1 | 2 |
| Runtime | 0 | 0 |
| Falhas de teste | 1 | 1 |
| **Total** | **2** | **3** |

## ✅ Qualidade de Código

| Métrica | ☕ Java | 🟣 Kotlin | Vencedor |
|---------|:------:|:-------:|---------|
| LOC produção | 198 | **132** | 🟣 Kotlin 🏆 |
| LOC testes | 261 | **244** | 🟣 Kotlin |
| Cobertura linha | 89,1% | **94,3%** | 🟣 Kotlin 🏆 |
| Cobertura branch | 81,3% | **85,7%** | 🟣 Kotlin 🏆 |

```
Linha  — Java    ██████████████████░░  89,1%
Linha  — Kotlin  ███████████████████░  94,3%  ← +5,2pp 🏆

Branch — Java    ████████████████░░░░  81,3%
Branch — Kotlin  █████████████████░░░  85,7%  ← +4,4pp 🏆
```

## 🏆 Placar — Experimento 1

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

## 🧠 Por Que Java Foi Mais Produtivo?

**Hipótese: densidade de dados de treinamento.**

Spring Boot com Java está presente em dezenas de milhões de arquivos públicos. O modelo
reconhece `@RestController`, `@Service`, `@SpringBootApplication` quase de memória.
Kotlin com Maven (em vez do Gradle padrão do Spring Initializr) adicionou atrito: o
`kotlin-maven-plugin` com `compilerPlugins: spring` aparece com muito menos frequência
nos exemplos públicos, forçando mais iterações.

**Isso não significa que Java é melhor — significa que a IA conhece Java melhor (ainda).**

---

---

# Experimento 2 — Padrões Arquiteturais

> **Variável:** arquitetura do código · **Constante:** Java 21 + Spring Boot 3.2 + Maven

Qual padrão arquitetural a IA implementa com menor custo, menos erros e maior conformidade?
Todas as 4 arquiteturas receberam PRDs detalhados com estrutura de pacotes obrigatória,
regras de dependência explícitas e nomenclatura mandatória.

## 🎯 Resultados

<table>
<tr>
<td align="center" width="25%">

### 🔵 MVC

| | |
|---|---|
| 💰 Custo | **$1.73** |
| ⏱ Duração | **6.3 min** |
| 📡 API calls | **72** |
| 🐛 Erros | **5** |
| 📏 LOC prod. | **245** |
| 🎯 Cobertura | **93%** |
| 📁 Arquivos | **12** |
| 🏗 Conform. | **10/10** |
| ✅ E2E | **12/12** |

</td>
<td align="center" width="25%">

### 🟢 Vertical Slice

| | |
|---|---|
| 💰 Custo | **$3.84** |
| ⏱ Duração | **5.4 min** |
| 📡 API calls | **80** |
| 🐛 Erros | **2** |
| 📏 LOC prod. | **310** |
| 🎯 Cobertura | **91.8%** |
| 📁 Arquivos | **23** |
| 🏗 Conform. | **10/10** |
| ✅ E2E | **12/12** |

</td>
<td align="center" width="25%">

### 🟠 Clean Arch

| | |
|---|---|
| 💰 Custo | **$3.18** |
| ⏱ Duração | **7.3 min** |
| 📡 API calls | **85** |
| 🐛 Erros | **1** |
| 📏 LOC prod. | **336** |
| 🎯 Cobertura | **97%** |
| 📁 Arquivos | **27** |
| 🏗 Conform. | **10/10** |
| ✅ E2E | **12/12** |

</td>
<td align="center" width="25%">

### 🔴 Hexagonal

| | |
|---|---|
| 💰 Custo | **$2.92** |
| ⏱ Duração | **8.4 min** |
| 📡 API calls | **96** |
| 🐛 Erros | **6** |
| 📏 LOC prod. | **288** |
| 🎯 Cobertura | **93.6%** |
| 📁 Arquivos | **19** |
| 🏗 Conform. | **10/10** |
| ✅ E2E | **12/12** |

</td>
</tr>
</table>

## 🔢 Tokens & Custo

<table>
<thead>
<tr><th>Métrica</th><th>🔵 MVC</th><th>🟢 V. Slice</th><th>🟠 Clean</th><th>🔴 Hexagonal</th><th>Melhor</th></tr>
</thead>
<tbody>
<tr><td>Output tokens</td><td>27.550</td><td>107.396</td><td>90.172</td><td>65.383</td><td>🔵 MVC 🏆</td></tr>
<tr><td>Cache creation</td><td>111.850</td><td>352.741</td><td>176.957</td><td>142.523</td><td>🔵 MVC 🏆</td></tr>
<tr><td>Cache read</td><td>2.976.920</td><td>3.020.234</td><td>3.880.112</td><td>4.680.032</td><td>🔵 MVC 🏆</td></tr>
<tr><td>Cache hit rate</td><td>96,38%</td><td>89,54%</td><td>95,64%</td><td>97,04%</td><td>🔴 Hexagonal</td></tr>
<tr><td>API calls</td><td>72</td><td>80</td><td>85</td><td>96</td><td>🔵 MVC 🏆</td></tr>
<tr><td><b>Custo total</b></td><td><b>$1,73</b></td><td><b>$3,84</b></td><td><b>$3,18</b></td><td><b>$2,92</b></td><td><b>🔵 MVC 🏆</b></td></tr>
<tr><td>Custo/endpoint</td><td>$0,35</td><td>$0,77</td><td>$0,64</td><td>$0,58</td><td>🔵 MVC 🏆</td></tr>
</tbody>
</table>

**Ranking de custo:**

```
🔵 MVC           ██████░░░░░░░░░░░░░░  $1,73   ← mais barato 🏆
🔴 Hexagonal     ████████████░░░░░░░░  $2,92
🟠 Clean Arch    █████████████░░░░░░░  $3,18
🟢 Vertical Slice████████████████░░░░  $3,84   ← mais caro
```

> Vertical Slice gerou **3,9× mais output tokens** que MVC para a mesma API.
> Cada slice replica a estrutura completa (controller + use case + DTO) por feature —
> o modelo escreve muito mais código, mesmo que bem organizado.

## ⚡ Velocidade & Iterações

| Métrica | 🔵 MVC | 🟢 V. Slice | 🟠 Clean | 🔴 Hexagonal | Melhor |
|---------|:------:|:-----------:|:--------:|:------------:|--------|
| Duração (min) | 6,3 | **5,4** | 7,3 | 8,4 | 🟢 V. Slice 🏆 |
| Tempo/endpoint | 1,26 | **1,08** | 1,46 | 1,68 | 🟢 V. Slice 🏆 |
| Throughput (ep/h) | 47,7 | **55,9** | 41,0 | 35,7 | 🟢 V. Slice 🏆 |
| Total de turns | 45 | 49 | 52 | 55 | 🔵 MVC |
| Tool calls | 44 | 48 | 51 | 54 | 🔵 MVC |

> Vertical Slice foi o **mais rápido** em tempo de relógio apesar de ser o mais caro —
> a IA escreveu muito output mas sem pausa para raciocínio complexo.
> Hexagonal foi o **mais lento**: as regras de injeção por interface geraram mais ciclos de correção.

## 🐛 Erros de Desenvolvimento

| Tipo | 🔵 MVC | 🟢 V. Slice | 🟠 Clean | 🔴 Hexagonal |
|------|:------:|:-----------:|:--------:|:------------:|
| Compilação | 3 | 2 | 1 | 3 |
| Runtime | 1 | 0 | 0 | 1 |
| Falhas de teste | 1 | 0 | 0 | 2 |
| **Total** | **5** | **2** | **1** | **6** |

```
🟠 Clean Arch    █░░░░░░░░░  1 erro    ← menos erros 🏆
🟢 Vert. Slice   ██░░░░░░░░  2 erros
🔵 MVC           █████░░░░░  5 erros
🔴 Hexagonal     ██████░░░░  6 erros   ← mais erros
```

> Clean Architecture teve apenas **1 erro** — a estrutura rígida de interfaces e camadas
> guiou o raciocínio da IA durante toda a sessão, resultando no código mais correto de primeira.

## ✅ Qualidade de Código

| Métrica | 🔵 MVC | 🟢 V. Slice | 🟠 Clean | 🔴 Hexagonal | Melhor |
|---------|:------:|:-----------:|:--------:|:------------:|--------|
| LOC produção | **245** | 310 | 336 | 288 | 🔵 MVC 🏆 |
| LOC testes | 295 | 222 | **462** | 310 | 🟠 Clean |
| Proporção testes | 54,6% | 41,7% | **57,9%** | 51,8% | 🟠 Clean 🏆 |
| Cobertura linha | 93% | 91,8% | **97%** | 93,6% | 🟠 Clean 🏆 |
| Cobertura branch | — | 75% | **100%** | 60,7% | 🟠 Clean 🏆 |

**Cobertura de linha:**

```
🟠 Clean Arch    ███████████████████░  97,0%  ← melhor 🏆
🔴 Hexagonal     ██████████████████░░  93,6%
🔵 MVC           ██████████████████░░  93,0%
🟢 Vert. Slice   █████████████████░░░  91,8%
```

> Clean Architecture gerou a **maior suite de testes** (462 LOC) e atingiu
> **100% de cobertura de branch** — cada interactor teve seus próprios testes de unidade
> isolados, sem dependência de Spring Boot Test.

## 🏗 Métricas de Arquitetura

| Métrica | 🔵 MVC | 🟢 V. Slice | 🟠 Clean | 🔴 Hexagonal |
|---------|:------:|:-----------:|:--------:|:------------:|
| Arquivos .java criados | 12 | **23** | **27** | 19 |
| Interfaces criadas | 1 | 1 | **6** | **6** |
| Pacotes (profundidade) | 9 | 10 | 10 | **15** |
| Conformidade estrutural | 10/10 | 10/10 | 10/10 | 10/10 |
| Violações de dependência | 0 | 0 | 0 | 0 |

> A IA respeitou **100% as regras de dependência** em todas as arquiteturas —
> nenhum vazamento de camada detectado em nenhum dos 4 padrões.

## 🏆 Placar — Experimento 2

| Categoria | 🔵 MVC | 🟢 V. Slice | 🟠 Clean | 🔴 Hexagonal |
|-----------|:------:|:-----------:|:--------:|:------------:|
| Custo | 🏆 **mais barato** | | | |
| Velocidade | | 🏆 **mais rápido** | | |
| Menos erros | | | 🏆 **só 1 erro** | |
| Cobertura | | | 🏆 **97% linha, 100% branch** | |
| Conformidade | 🤝 | 🤝 | 🤝 | 🤝 |
| E2E | 🤝 | 🤝 | 🤝 | 🤝 |

## 🧠 Por Que Esses Resultados?

**MVC é o mais barato porque é o padrão que a IA mais conhece.**

O padrão MVC do Spring Boot (`@RestController` → `@Service` → `@Repository`) está presente
em incontáveis tutoriais e projetos públicos. A IA o executa quase de memória — poucos tokens
de raciocínio, direto ao ponto.

**Vertical Slice foi o mais caro apesar de ser o mais rápido.**

Organizar por feature em vez de por camada parece simples, mas cada slice replica a estrutura
completa: controller + use case + DTO por operação. A IA escreveu mais código (107k output tokens
vs 27k do MVC) em menos tempo — ritmo alto, mas custo alto por output.

**Clean Architecture teve menos erros porque a estrutura rígida serve de guia.**

As 4 camadas concêntricas com a Dependency Rule bem definida no PRD deram à IA uma "trilha"
clara a seguir. Menos ambiguidade = menos erros de caminho = menos ciclos de correção.
O preço foi mais boilerplate: 27 arquivos, 6 interfaces, 462 LOC de testes.

**Hexagonal foi o mais desafiador.**

O isolamento do domínio (sem nenhum import de Spring em `domain/`) e a injeção por interfaces
(`TaskController` injeta `CreateTaskUseCase` e não `TaskService`) fogem do padrão mais comum
nos dados de treinamento. A IA cometeu mais erros de wiring e precisou de mais ciclos de
compilação para corrigir — 96 chamadas de API contra 72 do MVC.

---

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

### Experimento 1 — Java vs Kotlin

Abra o Claude Code na pasta `benchmark/` com `claude-sonnet-4-6` e peça:

```
"execute o benchmark-java-modo-1.md"
```

| Arquivo | Linguagem | Modo |
|---------|-----------|------|
| `benchmark-java-modo-1.md` | Java | Agente único sequencial |
| `benchmark-kotlin-modo-1.md` | Kotlin | Agente único sequencial |
| `benchmark-java-modo-2.md` | Java | Orquestrador + 7 subagentes paralelos |
| `benchmark-kotlin-modo-2.md` | Kotlin | Orquestrador + 7 subagentes paralelos |

### Experimento 2 — Arquiteturas

```
"execute o benchmark-arch-mvc.md"
```

| Arquivo | Arquitetura |
|---------|-------------|
| `benchmark-arch-mvc.md` | Layered MVC |
| `benchmark-arch-vertical-slice.md` | Vertical Slice |
| `benchmark-arch-clean.md` | Clean Architecture |
| `benchmark-arch-hexagonal.md` | Hexagonal (Ports & Adapters) |

### Gerar relatórios HTML

```bash
# Experimento 1 — Java vs Kotlin
python metrics/report.py

# Experimento 2 — Arquiteturas
python metrics/report.py --mode arch
```

---

## 📁 Estrutura

```
benchmark/
├── benchmark-*.md                    ← guias de execução auto-suficientes
├── java-implementation/              ← Exp. 1 Java (pom.xml + mvnw.cmd)
├── kotlin-implementation/            ← Exp. 1 Kotlin
├── java-implementation-mode2/        ← Exp. 1 Java Modo 2
├── kotlin-implementation-mode2/      ← Exp. 1 Kotlin Modo 2
├── arch-benchmark/
│   ├── mvc/                          ← Exp. 2 MVC (pom.xml + mvnw.cmd)
│   ├── vertical-slice/               ← Exp. 2 Vertical Slice
│   ├── clean-architecture/           ← Exp. 2 Clean Architecture
│   └── hexagonal/                    ← Exp. 2 Hexagonal
├── .claude/spec/                     ← PRDs detalhados por benchmark
├── spec/task-definition.md           ← especificação CRUD compartilhada
└── metrics/
    ├── collector.py    ← extrai tokens/custo/velocidade do JSONL
    ├── snapshot.py     ← snapshot pré/pós sessão
    ├── compare.py      ← tabela comparativa em Markdown
    └── report.py       ← relatório HTML interativo (Chart.js)
```

---

<div align="center">

**Executado com `claude-sonnet-4-6` · 2026-06-05**  
Rode você mesmo e compare com os seus resultados.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

</div>
