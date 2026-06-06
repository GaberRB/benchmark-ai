# Arquitetura Hexagonal (Ports & Adapters)

## O que é

**Hexagonal Architecture** (Alistair Cockburn, 2005) coloca o domínio no centro e isola-o do mundo externo por meio de **ports** (interfaces) e **adapters** (implementações). A aplicação pode ser "plugada" a qualquer tecnologia externa sem alterar o domínio.

---

## Diagrama

```
                    HTTP Client
                        │
              ┌─────────▼──────────┐
              │   ADAPTER IN/WEB   │
              │  TaskController    │  ← implementa nada, usa ports
              └─────────┬──────────┘
                        │  usa interfaces (ports de entrada)
        ┌───────────────▼────────────────────────────┐
        │              APPLICATION                   │
        │  ports/in/                                 │
        │  ┌──────────────────────────────────────┐ │
        │  │ CreateTaskUseCase  (interface)        │ │
        │  │ GetTaskUseCase     (interface)        │ │
        │  │ UpdateTaskUseCase  (interface)        │ │
        │  │ DeleteTaskUseCase  (interface)        │ │
        │  │ ListTasksUseCase   (interface)        │ │
        │  └──────────────────────────────────────┘ │
        │                                            │
        │  ports/out/                                │
        │  ┌──────────────────────────────────────┐ │
        │  │ TaskRepository     (interface)        │ │
        │  └──────────────────────────────────────┘ │
        │                                            │
        │  service/                                  │
        │  ┌──────────────────────────────────────┐ │
        │  │ TaskService  ← implementa os 5 ports  │ │
        │  │              de entrada               │ │
        │  └──────────────────────────────────────┘ │
        └───────────────────────────────────────────┘
                        │  usa port de saída
              ┌─────────▼──────────────┐
              │  ADAPTER OUT/PERSIST.  │
              │  InMemoryTaskRepository│  ← implementa TaskRepository
              └────────────────────────┘

        ┌───────────────────────────────────────────┐
        │              DOMAIN                       │
        │  Task.java  ← ZERO imports Spring          │
        └───────────────────────────────────────────┘
```

**Estrutura de pacotes:**

```
com.benchmark.taskmanager/
├── domain/
│   └── Task.java                            ← ZERO imports Spring
├── application/
│   ├── ports/
│   │   ├── in/
│   │   │   ├── CreateTaskUseCase.java       ← interface
│   │   │   ├── GetTaskUseCase.java          ← interface
│   │   │   ├── UpdateTaskUseCase.java       ← interface
│   │   │   ├── DeleteTaskUseCase.java       ← interface
│   │   │   └── ListTasksUseCase.java        ← interface
│   │   └── out/
│   │       └── TaskRepository.java          ← interface
│   └── service/
│       └── TaskService.java                 ← implementa todos os ports in
└── adapters/
    ├── in/
    │   └── web/
    │       └── TaskController.java          ← injeta interfaces, não TaskService
    └── out/
        └── persistence/
            └── InMemoryTaskRepository.java  ← implementa TaskRepository
```

---

## Regra de Dependência

```
adapters/in  →  application/ports/in  (interfaces)
application/service  →  application/ports/out  (interface)
adapters/out  →  application/ports/out  (implementa)
domain/  ←  NINGUÉM depende do domain exceto application
```

**Crítico:** `TaskController` injeta `CreateTaskUseCase` (interface), **nunca** `TaskService`.

---

## Vantagens

- **Testabilidade perfeita** — substitui qualquer adapter por um mock sem tocar no domínio
- **Independência de framework** — `domain/` e `application/` não têm Spring
- **Clareza de contratos** — ports explicitam exatamente o que o domínio precisa/oferece
- **Troca de tecnologia** — REST pode virar CLI sem alterar nada além de `adapters/in/`

## Desvantagens

- **Wiring complexo** — injetar 5 interfaces diferentes no controller confunde frameworks de DI
- **Muitas interfaces** — 6 interfaces (5 in + 1 out) para 5 operações CRUD
- **Nomes confusos** — UseCase? Port? Adapter? Service? A terminologia não é autoexplicativa
- **Maior risco de erro de wiring** — a IA errou mais aqui (6 erros) que em qualquer outra arquitetura

## Resultado no Benchmark

| Métrica | Valor |
|---------|-------|
| 💰 Custo | $2,92 |
| ⏱ Velocidade | 8,4 min |
| 🐛 Erros | **6 (maior de todos)** |
| 🎯 Cobertura | 93,6% |
| 🏗 Conformidade | 10/10 |
| ✅ E2E | 12/12 |

> **Hexagonal foi o mais desafiador em erros.** O isolamento do domínio e a injeção por interfaces
> criam wiring complexo — a IA frequentemente injetou `TaskService` diretamente no Controller
> em vez das interfaces, gerando erros de compilação e ciclos extras de correção.
