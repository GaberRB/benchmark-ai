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

---

## Modos de Execução

| Pasta | Linguagem | Modo |
|-------|-----------|------|
| `java-mode-1/` | Java | Agente único sequencial |
| `java-mode-2/` | Java | Orquestrador + 7 subagentes paralelos |
| `kotlin-mode-1/` | Kotlin | Agente único sequencial |
| `kotlin-mode-2/` | Kotlin | Orquestrador + 7 subagentes paralelos |

## Como Reproduzir

Abra o Claude Code na raiz do repo e execute o guia desejado:

```
"execute o experiments/exp-01-java-vs-kotlin/guides/benchmark-java-modo-1.md"
```

| Guia | Descrição |
|------|-----------|
| [`guides/benchmark-java-modo-1.md`](guides/benchmark-java-modo-1.md) | Java · agente sequencial |
| [`guides/benchmark-java-modo-2.md`](guides/benchmark-java-modo-2.md) | Java · orquestrador + subagentes |
| [`guides/benchmark-kotlin-modo-1.md`](guides/benchmark-kotlin-modo-1.md) | Kotlin · agente sequencial |
| [`guides/benchmark-kotlin-modo-2.md`](guides/benchmark-kotlin-modo-2.md) | Kotlin · orquestrador + subagentes |

Os resultados (JSON + HTML) são gerados em `results/` — ignorados pelo git (cada um gera os seus).
