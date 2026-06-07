# Arquitetura DDD Tático (Domain-Driven Design)

## O que é

**DDD Tático** é um conjunto de padrões para modelar o domínio de forma rica. Em vez de entidades anêmicas com getters/setters, o DDD cria **objetos com comportamento**. Os conceitos centrais são: **Value Objects** (imutáveis, validação no construtor), **Aggregate Root** (protege invariantes) e **Repository** como conceito de domínio.

---

## Diagrama

```
┌────────────────────────────────────────────────────────┐
│                    INTERFACES (web)                    │
│  TaskController    ← fala apenas com Application      │
│  CreateTaskRequest                                     │
│  UpdateTaskRequest                                     │
└──────────────────────────┬─────────────────────────────┘
                           │  usa TaskApplicationService
┌──────────────────────────▼─────────────────────────────┐
│                  APPLICATION                           │
│  TaskApplicationService                                │
│    • recebe DTOs crus (String, boolean)                │
│    • converte para objetos de domínio                  │
│    • chama Task.create(), task.updateTitle(), etc.     │
│    • injeta domain.repository.TaskRepository           │
│  CreateTaskCommand / UpdateTaskCommand (records)       │
│  TaskDto (record de saída com tipos primitivos)        │
└──────────────────────────┬─────────────────────────────┘
                           │  usa interfaces de domínio
┌──────────────────────────▼─────────────────────────────┐
│                    DOMAIN  ← núcleo                    │
│                                                        │
│  model/                                                │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Task (Aggregate Root)                          │  │
│  │  • static Task.create(title, description)       │  │
│  │  • task.updateTitle(newTitle)   ← comportamento │  │
│  │  • task.complete()              ← comportamento │  │
│  │  • task.reopen()                ← comportamento │  │
│  │  • SEM setters diretos                          │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │  TaskId (Value Object)                          │  │
│  │  • imutável (final fields)                      │  │
│  │  • validação no construtor (blank → Exception)  │  │
│  │  • equals/hashCode por valor                    │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Title (Value Object)                           │  │
│  │  • máx 200 chars — validado no construtor       │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Description (Value Object)                     │  │
│  │  • aceita null (converte para "")               │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
│  repository/                                           │
│  ┌─────────────────────────────────────────────────┐  │
│  │  TaskRepository (interface)                     │  │
│  │  • conceito de domínio — não é Spring Data!     │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
│  ZERO imports de org.springframework.*                 │
└──────────────────────────┬─────────────────────────────┘
                           │  implementa
┌──────────────────────────▼─────────────────────────────┐
│                 INFRASTRUCTURE                         │
│  InMemoryTaskRepository implements domain.TaskRepository│
└────────────────────────────────────────────────────────┘
```

**Estrutura de pacotes:**

```
com.benchmark.taskmanager/
├── domain/
│   ├── model/
│   │   ├── Task.java              ← Aggregate Root
│   │   ├── TaskId.java            ← Value Object
│   │   ├── Title.java             ← Value Object
│   │   └── Description.java       ← Value Object
│   ├── repository/
│   │   └── TaskRepository.java    ← interface (domínio)
│   └── exception/
│       ├── TaskNotFoundException.java
│       └── InvalidValueException.java
├── application/
│   ├── TaskApplicationService.java
│   └── dto/
│       ├── CreateTaskCommand.java
│       ├── UpdateTaskCommand.java
│       └── TaskDto.java
├── infrastructure/
│   └── persistence/
│       └── InMemoryTaskRepository.java
└── interfaces/
    └── web/
        ├── TaskController.java
        ├── CreateTaskRequest.java
        ├── UpdateTaskRequest.java
        └── GlobalExceptionHandler.java
```

---

## Regra de Dependência

```
interfaces  →  application  →  domain
infrastructure              →  domain

domain  =  ZERO imports Spring, ZERO imports de outras camadas
```

---

## Diferença-chave: Entidade Anêmica vs Aggregate Root

```java
// ❌ Entidade anêmica (anti-pattern)
task.setTitle(newTitle);
task.setCompleted(true);

// ✅ Aggregate Root com comportamento
task.updateTitle(newTitle);    // valida via new Title(newTitle)
task.complete();               // aplica a regra de negócio
```

---

## Vantagens

- **Domínio rico** — validações vivem onde devem: nos Value Objects
- **Invariantes protegidas** — o Aggregate Root garante consistência
- **Testabilidade do domínio** — entities testáveis sem Spring, sem mock
- **Linguagem ubíqua** — código reflete o vocabulário do negócio

## Desvantagens

- **Mais abstrações** — Value Objects imutáveis parecem overhead para CRUDs simples
- **Conversão obrigatória** — Application Service converte domain → DTO e vice-versa
- **IAs tendem a simplificar** — a IA no benchmark criou apenas 1 interface (TaskRepository) quando o ideal seria interfaces de use case também (8/10 de conformidade)

## Resultado no Benchmark

| Métrica | Valor |
|---------|-------|
| 💰 Custo | $2,33 |
| ⏱ Velocidade | **5,0 min (mais rápido)** |
| 🐛 Erros | **1 (empatado com Clean)** |
| 🎯 Cobertura | 88% |
| 🏗 Conformidade | 8/10 |
| ✅ E2E | 12/12 |

> **DDD foi o mais rápido** (5 min, 37 turns). O modelo mental dos Value Objects
> é claro — a IA sabia exatamente onde colocar cada validação.
> Perdeu 2 pontos de conformidade por não criar interfaces de use case na camada de aplicação.
