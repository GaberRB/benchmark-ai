# PRD — Task Manager API: CQRS (Command Query Responsibility Segregation)

## Visão Geral

Implementar a Task Manager REST API segundo o padrão **CQRS** (Greg Young / Martin Fowler):
separar explicitamente as operações de **escrita** (Commands) das operações de **leitura**
(Queries). Cada intenção é representada por um objeto imutável (Command ou Query) que é
processado por um Handler dedicado.

```
HTTP Request
     │
     ▼
TaskController
     │
     ├── POST /tasks    → CreateTaskCommand  → CreateTaskHandler → store → Task
     ├── PUT  /tasks/id → UpdateTaskCommand  → UpdateTaskHandler → store → Task
     ├── DEL  /tasks/id → DeleteTaskCommand  → DeleteTaskHandler → store → void
     │
     ├── GET  /tasks    → ListTasksQuery     → ListTasksHandler  → store → List<Task>
     └── GET  /tasks/id → GetTaskQuery       → GetTaskHandler    → store → Task
```

**Não há event sourcing** neste benchmark. O modelo de dados é simples (in-memory store)
e o CQRS se manifesta apenas na separação de handlers.

---

## Stack Obrigatória

- Java 21
- Spring Boot 3.2 (pom.xml já configurado em `arch-benchmark/cqrs/pom.xml`)
- Maven (`.\mvnw.cmd`)
- Storage in-memory (`ConcurrentHashMap`)
- JUnit 5 + Spring Boot Test
- JaCoCo (mínimo 80% de cobertura)
- **MODELO OBRIGATÓRIO:** `claude-sonnet-4-6`

---

## Estrutura de Pacotes OBRIGATÓRIA

```
src/main/java/com/benchmark/taskmanager/
├── TaskManagerApplication.java
│
├── commands/
│   ├── create/
│   │   ├── CreateTaskCommand.java          ← record ou classe imutável (title, description)
│   │   └── CreateTaskHandler.java          ← @Component, método: Task handle(CreateTaskCommand)
│   ├── update/
│   │   ├── UpdateTaskCommand.java          ← record (id, title, description, completed)
│   │   └── UpdateTaskHandler.java          ← @Component, método: Task handle(UpdateTaskCommand)
│   └── delete/
│       ├── DeleteTaskCommand.java          ← record (id)
│       └── DeleteTaskHandler.java          ← @Component, método: void handle(DeleteTaskCommand)
│
├── queries/
│   ├── get/
│   │   ├── GetTaskQuery.java               ← record (id)
│   │   └── GetTaskHandler.java             ← @Component, método: Task handle(GetTaskQuery)
│   └── list/
│       ├── ListTasksQuery.java             ← record ou classe (sem campos)
│       └── ListTasksHandler.java           ← @Component, método: List<Task> handle(ListTasksQuery)
│
├── model/
│   ├── Task.java                           ← entidade (id, title, description, completed, createdAt, updatedAt)
│   ├── TaskRepository.java                 ← interface
│   └── InMemoryTaskRepository.java         ← @Repository, ConcurrentHashMap
│
└── api/
    ├── TaskController.java                 ← @RestController, injeta todos os Handlers
    ├── CreateTaskRequest.java              ← DTO HTTP (title, description)
    ├── UpdateTaskRequest.java              ← DTO HTTP (title?, description?, completed?)
    ├── GlobalExceptionHandler.java         ← @RestControllerAdvice
    └── TaskNotFoundException.java          ← RuntimeException

src/test/java/com/benchmark/taskmanager/
├── commands/create/
│   └── CreateTaskHandlerTest.java
├── commands/update/
│   └── UpdateTaskHandlerTest.java
├── commands/delete/
│   └── DeleteTaskHandlerTest.java
├── queries/get/
│   └── GetTaskHandlerTest.java
├── queries/list/
│   └── ListTasksHandlerTest.java
└── api/
    └── TaskControllerTest.java
```

---

## Regras de Dependência (OBRIGATÓRIO)

```
api/TaskController  →  commands/*/Handler  +  queries/*/Handler
commands/*/Handler  →  model/TaskRepository (interface)
queries/*/Handler   →  model/TaskRepository (interface)

model/InMemoryTaskRepository  implementa  model/TaskRepository
```

**Proibido:**
- `TaskController` não acessa `TaskRepository` diretamente (apenas via handlers)
- Command Handlers não chamam Query Handlers e vice-versa
- `commands/*/Handler` não importam `queries/` (e vice-versa)
- Commands/Queries são objetos imutáveis (use `record` Java 16+ ou campos `final`)

---

## Nomenclatura Obrigatória

| Classe | Pacote | Papel |
|--------|--------|-------|
| `CreateTaskCommand` | commands.create | Intenção de criar (imutável) |
| `CreateTaskHandler` | commands.create | Processa CreateTaskCommand |
| `UpdateTaskCommand` | commands.update | Intenção de atualizar (imutável) |
| `UpdateTaskHandler` | commands.update | Processa UpdateTaskCommand |
| `DeleteTaskCommand` | commands.delete | Intenção de deletar (imutável) |
| `DeleteTaskHandler` | commands.delete | Processa DeleteTaskCommand |
| `GetTaskQuery` | queries.get | Intenção de buscar por ID (imutável) |
| `GetTaskHandler` | queries.get | Processa GetTaskQuery |
| `ListTasksQuery` | queries.list | Intenção de listar (imutável) |
| `ListTasksHandler` | queries.list | Processa ListTasksQuery |
| `Task` | model | Entidade |
| `TaskRepository` | model | Interface de repositório |
| `InMemoryTaskRepository` | model | Impl in-memory |
| `TaskController` | api | HTTP entry point |
| `TaskNotFoundException` | api | RuntimeException |

---

## Assinatura dos Handlers (OBRIGATÓRIO)

```java
// Command handlers — retornam o resultado da operação
public class CreateTaskHandler {
    public Task handle(CreateTaskCommand command) { ... }
}
public class UpdateTaskHandler {
    public Task handle(UpdateTaskCommand command) { ... }
}
public class DeleteTaskHandler {
    public void handle(DeleteTaskCommand command) { ... }
}

// Query handlers — retornam dados sem efeitos colaterais
public class GetTaskHandler {
    public Task handle(GetTaskQuery query) { ... }
}
public class ListTasksHandler {
    public List<Task> handle(ListTasksQuery query) { ... }
}
```

---

## Como o Controller Despacha

```java
// Exemplo simplificado de como o TaskController usa os handlers:
// POST /tasks → monta CreateTaskCommand → chama createTaskHandler.handle(cmd) → retorna Task
// GET /tasks/{id} → monta GetTaskQuery → chama getTaskHandler.handle(query) → retorna Task
// etc.
```

O Controller **não contém lógica de negócio** — apenas traduz HTTP → Command/Query → HTTP.

---

## Endpoints e Validações

Idênticos à spec em `spec/task-definition.md`.
- `TaskNotFoundException` → 404 `{"error":"Task not found"}`
- title inválido → 400 com mensagem de erro adequada

---

## Critérios de Aceite

- `.\mvnw.cmd compile` → BUILD SUCCESS
- `.\mvnw.cmd test` → 0 failures, 0 errors, cobertura linha ≥ 80%
- 12/12 cenários E2E passando
- Commands e Queries são objetos imutáveis (`record` preferencialmente)
- `TaskController` não acessa `TaskRepository` diretamente
- Command Handlers não importam Query Handlers (e vice-versa)
