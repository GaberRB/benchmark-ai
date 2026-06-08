# Arquitetura CQRS (Command Query Responsibility Segregation)

## O que é

**CQRS** separa as operações de **escrita** (Commands — mudam estado) das operações de **leitura** (Queries — retornam dados). Cada operação tem seu próprio handler dedicado. O Controller despacha para o handler correto.

---

## Diagrama

```
                      HTTP Request
                           │
             ┌─────────────▼──────────────────────────────┐
             │              CONTROLLER                     │
             │  TaskController                             │
             │  • POST   → CreateTaskCommand → handler    │
             │  • PUT    → UpdateTaskCommand → handler    │
             │  • DELETE → DeleteTaskCommand → handler    │
             │  • GET /  → ListTasksQuery    → handler    │
             │  • GET /{id} → GetTaskQuery   → handler    │
             └─────────────┬──────────────────────────────┘
                           │
           ┌───────────────┴──────────────────┐
           │                                  │
   ┌───────▼────────┐              ┌──────────▼──────────┐
   │    COMMANDS    │              │       QUERIES       │
   │  (escrita)     │              │     (leitura)       │
   │                │              │                     │
   │ commands/      │              │ queries/            │
   │ ├── create/    │              │ ├── get/            │
   │ │   CreateTask │              │ │   GetTaskQuery    │
   │ │   Command    │              │ │   GetTaskHandler  │
   │ │   Handler    │              │ └── list/           │
   │ ├── update/    │              │     ListTasksQuery  │
   │ │   UpdateTask │              │     ListTasksHandler│
   │ │   Command    │              └─────────┬───────────┘
   │ │   Handler    │                        │
   │ └── delete/    │                        │
   │     DeleteTask │                        │
   │     Command    │                        │
   │     Handler    │                        │
   └───────┬────────┘                        │
           │                                 │
           └──────────────┬──────────────────┘
                          │  ambos usam
              ┌───────────▼──────────────┐
              │     MODEL / REPOSITORY   │
              │  Task.java               │
              │  TaskRepository (iface)  │
              │  InMemoryTaskRepository  │
              └──────────────────────────┘
```

**Estrutura de pacotes:**

```
com.benchmark.taskmanager/
├── commands/
│   ├── create/
│   │   ├── CreateTaskCommand.java
│   │   └── CreateTaskHandler.java
│   ├── update/
│   │   ├── UpdateTaskCommand.java
│   │   └── UpdateTaskHandler.java
│   └── delete/
│       ├── DeleteTaskCommand.java
│       └── DeleteTaskHandler.java
├── queries/
│   ├── get/
│   │   ├── GetTaskQuery.java
│   │   └── GetTaskHandler.java
│   └── list/
│       ├── ListTasksQuery.java
│       └── ListTasksHandler.java
├── model/
│   ├── Task.java
│   ├── TaskRepository.java
│   └── InMemoryTaskRepository.java
└── api/
    ├── TaskController.java
    ├── CreateTaskRequest.java
    ├── UpdateTaskRequest.java
    ├── TaskResponse.java
    ├── TaskNotFoundException.java
    └── GlobalExceptionHandler.java
```

---

## Fluxo de uma requisição

```
POST /tasks  {"title": "Buy milk"}
    ↓
TaskController.createTask(request)
    ↓
CreateTaskCommand command = new CreateTaskCommand(request.title(), request.description())
    ↓
createTaskHandler.handle(command)
    ├── task = new Task(uuid, command.title(), command.description())
    └── taskRepository.save(task)
    ↓
retorna TaskResponse(task.id(), task.title(), ...)

GET /tasks/{id}
    ↓
TaskController.getTask(id)
    ↓
GetTaskQuery query = new GetTaskQuery(id)
    ↓
getTaskHandler.handle(query)
    └── return taskRepository.findById(query.id())
    ↓
retorna TaskResponse
```

---

## Commands vs Queries

```
Command = muda estado, não precisa retornar dados (pode retornar para conveniência da API)
Query   = lê estado, NUNCA muda dados (sem side effects)

CreateTaskCommand  → CREATE no repositório
UpdateTaskCommand  → UPDATE no repositório
DeleteTaskCommand  → DELETE no repositório
GetTaskQuery       → SELECT por ID (read-only)
ListTasksQuery     → SELECT all (read-only)
```

---

## Vantagens

- **Separação clara de responsabilidades** — escrita e leitura têm lógicas completamente isoladas
- **Escalabilidade** — em sistemas distribuídos, lados Command e Query podem escalar independentemente
- **Otimização de leitura** — Query side pode ter read models otimizados (projeções, caches)
- **Extensível** — adicionar um novo Command não afeta os Queries

## Desvantagens

- **Muitos arquivos** — 5 commands/queries × 2 (command + handler) = 10 classes só para handlers
- **Complexidade para CRUD simples** — um CRUD básico não se beneficia da separação
- **Padrão menos comum** — especialmente em projetos Spring Boot simples (→ mais erros de IA)
- **CQRS completo** → event sourcing → complexidade exponencial (fora do escopo deste benchmark)

## Resultado no Benchmark

| Métrica | Valor |
|---------|-------|
| 💰 Custo | $3,27 |
| ⏱ Velocidade | 8,81 min |
| 🐛 Erros | 2 |
| 🎯 Cobertura | **95%** |
| 🏗 Conformidade | 10/10 |
| ✅ E2E | 12/12 |

> **CQRS foi o padrão mais custoso por endpoint** ($0,65) e exigiu mais turns (68) —
> handlers separados para command/query fogem do padrão CRUD padrão nos dados de treinamento.
> Surpreendentemente, 95% de cobertura e apenas 2 erros — a separação clara guiou os testes.
