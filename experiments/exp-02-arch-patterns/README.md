# Experimento 2 — Padrões Arquiteturais

> **Variável:** arquitetura (7 padrões) · **Constante:** Java 21 + Spring Boot 3.2, Claude Code `claude-sonnet-4-6`  
> **Pergunta:** qual padrão arquitetural a IA implementa com menor custo, menos erros e maior conformidade?

Todas as arquiteturas receberam PRDs detalhados com estrutura de pacotes obrigatória, regras de dependência explícitas e nomenclatura mandatória.

---

## Resultados

<table>
<tr>
<td align="center">

### 🔵 MVC

| | |
|---|---|
| 💰 Custo | **$1,73** |
| ⏱ Duração | **6,3 min** |
| 📡 API calls | **72** |
| 🐛 Erros | **5** |
| 📏 LOC prod. | **245** |
| 🎯 Cobertura | **93,0%** |
| 📁 Arquivos | **12** |
| 🏗 Conform. | **10/10** |
| ✅ E2E | **12/12** |

</td>
<td align="center">

### 🟢 Vertical Slice

| | |
|---|---|
| 💰 Custo | **$3,84** |
| ⏱ Duração | **5,4 min** |
| 📡 API calls | **80** |
| 🐛 Erros | **2** |
| 📏 LOC prod. | **310** |
| 🎯 Cobertura | **91,8%** |
| 📁 Arquivos | **23** |
| 🏗 Conform. | **10/10** |
| ✅ E2E | **12/12** |

</td>
<td align="center">

### 🟠 Clean Architecture

| | |
|---|---|
| 💰 Custo | **$3,18** |
| ⏱ Duração | **7,3 min** |
| 📡 API calls | **85** |
| 🐛 Erros | **1** |
| 📏 LOC prod. | **336** |
| 🎯 Cobertura | **97,0%** |
| 📁 Arquivos | **27** |
| 🏗 Conform. | **10/10** |
| ✅ E2E | **12/12** |

</td>
<td align="center">

### 🔴 Hexagonal

| | |
|---|---|
| 💰 Custo | **$2,92** |
| ⏱ Duração | **8,4 min** |
| 📡 API calls | **96** |
| 🐛 Erros | **6** |
| 📏 LOC prod. | **288** |
| 🎯 Cobertura | **93,6%** |
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
| 💰 Custo | **$2,33** |
| ⏱ Duração | **5,0 min** |
| 📡 API calls | **51** |
| 🐛 Erros | **1** |
| 📏 LOC prod. | **295** |
| 🎯 Cobertura | **88,0%** |
| 📁 Arquivos | **17** |
| 🏗 Conform. | **8/10** |
| ✅ E2E | **12/12** |

</td>
<td align="center">

### 🟡 Event-Driven

| | |
|---|---|
| 💰 Custo | **$2,22** |
| ⏱ Duração | **8,85 min** |
| 📡 API calls | **63** |
| 🐛 Erros | **5** |
| 📏 LOC prod. | **373** |
| 🎯 Cobertura | **90,0%** |
| 📁 Arquivos | **22** |
| 🏗 Conform. | **10/10** |
| ✅ E2E | **12/12** |

</td>
<td align="center">

### 🟣 CQRS

| | |
|---|---|
| 💰 Custo | **$3,27** |
| ⏱ Duração | **8,81 min** |
| 📡 API calls | **97** |
| 🐛 Erros | **2** |
| 📏 LOC prod. | **312** |
| 🎯 Cobertura | **95,0%** |
| 📁 Arquivos | **25** |
| 🏗 Conform. | **10/10** |
| ✅ E2E | **12/12** |

</td>
<td></td>
</tr>
</table>

---

## Tokens & Custo

| Métrica | 🔵 MVC | 🟢 V.Slice | 🟠 Clean | 🔴 Hexag. | 🟤 DDD | 🟡 Event-Dr. | 🟣 CQRS | Melhor |
|---------|:------:|:---------:|:--------:|:---------:|:------:|:------------:|:-------:|--------|
| Output tokens | 27.550 | 107.396 | 90.172 | 65.383 | 74.224 | 57.293 | 63.869 | 🔵 MVC 🏆 |
| Cache hit rate | 96,38% | 89,54% | 95,64% | 97,04% | 93,17% | 94,75% | 95,78% | 🔴 Hexag. |
| **Custo total** | $1,73 | $3,84 | $3,18 | $2,92 | $2,33 | **$2,22** | $3,27 | **🟡 Event-Dr. 🏆** |
| Custo/endpoint | $0,35 | $0,77 | $0,64 | $0,58 | $0,47 | **$0,44** | $0,65 | **🟡 Event-Dr. 🏆** |

**Ranking de custo:**

```
🟡 Event-Driven  ████████████░░░░░░░░  $2,22   ← mais barato 🏆
🔵 MVC           █████████░░░░░░░░░░░  $1,73   ← menos output tokens
🟤 DDD           ████████████░░░░░░░░  $2,33
🔴 Hexagonal     ███████████████░░░░░  $2,92
🟠 Clean Arch    ████████████████░░░░  $3,18
🟣 CQRS          █████████████████░░░  $3,27
🟢 Vertical Slice████████████████████  $3,84   ← mais caro
```

---

## Velocidade & Iterações

| Métrica | 🔵 MVC | 🟢 V.Slice | 🟠 Clean | 🔴 Hexag. | 🟤 DDD | 🟡 Event-Dr. | 🟣 CQRS | Melhor |
|---------|:------:|:---------:|:--------:|:---------:|:------:|:------------:|:-------:|--------|
| Duração (min) | 6,3 | 5,4 | 7,3 | 8,4 | **5,0** | 8,85 | 8,81 | 🟤 DDD 🏆 |
| Throughput (ep/h) | 47,7 | 55,9 | 41,0 | 35,7 | **60,0** | 33,9 | 34,1 | 🟤 DDD 🏆 |
| Total de turns | 45 | 49 | 52 | 55 | **37** | 47 | 68 | 🟤 DDD 🏆 |

---

## Erros de Desenvolvimento

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

---

## Qualidade de Código

| Métrica | 🔵 MVC | 🟢 V.Slice | 🟠 Clean | 🔴 Hexag. | 🟤 DDD | 🟡 Event-Dr. | 🟣 CQRS | Melhor |
|---------|:------:|:---------:|:--------:|:---------:|:------:|:------------:|:-------:|--------|
| LOC produção | **245** | 310 | 336 | 288 | 295 | 373 | 312 | 🔵 MVC 🏆 |
| Cobertura linha | 93% | 91,8% | **97%** | 93,6% | 88% | 90% | 95% | 🟠 Clean 🏆 |
| Cobertura branch | — | 75% | **100%** | 60,7% | — | — | 91,7% | 🟠 Clean 🏆 |

---

## Métricas de Arquitetura

| Métrica | 🔵 MVC | 🟢 V.Slice | 🟠 Clean | 🔴 Hexag. | 🟤 DDD | 🟡 Event-Dr. | 🟣 CQRS |
|---------|:------:|:---------:|:--------:|:---------:|:------:|:------------:|:-------:|
| Arquivos .java | 12 | 23 | **27** | 19 | 17 | 22 | **25** |
| Interfaces | 1 | 1 | **6** | **6** | 1 | **4** | 1 |
| Conformidade | 10/10 | 10/10 | 10/10 | 10/10 | **8/10** | 10/10 | 10/10 |
| Violações dep. | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

---

## Placar

| Categoria | 🔵 MVC | 🟢 V.Slice | 🟠 Clean | 🔴 Hexag. | 🟤 DDD | 🟡 Event-Dr. | 🟣 CQRS |
|-----------|:------:|:---------:|:--------:|:---------:|:------:|:------------:|:-------:|
| Custo total | | | | | | 🏆 **$2,22** | |
| Output tokens | 🏆 mais baixo | | | | | | |
| Velocidade | | | | | 🏆 **5 min / 60 ep/h** | | |
| Menos erros | | | 🏆 **1 erro** | | 🏆 **1 erro** | | |
| Cobertura | | | 🏆 **97% / 100% branch** | | | | |
| E2E | 🤝 | 🤝 | 🤝 | 🤝 | 🤝 | 🤝 | 🤝 |

---

## Por Que Esses Resultados?

**MVC domina em output tokens** — `@RestController → @Service → @Repository` está em incontáveis tutoriais. A IA escreve esse padrão quase de memória.

**Event-Driven mais barato no total** graças ao uso eficiente de cache. O padrão de publicar eventos é verboso mas repetitivo — cache read a $0,30/M vs output a $15/M.

**DDD mais rápido** porque Value Objects são um contrato claro. A IA completou em 37 turns vs 68 do CQRS. Perdeu 2 pontos de conformidade por não criar interfaces de use case.

**Clean Architecture menos erros** — a Dependency Rule é um guia preciso. As 4 camadas concêntricas com regras explícitas no PRD deram à IA uma "trilha" sem ambiguidade.

**Hexagonal mais erros (6)** — isolamento do domínio (zero imports Spring em `domain/`) e injeção por interfaces criam wiring complexo.

---

## Como Reproduzir

Abra o Claude Code na raiz do repo e execute o guia da arquitetura desejada:

```
"execute o experiments/exp-02-arch-patterns/guides/benchmark-arch-clean.md"
```

| Guia | Arquitetura | Guia Teórico |
|------|-------------|--------------|
| [`guides/benchmark-arch-mvc.md`](guides/benchmark-arch-mvc.md) | MVC | [shared/docs/arch-mvc.md](../../shared/docs/arch-mvc.md) |
| [`guides/benchmark-arch-vertical-slice.md`](guides/benchmark-arch-vertical-slice.md) | Vertical Slice | [shared/docs/arch-vertical-slice.md](../../shared/docs/arch-vertical-slice.md) |
| [`guides/benchmark-arch-clean.md`](guides/benchmark-arch-clean.md) | Clean Architecture | [shared/docs/arch-clean.md](../../shared/docs/arch-clean.md) |
| [`guides/benchmark-arch-hexagonal.md`](guides/benchmark-arch-hexagonal.md) | Hexagonal | [shared/docs/arch-hexagonal.md](../../shared/docs/arch-hexagonal.md) |
| [`guides/benchmark-arch-ddd.md`](guides/benchmark-arch-ddd.md) | DDD Tático | [shared/docs/arch-ddd.md](../../shared/docs/arch-ddd.md) |
| [`guides/benchmark-arch-event-driven.md`](guides/benchmark-arch-event-driven.md) | Event-Driven | [shared/docs/arch-event-driven.md](../../shared/docs/arch-event-driven.md) |
| [`guides/benchmark-arch-cqrs.md`](guides/benchmark-arch-cqrs.md) | CQRS | [shared/docs/arch-cqrs.md](../../shared/docs/arch-cqrs.md) |
