# PRD — Task Manager API: Event-Driven Architecture

## Objetivo

Implementar a mesma Task Manager REST API usando **Event-Driven Architecture** com Java 21 + Spring Boot 3.2.

A implementação será avaliada pela capacidade do agente IA de:
- Modelar Domain Events imutáveis para cada mutação de estado
- Implementar um EventBus desacoplado (publisher não conhece os handlers)
- Escrever handlers que reagem aos eventos de forma independente

---

## Stack Técnica

- Java 21
- Spring Boot 3.2.0
- Maven (pom.xml já fornecido)
- Sem banco de dados — persistência em memória
- Sem Lombok, sem MapStruct
- **Sem Spring Events** (`ApplicationEventPublisher`) — implementar EventBus manual

---

## Estrutura de Pacotes OBRIGATÓRIA

```
src/main/java/com/benchmark/taskmanager/
├── events/
│   ├── DomainEvent.java           ← interface base
│   ├── TaskCreatedEvent.java      ← record imutável
│   ├── TaskUpdatedEvent.java      ← record imutável
│   ├── TaskDeletedEvent.java      ← record imutável
│   ├── EventHandler.java          ← @FunctionalInterface
│   ├── EventBus.java              ← interface
│   └── InMemoryEventBus.java      ← @Component, implements EventBus
├── handlers/
│   ├── TaskCreatedHandler.java
│   ├── TaskUpdatedHandler.java
│   └── TaskDeletedHandler.java
├── model/
│   ├── Task.java
│   └── TaskStatus.java            ← enum: PENDING, IN_PROGRESS, DONE
├── repository/
│   ├── TaskRepository.java        ← interface
│   └── InMemoryTaskRepository.java
├── service/
│   └── TaskService.java           ← publica eventos após cada operação
└── api/
    ├── TaskController.java
    ├── CreateTaskRequest.java
    ├── UpdateTaskRequest.java
    ├── TaskResponse.java
    ├── TaskNotFoundException.java
    └── GlobalExceptionHandler.java
```

---

## Regras de Dependência (OBRIGATÓRIAS)

```
api/      →  service  →  repository (interface)
                       →  eventbus (interface)
handlers  →  podem consultar repository se necessário
events/   →  ZERO dependências externas
```

**Violações que descartam o benchmark:**
- `TaskService` conhecendo os `Handler` diretamente
- `EventBus` usando `ApplicationEventPublisher` do Spring
- Events com estado mutável (campos não-final)

---

## Domain Events

### DomainEvent.java — interface base
```java
public interface DomainEvent {
    String eventId();
    java.time.Instant occurredAt();
    String aggregateId();
}
```

### TaskCreatedEvent.java
```java
public record TaskCreatedEvent(
    String eventId,
    java.time.Instant occurredAt,
    String aggregateId,
    String title,
    String description
) implements DomainEvent {}
```

### TaskUpdatedEvent.java
```java
public record TaskUpdatedEvent(
    String eventId,
    java.time.Instant occurredAt,
    String aggregateId,
    String newTitle,
    String newDescription,
    boolean completed
) implements DomainEvent {}
```

### TaskDeletedEvent.java
```java
public record TaskDeletedEvent(
    String eventId,
    java.time.Instant occurredAt,
    String aggregateId
) implements DomainEvent {}
```

---

## EventBus

### EventHandler.java
```java
@FunctionalInterface
public interface EventHandler<T extends DomainEvent> {
    void handle(T event);
}
```

### EventBus.java
```java
public interface EventBus {
    <T extends DomainEvent> void subscribe(Class<T> eventType, EventHandler<T> handler);
    void publish(DomainEvent event);
}
```

### InMemoryEventBus.java
```java
@Component
public class InMemoryEventBus implements EventBus {
    // Map<Class<?>, List<EventHandler<?>>>
    // subscribe: adiciona handler à lista do tipo
    // publish: invoca todos handlers registrados para event.getClass()
    // loga WARNING se nenhum handler encontrado (não lança exceção)

    // Handlers injetados via construtor Spring + registrados no @PostConstruct
}
```

Registro dos handlers via `@PostConstruct`:
```java
@PostConstruct
public void registerHandlers() {
    subscribe(TaskCreatedEvent.class, taskCreatedHandler);
    subscribe(TaskUpdatedEvent.class, taskUpdatedHandler);
    subscribe(TaskDeletedEvent.class, taskDeletedHandler);
}
```

---

## Handlers

### TaskCreatedHandler.java
```java
@Component
public class TaskCreatedHandler implements EventHandler<TaskCreatedEvent> {
    // Logger: "Task created: {id} - {title}"
    @Override public void handle(TaskCreatedEvent event) { ... }
}
```

### TaskUpdatedHandler.java
```java
@Component
public class TaskUpdatedHandler implements EventHandler<TaskUpdatedEvent> {
    // Logger: "Task updated: {id}, completed={completed}"
    @Override public void handle(TaskUpdatedEvent event) { ... }
}
```

### TaskDeletedHandler.java
```java
@Component
public class TaskDeletedHandler implements EventHandler<TaskDeletedEvent> {
    // Logger: "Task deleted: {id}"
    @Override public void handle(TaskDeletedEvent event) { ... }
}
```

---

## Model

### TaskStatus.java
```java
public enum TaskStatus { PENDING, IN_PROGRESS, DONE }
```

### Task.java
```java
public class Task {
    private String id;
    private String title;
    private String description;
    private TaskStatus status; // começa como PENDING
    // getters + setters
}
```

---

## Repository

### TaskRepository.java
```java
public interface TaskRepository {
    Task save(Task task);
    Optional<Task> findById(String id);
    List<Task> findAll();
    void deleteById(String id);
    boolean existsById(String id);
}
```

### InMemoryTaskRepository.java
```java
@Repository
public class InMemoryTaskRepository implements TaskRepository {
    private final Map<String, Task> store = new ConcurrentHashMap<>();
}
```

---

## Service

### TaskService.java — publica eventos após cada operação
```java
@Service
public class TaskService {
    private final TaskRepository repository;
    private final EventBus eventBus;

    // createTask: persiste → publica TaskCreatedEvent
    // updateTask: busca → atualiza → persiste → publica TaskUpdatedEvent
    // deleteTask: verifica existência → deleta → publica TaskDeletedEvent
    // getTask: busca ou lança TaskNotFoundException
    // listTasks: retorna findAll()
}
```

**Invariante:** evento publicado **após** sucesso da operação, nunca antes.

---

## API

### TaskController.java
```java
@RestController
@RequestMapping("/tasks")
public class TaskController {
    private final TaskService taskService;

    @PostMapping          → 201 Created
    @GetMapping           → 200 OK + lista
    @GetMapping("/{id}")  → 200 OK ou 404
    @PutMapping("/{id}")  → 200 OK ou 404
    @DeleteMapping("/{id}") → 204 No Content ou 404
}
```

### TaskResponse.java
```java
public record TaskResponse(String id, String title, String description, String status) {}
```

### GlobalExceptionHandler.java
- `TaskNotFoundException` → 404
- `IllegalArgumentException` → 400

---

## API REST

| Método | Endpoint | Body | Status sucesso |
|--------|----------|------|----------------|
| POST | /tasks | `{"title":"...","description":"..."}` | 201 |
| GET | /tasks | — | 200 |
| GET | /tasks/{id} | — | 200 |
| PUT | /tasks/{id} | `{"title":"...","description":"...","completed":bool}` | 200 |
| DELETE | /tasks/{id} | — | 204 |

---

## Casos de Borda

- POST sem `title` ou `title` em branco → 400
- GET/PUT/DELETE com ID inexistente → 404
- Cada operação de mutação gera exatamente 1 evento

---

## Testes Obrigatórios

Cobertura JaCoCo mínima: **80% de linhas** (BUILD FAILURE se menor).

Testar obrigatoriamente:
1. **InMemoryEventBus** — subscribe + publish (handler chamado com o evento correto)
2. **TaskService** — cada método publica o evento esperado (mock do EventBus)
3. **TaskController** — happy path e erros via MockMvc
4. **Handlers** — método `handle()` sem lançar exceção

---

## Critério de Conformidade Arquitetural (para preenchimento manual)

| Ponto | OK? |
|-------|-----|
| Events são records imutáveis | ☐ |
| Events implementam DomainEvent com eventId + occurredAt | ☐ |
| EventBus é interface (desacoplamento) | ☐ |
| InMemoryEventBus não usa ApplicationEventPublisher | ☐ |
| TaskService injeta EventBus como interface | ☐ |
| Evento publicado após sucesso da operação | ☐ |
| TaskService não conhece handlers diretamente | ☐ |
| Handlers registrados via injeção/@PostConstruct | ☐ |
| Pelo menos 3 handlers distintos | ☐ |
| EventBus invoca todos handlers do tipo correto | ☐ |

Pontuação: 1 ponto por item → `arch_conformance` = soma (0-10).
