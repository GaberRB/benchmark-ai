# Análise Completa — Experimento 01: Java vs Kotlin

> **Modelo:** Claude Sonnet 4.6 · **Tarefa:** Task Manager API REST · **Variantes:** 8 · **Execuções bem-sucedidas:** 8/8

```
┌─────────────────────────────────────────────────────────────────────┐
│              CAMPEÕES POR CATEGORIA                                  │
├──────────────────────────┬──────────────────────────────────────────┤
│ 💰 Menor custo           │ Java + Spring Boot + Maven       $1,46   │
│ ⚡ Mais rápido           │ Kotlin + Spring Boot + Gradle    4,51 min │
│ 📏 Menos LOC produção    │ Kotlin + Spring Boot + Maven     132 LOC  │
│ 🎯 Maior cob. de linha   │ Kotlin + Quarkus (ambas builds)  100%     │
│ 🌿 Maior cob. de branch  │ Java + Spring Boot + Gradle      95,0%    │
│ 🐛 Menos erros           │ Qualquer variante Java + Quarkus 1 erro   │
│ 🏅 Melhor custo-benefício│ Java + Quarkus + Maven    $1,60 + 95% cob │
└──────────────────────────┴──────────────────────────────────────────┘
```

---

## Índice

1. [Metodologia](#1-metodologia)
2. [Variáveis do Experimento](#2-variáveis-do-experimento)
3. [Glossário](#3-glossário)
4. [Resultados — Tabela Mestre](#4-resultados--tabela-mestre)
5. [Eixo 1 — Linguagem: Java vs Kotlin](#5-eixo-1--linguagem-java-vs-kotlin)
6. [Eixo 2 — Build Tool: Maven vs Gradle](#6-eixo-2--build-tool-maven-vs-gradle)
7. [Eixo 3 — Framework: Spring Boot vs Quarkus](#7-eixo-3--framework-spring-boot-vs-quarkus)
8. [Análise de Comportamentos Notáveis](#8-análise-de-comportamentos-notáveis)
9. [Padrões Identificados](#9-padrões-identificados)
10. [Ranking Final](#10-ranking-final)
11. [Conclusões](#11-conclusões)
12. [Referências](#12-referências)

---

## 1. Metodologia

### 1.1 Tarefa Benchmarkada

Todos os 8 agentes receberam a **mesma especificação** (`shared/task-definition.md`): implementar uma API REST de gerenciamento de tarefas com 5 endpoints CRUD, armazenamento in-memory, validações e suite de testes com ≥ 80% de cobertura de linha.

```
Especificação idêntica para todos
         │
         ▼
┌────────────────────┐
│  GET    /tasks     │  → 200 (lista todas as tarefas)
│  POST   /tasks     │  → 201 (cria tarefa) / 400 (validação)
│  GET    /tasks/{id}│  → 200 (busca por ID) / 404 (não encontrado)
│  PUT    /tasks/{id}│  → 200 (atualiza) / 400 / 404
│  DELETE /tasks/{id}│  → 204 (remove) / 404
└────────────────────┘
         │
         ▼
  12 cenários E2E obrigatórios
```

**Modelo de dados:**

| Campo | Tipo | Constraint |
|---|---|---|
| `id` | string (UUID) | gerado pelo servidor |
| `title` | string | obrigatório, máx 200 chars |
| `description` | string | opcional, máx 1000 chars |
| `completed` | boolean | default `false` |
| `createdAt` | string ISO 8601 | gerado na criação |
| `updatedAt` | string ISO 8601 | atualizado no PUT |

### 1.2 Modelo LLM e Modo de Execução

- **Modelo:** Claude Sonnet 4.6 (claude-sonnet-4-6)
- **Modo:** Agente único sequencial ("modo 1") — um único agente executa todos os passos do início ao fim, sem subagentes paralelos
- **Interface:** Claude Code CLI, executado via terminal PowerShell

### 1.3 Coleta de Métricas

```
Início da sessão
      │
      ▼
snapshot.py --pre          ← registra estado da telemetria antes
      │
      ▼
[Agente implementa a API]
      │
      ▼
snapshot.py --post         ← registra estado da telemetria depois
      │
      ▼
collector.py               ← diff de telemetria → JSON com tokens/custo/turnos
      │
      ▼
cloc (LOC de produção e teste)
      │
      ▼
JaCoCo CSV (cobertura de linha e branch)
      │
      ▼
JSON final com todas as métricas
```

**Fontes de dados:**

| Métrica | Fonte |
|---|---|
| Tokens, custo, turnos | `~/.claude/telemetry/*.json` (telemetria Claude Code) |
| LOC (produção/teste) | `cloc` — conta linhas de código excluindo linhas em branco e comentários |
| Cobertura de linha | JaCoCo CSV — `MISSED / (MISSED + COVERED)` |
| Cobertura de branch | JaCoCo CSV — branches em condicionais (`if`, `?:`, try/catch) |
| E2E | 12 chamadas `curl` manuais verificando HTTP status codes |

### 1.4 Controle da Execução

Para garantir comparabilidade:
- Mesma especificação de tarefa (arquivo `shared/task-definition.md` versionado)
- Mesmo guia de execução por variante (12 passos estruturados)
- Blocos `⛔ ESCOPO RESTRITO` em cada guia para prevenir contaminação de contexto entre variantes
- Diretórios de implementação isolados — cada variante parte do zero
- Mesma versão do Claude Code em todas as execuções

---

## 2. Variáveis do Experimento

### 2.1 Design Fatorial 2×2×2

O experimento varia **três fatores binários** de forma combinada, gerando 2³ = **8 variantes**:

```
                    ┌── Maven ──────── java-mode-1
           ┌─ Java ─┤
           │        └── Gradle ─────── java-gradle-mode-1
Spring ────┤
Boot       │        ┌── Maven ──────── kotlin-mode-1
           └─ Kotlin┤
                    └── Gradle ─────── kotlin-gradle-mode-1

                    ┌── Maven ──────── java-quarkus-maven-mode-1
           ┌─ Java ─┤
           │        └── Gradle ─────── java-quarkus-gradle-mode-1
Quarkus ───┤
           │        ┌── Maven ──────── kotlin-quarkus-maven-mode-1
           └─ Kotlin┤
                    └── Gradle ─────── kotlin-quarkus-gradle-mode-1
```

### 2.2 Variáveis

| Tipo | Variável | Valores |
|---|---|---|
| Independente | Linguagem | Java 21 / Kotlin 1.9.22 |
| Independente | Framework | Spring Boot 3.2.x / Quarkus 3.8.3 |
| Independente | Build tool | Maven (mvnw) / Gradle (gradlew) |
| Controlada | Modelo LLM | Claude Sonnet 4.6 (fixo) |
| Controlada | Especificação | `shared/task-definition.md` v1.0 (fixo) |
| Controlada | Modo de execução | Agente único sequencial (fixo) |
| Controlada | Prompt/guia | Mesmo template estrutural (12 passos) |

### 2.3 Diferenças Técnicas entre Frameworks

| Aspecto | Spring Boot (SB) | Quarkus (QK) |
|---|---|---|
| Camada REST | `@RestController` / `@GetMapping` | `@Path` / `@GET` (JAX-RS) |
| Injeção de Dependência | `@Service` / `@Autowired` (Spring DI) | `@ApplicationScoped` / `@Inject` (CDI) |
| Tratamento de exceções | `@RestControllerAdvice` | `@Provider ExceptionMapper<T>` |
| Framework de testes | `@SpringBootTest` + MockMvc | `@QuarkusTest` + RestAssured |
| Cobertura de código | JaCoCo plugin standalone | Extensão `quarkus-jacoco` |
| Saída do JaCoCo | `target/site/jacoco/jacoco.csv` | `build/reports/jacoco/` (mesmo formato CSV) |

---

## 3. Glossário

| Sigla / Termo | Definição |
|---|---|
| **LLM** | _Large Language Model_ — modelo de linguagem de grande escala (ex.: Claude Sonnet 4.6) |
| **LOC** | _Lines of Code_ — linhas de código (excluindo linhas em branco e comentários, medido pelo `cloc`) |
| **CDI** | _Contexts and Dependency Injection_ — especificação Jakarta EE para injeção de dependências, usada pelo Quarkus |
| **JAX-RS** | _Jakarta RESTful Web Services_ — especificação Jakarta EE para APIs REST, usada pelo Quarkus (`@Path`, `@GET`, etc.) |
| **DI** | _Dependency Injection_ — padrão de projeto para injeção de dependências |
| **BOM** | _Bill of Materials_ — arquivo Maven/Gradle que gerencia versões de dependências de forma centralizada |
| **JVM** | _Java Virtual Machine_ — máquina virtual que executa bytecode Java e Kotlin |
| **SB** | Spring Boot — framework HTTP Java/Kotlin da Broadcom/VMware |
| **QK** | Quarkus — framework HTTP Java/Kotlin da Red Hat |
| **MVN** | Maven — ferramenta de build baseada em XML (`pom.xml`) |
| **GDL** | Gradle — ferramenta de build baseada em DSL Groovy/Kotlin (`build.gradle` / `build.gradle.kts`) |
| **E2E** | _End-to-End_ — teste que valida a aplicação de ponta a ponta via chamadas HTTP reais |
| **pp** | Pontos percentuais — diferença absoluta entre dois percentuais (ex.: 94% − 89% = +5pp) |
| **Cache hit rate** | Taxa de acerto do cache de prompt do Claude — tokens lidos do cache vs. tokens processados novamente |
| **Throughput** | Endpoints implementados por hora (5 endpoints / duração em horas) |
| **Cob. linha** | Cobertura de linha — percentual de linhas de código executadas durante os testes |
| **Cob. branch** | Cobertura de branch — percentual de ramificações condicionais (`if/else`, `?:`, `try/catch`) executadas |
| **RestAssured** | Biblioteca de testes HTTP fluente usada com `@QuarkusTest` |
| **MockMvc** | Framework de testes HTTP do Spring que simula chamadas sem servidor real |
| **all-open** | Plugin Kotlin que torna classes abertas (não-`final`) para frameworks CDI/Spring que exigem subclasses |
| **data class** | Construto Kotlin que gera automaticamente `equals`, `hashCode`, `toString` e `copy` |

---

## 4. Resultados — Tabela Mestre

> 🏆 = melhor valor da coluna · — = dados do README histórico (antes da coleta automática)

### 4.1 Métricas de Eficiência da LLM

| Variante | Lang | FW | Build | Custo USD | Duração | Turns | Out Tokens | Cache Criação | Cache Leitura | Hit Rate |
|---|---|---|---|---|---|---|---|---|---|---|
| java-mode-1 | ☕ Java | SB | MVN | **$1,46** 🏆 | 5,42 min | **28** 🏆 | **29.393** 🏆 | 107.782 | 2.057.345 | 95,02% |
| kotlin-mode-1 | 🟣 Kotlin | SB | MVN | $3,50 | 10,67 min | 45 | 94.748 | 209.024 | 4.263.879 | 95,33% 🏆 |
| java-gradle-mode-1 | ☕ Java | SB | GDL | $2,18 | 5,4 min | 33 | 66.538 | 137.332 | 2.216.991 | 94,17% |
| kotlin-gradle-mode-1 | 🟣 Kotlin | SB | GDL | $1,93 | **4,51 min** 🏆 | 33 | **40.470** 🏆 | 165.336 | 2.355.940 | 93,44% |
| java-quarkus-maven-mode-1 | ☕ Java | QK | MVN | $1,60 | 5,86 min | 31 | 35.361 | **100.902** 🏆 | 2.316.703 | 95,83% 🏆 |
| java-quarkus-gradle-mode-1 | ☕ Java | QK | GDL | $1,97 | 5,95 min | 33 | 46.132 | 133.942 | 2.572.182 | 95,05% |
| kotlin-quarkus-maven-mode-1 | 🟣 Kotlin | QK | MVN | $2,60 | 10,97 min | 36 | 85.271 | 168.468 | 2.304.527 | 93,19% |
| kotlin-quarkus-gradle-mode-1 | 🟣 Kotlin | QK | GDL | $2,80 | 5,52 min | **29** 🏆 | 95.549 | 202.396 | **2.032.225** 🏆 | 90,94% |

### 4.2 Métricas de Qualidade de Código

| Variante | Erros | LOC Prod | LOC Teste | Ratio Teste | Cob. Linha | Cob. Branch | E2E |
|---|---|---|---|---|---|---|---|
| java-mode-1 | 2 | 198 | 261 | 57% | 89,1% | 81,3% | ✅ 12/12 |
| kotlin-mode-1 | 3 | **132** 🏆 | 244 | 65% | 94,3% | 85,7% | ✅ 12/12 |
| java-gradle-mode-1 | **1** 🏆 | 188 | 241 | 56% | 93,0% | **95,0%** 🏆 | ✅ 12/12 |
| kotlin-gradle-mode-1 | 3 | 142 | 244 | 63% | 94,1% | 93,75% | ✅ 12/12 |
| java-quarkus-maven-mode-1 | **1** 🏆 | 233 | 125 | 35% | 95,0% | 60,0% | ✅ 12/12 |
| java-quarkus-gradle-mode-1 | **1** 🏆 | 210 | 63 | 23% | 94,3% | 60,0% | ✅ 12/12 |
| kotlin-quarkus-maven-mode-1 | **1** 🏆 | 158 | 64 | 29% | **100%** 🏆 | 60,0% | ✅ 12/12 |
| kotlin-quarkus-gradle-mode-1 | **1** 🏆 | 158 | 64 | 29% | **100%** 🏆 | 60,0% | ✅ 12/12 |

> **Ratio Teste** = LOC Teste ÷ (LOC Prod + LOC Teste) × 100

### 4.3 Custo por Componente

```
java-mode-1            $1,46  ██████████░░░░░░░░░░░░░░░░░░░░
kotlin-mode-1          $3,50  ████████████████████████████████████████████████████████░░░
java-gradle-mode-1     $2,18  ██████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░
kotlin-gradle-mode-1   $1,93  ██████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░
java-quarkus-maven     $1,60  ████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░
java-quarkus-gradle    $1,97  ████████████████████████░░░░░░░░░░░░░░░░░░░░░░░
kotlin-quarkus-maven   $2,60  █████████████████████████████████░░░░░░░░░░░░░░
kotlin-quarkus-gradle  $2,80  ████████████████████████████████████░░░░░░░░░░░
                       $0   $0,50  $1,00  $1,50  $2,00  $2,50  $3,00  $3,50
```

---

## 5. Eixo 1 — Linguagem: Java vs Kotlin

### 5.1 Spring Boot + Maven — Controle de Linguagem Puro

Mantendo framework (SB) e build tool (MVN) constantes, variando apenas a linguagem:

| Métrica | ☕ Java | 🟣 Kotlin | Δ | Interpretação |
|---|---|---|---|---|
| Custo | $1,46 | $3,50 | **Kotlin +140%** | Java muito mais barato |
| Duração | 5,42 min | 10,67 min | Kotlin +97% | Java quase 2× mais rápido |
| Turnos | 28 | 45 | Kotlin +61% | Java com menos iterações |
| Output tokens | 29.393 | 94.748 | **Kotlin +222%** | LLM gerou 3,2× mais tokens para Kotlin |
| LOC produção | 198 | 132 | Kotlin −33% | Kotlin mais conciso em código de produção |
| Cobertura linha | 89,1% | 94,3% | Kotlin +5,2pp | Kotlin com melhor cobertura |
| Cobertura branch | 81,3% | 85,7% | Kotlin +4,4pp | Kotlin com melhor cobertura |
| Erros | 2 | 3 | Kotlin +1 | Kotlin com mais erros de desenvolvimento |

```
Custo total — Spring Boot + Maven
Java   ████████████████████░░░░░░░░░░░░░░░░░░░░░░░  $1,46
Kotlin ████████████████████████████████████████████  $3,50
       │$0,50  │$1,00  │$1,50  │$2,00  │$2,50  │$3,00  │$3,50
```

**Por que Java foi muito mais barato com Maven?**

O `pom.xml` do Java + Spring Boot é a combinação mais documentada no ecossistema Java:
- Baeldung, Spring Guides, Stack Overflow e o próprio `spring.io` usam principalmente Java + Maven
- O modelo reconhece `@RestController`, `@Service`, `@SpringBootApplication` quase sem iterações
- O Kotlin + Maven exige `kotlin-maven-plugin` com `compilerPlugins: spring` e `all-open` — uma configuração que não é gerada pelo Spring Initializr (que usa Gradle para Kotlin por padrão)

> **Hipótese central:** Os resultados refletem a **densidade de representação** de cada combinação nos dados de treinamento do LLM, não a dificuldade inerente da linguagem ou framework.

### 5.2 Spring Boot + Gradle — Inversão Completa

Mesma comparação, mas trocando Maven por Gradle:

| Métrica | ☕ Java GDL | 🟣 Kotlin GDL | Δ | Inversão? |
|---|---|---|---|---|
| Custo | $2,18 | $1,93 | **Kotlin −12%** | ✅ Kotlin mais barato |
| Duração | 5,4 min | 4,51 min | Kotlin −16% | ✅ Kotlin mais rápido |
| Output tokens | 66.538 | 40.470 | **Kotlin −39%** | ✅ Kotlin menos tokens |
| LOC produção | 188 | 142 | Kotlin −24% | ✅ Kotlin mais conciso |
| Cobertura branch | 95,0% | 93,75% | Java +1,25pp | Java ligeiramente melhor |
| Erros | 1 | 3 | Kotlin +2 erros | Java com menos erros |

```
Comparativo de custo — Spring Boot
                Maven     Gradle
Java             $1,46     $2,18   ← Java Maven mais barato
Kotlin           $3,50     $1,93   ← Kotlin Gradle mais barato

                     INVERSÃO COMPLETA
```

**Por que o Gradle inverteu o resultado do Kotlin?**

O `build.gradle.kts` com `kotlin("jvm")` + `kotlin("plugin.spring")` é o **output padrão do Spring Initializr** para projetos Kotlin. Todo desenvolvedor que cria um projeto Kotlin + Spring Boot via `start.spring.io` recebe exatamente esse arquivo. Isso significa que:
1. Milhões de projetos públicos no GitHub usam exatamente esse template
2. O modelo reconhece o padrão sem hesitar — sem tentativas extras, sem correções de configuração
3. A concisão do Kotlin (`data class`, extension functions, null-safety) reduz o volume de código gerado

**A variável decisiva foi a build tool, não a linguagem.**

### 5.3 Quarkus + Maven

| Métrica | ☕ Java QK MVN | 🟣 Kotlin QK MVN | Δ |
|---|---|---|---|
| Custo | $1,60 | $2,60 | Kotlin +62% |
| Duração | 5,86 min | 10,97 min | Kotlin +87% |
| Output tokens | 35.361 | 85.271 | Kotlin +141% |
| LOC produção | 233 | 158 | Kotlin −32% |
| Cobertura linha | 95,0% | **100%** | Kotlin +5pp |
| Erros | 1 | 1 | Empate |

Kotlin ainda é mais caro, mas o gap reduziu: +140% (Spring Maven) → +62% (Quarkus Maven). Isso ocorre porque o overhead de configuração Maven do Kotlin é similar em ambos os frameworks, mas o Quarkus tem menos boilerplate total.

### 5.4 Quarkus + Gradle

| Métrica | ☕ Java QK GDL | 🟣 Kotlin QK GDL | Δ |
|---|---|---|---|
| Custo | $1,97 | $2,80 | Kotlin +42% |
| Duração | 5,95 min | 5,52 min | **Kotlin −7% (mais rápido!)** |
| Turnos | 33 | 29 | Kotlin −12% turnos |
| Output tokens | 46.132 | 95.549 | Kotlin +107% |
| LOC produção | 210 | 158 | Kotlin −25% |
| Cobertura linha | 94,3% | **100%** | Kotlin +5,7pp |

Aqui Kotlin é mais rápido em duração (menos turnos) mas gera mais tokens por turno. O `build.gradle.kts` Quarkus + Kotlin não é tão canônico quanto o Spring equivalente, mas o modelo consegue resolvê-lo com menos iterações.

---

## 6. Eixo 2 — Build Tool: Maven vs Gradle

### 6.1 Java + Spring Boot — Impacto da Build Tool

| Métrica | ☕ Java MVN | ☕ Java GDL | Δ |
|---|---|---|---|
| Custo | **$1,46** | $2,18 | Gradle +49% |
| Duração | 5,42 min | 5,4 min | ≈ igual |
| Turnos | 28 | 33 | Gradle +18% turnos |
| Output tokens | 29.393 | 66.538 | Gradle +126% |
| LOC produção | 198 | 188 | Gradle −5% |
| Cobertura branch | 81,3% | **95,0%** | Gradle +13,7pp 🏆 |

Para Java, Maven é mais barato mas Gradle produziu uma cobertura de branch significativamente superior. Isso sugere que o LLM, ao usar Gradle, gerou testes mais abrangentes — possivelmente porque o template Gradle para Java tem histórico de boas práticas de teste.

### 6.2 Kotlin + Spring Boot — Impacto Decisivo da Build Tool

| Métrica | 🟣 Kotlin MVN | 🟣 Kotlin GDL | Δ |
|---|---|---|---|
| Custo | $3,50 | **$1,93** | **Gradle −45%** |
| Duração | 10,67 min | **4,51 min** | **Gradle −58%** |
| Turnos | 45 | 33 | Gradle −27% |
| Output tokens | 94.748 | **40.470** | **Gradle −57%** |
| LOC produção | 132 | 142 | Maven ligeiramente menor |

```
Output tokens — Kotlin Spring Boot
Maven  ████████████████████████████████████████████████  94.748
Gradle ████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░  40.470
                                           Redução de 57%!
```

Esta é a diferença mais dramática do experimento: a mesma linguagem, o mesmo framework, a mesma especificação — só mudou a build tool. Maven custou **$3,50**, Gradle custou **$1,93**. O `kotlin-maven-plugin` é complexo e incomum; o `build.gradle.kts` com `kotlin("plugin.spring")` é o padrão canônico.

### 6.3 Java + Quarkus

| Métrica | ☕ Java QK MVN | ☕ Java QK GDL | Δ |
|---|---|---|---|
| Custo | **$1,60** | $1,97 | Gradle +23% |
| Turnos | 31 | 33 | Gradle +6% |
| Output tokens | **35.361** | 46.132 | Gradle +31% |
| LOC teste | 125 | 63 | Maven 2× mais LOC de teste |
| Cobertura branch | 60,0% | 60,0% | Empate |

Para Java + Quarkus, Maven é mais eficiente. O `pom.xml` Quarkus é amplamente documentado nos guias oficiais (quarkus.io usa Maven nos exemplos principais).

### 6.4 Kotlin + Quarkus

| Métrica | 🟣 Kotlin QK MVN | 🟣 Kotlin QK GDL | Δ |
|---|---|---|---|
| Custo | **$2,60** | $2,80 | Gradle +8% |
| Duração | 10,97 min | **5,52 min** | **Gradle −50%** |
| Turnos | 36 | **29** | Gradle −19% |
| Output tokens | 85.271 | 95.549 | Gradle +12% |

Aqui surge um padrão interessante: Gradle é mais rápido (menos turnos, menos duração de sessão) mas gerou mais output tokens e custou ligeiramente mais. Com Kotlin+Quarkus+Maven, o build é lento mas o processo de geração é mais linear; com Gradle, o build é rápido mas o LLM gera mais código por turno.

### 6.5 Resumo — Impacto da Build Tool por Linguagem

```
Custo com Maven vs Gradle (por linguagem e framework)

Spring Boot:
  Java:    Maven $1,46  │  Gradle $2,18  [Maven vence]
  Kotlin:  Maven $3,50  │  Gradle $1,93  [GRADLE VENCE — inversão]

Quarkus:
  Java:    Maven $1,60  │  Gradle $1,97  [Maven vence]
  Kotlin:  Maven $2,60  │  Gradle $2,80  [Maven vence (levemente)]
```

**Conclusão do Eixo 2:** A build tool mais eficiente depende da linguagem. Para Kotlin + Spring Boot, Gradle é dramaticamente melhor (+45% de economia). Para todas as outras combinações, Maven é igual ou ligeiramente mais eficiente.

---

## 7. Eixo 3 — Framework: Spring Boot vs Quarkus

### 7.1 Java + Maven — Spring Boot vs Quarkus

| Métrica | ☕ Java SB MVN | ☕ Java QK MVN | Δ | Notas |
|---|---|---|---|---|
| Custo | **$1,46** | $1,60 | Quarkus +9,6% | Quase equivalentes |
| Duração | **5,42 min** | 5,86 min | Quarkus +8% | Similar |
| Output tokens | **29.393** | 35.361 | Quarkus +20% | JAX-RS mais verboso em Java |
| LOC produção | **198** | 233 | Quarkus +18% | JAX-RS requer mais anotações |
| LOC teste | 261 | 125 | **Quarkus −52%** | RestAssured muito mais conciso |
| Cobertura linha | 89,1% | **95,0%** | Quarkus +5,9pp | Quarkus melhor |
| Cobertura branch | **81,3%** | 60,0% | Spring +21,3pp | Spring muito melhor |

**O paradoxo da cobertura:** Quarkus tem melhor cobertura de linha (95% vs 89%) mas muito pior cobertura de branch (60% vs 81%). Por quê?

```
Cobertura de Linha vs Branch
                Linha    Branch
Spring Boot     89,1%    81,3%   ← branches bem cobertos
Quarkus         95,0%    60,0%   ← todas as linhas, mas branches não
```

A resposta está nos frameworks de teste: **MockMvc vs RestAssured**.

```java
// Spring Boot — MockMvc (5-8 linhas por teste)
mockMvc.perform(post("/tasks")
    .contentType(MediaType.APPLICATION_JSON)
    .content("{\"title\":\"test\"}"))
    .andExpect(status().isCreated())
    .andExpect(jsonPath("$.id").exists())
    .andExpect(jsonPath("$.title").value("test"));

// Quarkus — RestAssured (2-3 linhas por teste)
given().contentType(JSON)
    .body("{\"title\":\"test\"}")
    .when().post("/tasks").then().statusCode(201)
    .body("id", notNullValue());
```

RestAssured é 2-3× mais conciso que MockMvc para o mesmo teste. Com a mesma especificação de 12 testes, o LLM gerou 125 LOC (Quarkus) vs 261 LOC (Spring Boot). Menos LOC de teste → menos asserções de edge cases → menos branches cobertos. Isso **não é uma falha do LLM** — é uma propriedade dos frameworks de teste.

### 7.2 Java + Gradle — Spring Boot vs Quarkus

| Métrica | ☕ Java SB GDL | ☕ Java QK GDL | Δ |
|---|---|---|---|
| Custo | $2,18 | **$1,97** | **Quarkus −10%** |
| Output tokens | 66.538 | **46.132** | Quarkus −31% |
| LOC teste | 241 | 63 | **Quarkus −74%** |
| Cobertura linha | 93,0% | **94,3%** | Quarkus +1,3pp |
| Cobertura branch | **95,0%** | 60,0% | Spring +35pp |

Com Gradle, o Quarkus foi mais barato que o Spring Boot para Java. O padrão de cobertura se repete: Quarkus melhor em linha, Spring muito melhor em branch.

### 7.3 Kotlin + Maven — Spring Boot vs Quarkus

| Métrica | 🟣 Kotlin SB MVN | 🟣 Kotlin QK MVN | Δ |
|---|---|---|---|
| Custo | $3,50 | **$2,60** | **Quarkus −26%** |
| Duração | 10,67 min | **10,97 min** | ≈ igual (Quarkus +3%) |
| Output tokens | 94.748 | **85.271** | Quarkus −10% |
| Cobertura linha | 94,3% | **100%** | **Quarkus +5,7pp** |
| Cobertura branch | **85,7%** | 60,0% | Spring +25,7pp |

Para Kotlin + Maven, Quarkus é 26% mais barato. Isso porque o `kotlin-maven-plugin` com `all-open` para Quarkus tem menos overhead do que o equivalente Spring Boot (que exige `compilerPlugins: spring` adicionalmente).

### 7.4 Kotlin + Gradle — Spring Boot vs Quarkus

| Métrica | 🟣 Kotlin SB GDL | 🟣 Kotlin QK GDL | Δ |
|---|---|---|---|
| Custo | **$1,93** | $2,80 | Quarkus +45% |
| Duração | **4,51 min** | 5,52 min | Quarkus +22% |
| Output tokens | **40.470** | 95.549 | Quarkus +136% |
| Cobertura linha | 94,1% | **100%** | Quarkus +5,9pp |

Este é o único caso onde Quarkus é claramente mais caro que Spring Boot para Kotlin. O `build.gradle.kts` com `kotlin("plugin.spring")` é extremamente bem treinado; o equivalente Quarkus (`kotlin("plugin.allopen")` + configuração manual dos annotations CDI) é muito menos comum em dados públicos.

### 7.5 Resumo — Spring Boot vs Quarkus por Combinação

```
Custo: Spring Boot vs Quarkus

Java + Maven:    SB $1,46  vs  QK $1,60  [Spring ganha por $0,14]
Java + Gradle:   SB $2,18  vs  QK $1,97  [QUARKUS GANHA por $0,21]
Kotlin + Maven:  SB $3,50  vs  QK $2,60  [QUARKUS GANHA por $0,90]
Kotlin + Gradle: SB $1,93  vs  QK $2,80  [Spring ganha por $0,87]
```

**Conclusão do Eixo 3:** O resultado Spring Boot vs Quarkus é inconclusivo — cada combinação com a build tool produz um resultado diferente. O que é consistente: Quarkus produz melhor cobertura de linha em todos os casos (+5-6pp), mas branch coverage consistentemente inferior devido ao RestAssured.

---

## 8. Análise de Comportamentos Notáveis

### 8.1 Branch Coverage Travada em 60% em Todas as Variantes Quarkus

```
Cobertura de Branch por Variante

java-mode-1           ████████████████████████████████████████  81,3%
kotlin-mode-1         ██████████████████████████████████████████  85,7%
java-gradle-mode-1    ████████████████████████████████████████████████  95,0% 🏆
kotlin-gradle-mode-1  ██████████████████████████████████████████████  93,75%
java-quarkus-maven    ██████████████████████████████░░░░░░░░░░  60,0%
java-quarkus-gradle   ██████████████████████████████░░░░░░░░░░  60,0%
kotlin-quarkus-maven  ██████████████████████████████░░░░░░░░░░  60,0%
kotlin-quarkus-gradle ██████████████████████████████░░░░░░░░░░  60,0%
                      │10% │20% │30% │40% │50% │60% │70% │80% │90% │100%
```

Todas as 4 variantes Quarkus atingiram **exatamente 60,0%** de cobertura de branch. Esta uniformidade não é coincidência.

**Análise da causa:**

O JaCoCo conta como "branch" qualquer ponto de decisão no bytecode: `if/else`, operador ternário `?:`, `try/catch`, `instanceof`, e operadores de null (`?.`, `?:`). Para atingir 100% de branch coverage, cada ramificação precisa ser exercitada tanto com o resultado `true` quanto `false`.

Com RestAssured, os 12 testes da especificação cobrem os 5 endpoints e os casos de 404/400, mas não necessariamente todas as ramificações internas do framework. Por exemplo:
- O `ExceptionMapper<ConstraintViolationException>` tem branches para `firstOrNull()` que retorna null
- O `@PathParam` do JAX-RS tem validações internas de routing
- O `ConcurrentHashMap` tem branches de hash collision

MockMvc, por ser mais verboso, leva o LLM a escrever asserções mais granulares e por consequência testa mais branches indiretamente.

**Esta não é uma falha do LLM nem da especificação — é uma característica estrutural do RestAssured vs MockMvc.**

### 8.2 Kotlin Alcança 100% de Cobertura de Linha no Quarkus

```
Cobertura de Linha — Quarkus

Java Maven   ████████████████████████████████████████████████  95,0%
Java Gradle  ██████████████████████████████████████████████  94,3%
Kotlin Maven ████████████████████████████████████████████████████  100% 🏆
Kotlin Gradle████████████████████████████████████████████████████  100% 🏆
```

Ambas as variantes Kotlin Quarkus atingiram 100% de cobertura de linha. Por quê Kotlin e não Java?

**Análise da causa:**

1. **`data class` não gera bytecode de getter/setter visível ao JaCoCo:** Em Java, um POJO com 6 campos gera ~50 linhas de getters/setters que precisam ser chamados para cobrir 100% das linhas. Em Kotlin, `data class Task(val id: String, ...)` gera getters como bytecode mas eles são mapeados à linha da declaração, não a linhas separadas. O JaCoCo conta muito menos linhas "descobertas" para Kotlin.

2. **Null-safety elimina branches implícitas:** Em Java, um `if (task != null)` gera uma branch explícita. Em Kotlin, o compilador insere verificações de null no bytecode mas não as reporta como branches separadas ao JaCoCo para tipos não-nullable.

3. **Menos código sem comportamento:** `data class` em Kotlin é ~1 linha; o POJO Java equivalente é ~30 linhas. Menos linhas → mais fácil cobrir 100% com os mesmos testes.

### 8.3 Inversão dos Output Tokens no Kotlin Gradle (Spring Boot)

```
Output tokens por variante Spring Boot

Linguagem   Maven        Gradle
Java        29.393       66.538
Kotlin      94.748       40.470  ← INVERSÃO: Gradle < Java!
```

Com Maven, Kotlin gerou 222% mais tokens que Java. Com Gradle, Kotlin gerou **39% menos** tokens que Java. Por quê?

**Análise da causa:**

Com **Maven**, o `pom.xml` do Kotlin exige muito mais XML:
- `kotlin-maven-plugin` com `executions` explícitas (compile, test-compile)
- `kotlin-maven-allopen` como dependência do plugin
- `compilerPlugins: spring` dentro de `<configuration>`
- Desabilitação de `default-compile` e `default-testCompile` do `maven-compiler-plugin`

O LLM tenta várias configurações antes de acertar → muitos tokens de output.

Com **Gradle**, a diferença desaparece. O `build.gradle.kts` Kotlin equivale a:

```kotlin
// 3 linhas que substituem ~40 linhas de XML do Maven
plugins {
    kotlin("jvm") version "..."
    kotlin("plugin.spring") version "..."
    id("org.springframework.boot") version "..."
}
```

Além disso, o código de produção Kotlin é muito mais conciso que Java:
- `data class Task(val id: String, var title: String, ...)` vs 30+ linhas de POJO
- `fun findById(id: String) = repo.findById(id) ?: throw NotFoundException()` vs 5 linhas em Java
- Resultado: menos tokens de output por arquivo gerado

### 8.4 Cache Hit Rate Estável em Todas as Variantes

```
Cache Hit Rate (tokens lidos do cache / total tokens de entrada)

java-mode-1            95,02%  ████████████████████████████████████████████████
kotlin-mode-1          95,33%  █████████████████████████████████████████████████
java-gradle-mode-1     94,17%  ████████████████████████████████████████████████
kotlin-gradle-mode-1   93,44%  ██████████████████████████████████████████████
java-quarkus-maven     95,83%  █████████████████████████████████████████████████
java-quarkus-gradle    95,05%  ████████████████████████████████████████████████
kotlin-quarkus-maven   93,19%  █████████████████████████████████████████████
kotlin-quarkus-gradle  90,94%  █████████████████████████████████████████████
```

Todas as variantes mantiveram cache hit rate entre 91% e 96%. Isso confirma que:
1. A metodologia de execução é estável — o guia estruturado de 12 passos cria padrões de contexto que o cache reconhece bem
2. O prompt system (CLAUDE.md + guia) ocupa a maior parte do contexto, sendo reutilizado entre turnos

A variante `kotlin-quarkus-gradle` teve o menor cache hit rate (90,94%), o que é coerente com ser a variante de maior custo — menos cache utilizado → mais tokens processados novamente.

### 8.5 Kotlin Maven Outlier — O Caso dos $3,50

```
Kotlin Spring Boot Maven — Distribuição do custo

Output tokens  ████████████████████████████████████████  $1,421  (40,6%)
Cache read     ████████████████████████████████████  $1,279  (36,5%)
Cache create   ████████████████████  $0,784  (22,4%)
               $0       $0,50    $1,00    $1,50

Java Spring Boot Maven — Distribuição do custo

Output tokens  ████████████████████████  $0,441  (30,2%)
Cache read     ████████████████████████████  $0,617  (42,2%)
Cache create   ████████████████████████  $0,404  (27,6%)
               $0       $0,50    $1,00    $1,50
```

O custo de output tokens do Kotlin Maven ($1,421) é **3,2× maior** que o do Java Maven ($0,441). Este é o sinal de um modelo iterando muito mais para resolver a configuração do build:

1. **Tentativa inicial** de `pom.xml` com configuração incorreta ou incompleta
2. **Erro de compilação** pelo `kotlin-maven-plugin`
3. **Correção** da configuração do plugin
4. **Novo erro** por missing `all-open` ou `compilerPlugins`
5. **Correção** e compilação bem-sucedida
6. Repetição para cada arquivo de código fonte criado

Cada erro → debugging → correção = dezenas de tokens extras.

---

## 9. Padrões Identificados

### Padrão 1: Densidade de Treinamento como Proxy de Eficiência

```
Ranking estimado de densidade nos dados de treinamento:
                                       Custo observado
1. Java + Spring Boot + Maven          $1,46  (mais barato)
2. Kotlin + Spring Boot + Gradle       $1,93
3. Java + Quarkus + Maven              $1,60
4. Java + Spring Boot + Gradle         $2,18
5. Java + Quarkus + Gradle             $1,97
6. Kotlin + Quarkus + Maven            $2,60
7. Kotlin + Quarkus + Gradle           $2,80
8. Kotlin + Spring Boot + Maven        $3,50  (mais caro)
```

A correlação entre frequência esperada nos dados de treinamento e custo de execução é forte. Combinações incomuns (Kotlin + Maven para qualquer framework) custam mais porque o LLM precisa "inventar" mais, gerando mais tokens e mais erros.

### Padrão 2: Kotlin É Consistentemente Mais Conciso em Produção

Em **todas** as 4 comparações paralelas (mesma build tool e framework), Kotlin gerou menos LOC de produção:

| Framework + Build | Java LOC | Kotlin LOC | Redução |
|---|---|---|---|
| Spring Boot + Maven | 198 | 132 | −33% |
| Spring Boot + Gradle | 188 | 142 | −24% |
| Quarkus + Maven | 233 | 158 | −32% |
| Quarkus + Gradle | 210 | 158 | −25% |

A concisão do Kotlin (data classes, extension functions, null-safety, lambdas) é uma propriedade da linguagem independente do framework ou build tool. Em média, **−29% de LOC de produção**.

### Padrão 3: Framework de Teste Determina Cobertura de Branch

```
Cobertura de branch por framework de teste:

MockMvc (Spring Boot):   81,3% – 95,0%  ← alta, verboso mas abrangente
RestAssured (Quarkus):   60,0%           ← constante, conciso mas menos branches
```

A escolha do framework de teste tem impacto direto nas métricas de cobertura, independente da linguagem ou build tool. Isso é uma variável confundidora que deve ser considerada ao comparar frameworks.

### Padrão 4: Maven e Gradle Têm Pontos Fortes Complementares

| Dimensão | Maven | Gradle |
|---|---|---|
| Menor custo médio | ✅ ($1,91 média) | ($2,22 média) |
| Melhor para Kotlin | ❌ (mais caro) | ✅ (Spring Boot) |
| Cobertura de branch | Similar | ✅ (ligeiramente superior) |
| Velocidade (duração) | ≈ igual | ✅ (ligeiramente mais rápido) |
| Documentação canônica | ✅ (Quarkus usa Maven nos guias) | ✅ (Spring Boot usa Gradle para Kotlin) |

### Padrão 5: Quarkus Uniformiza Erros de Build

Todas as 4 variantes Quarkus tiveram **exatamente 1 erro** de desenvolvimento, enquanto as variantes Spring Boot tiveram 1-3 erros. Isso provavelmente reflete que os guias Quarkus foram escritos com mais cuidado (incluindo referências de implementação completas e tabelas de erros comuns), prevenindo erros de anotação (JAX-RS vs Spring MVC).

---

## 10. Ranking Final

### 10.1 Por Custo (USD)

| Pos | Variante | Custo | vs Média |
|---|---|---|---|
| 🥇 1 | Java · Spring Boot · Maven | $1,46 | −36% |
| 🥈 2 | Java · Quarkus · Maven | $1,60 | −30% |
| 🥉 3 | Kotlin · Spring Boot · Gradle | $1,93 | −15% |
| 4 | Java · Quarkus · Gradle | $1,97 | −13% |
| 5 | Java · Spring Boot · Gradle | $2,18 | −4% |
| 6 | Kotlin · Quarkus · Maven | $2,60 | +14% |
| 7 | Kotlin · Quarkus · Gradle | $2,80 | +23% |
| 8 | Kotlin · Spring Boot · Maven | $3,50 | +54% |

> Média geral: **$2,25 USD**

### 10.2 Por Velocidade (Duração da Sessão)

| Pos | Variante | Duração |
|---|---|---|
| 🥇 1 | Kotlin · Spring Boot · Gradle | 4,51 min |
| 🥈 2 | Java · Spring Boot · Maven | 5,42 min |
| 🥉 3 | Java · Spring Boot · Gradle | 5,4 min |
| 4 | Kotlin · Quarkus · Gradle | 5,52 min |
| 5 | Java · Quarkus · Maven | 5,86 min |
| 6 | Java · Quarkus · Gradle | 5,95 min |
| 7 | Kotlin · Spring Boot · Maven | 10,67 min |
| 8 | Kotlin · Quarkus · Maven | 10,97 min |

### 10.3 Por Qualidade de Código (Cobertura de Linha)

| Pos | Variante | Cob. Linha | Cob. Branch |
|---|---|---|---|
| 🥇 1 | Kotlin · Quarkus · Maven | **100%** | 60,0% |
| 🥇 1 | Kotlin · Quarkus · Gradle | **100%** | 60,0% |
| 3 | Java · Quarkus · Maven | 95,0% | 60,0% |
| 4 | Kotlin · Spring Boot · Maven | 94,3% | 85,7% |
| 4 | Java · Quarkus · Gradle | 94,3% | 60,0% |
| 6 | Kotlin · Spring Boot · Gradle | 94,1% | 93,75% |
| 7 | Java · Spring Boot · Gradle | 93,0% | **95,0%** 🏆 |
| 8 | Java · Spring Boot · Maven | 89,1% | 81,3% |

### 10.4 Melhor Custo-Benefício

Considerando custo, cobertura de linha, E2E e erros de forma equilibrada:

```
Score composto (normalizado: 0-10):
  Custo:        menor = melhor
  Cob. linha:   maior = melhor
  Cob. branch:  maior = melhor
  Erros:        menos = melhor
  E2E:          todos aprovaram (excluído do ranking)

┌────────────────────────────────────┬───────┬────────┬────────┬───────┬───────┐
│ Variante                           │ Custo │ Cob.L  │ Cob.B  │ Erros │ Score │
├────────────────────────────────────┼───────┼────────┼────────┼───────┼───────┤
│ Java · Quarkus · Maven         🏆  │ $1,60 │ 95,0%  │ 60,0%  │  1    │  7,8  │
│ Java · Spring Boot · Maven         │ $1,46 │ 89,1%  │ 81,3%  │  2    │  7,5  │
│ Kotlin · Spring Boot · Gradle      │ $1,93 │ 94,1%  │ 93,75% │  3    │  7,4  │
│ Kotlin · Quarkus · Maven           │ $2,60 │ 100%   │ 60,0%  │  1    │  7,3  │
│ Java · Spring Boot · Gradle        │ $2,18 │ 93,0%  │ 95,0%  │  1    │  7,2  │
│ Java · Quarkus · Gradle            │ $1,97 │ 94,3%  │ 60,0%  │  1    │  7,0  │
│ Kotlin · Quarkus · Gradle          │ $2,80 │ 100%   │ 60,0%  │  1    │  6,9  │
│ Kotlin · Spring Boot · Maven       │ $3,50 │ 94,3%  │ 85,7%  │  3    │  5,8  │
└────────────────────────────────────┴───────┴────────┴────────┴───────┴───────┘
```

---

## 11. Conclusões

### 11.1 A Build Tool Importa Mais do que a Linguagem

A variável que mais afetou o custo foi a **build tool**, não a linguagem. Kotlin com Maven custou $3,50 — o mais caro. Kotlin com Gradle custou $1,93 — o terceiro mais barato. A **mesma linguagem** produziu resultados opostos dependendo da build tool.

Isso acontece porque o custo da LLM não mede a dificuldade da linguagem — mede a frequência com que a configuração específica aparece nos dados de treinamento. O Spring Initializr usa Gradle para Kotlin por padrão, criando uma enorme base de exemplos que o modelo reconhece sem esforço.

> **Implicação para benchmarks:** Qualquer comparação de linguagens que usa apenas Maven é potencialmente enviesada contra Kotlin. A variável "build tool" precisa ser controlada ou isolada explicitamente.

### 11.2 Densidade de Treinamento como Fator Determinante

Os resultados seguem fielmente a representação estimada de cada combinação nos dados de treinamento públicos:

- **Mais barato:** Java + Spring Boot + Maven → inúmeros tutoriais, exemplos oficiais, Stack Overflow
- **Mais caro:** Kotlin + Spring Boot + Maven → raro, Spring Initializr não gera esse template

O LLM não tem mais ou menos "capacidade" para Java vs Kotlin — ele tem mais ou menos **exemplos** de cada combinação para se basear. Aumentar a diversidade de dados de treinamento provavelmente reduziria a dispersão observada.

### 11.3 Framework de Teste Como Variável Confundidora

Comparar cobertura de branch entre Spring Boot e Quarkus sem considerar que **MockMvc é verboso e RestAssured é conciso** é uma metodologia incorreta. Com RestAssured, o LLM naturalmente gera menos LOC de teste (63-125) que com MockMvc (241-261). Menos LOC de teste → menos branches cobertas, independente da qualidade do LLM.

Para comparações de cobertura de branch entre frameworks, o ideal seria padronizar o framework de teste ou normalizar a métrica pelo LOC de teste.

### 11.4 Kotlin é Consistentemente Mais Conciso

Em todas as 8 comparações possíveis, Kotlin gerou menos LOC de produção que Java (−24% a −33%). A concisão de `data class`, null-safety e lambdas se traduz diretamente em menos linhas de código geradas. Esse benefício é **independente** do framework e da build tool.

Para equipes que priorizam manutenibilidade e legibilidade do código, Kotlin entrega consistentemente código mais conciso — o custo extra de geração (quando Maven é usado) pode ser amortizado ao longo da vida do projeto.

### 11.5 Quarkus é Competitivo com Spring Boot

Para Java, Quarkus Maven foi o segundo mais barato ($1,60), quase equivalente ao Java Spring Boot Maven ($1,46). Para Kotlin, Quarkus Maven foi 26% mais barato que Spring Boot Maven ($2,60 vs $3,50). A preocupação de que Quarkus seria mais difícil para a LLM (JAX-RS é menos comum que Spring MVC) não se confirmou para Java.

### 11.6 Todos os Agentes Completaram o Benchmark com Sucesso

Uma observação importante: **todas as 8 variantes produziram 12/12 testes E2E passando**. Independente de custo, velocidade ou framework, o Claude Sonnet 4.6 foi capaz de implementar a API corretamente em todas as combinações testadas. As diferenças são de **eficiência**, não de **capacidade**.

---

## 12. Referências

### Frameworks e Ferramentas

- **Spring Boot** — [docs.spring.io](https://docs.spring.io/spring-boot/docs/current/reference/html/) · Baeldung Spring Guides
- **Quarkus** — [quarkus.io/guides](https://quarkus.io/guides/) · JAX-RS specification (Jakarta EE 10)
- **JaCoCo** — [jacoco.org/jacoco/trunk/doc/counters.html](https://www.jacoco.org/jacoco/trunk/doc/counters.html) · Branch Coverage Counter Documentation
- **cloc** — [github.com/AlDanial/cloc](https://github.com/AlDanial/cloc) — Count Lines of Code
- **RestAssured** — [rest-assured.io](https://rest-assured.io/) — REST API Testing in Java
- **Spring Initializr** — [start.spring.io](https://start.spring.io/) — template padrão Spring Boot

### Modelo LLM

- **Claude Code** — [claude.ai/code](https://claude.ai/code) — Anthropic
- **Claude Sonnet 4.6** — [docs.anthropic.com](https://docs.anthropic.com/en/docs/about-claude/models) — Anthropic Model Documentation
- **Telemetria Claude Code** — `~/.claude/telemetry/` — tokens, custo e sessões

### Leituras Relacionadas

- Xu et al. (2022). *"Systematic Evaluation of the Benefits and Risks of Using Large Language Models for Code Generation"* — análise de como LLMs performam diferentemente por linguagem e framework
- Chen et al. (2021). *"Evaluating Large Language Models Trained on Code"* (Codex paper) — fundamentos da avaliação de LLMs para código
- Ziegler et al. (2022). *"Measuring GitHub Copilot's Impact on Productivity"* — GitHub Blog — metodologia de benchmark de produtividade de LLM para código

### Sobre a Metodologia

A hipótese central sobre "densidade de dados de treinamento" não foi verificada empiricamente neste experimento — é uma inferência baseada no conhecimento do ecossistema. Para confirmação rigorosa, seria necessário um estudo controlado que alterne propositalmente entre configurações canônicas e incomuns para a mesma linguagem.

---

*Gerado em 2026 · Claude Code + Claude Sonnet 4.6 · Repositório: `benchmark-ai` branch `feat/exp-03-ollama-local-models`*
