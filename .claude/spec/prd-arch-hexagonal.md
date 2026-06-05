# PRD — Task Manager API: Hexagonal Architecture (Ports & Adapters)

## Visão Geral

Implementar a Task Manager REST API especificada em `spec/task-definition.md` segundo a
**Arquitetura Hexagonal (Ports & Adapters)** de Alistair Cockburn.

O princípio central: o **domínio** está no centro e não conhece o mundo externo (sem imports
de Spring, sem HTTP, sem dependência de infra). A comunicação entre o domínio e o exterior
acontece exclusivamente através de **portas** (interfaces Java). O exterior implementa
**adaptadores** que conversam com as portas.

```
  [ HTTP / Spring MVC ]              [ In-Memory Store ]
          ↓                                  ↑
  Adapter IN (web)         Domain       Adapter OUT (persistence)
  TaskController    →   Application   ← InMemoryTaskRepository
                         Ports/In          Ports/Out
                         (interfaces)      (interfaces)
```

---

## Stack Obrigatória

- Java 21
- Spring Boot 3.2 (pom.xml já configurado em `arch-benchmark/hexagonal/pom.xml`)
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
├── domain/
│   └── Task.java                           ← entidade pura (sem anotações Spring/framework)
│
├── application/
│   ├── ports/
│   │   ├── in/                             ← O QUE o domínio EXPÕE ao exterior
│   │   │   ├── CreateTaskUseCase.java      ← interface
│   │   │   ├── GetTaskUseCase.java         ← interface
│   │   │   ├── UpdateTaskUseCase.java      ← interface
│   │   │   ├── DeleteTaskUseCase.java      ← interface
│   │   │   └── ListTasksUseCase.java       ← interface
│   │   └── out/                            ← O QUE o domínio PRECISA do exterior
│   │       └── TaskRepository.java         ← interface
│   └── service/
│       └── TaskService.java                ← @Service, implementa TODAS as portas de entrada
│
├── adapters/
│   ├── in/
│   │   └── web/
│   │       ├── TaskController.java         ← @RestController, injeta as interfaces de porta
│   │       ├── CreateTaskRequest.java      ← DTO HTTP
│   │       ├── UpdateTaskRequest.java      ← DTO HTTP
│   │       └── GlobalExceptionHandler.java ← @RestControllerAdvice
│   └── out/
│       └── persistence/
│           └── InMemoryTaskRepository.java ← @Repository, implementa TaskRepository port
│
└── exception/
    └── TaskNotFoundException.java          ← RuntimeException

src/test/java/com/benchmark/taskmanager/
├── application/service/
│   └── TaskServiceTest.java
└── adapters/in/web/
    └── TaskControllerTest.java
```

---

## Regras de Dependência (OBRIGATÓRIO)

```
adapters/in/web   →  application/ports/in  (interfaces)
application/service implementa application/ports/in
application/service →  application/ports/out (interface)
adapters/out/persistence implementa application/ports/out

domain/Task  ←  usada por todos exceto adapters/out
```

**Lei de Dependência — o domínio nunca importa de fora:**
- `domain/Task.java` → **ZERO imports** de `org.springframework`, `adapters`, ou `application`
- `application/ports/in/*.java` → podem importar apenas `domain/`
- `application/ports/out/*.java` → podem importar apenas `domain/`
- `application/service/TaskService.java` → importa `ports/in`, `ports/out`, `domain`, `exception`
- `adapters/in/web/*.java` → importam `ports/in`, `domain` (apenas para response), Spring Web
- `adapters/out/persistence/*.java` → importam `ports/out`, `domain`

**Proibido:**
- `TaskController` não importa `TaskService` diretamente (apenas as interfaces de porta)
- `TaskService` não importa `InMemoryTaskRepository` diretamente (apenas a interface `TaskRepository`)
- Nenhuma classe de `domain/` importa Spring

---

## Nomenclatura Obrigatória

| Classe | Localização | Papel |
|--------|-------------|-------|
| `Task` | domain | Entidade de domínio |
| `CreateTaskUseCase` | application/ports/in | Porta de entrada (interface) |
| `GetTaskUseCase` | application/ports/in | Porta de entrada (interface) |
| `UpdateTaskUseCase` | application/ports/in | Porta de entrada (interface) |
| `DeleteTaskUseCase` | application/ports/in | Porta de entrada (interface) |
| `ListTasksUseCase` | application/ports/in | Porta de entrada (interface) |
| `TaskRepository` | application/ports/out | Porta de saída (interface) |
| `TaskService` | application/service | Implementa todas as portas de entrada |
| `TaskController` | adapters/in/web | Adapter HTTP de entrada |
| `InMemoryTaskRepository` | adapters/out/persistence | Adapter de persistência de saída |
| `TaskNotFoundException` | exception | Exceção de domínio |

---

## Interfaces das Portas de Entrada

```java
// Exemplo — CreateTaskUseCase.java
public interface CreateTaskUseCase {
    Task execute(String title, String description);
}

// Exemplo — GetTaskUseCase.java
public interface GetTaskUseCase {
    Task execute(String id);
}

// Exemplo — UpdateTaskUseCase.java
public interface UpdateTaskUseCase {
    Task execute(String id, String title, String description, Boolean completed);
}

// Exemplo — DeleteTaskUseCase.java
public interface DeleteTaskUseCase {
    void execute(String id);
}

// Exemplo — ListTasksUseCase.java
public interface ListTasksUseCase {
    List<Task> execute();
}
```

---

## Interface da Porta de Saída

```java
// TaskRepository.java
public interface TaskRepository {
    Task save(Task task);
    Optional<Task> findById(String id);
    List<Task> findAll();
    void deleteById(String id);
    boolean existsById(String id);
}
```

---

## Endpoints e Validações

Idênticos à spec em `spec/task-definition.md`. Ver também o comportamento de erros:
- `TaskNotFoundException` → 404 `{"error":"Task not found"}`
- title inválido → 400 `{"error":"title is required"}` ou similar

---

## Critérios de Aceite

- `.\mvnw.cmd compile` → BUILD SUCCESS
- `.\mvnw.cmd test` → 0 failures, 0 errors, cobertura linha ≥ 80%
- 12/12 cenários E2E passando
- `domain/Task.java` sem nenhum import de Spring ou de `adapters/`
- `TaskController` injeta interfaces (não `TaskService` diretamente)
- `TaskService` injeta `TaskRepository` interface (não `InMemoryTaskRepository`)
