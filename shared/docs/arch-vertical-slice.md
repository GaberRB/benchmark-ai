# Arquitetura Vertical Slice

## O que é

**Vertical Slice Architecture** organiza o código por **funcionalidade (feature/caso de uso)**, não por camada técnica. Cada "fatia vertical" contém tudo que é necessário para uma operação: o controller, o use case e os DTOs — juntos, no mesmo pacote.

---

## Diagrama

```
┌────────────────────────────────────────────────────────────────┐
│                    HTTP Request                                │
└──────┬───────────┬───────────┬───────────┬──────────┬─────────┘
       │           │           │           │          │
   POST /tasks  GET /tasks  GET /{id}  PUT /{id}  DELETE /{id}
       │           │           │           │          │
┌──────▼──┐  ┌────▼────┐  ┌───▼────┐  ┌──▼──────┐ ┌──▼──────┐
│ create/ │  │  list/  │  │  get/  │  │ update/ │ │ delete/ │
│         │  │         │  │        │  │         │ │         │
│Controller  │Controller  │Controller  │Controller │Controller
│Request  │  │         │  │        │  │Request  │ │         │
│UseCase  │  │UseCase  │  │UseCase │  │UseCase  │ │UseCase  │
└────┬────┘  └────┬────┘  └───┬────┘  └────┬────┘ └────┬────┘
     │            │            │             │           │
     └────────────┴────────────┴─────────────┴───────────┘
                                    │
                        ┌───────────▼────────────┐
                        │         shared/        │
                        │  Task.java             │
                        │  TaskRepository        │
                        │  InMemoryTaskRepository│
                        └────────────────────────┘
```

**Estrutura de pacotes:**

```
com.benchmark.taskmanager/
├── tasks/
│   ├── create/
│   │   ├── CreateTaskController.java
│   │   ├── CreateTaskRequest.java
│   │   └── CreateTaskUseCase.java
│   ├── get/
│   │   ├── GetTaskController.java
│   │   └── GetTaskUseCase.java
│   ├── update/
│   │   ├── UpdateTaskController.java
│   │   ├── UpdateTaskRequest.java
│   │   └── UpdateTaskUseCase.java
│   ├── delete/
│   │   ├── DeleteTaskController.java
│   │   └── DeleteTaskUseCase.java
│   ├── list/
│   │   ├── ListTasksController.java
│   │   └── ListTasksUseCase.java
│   └── shared/
│       ├── Task.java
│       ├── TaskRepository.java
│       └── InMemoryTaskRepository.java
└── exception/
    └── GlobalExceptionHandler.java
```

---

## Regra de Dependência

```
Cada slice é independente — não chama outro slice diretamente.
Todos os slices compartilham apenas o pacote shared/.
```

---

## Vantagens

- **Alta coesão por feature** — toda a lógica de "criar tarefa" está em `tasks/create/`
- **Fácil de adicionar features** — cria-se um novo pacote sem tocar nos outros
- **Testes focados** — cada slice testa sua própria responsabilidade
- **Onboarding rápido** — desenvolvedor novo acha tudo sobre uma feature em um lugar

## Desvantagens

- **Repetição de código** — cada slice replica estrutura de controller + use case + DTO
- **Mais arquivos** — 23 arquivos vs 12 do MVC para a mesma API
- **Shared cresce sem controle** — tudo que é "genérico" acaba no shared/
- **Mais caro para a IA** — estrutura repetitiva gera muitos output tokens (107k)

## Resultado no Benchmark

| Métrica | Valor |
|---------|-------|
| 💰 Custo | $3,84 (mais caro) |
| ⏱ Velocidade | 5,4 min (2º mais rápido) |
| 🐛 Erros | 2 |
| 🎯 Cobertura | 91,8% |
| 🏗 Conformidade | 10/10 |
| ✅ E2E | 12/12 |

> **Paradoxo custo-velocidade:** 2º mais rápido mas mais caro. A IA escreve rápido e em volume —
> cada slice replica a estrutura completa, gerando 3,9× mais output tokens que o MVC.
