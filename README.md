<div align="center">

# 🔬 AI Coding Benchmark

**Medimos custo, velocidade e qualidade da IA em dois experimentos controlados.**

[![Model](https://img.shields.io/badge/Model-claude--sonnet--4--6-orange?style=flat-square)](https://anthropic.com)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-2.1.167-orange?style=flat-square)](https://claude.ai/code)
[![Framework](https://img.shields.io/badge/Framework-Spring%20Boot%203.2-6db33f?style=flat-square)](https://spring.io/projects/spring-boot)
[![Build](https://img.shields.io/badge/Build-Maven%203.9-c71a36?style=flat-square)](https://maven.apache.org)
[![E2E](https://img.shields.io/badge/E2E-108%2F108%20✅-brightgreen?style=flat-square)](#)

</div>

---

## Os Experimentos

Mesmo agente, mesma tarefa (Task Manager REST API — 5 endpoints CRUD, storage in-memory, validação, cobertura ≥ 80%), mesmo modelo (`claude-sonnet-4-6`).

| # | Variável | Constante | Pergunta |
|---|----------|-----------|---------|
| 1 | **Linguagem** (Java vs Kotlin) | Arquitetura MVC | Qual linguagem a IA implementa melhor? |
| 2 | **Arquitetura** (MVC / Vertical Slice / Clean / Hexagonal / DDD / Event-Driven / CQRS) | Linguagem Java | Qual padrão arquitetural a IA executa melhor? |

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
Todas as 7 arquiteturas receberam PRDs detalhados com estrutura de pacotes obrigatória,
regras de dependência explícitas e nomenclatura mandatória.

## 🎯 Resultados

<table>
<tr>
<td align="center">

### 🔵 MVC

| | |
|---|---|
| 💰 Custo | **$1.73** |
| ⏱ Duração | **6.3 min** |
| 📡 API calls | **72** |
| 🐛 Erros | **5** |
| 📏 LOC prod. | **245** |
| 🎯 Cobertura | **93.0%** |
| 📁 Arquivos | **12** |
| 🏗 Conform. | **10/10** |
| ✅ E2E | **12/12** |

</td>
<td align="center">

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
<td align="center">

### 🟠 Clean Arch

| | |
|---|---|
| 💰 Custo | **$3.18** |
| ⏱ Duração | **7.3 min** |
| 📡 API calls | **85** |
| 🐛 Erros | **1** |
| 📏 LOC prod. | **336** |
| 🎯 Cobertura | **97.0%** |
| 📁 Arquivos | **27** |
| 🏗 Conform. | **10/10** |
| ✅ E2E | **12/12** |

</td>
<td align="center">

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
<tr>
<td align="center">

### 🟤 DDD Tático

| | |
|---|---|
| 💰 Custo | **$2.33** |
| ⏱ Duração | **5.0 min** |
| 📡 API calls | **51** |
| 🐛 Erros | **1** |
| 📏 LOC prod. | **295** |
| 🎯 Cobertura | **88.0%** |
| 📁 Arquivos | **17** |
| 🏗 Conform. | **8/10** |
| ✅ E2E | **12/12** |

</td>
<td align="center">

### 🟡 Event-Driven

| | |
|---|---|
| 💰 Custo | **$2.22** |
| ⏱ Duração | **8.85 min** |
| 📡 API calls | **63** |
| 🐛 Erros | **5** |
| 📏 LOC prod. | **373** |
| 🎯 Cobertura | **90.0%** |
| 📁 Arquivos | **22** |
| 🏗 Conform. | **10/10** |
| ✅ E2E | **12/12** |

</td>
<td align="center">

### 🟣 CQRS

| | |
|---|---|
| 💰 Custo | **$3.27** |
| ⏱ Duração | **8.81 min** |
| 📡 API calls | **97** |
| 🐛 Erros | **2** |
| 📏 LOC prod. | **312** |
| 🎯 Cobertura | **95.0%** |
| 📁 Arquivos | **25** |
| 🏗 Conform. | **10/10** |
| ✅ E2E | **12/12** |

</td>
<td align="center">
</td>
</tr>
</table>

## 🔢 Tokens & Custo

<table>
<thead>
<tr><th>Métrica</th><th>🔵 MVC</th><th>🟢 V.Slice</th><th>🟠 Clean</th><th>🔴 Hexag.</th><th>🟤 DDD</th><th>🟡 Event-Dr.</th><th>🟣 CQRS</th><th>Melhor</th></tr>
</thead>
<tbody>
<tr><td>Output tokens</td><td>27.550</td><td>107.396</td><td>90.172</td><td>65.383</td><td>74.224</td><td>57.293</td><td>63.869</td><td>🔵 MVC 🏆</td></tr>
<tr><td>Cache creation</td><td>111.850</td><td>352.741</td><td>176.957</td><td>142.523</td><td>154.604</td><td>148.386</td><td>219.151</td><td>🔵 MVC 🏆</td></tr>
<tr><td>Cache read</td><td>2.976.920</td><td>3.020.234</td><td>3.880.112</td><td>4.680.032</td><td>2.109.868</td><td>2.676.163</td><td>4.976.768</td><td>🟤 DDD 🏆</td></tr>
<tr><td>Cache hit rate</td><td>96,38%</td><td>89,54%</td><td>95,64%</td><td>97,04%</td><td>93,17%</td><td>94,75%</td><td>95,78%</td><td>🔴 Hexagonal</td></tr>
<tr><td>API calls</td><td>72</td><td>80</td><td>85</td><td>96</td><td>51</td><td>63</td><td>97</td><td>🟤 DDD 🏆</td></tr>
<tr><td><b>Custo total</b></td><td>$1,73</td><td>$3,84</td><td>$3,18</td><td>$2,92</td><td>$2,33</td><td><b>$2,22</b></td><td>$3,27</td><td><b>🟡 Event-Dr. 🏆</b></td></tr>
<tr><td>Custo/endpoint</td><td>$0,35</td><td>$0,77</td><td>$0,64</td><td>$0,58</td><td>$0,47</td><td><b>$0,44</b></td><td>$0,65</td><td><b>🟡 Event-Dr. 🏆</b></td></tr>
</tbody>
</table>

**Ranking de custo:**

```
🟡 Event-Driven  ████████████░░░░░░░░  $2,22   ← mais barato 🏆
🔵 MVC           █████████░░░░░░░░░░░  $1,73   ← mais barato (output tokens)
🟤 DDD           ████████████░░░░░░░░  $2,33
🔴 Hexagonal     ███████████████░░░░░  $2,92
🟠 Clean Arch    ████████████████░░░░  $3,18
🟣 CQRS          █████████████████░░░  $3,27
🟢 Vertical Slice████████████████████  $3,84   ← mais caro
```

> Event-Driven foi o **mais barato no total** ($2,22) por usar cache pesadamente e ter o menor
> output por endpoint ($0,44). MVC ainda domina em output tokens brutos — escreve muito menos código.
> CQRS foi o **mais caro por endpoint** ($0,65) — padrão menos frequente nos dados de treinamento.

## ⚡ Velocidade & Iterações

| Métrica | 🔵 MVC | 🟢 V.Slice | 🟠 Clean | 🔴 Hexag. | 🟤 DDD | 🟡 Event-Dr. | 🟣 CQRS | Melhor |
|---------|:------:|:---------:|:--------:|:---------:|:------:|:------------:|:-------:|--------|
| Duração (min) | 6,3 | 5,4 | 7,3 | 8,4 | **5,0** | 8,85 | 8,81 | 🟤 DDD 🏆 |
| Tempo/endpoint | 1,26 | 1,08 | 1,46 | 1,68 | **1,0** | 1,77 | 1,76 | 🟤 DDD 🏆 |
| Throughput (ep/h) | 47,7 | 55,9 | 41,0 | 35,7 | **60,0** | 33,9 | 34,1 | 🟤 DDD 🏆 |
| Total de turns | 45 | 49 | 52 | 55 | **37** | 47 | 68 | 🟤 DDD 🏆 |
| Tool calls | 44 | 48 | 51 | 54 | **36** | 46 | 64 | 🟤 DDD 🏆 |

> **DDD foi o mais rápido** em todas as métricas de velocidade — 37 turns, 5 minutos, 60 ep/h.
> Os Value Objects com validação no construtor deram à IA um modelo mental muito claro.
> CQRS exigiu mais turns (68) — o padrão de handlers separados para command/query é incomum em CRUDs.

## 🐛 Erros de Desenvolvimento

| Tipo | 🔵 MVC | 🟢 V.Slice | 🟠 Clean | 🔴 Hexag. | 🟤 DDD | 🟡 Event-Dr. | 🟣 CQRS |
|------|:------:|:---------:|:--------:|:---------:|:------:|:------------:|:-------:|
| Compilação | 3 | 2 | 1 | 3 | 1 | 2 | 0 |
| Runtime | 1 | 0 | 0 | 1 | 0 | 1 | 0 |
| Falhas de teste | 1 | 0 | 0 | 2 | 0 | 2 | 2 |
| **Total** | **5** | **2** | **1** | **6** | **1** | **5** | **2** |

```
🟠 Clean Arch    █░░░░░░░░░  1 erro    ← menos erros 🏆 (empate com DDD)
🟤 DDD           █░░░░░░░░░  1 erro    ← menos erros 🏆 (empate com Clean)
🟢 Vert. Slice   ██░░░░░░░░  2 erros
🟣 CQRS          ██░░░░░░░░  2 erros
🔵 MVC           █████░░░░░  5 erros
🟡 Event-Driven  █████░░░░░  5 erros
🔴 Hexagonal     ██████░░░░  6 erros   ← mais erros
```

## ✅ Qualidade de Código

| Métrica | 🔵 MVC | 🟢 V.Slice | 🟠 Clean | 🔴 Hexag. | 🟤 DDD | 🟡 Event-Dr. | 🟣 CQRS | Melhor |
|---------|:------:|:---------:|:--------:|:---------:|:------:|:------------:|:-------:|--------|
| LOC produção | **245** | 310 | 336 | 288 | 295 | 373 | 312 | 🔵 MVC 🏆 |
| LOC testes | 295 | 222 | **462** | 310 | 311 | 317 | 327 | 🟠 Clean 🏆 |
| Cobertura linha | 93% | 91,8% | **97%** | 93,6% | 88% | 90% | 95% | 🟠 Clean 🏆 |
| Cobertura branch | — | 75% | **100%** | 60,7% | — | — | 91,7% | 🟠 Clean 🏆 |

**Cobertura de linha:**

```
🟠 Clean Arch    ███████████████████░  97,0%  ← melhor 🏆
🟣 CQRS          ███████████████████░  95,0%
🔴 Hexagonal     ██████████████████░░  93,6%
🔵 MVC           ██████████████████░░  93,0%
🟢 Vert. Slice   █████████████████░░░  91,8%
🟡 Event-Driven  ██████████████████░░  90,0%
🟤 DDD           █████████████████░░░  88,0%
```

## 🏗 Métricas de Arquitetura

| Métrica | 🔵 MVC | 🟢 V.Slice | 🟠 Clean | 🔴 Hexag. | 🟤 DDD | 🟡 Event-Dr. | 🟣 CQRS |
|---------|:------:|:---------:|:--------:|:---------:|:------:|:------------:|:-------:|
| Arquivos .java | 12 | 23 | **27** | 19 | 17 | 22 | **25** |
| Interfaces | 1 | 1 | **6** | **6** | 1 | **4** | 1 |
| Pacotes | 9 | 10 | 10 | **15** | 13 | 9 | 12 |
| Conformidade | 10/10 | 10/10 | 10/10 | 10/10 | **8/10** | 10/10 | 10/10 |
| Violações dep. | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

> DDD foi o único padrão com conformidade abaixo de 10/10 (8/10) — a IA criou apenas 1 interface
> (`TaskRepository`) quando o ideal seria também interfaces para casos de uso na camada de aplicação.
> Todas as outras arquiteturas respeitaram 100% as regras de dependência.

## 📖 Guias Teóricos

Cada arquitetura tem um documento explicando o conceito, diagrama visual e análise dos resultados:

| Arquitetura | Documento |
|-------------|-----------|
| 🔵 MVC | [docs/arch-mvc.md](docs/arch-mvc.md) |
| 🟢 Vertical Slice | [docs/arch-vertical-slice.md](docs/arch-vertical-slice.md) |
| 🟠 Clean Architecture | [docs/arch-clean.md](docs/arch-clean.md) |
| 🔴 Hexagonal | [docs/arch-hexagonal.md](docs/arch-hexagonal.md) |
| 🟤 DDD Tático | [docs/arch-ddd.md](docs/arch-ddd.md) |
| 🟡 Event-Driven | [docs/arch-event-driven.md](docs/arch-event-driven.md) |
| 🟣 CQRS | [docs/arch-cqrs.md](docs/arch-cqrs.md) |

## 🏆 Placar — Experimento 2

| Categoria | 🔵 MVC | 🟢 V.Slice | 🟠 Clean | 🔴 Hexag. | 🟤 DDD | 🟡 Event-Dr. | 🟣 CQRS |
|-----------|:------:|:---------:|:--------:|:---------:|:------:|:------------:|:-------:|
| Custo total | | | | | | 🏆 **$2,22** | |
| Output tokens | 🏆 **mais baixo** | | | | | | |
| Velocidade | | | | | 🏆 **5 min / 60 ep/h** | | |
| Menos erros | | | 🏆 **1 erro** | | 🏆 **1 erro** | | |
| Cobertura | | | 🏆 **97% / 100% branch** | | | | |
| Conformidade | 🤝 | 🤝 | 🤝 | 🤝 | ⚠️ 8/10 | 🤝 | 🤝 |
| E2E | 🤝 | 🤝 | 🤝 | 🤝 | 🤝 | 🤝 | 🤝 |

## 🧠 Por Que Esses Resultados?

**MVC domina em output tokens porque é o padrão mais treinado.**

Spring Boot com `@RestController → @Service → @Repository` está presente em incontáveis tutoriais.
A IA escreve esse padrão quase de memória — poucos tokens de raciocínio, código direto.

**Event-Driven foi o mais barato no total graças ao uso eficiente de cache.**

O padrão de publicar eventos é verboso mas repetitivo — uma vez que o modelo entendeu o EventBus,
usou cache intensamente para os handlers seguintes. Cache read de 2,67M tokens a $0,30/M é muito
mais barato que output tokens a $15/M.

**DDD foi o mais rápido porque Value Objects são um contrato claro.**

A estrutura `TaskId`, `Title`, `Description` → `Task (Aggregate Root)` → `TaskApplicationService`
cria um fluxo unidirecional simples. A IA completou em 37 turns (vs 68 do CQRS). O custo de $2,33
é razoável para o que entregou — mas perdeu 2 pontos de conformidade por não criar interfaces de
use case na camada de aplicação.

**Clean Architecture teve menos erros porque a Dependency Rule é um guia preciso.**

As 4 camadas concêntricas com regras explícitas no PRD deram à IA uma "trilha" sem ambiguidade.
Resultado: 1 erro, 97% de cobertura, 100% de branch. O preço foi boilerplate: 27 arquivos, 462 LOC de testes.

**CQRS foi o mais custoso por endpoint ($0,65) e exigiu mais turns (68).**

Handlers separados para command e query fogem do padrão CRUD padrão nos dados de treinamento.
A IA precisou de mais ciclos de raciocínio para montar o dispatch correto, resultando em 97
chamadas de API — o maior número de todos.

**Hexagonal foi o mais desafiador em erros (6).**

O isolamento do domínio (zero imports Spring em `domain/`) e injeção por interfaces criam wiring
complexo que a IA frequentemente errou, precisando de ciclos de compilação extras.

**Vertical Slice: o paradoxo custo-velocidade.**

Mais caro ($3,84) mas segundo mais rápido (5,4 min). A IA escreve muito e rápido — cada slice
replica a estrutura completa (controller + use case + DTO), gerando 107k output tokens vs 27k do MVC.

---

---

## 🚀 Como Rodar

### Pré-requisitos

```bash
java -version      # Java 21+
mvn -version       # Maven 3.9+
python --version   # Python 3.10+
claude --version   # Claude Code CLI
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

| Arquivo | Arquitetura | Guia teórico |
|---------|-------------|--------------|
| `benchmark-arch-mvc.md` | Layered MVC | [docs/arch-mvc.md](docs/arch-mvc.md) |
| `benchmark-arch-vertical-slice.md` | Vertical Slice | [docs/arch-vertical-slice.md](docs/arch-vertical-slice.md) |
| `benchmark-arch-clean.md` | Clean Architecture | [docs/arch-clean.md](docs/arch-clean.md) |
| `benchmark-arch-hexagonal.md` | Hexagonal (Ports & Adapters) | [docs/arch-hexagonal.md](docs/arch-hexagonal.md) |
| `benchmark-arch-ddd.md` | DDD Tático | [docs/arch-ddd.md](docs/arch-ddd.md) |
| `benchmark-arch-event-driven.md` | Event-Driven | [docs/arch-event-driven.md](docs/arch-event-driven.md) |
| `benchmark-arch-cqrs.md` | CQRS | [docs/arch-cqrs.md](docs/arch-cqrs.md) |

### Gerar relatórios HTML

```bash
# Experimento 1 — Java vs Kotlin
python metrics/report.py

# Experimento 2 — Arquiteturas (7 padrões)
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
│   ├── mvc/                          ← Exp. 2 MVC
│   ├── vertical-slice/               ← Exp. 2 Vertical Slice
│   ├── clean-architecture/           ← Exp. 2 Clean Architecture
│   ├── hexagonal/                    ← Exp. 2 Hexagonal
│   ├── ddd/                          ← Exp. 2 DDD Tático
│   ├── event-driven/                 ← Exp. 2 Event-Driven
│   └── cqrs/                         ← Exp. 2 CQRS
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

**Executado com `claude-sonnet-4-6` · 2026-06-06**  
Rode você mesmo e compare com os seus resultados.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

</div>
