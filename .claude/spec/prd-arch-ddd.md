# PRD — Task Manager API: DDD Tático (Domain-Driven Design)

## Objetivo

Implementar a mesma Task Manager REST API usando **DDD Tático** com Java 21 + Spring Boot 3.2.

A implementação será avaliada pela capacidade do agente IA de modelar o domínio corretamente:
Value Objects imutáveis, Aggregate Root com invariantes, Repository como abstração de domínio.

---

## Stack Técnica

- Java 21
- Spring Boot 3.2.0
- Maven (pom.xml já fornecido)
- Sem banco de dados — persistência em memória
- Sem Lombok, sem MapStruct

---

## Estrutura de Pacotes OBRIGATÓRIA

```
src/main/java/com/benchmark/taskmanager/
├── domain/
│   ├── model/
│   │   ├── Task.java              ← Aggregate Root
│   │   ├── TaskId.java            ← Value Object
│   │   ├── Title.java             ← Value Object
│   │   └── Description.java       ← Value Object
│   ├── repository/
│   │   └── TaskRepository.java    ← interface (conceito de domínio)
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
│       └── InMemoryTaskRepository.java  ← implements domain.repository.TaskRepository
└── interfaces/
    └── web/
        ├── TaskController.java
        ├── CreateTaskRequest.java
        ├── UpdateTaskRequest.java
        └── GlobalExceptionHandler.java
```

---

## Regras de Dependência (OBRIGATÓRIAS)

```
interfaces  →  application  →  domain
infrastructure              →  domain

domain tem ZERO imports de Spring, ZERO imports de outras camadas
application NÃO conhece infrastructure (injeta a interface domain.repository)
interfaces NÃO fala com domain diretamente — usa application
```

**Violações que descartam o benchmark:**
- `domain/` com qualquer `import org.springframework.*`
- `application/` importando `infrastructure/`
- Controller chamando `TaskRepository` diretamente

---

## Entidades de Domínio

### TaskId.java — Value Object
```java
public final class TaskId {
    private final String value;

    public TaskId(String value) {
        if (value == null || value.isBlank()) throw new InvalidValueException("TaskId cannot be blank");
        this.value = value;
    }

    public static TaskId generate() {
        return new TaskId(java.util.UUID.randomUUID().toString());
    }

    public String getValue() { return value; }

    @Override public boolean equals(Object o) { ... }
    @Override public int hashCode() { ... }
    @Override public String toString() { return value; }
}
```

### Title.java — Value Object
```java
public final class Title {
    private final String value;

    public Title(String value) {
        if (value == null || value.isBlank()) throw new InvalidValueException("Title cannot be blank");
        if (value.length() > 200) throw new InvalidValueException("Title max length is 200");
        this.value = value.trim();
    }

    public String getValue() { return value; }
    // equals/hashCode/toString por value
}
```

### Description.java — Value Object
```java
public final class Description {
    private final String value;

    public Description(String value) {
        // aceita null/blank — descrição é opcional
        this.value = (value == null) ? "" : value.trim();
    }

    public String getValue() { return value; }
    // equals/hashCode/toString por value
}
```

### Task.java — Aggregate Root
```java
public class Task {
    private final TaskId id;
    private Title title;
    private Description description;
    private boolean completed;

    // Criação via factory method (encapsula ID gerado)
    public static Task create(String title, String description) {
        return new Task(TaskId.generate(), new Title(title), new Description(description));
    }

    // Construtor privado — só o factory e repositório usam
    private Task(TaskId id, Title title, Description description) { ... }

    // Comportamento do domínio — NÃO expõe setters diretos
    public void updateTitle(String newTitle) {
        this.title = new Title(newTitle); // validação embutida no Value Object
    }

    public void updateDescription(String newDescription) {
        this.description = new Description(newDescription);
    }

    public void complete() {
        this.completed = true;
    }

    public void reopen() {
        this.completed = false;
    }

    // Getters (sem setters)
    public TaskId getId() { return id; }
    public Title getTitle() { return title; }
    public Description getDescription() { return description; }
    public boolean isCompleted() { return completed; }
}
```

### TaskRepository.java — Abstração de Domínio (interface)
```java
// Fica em domain/repository — é um conceito de domínio, não de infraestrutura
public interface TaskRepository {
    void save(Task task);
    Optional<Task> findById(TaskId id);
    List<Task> findAll();
    void delete(TaskId id);
    boolean existsById(TaskId id);
}
```

---

## Camada de Aplicação

### CreateTaskCommand.java / UpdateTaskCommand.java
- Records imutáveis (Java 16+) com os dados brutos vindos da interface
- Sem lógica de negócio

### TaskDto.java
- Record de saída com tipos primitivos (String, boolean) — não expõe Value Objects para fora
- `String id, String title, String description, boolean completed`

### TaskApplicationService.java
```java
@Service
public class TaskApplicationService {
    private final TaskRepository taskRepository; // interface de domínio — Spring injeta InMemory

    // Create: monta Value Objects → chama Task.create() → salva
    public TaskDto createTask(CreateTaskCommand cmd) { ... }

    // Get: busca por TaskId → converte para TaskDto
    public TaskDto getTask(String id) { ... }

    // Update: busca → chama métodos de comportamento → salva
    public TaskDto updateTask(String id, UpdateTaskCommand cmd) { ... }

    // Delete
    public void deleteTask(String id) { ... }

    // List
    public List<TaskDto> listTasks() { ... }
}
```

---

## Camada de Infraestrutura

### InMemoryTaskRepository.java
```java
@Repository
public class InMemoryTaskRepository implements TaskRepository {
    private final Map<String, Task> store = new ConcurrentHashMap<>();

    @Override public void save(Task task) { store.put(task.getId().getValue(), task); }
    @Override public Optional<Task> findById(TaskId id) { ... }
    @Override public List<Task> findAll() { ... }
    @Override public void delete(TaskId id) { store.remove(id.getValue()); }
    @Override public boolean existsById(TaskId id) { return store.containsKey(id.getValue()); }
}
```

---

## Camada de Interfaces (Web)

### TaskController.java
```java
@RestController
@RequestMapping("/tasks")
public class TaskController {
    private final TaskApplicationService taskService;

    @PostMapping   → createTask  → 201 Created + body
    @GetMapping    → listTasks   → 200 OK + lista
    @GetMapping("/{id}") → getTask → 200 OK ou 404
    @PutMapping("/{id}") → updateTask → 200 OK ou 404
    @DeleteMapping("/{id}") → deleteTask → 204 No Content ou 404
}
```

### GlobalExceptionHandler.java
- `@RestControllerAdvice`
- `TaskNotFoundException` → 404
- `InvalidValueException` → 400

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

- POST sem `title` → 400 Bad Request
- POST com `title` > 200 chars → 400 Bad Request
- GET/PUT/DELETE com ID inexistente → 404 Not Found
- PUT com `title` em branco → 400 Bad Request

---

## Testes Obrigatórios

Cobertura JaCoCo mínima: **80% de linhas** (BUILD FAILURE se menor).

Testar obrigatoriamente:
1. **Value Objects** — validação no construtor (null, blank, > max length)
2. **Task Aggregate Root** — factory method, métodos de comportamento
3. **TaskApplicationService** — todos os 5 casos de uso com mocks do repository
4. **TaskController** — happy path e cenários de erro via MockMvc

---

## Critério de Conformidade Arquitetural (para preenchimento manual)

Revisar após a implementação:

| Ponto | OK? |
|-------|-----|
| Value Objects imutáveis (sem setters) | ☐ |
| Value Objects com validação no construtor | ☐ |
| Task expõe comportamento, não setters | ☐ |
| TaskRepository é interface em `domain/` | ☐ |
| `domain/` sem imports Spring | ☐ |
| `application/` injeta interface, não InMemory | ☐ |
| `interfaces/` não acessa domain diretamente | ☐ |
| Conversão Domain→DTO na camada `application/` | ☐ |

Pontuação: 1 ponto por item → nota `arch_conformance` = soma (0-10, ajustado se >8 itens).
