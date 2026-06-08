# BENCHMARK — Domain-Driven Design (DDD)

Implement the Task Manager REST API using **DDD Tático**.

**Stack**: Java 21, Spring Boot 3.2, Maven  
**Storage**: in-memory (ConcurrentHashMap)

> `mvn compile && mvn test` runs automatically after each change you make.
> Fix any failures and continue until all tests pass with ≥ 80% line coverage.
> When done, output exactly: `IMPLEMENTATION COMPLETE`

---

## Package Structure

```
src/main/java/com/benchmark/taskmanager/
├── TaskManagerApplication.java
├── domain/
│   ├── model/
│   │   └── Task.java                              ← Aggregate Root, ZERO Spring/infra imports
│   ├── valueobject/
│   │   └── TaskId.java                            ← Value Object wrapping UUID
│   └── repository/
│       └── TaskRepository.java                    ← domain repository interface
├── application/
│   ├── service/
│   │   └── TaskApplicationService.java            ← @Service, orchestrates domain
│   └── dto/
│       ├── CreateTaskCommand.java
│       └── UpdateTaskCommand.java
├── infrastructure/
│   └── persistence/
│       └── InMemoryTaskRepositoryImpl.java        ← @Repository, implements domain TaskRepository
├── interfaces/
│   └── rest/
│       ├── TaskController.java                    ← @RestController
│       └── dto/
│           ├── CreateTaskRequest.java             ← @NotBlank on title only
│           └── UpdateTaskRequest.java             ← title nullable (no @NotBlank)
└── shared/
    └── exception/
        ├── TaskNotFoundException.java
        └── GlobalExceptionHandler.java            ← @RestControllerAdvice

src/test/java/com/benchmark/taskmanager/
└── TaskManagerTest.java
```

### DDD Rules (CRITICAL)
- `domain/` is the innermost layer: ZERO imports from Spring Web, infrastructure, or interfaces
- `application/` orchestrates the domain — calls domain objects and domain repository interface
- `infrastructure/` implements domain interfaces — no domain logic here
- `interfaces/rest/` adapts HTTP to application commands — calls `TaskApplicationService`

**Violations automatically detected:**
- `domain/` importing `org.springframework.web` → FAIL
- `domain/` importing `infrastructure` → FAIL

---

## Data Model

```java
// Task.java in domain/model/ — no Spring imports
// TaskId.java wraps UUID: record TaskId(UUID value) {}
String id;          // stored as TaskId value object internally, exposed as String via REST
String title;       // required, max 200 chars
String description; // optional, max 1000 chars
boolean completed;  // default false
String createdAt;   // ISO 8601 UTC
String updatedAt;   // ISO 8601 UTC
```

---

## Endpoints

| Method | Path         | Success | Error     |
|--------|--------------|---------|-----------|
| GET    | /tasks       | 200     | —         |
| POST   | /tasks       | 201     | 400       |
| GET    | /tasks/{id}  | 200     | 404       |
| PUT    | /tasks/{id}  | 200     | 400 / 404 |
| DELETE | /tasks/{id}  | 204     | 404       |

---

## Validation Rules

- `title` absent or blank → 400: `{"error": "title is required"}`
- `title` > 200 chars → 400: `{"error": "title must not exceed 200 characters"}`
- `description` > 1000 chars → 400: `{"error": "description must not exceed 1000 characters"}`
- ID not found → 404: `{"error": "Task not found"}`

**CRITICAL**: Use `@PathVariable String id` (not `UUID`). Handle `IllegalArgumentException` → `TaskNotFoundException` (404).

---

## PUT Partial Update

Only update fields present in the request. Always refresh `updatedAt`.

---

## Implementation Order

1. Write `domain/` layer (Task, TaskId, TaskRepository interface)
2. Write `application/` layer (TaskApplicationService, commands)
3. Write `infrastructure/` layer (InMemoryTaskRepositoryImpl)
4. Write `interfaces/rest/` layer (TaskController, DTOs)
5. Write `shared/exception/` and `TaskManagerApplication.java`
6. Write `TaskManagerTest.java` — cover all endpoints including 400 and 404 cases
7. Fix failures until BUILD SUCCESS with 0 failures, coverage ≥ 80%
8. Output: `IMPLEMENTATION COMPLETE`
