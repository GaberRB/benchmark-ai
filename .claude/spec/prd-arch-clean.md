# PRD — Task Manager API: Clean Architecture (Uncle Bob)

## Visão Geral

Implementar a Task Manager REST API segundo a **Clean Architecture** de Robert C. Martin
(Uncle Bob), conforme descrita no livro "Clean Architecture" (2017).

O modelo é de **camadas concêntricas** com uma única regra de dependência: **o código de
uma camada só pode depender de camadas mais internas**. As camadas externas conhecem as
internas; as internas são completamente ignorantes das externas.

```
┌─────────────────────────────────────────────┐
│  Frameworks & Drivers (Spring, in-memory)   │
│  ┌───────────────────────────────────────┐  │
│  │  Interface Adapters (controllers,     │  │
│  │  gateways)                            │  │
│  │  ┌─────────────────────────────────┐  │  │
│  │  │  Use Cases (application rules)  │  │  │
│  │  │  ┌───────────────────────────┐  │  │  │
│  │  │  │  Entities (business rules) │  │  │  │
│  │  │  └───────────────────────────┘  │  │  │
│  │  └─────────────────────────────────┘  │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

---

## Stack Obrigatória

- Java 21
- Spring Boot 3.2 (pom.xml já configurado em `arch-benchmark/clean-architecture/pom.xml`)
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
├── entities/
│   └── Task.java                          ← regra de negócio enterprise (sem Spring)
│
├── usecases/
│   ├── TaskGateway.java                   ← interface (depende apenas de entities)
│   ├── CreateTaskInteractor.java          ← implements CreateTaskInputPort
│   ├── GetTaskInteractor.java             ← implements GetTaskInputPort
│   ├── UpdateTaskInteractor.java          ← implements UpdateTaskInputPort
│   ├── DeleteTaskInteractor.java          ← implements DeleteTaskInputPort
│   ├── ListTasksInteractor.java           ← implements ListTasksInputPort
│   ├── CreateTaskInputPort.java           ← interface: Task execute(String title, String desc)
│   ├── GetTaskInputPort.java              ← interface: Task execute(String id)
│   ├── UpdateTaskInputPort.java           ← interface: Task execute(String id, ...)
│   ├── DeleteTaskInputPort.java           ← interface: void execute(String id)
│   └── ListTasksInputPort.java            ← interface: List<Task> execute()
│
├── interfaceadapters/
│   ├── controllers/
│   │   ├── TaskController.java            ← @RestController, injeta InputPort interfaces
│   │   ├── CreateTaskRequest.java
│   │   ├── UpdateTaskRequest.java
│   │   └── GlobalExceptionHandler.java    ← @RestControllerAdvice
│   └── gateways/
│       └── TaskGatewayImpl.java           ← @Component, implementa TaskGateway
│
└── frameworks/
    └── persistence/
        └── InMemoryTaskRepository.java    ← @Repository, usado por TaskGatewayImpl

src/test/java/com/benchmark/taskmanager/
├── usecases/
│   └── CreateTaskInteractorTest.java
│   └── GetTaskInteractorTest.java
└── interfaceadapters/controllers/
    └── TaskControllerTest.java
```

---

## Regras de Dependência (OBRIGATÓRIO — A Dependency Rule)

**Uma camada nunca importa de uma camada mais externa que ela:**

| Camada | Pode importar de |
|--------|-----------------|
| `entities/` | nada (zero dependências externas) |
| `usecases/` | `entities/` apenas |
| `interfaceadapters/` | `usecases/` e `entities/` |
| `frameworks/` | `interfaceadapters/`, `usecases/`, `entities/` |

**Violações proibidas:**
- `entities/Task.java` → **ZERO imports** de outras camadas deste projeto ou Spring
- `usecases/*.java` → **ZERO imports** de `interfaceadapters` ou `frameworks`
- `usecases/TaskGateway.java` → usa apenas `Task` (retorna `Task`, recebe `Task`)
- `TaskController` injeta `*InputPort` interfaces (não os Interactors diretamente)
- `TaskGatewayImpl` implementa `TaskGateway` e usa `InMemoryTaskRepository`

---

## Nomenclatura Obrigatória

| Classe | Camada | Papel |
|--------|--------|-------|
| `Task` | entities | Entidade enterprise |
| `TaskGateway` | usecases | Interface para acesso a dados (output boundary) |
| `CreateTaskInputPort` | usecases | Interface de entrada (use case boundary) |
| `GetTaskInputPort` | usecases | Interface de entrada |
| `UpdateTaskInputPort` | usecases | Interface de entrada |
| `DeleteTaskInputPort` | usecases | Interface de entrada |
| `ListTasksInputPort` | usecases | Interface de entrada |
| `CreateTaskInteractor` | usecases | Implementa CreateTaskInputPort |
| `GetTaskInteractor` | usecases | Implementa GetTaskInputPort |
| `UpdateTaskInteractor` | usecases | Implementa UpdateTaskInputPort |
| `DeleteTaskInteractor` | usecases | Implementa DeleteTaskInputPort |
| `ListTasksInteractor` | usecases | Implementa ListTasksInputPort |
| `TaskController` | interfaceadapters/controllers | HTTP adapter |
| `TaskGatewayImpl` | interfaceadapters/gateways | Implementa TaskGateway |
| `InMemoryTaskRepository` | frameworks/persistence | Storage ConcurrentHashMap |
| `TaskNotFoundException` | usecases ou entities | RuntimeException |

---

## Interfaces de Casos de Uso (Input Ports)

```java
public interface CreateTaskInputPort {
    Task execute(String title, String description);
}
public interface GetTaskInputPort {
    Task execute(String id);
}
public interface UpdateTaskInputPort {
    Task execute(String id, String title, String description, Boolean completed);
}
public interface DeleteTaskInputPort {
    void execute(String id);
}
public interface ListTasksInputPort {
    List<Task> execute();
}
```

## Interface do Gateway (Output Boundary)

```java
public interface TaskGateway {
    Task save(Task task);
    Optional<Task> findById(String id);
    List<Task> findAll();
    void deleteById(String id);
    boolean existsById(String id);
}
```

---

## Endpoints e Validações

Idênticos à spec em `spec/task-definition.md`.
- `TaskNotFoundException` → 404 `{"error":"Task not found"}`
- title inválido → 400 com mensagem apropriada

---

## Critérios de Aceite

- `.\mvnw.cmd compile` → BUILD SUCCESS
- `.\mvnw.cmd test` → 0 failures, 0 errors, cobertura linha ≥ 80%
- 12/12 cenários E2E passando
- `entities/Task.java` sem imports de Spring ou de outras camadas do projeto
- `usecases/` sem imports de `interfaceadapters/` ou `frameworks/`
- `TaskController` injeta apenas `*InputPort` interfaces
