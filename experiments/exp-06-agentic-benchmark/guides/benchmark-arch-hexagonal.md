# BENCHMARK — Hexagonal Architecture (Ports & Adapters)

Implement the Task Manager REST API using **Hexagonal Architecture** in $tech_stack.
Storage: $storage_desc

---

## Task Specification

$task_definition

---

## Required Files

### Production — `$src_base/`
$prod_files

### Test — `$test_base/`
$test_file

---

## Package Structure

```
$src_base/
├── TaskManagerApplication.java
├── domain/
│   ├── model/
│   │   └── Task.java                          ← pure domain object, ZERO Spring/adapter imports
│   ├── port/
│   │   ├── in/
│   │   │   └── TaskUseCase.java               ← driving port (interface)
│   │   └── out/
│   │       └── TaskRepositoryPort.java        ← driven port (interface)
│   └── service/
│       └── TaskServiceImpl.java               ← implements TaskUseCase, injects TaskRepositoryPort
├── adapter/
│   ├── in/
│   │   └── web/
│   │       ├── TaskController.java            ← @RestController, driving adapter
│   │       └── dto/
│   │           ├── CreateTaskRequest.java     ← @NotBlank on title only
│   │           └── UpdateTaskRequest.java     ← title nullable (no @NotBlank)
│   └── out/
│       └── persistence/
│           └── InMemoryTaskRepository.java    ← @Repository, driven adapter, implements TaskRepositoryPort
├── config/
│   └── AppConfig.java                         ← @Configuration, @Bean wiring
└── shared/
    └── exception/
        ├── TaskNotFoundException.java
        └── GlobalExceptionHandler.java        ← @RestControllerAdvice
```

### Hexagonal Rules (CRITICAL)
- **Domain core** (`domain/`) must NEVER import `org.springframework` or `adapter/`
- **Adapters** (`adapter/`) depend on domain ports — never on each other
- **Driving adapters** (`adapter/in/`) call domain via `TaskUseCase` interface
- **Driven adapters** (`adapter/out/`) implement domain port `TaskRepositoryPort`
- `AppConfig` wires `TaskServiceImpl(repository)` as a `@Bean`

Violations that are automatically detected:
- `domain/` importing `org.springframework` → FAIL
- `domain/` importing `adapter/` → FAIL

---

## Domain Rules

### Endpoints
| Method | Path         | Success | Error     |
|--------|--------------|---------|-----------|
| GET    | /tasks       | 200     | —         |
| POST   | /tasks       | 201     | 400       |
| GET    | /tasks/{id}  | 200     | 404       |
| PUT    | /tasks/{id}  | 200     | 400 / 404 |
| DELETE | /tasks/{id}  | 204     | 404       |

### Validation
$validation_rules

### PUT Partial Update
$partial_update_rules

### E2E Requirements
$e2e_rules

---

## Implementation Steps

### STEP 1 — Write domain layer (no Spring)
- `domain/model/Task.java`
- `domain/port/in/TaskUseCase.java`
- `domain/port/out/TaskRepositoryPort.java`
- `domain/service/TaskServiceImpl.java`

### STEP 2 — Write adapters
- `adapter/in/web/TaskController.java` (injects `TaskUseCase`)
- DTOs in `adapter/in/web/dto/`
- `adapter/out/persistence/InMemoryTaskRepository.java` (implements `TaskRepositoryPort`)

### STEP 3 — Write config and exceptions
- `config/AppConfig.java`
- `shared/exception/TaskNotFoundException.java`
- `shared/exception/GlobalExceptionHandler.java`

### STEP 4 — Compile
```
mvn compile
```
Fix any errors. $build_fix_rules

### STEP 5 — Write the test file
`$test_base/$test_file` using $test_framework.
Test ALL endpoints. Target: $coverage_target%+ coverage.

### STEP 6 — Run tests
```
mvn test
```
Repeat until 0 failures, 0 errors.

### STEP 7 — Done
Say exactly: $completion_signal
