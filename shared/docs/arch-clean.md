# Arquitetura Clean Architecture (Uncle Bob)

## O que é

**Clean Architecture** organiza o código em **camadas concêntricas** onde as dependências sempre apontam para dentro (Dependency Rule). O centro (entities) não conhece nada externo. Frameworks e bancos de dados ficam na borda externa.

---

## Diagrama

```
╔═══════════════════════════════════════════════════════════════╗
║  FRAMEWORKS & DRIVERS (camada mais externa)                   ║
║  ┌──────────────────────────────────────────────────────┐    ║
║  │  INTERFACE ADAPTERS                                  │    ║
║  │  ┌────────────────────────────────────────────┐     │    ║
║  │  │  USE CASES                                 │     │    ║
║  │  │  ┌──────────────────────────────────┐     │     │    ║
║  │  │  │        ENTITIES                  │     │     │    ║
║  │  │  │  Task.java                       │     │     │    ║
║  │  │  │  (enterprise business rules)     │     │     │    ║
║  │  │  │  ZERO imports de qualquer coisa  │     │     │    ║
║  │  │  └──────────────────────────────────┘     │     │    ║
║  │  │  TaskGateway (interface)                  │     │    ║
║  │  │  CreateTaskInteractor                     │     │    ║
║  │  │  GetTaskInteractor                        │     │    ║
║  │  │  UpdateTaskInteractor                     │     │    ║
║  │  │  DeleteTaskInteractor                     │     │    ║
║  │  │  ListTasksInteractor                      │     │    ║
║  │  └────────────────────────────────────────────┘     │    ║
║  │  TaskController (injeta InputPort interfaces)        │    ║
║  │  TaskGatewayImpl                                     │    ║
║  └──────────────────────────────────────────────────────┘    ║
║  InMemoryTaskRepository (Spring @Repository)                  ║
╚═══════════════════════════════════════════════════════════════╝
```

**Estrutura de pacotes:**

```
com.benchmark.taskmanager/
├── entities/
│   └── Task.java                    ← ZERO imports
├── usecases/
│   ├── TaskGateway.java             ← interface (output port)
│   ├── CreateTaskInputPort.java     ← interface (input port)
│   ├── CreateTaskInteractor.java    ← implementa CreateTaskInputPort
│   ├── GetTaskInputPort.java
│   ├── GetTaskInteractor.java
│   ├── UpdateTaskInputPort.java
│   ├── UpdateTaskInteractor.java
│   ├── DeleteTaskInputPort.java
│   ├── DeleteTaskInteractor.java
│   ├── ListTasksInputPort.java
│   └── ListTasksInteractor.java
├── interfaceadapters/
│   ├── controllers/
│   │   └── TaskController.java      ← injeta InputPort interfaces
│   └── gateways/
│       └── TaskGatewayImpl.java     ← implementa TaskGateway
└── frameworks/
    └── persistence/
        └── InMemoryTaskRepository.java
```

---

## Regra de Dependência

```
frameworks  →  interfaceadapters  →  usecases  →  entities
```

**Nunca o inverso.** `entities/` tem ZERO imports. `usecases/` só importa `entities/`.
O `TaskController` injeta `CreateTaskInputPort` (interface), nunca `CreateTaskInteractor` (implementação).

---

## Vantagens

- **Testabilidade máxima** — entities e usecases testáveis sem Spring, sem banco
- **Flexibilidade de infraestrutura** — trocar banco de dados não toca em nada além de `frameworks/`
- **Menos erros de design** — a Dependency Rule serve de guia para toda decisão
- **Alta cobertura natural** — interactors isolados são simples de testar com mocks

## Desvantagens

- **Muitas interfaces** — 6 interfaces para 5 operações CRUD
- **Boilerplate elevado** — 27 arquivos, ~800 LOC total
- **Curva de aprendizado** — conceitos de InputPort/Interactor/Gateway confundem iniciantes
- **Over-engineering para CRUDs simples** — complexidade não proporcional à lógica de negócio

## Resultado no Benchmark

| Métrica | Valor |
|---------|-------|
| 💰 Custo | $3,18 |
| ⏱ Velocidade | 7,3 min |
| 🐛 Erros | **1 (menor de todos)** |
| 🎯 Cobertura | **97% linha, 100% branch** |
| 🏗 Conformidade | 10/10 |
| ✅ E2E | 12/12 |

> **Clean Architecture teve menos erros porque a estrutura rígida serve de guia.**
> A Dependency Rule bem definida no PRD deu à IA uma trilha sem ambiguidade.
> Resultado: 1 erro de compilação, 462 LOC de testes, 100% de cobertura de branch.
