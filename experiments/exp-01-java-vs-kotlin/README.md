# Experimento 1 — Java vs Kotlin

> **Variável:** linguagem · **Constante:** arquitetura MVC, Claude Code `claude-sonnet-4-6`  
> **Pergunta:** qual linguagem a IA implementa com menor custo, menos erros e mais qualidade?

---

## Resultados

<table>
<tr>
<td align="center" width="50%">

### ☕ Java

| | |
|---|---|
| 💰 Custo | **$1,46 USD** |
| ⏱ Duração | **5,4 min** |
| 📡 API calls | **50** |
| 🐛 Erros | **2** |
| 📏 LOC produção | **198** |
| 🎯 Cobertura linha | **89,1%** |
| ✅ E2E | **12 / 12** |

</td>
<td align="center" width="50%">

### 🟣 Kotlin

| | |
|---|---|
| 💰 Custo | **$3,50 USD** |
| ⏱ Duração | **10,7 min** |
| 📡 API calls | **83** |
| 🐛 Erros | **3** |
| 📏 LOC produção | **132** |
| 🎯 Cobertura linha | **94,3%** |
| ✅ E2E | **12 / 12** |

</td>
</tr>
</table>

---

## Tokens & Custo

| Métrica | ☕ Java | 🟣 Kotlin | Δ | Vencedor |
|---------|--------|---------|---|---------|
| Input tokens | 56 | 6.719 | Kotlin +11.898% | ☕ Java |
| Output tokens | 29.393 | 94.748 | Kotlin +222% | ☕ Java 🏆 |
| Cache creation | 107.782 | 209.024 | Kotlin +94% | ☕ Java |
| Cache read | 2.057.345 | 4.263.879 | Kotlin +107% | ☕ Java |
| Cache hit rate | 95,02% | 95,33% | ≈ empate | 🤝 |
| **Custo total** | **$1,4624** | **$3,5044** | **Kotlin +140%** | **☕ Java 🏆** |
| Custo por endpoint | $0,2925 | $0,7009 | Kotlin +140% | ☕ Java |

**Breakdown do custo:**

```
☕ Java  — $1,46 total
  Output tokens ████████████░░░░░░░░ $0,441  30,2%
  Cache read    █████████████████░░░ $0,617  42,2%
  Cache create  ███████████░░░░░░░░░ $0,404  27,6%

🟣 Kotlin — $3,50 total
  Output tokens ████████░░░░░░░░░░░░ $1,421  40,6%
  Cache read    ███████░░░░░░░░░░░░░ $1,279  36,5%
  Cache create  ████░░░░░░░░░░░░░░░░ $0,784  22,4%
```

---

## Velocidade & Iterações

| Métrica | ☕ Java | 🟣 Kotlin | Vencedor |
|---------|--------|---------|---------|
| Duração da sessão | **5,42 min** | 10,67 min | ☕ Java 🏆 |
| Tempo por endpoint | 1,08 min | 2,13 min | ☕ Java |
| Throughput | 55,35 ep/h | 28,12 ep/h | ☕ Java |
| Total de turns | **28** | 45 | ☕ Java |
| Tool calls | 27 | 44 | ☕ Java |

---

## Erros de Desenvolvimento

| Tipo | ☕ Java | 🟣 Kotlin |
|------|:------:|:--------:|
| Compilação | 1 | 2 |
| Runtime | 0 | 0 |
| Falhas de teste | 1 | 1 |
| **Total** | **2** | **3** |

---

## Qualidade de Código

| Métrica | ☕ Java | 🟣 Kotlin | Vencedor |
|---------|:------:|:-------:|---------|
| LOC produção | 198 | **132** | 🟣 Kotlin 🏆 |
| LOC testes | 261 | **244** | 🟣 Kotlin |
| Cobertura linha | 89,1% | **94,3%** | 🟣 Kotlin 🏆 |
| Cobertura branch | 81,3% | **85,7%** | 🟣 Kotlin 🏆 |

---

## Placar

| Categoria | ☕ Java | 🟣 Kotlin |
|-----------|:------:|:--------:|
| Custo | 🏆 2,4× mais barato | |
| Velocidade | 🏆 2× mais rápido | |
| Output tokens | 🏆 3,2× menos | |
| Erros | 🏆 menos 1 erro | |
| LOC (concisão) | | 🏆 33% menos linhas |
| Cobertura linha | | 🏆 +5,2pp (94,3%) |
| Cobertura branch | | 🏆 +4,4pp (85,7%) |
| E2E | 🤝 Empate | 🤝 Empate |

---

## Por Que Java Foi Mais Produtivo?

**Hipótese: densidade de dados de treinamento.**

Spring Boot com Java está presente em dezenas de milhões de arquivos públicos. O modelo
reconhece `@RestController`, `@Service`, `@SpringBootApplication` quase de memória.
Kotlin com Maven (em vez do Gradle padrão do Spring Initializr) adicionou atrito: o
`kotlin-maven-plugin` com `compilerPlugins: spring` aparece com muito menos frequência
nos exemplos públicos, forçando mais iterações.

**Essa hipótese foi confirmada pelo experimento Gradle abaixo:** com o `build.gradle.kts`
padrão do Spring Initializr, Kotlin superou Java em custo e velocidade.

---

## Modos de Execução

| Pasta | Linguagem | Build tool | Modo |
|-------|-----------|------------|------|
| `java-mode-1/` | Java | Maven | Agente único sequencial |
| `java-mode-2/` | Java | Maven | Orquestrador + 7 subagentes paralelos |
| `kotlin-mode-1/` | Kotlin | Maven | Agente único sequencial |
| `kotlin-mode-2/` | Kotlin | Maven | Orquestrador + 7 subagentes paralelos |
| `java-gradle-mode-1/` | Java | **Gradle** | Agente único sequencial |
| `kotlin-gradle-mode-1/` | Kotlin | **Gradle** | Agente único sequencial |

## Como Reproduzir

Abra o Claude Code na raiz do repo e execute o guia desejado:

```
"execute o experiments/exp-01-java-vs-kotlin/guides/benchmark-java-modo-1.md"
```

| Guia | Descrição |
|------|-----------|
| [`guides/benchmark-java-modo-1.md`](guides/benchmark-java-modo-1.md) | Java · Maven · agente sequencial |
| [`guides/benchmark-java-modo-2.md`](guides/benchmark-java-modo-2.md) | Java · Maven · orquestrador + subagentes |
| [`guides/benchmark-kotlin-modo-1.md`](guides/benchmark-kotlin-modo-1.md) | Kotlin · Maven · agente sequencial |
| [`guides/benchmark-kotlin-modo-2.md`](guides/benchmark-kotlin-modo-2.md) | Kotlin · Maven · orquestrador + subagentes |
| [`guides/benchmark-java-gradle-modo-1.md`](guides/benchmark-java-gradle-modo-1.md) | Java · **Gradle** · agente sequencial |
| [`guides/benchmark-kotlin-gradle-modo-1.md`](guides/benchmark-kotlin-gradle-modo-1.md) | Kotlin · **Gradle** · agente sequencial |

Os resultados (JSON + HTML) são gerados em `tools/reports/` — ignorados pelo git (cada um gera os seus).

---

## Variante Gradle — Java vs Kotlin

> Build tool: **Gradle 8.13** · Mesmo modelo (`claude-sonnet-4-6`) e arquitetura MVC

<table>
<tr>
<td align="center" width="50%">

### ☕ Java Gradle

| | |
|---|---|
| 💰 Custo | **$2,18 USD** |
| ⏱ Duração | **5,4 min** |
| 📡 API calls | **58** |
| 🐛 Erros | **1** |
| 📏 LOC produção | **188** |
| 🎯 Cobertura linha | **93,0%** |
| 🌿 Cobertura branch | **95,0%** |
| ✅ E2E | **12 / 12** |

</td>
<td align="center" width="50%">

### 🟣 Kotlin Gradle

| | |
|---|---|
| 💰 Custo | **$1,93 USD** |
| ⏱ Duração | **4,51 min** |
| 📡 API calls | **61** |
| 🐛 Erros | **3** |
| 📏 LOC produção | **142** |
| 🎯 Cobertura linha | **94,1%** |
| 🌿 Cobertura branch | **93,75%** |
| ✅ E2E | **12 / 12** |

</td>
</tr>
</table>

### Tokens & Custo — Gradle

| Métrica | ☕ Java Gradle | 🟣 Kotlin Gradle | Vencedor |
|---------|--------------|----------------|---------|
| Output tokens | 66.538 | **40.470** | 🟣 Kotlin 🏆 |
| Cache creation | **137.332** | 165.336 | ☕ Java |
| Cache read | **2.216.991** | 2.355.940 | ☕ Java |
| Cache hit rate | **94,17%** | 93,44% | ☕ Java |
| **Custo total** | $2,18 | **$1,93** | **🟣 Kotlin 🏆** |

### Placar — Gradle

| Categoria | ☕ Java Gradle | 🟣 Kotlin Gradle |
|---|---|---|
| Custo | | 🏆 12% mais barato |
| Velocidade | | 🏆 16% mais rápido |
| Erros de build | 🏆 apenas 1 | |
| LOC (concisão) | | 🏆 24% menos linhas |
| Cobertura linha | | 🏆 +1,1pp (94,1%) |
| Cobertura branch | 🏆 95,0% | |
| E2E | 🤝 Empate | 🤝 Empate |

---

## Maven vs Gradle — Impacto da Build Tool

| Variante | Custo | Duração | Erros | LOC prod | Cob. linha | Cob. branch |
|---|---|---|---|---|---|---|
| ☕ Java Maven | **$1,46** 🏆 | 5,4 min | 2 | 198 | 89,1% | 81,3% |
| ☕ Java Gradle | $2,18 | 5,4 min | **1** 🏆 | 188 | 93,0% | **95,0%** 🏆 |
| 🟣 Kotlin Maven | $3,50 | 10,7 min | 3 | **132** | 94,3% | 85,7% |
| 🟣 Kotlin Gradle | $1,93 | **4,51 min** 🏆 | 3 | 142 | **94,1%** | 93,75% |

Kotlin Maven custou **140% mais** que Java Maven. Com Gradle, a diferença desaparece — Kotlin Gradle foi
até mais barato que Java Gradle. A variável que mudou o resultado não foi a linguagem, foi a build tool.

---

## Minha Análise — Por Que o Gradle Mudou Tudo para o Kotlin?

**Por que Kotlin Maven foi tão caro e lento?**

O `pom.xml` do Kotlin com Maven exige uma configuração específica e pouco usual: o `kotlin-maven-plugin`
com `<execution>compile</execution>` e `<execution>test-compile</execution>` explícitas, o
`kotlin-maven-allopen` como dependência do próprio plugin, e `compilerPlugins: spring` dentro de
`<configuration>`. Essa estrutura não é gerada pelo Spring Initializr — que usa Gradle por padrão
para Kotlin. O modelo provavelmente viu essa combinação poucas vezes nos dados de treinamento, o que
gerou mais tentativas, mais correções e mais tokens gastos.

**Por que Kotlin Gradle funcionou melhor?**

O `build.gradle.kts` com `kotlin("plugin.spring")` é exatamente o que o Spring Initializr gera. Todo
projeto Kotlin + Spring Boot iniciado via start.spring.io usa esse padrão. O modelo reconheceu a
configuração quase de memória: `kotlin("jvm")` + `kotlin("plugin.spring")`, sem execuções manuais nem
dependências de plugin extras. Menos fricção → menos iterações → menos custo.

**Por que Java Maven ainda vence em custo absoluto?**

Java + Maven é a combinação mais representada nos dados de treinamento. O Spring Boot Tutorial oficial,
Baeldung, Stack Overflow, GitHub — a esmagadora maioria dos exemplos usa `pom.xml` + Java. O modelo
literalmente reconhece essa configuração sem hesitar. Qualquer desvio desse padrão canônico aumenta
o atrito, mesmo que pequeno.

**O que esse resultado sugere para benchmarks futuros?**

A ferramenta de build não é neutra — ela muda a dificuldade percebida pelo modelo. Benchmarks de
linguagem precisam controlar a build tool separadamente para isolar o efeito da linguagem. Se você
testasse apenas Maven, concluiria que Kotlin é 140% mais caro que Java. Se testasse apenas Gradle,
concluiria que são praticamente equivalentes — Kotlin até ligeiramente mais barato. A variável era
a ferramenta de build, não a linguagem.
