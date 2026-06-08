# BENCHMARK — Clean Architecture

Implement the Task Manager REST API using **Clean Architecture** in $tech_stack.
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
│   ├── entity/
│   │   └── Task.java                        ← ZERO Spring imports, ZERO infrastructure imports
│   └── port/
│       ├── in/
│       │   └── TaskUseCase.java             ← interface (depends only on domain)
│       └── out/
│           └── TaskRepositoryPort.java      ← interface (depends only on domain)
├── application/
│   └── service/
│       └── TaskApplicationService.java      ← @Service, implements TaskUseCase
├── infrastructure/
│   ├── adapter/
│   │   ├── web/
│   │   │   ├── TaskController.java          ← @RestController
│   │   │   └── dto/
│   │   │       ├── CreateTaskRequest.java   ← @NotBlank on title only
│   │   │       └── UpdateTaskRequest.java   ← title nullable (no @NotBlank)
│   │   └── persistence/
│   │       └── InMemoryTaskRepository.java  ← @Repository, implements TaskRepositoryPort
│   └── config/
│       └── BeanConfig.java                  ← @Configuration, @Bean wiring
└── shared/
    └── exception/
        ├── TaskNotFoundException.java
        └── GlobalExceptionHandler.java      ← @RestControllerAdvice
```

### Dependency Rule (CRITICAL)
Dependencies point INWARD only. Inner layers must NEVER import outer layers.

| Layer          | May import from                         |
|----------------|-----------------------------------------|
| `domain/`      | nothing from this project               |
| `application/` | `domain/` only                          |
| `infrastructure/` | `application/` + `domain/`          |

Violations that are automatically detected:
- `domain/` importing `org.springframework` → FAIL
- `domain/` importing `infrastructure` → FAIL

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

### STEP 1 — Write domain layer first
`domain/entity/Task.java` and `domain/port/in/TaskUseCase.java` and `domain/port/out/TaskRepositoryPort.java`.
These must have ZERO Spring imports.

### STEP 2 — Write application layer
`application/service/TaskApplicationService.java` — implements TaskUseCase, injects TaskRepositoryPort.

### STEP 3 — Write infrastructure layer
- `infrastructure/adapter/web/TaskController.java` — injects TaskUseCase (the interface, not the impl)
- DTOs in `infrastructure/adapter/web/dto/`
- `infrastructure/adapter/persistence/InMemoryTaskRepository.java` — implements TaskRepositoryPort
- `infrastructure/config/BeanConfig.java` — @Bean wiring of TaskApplicationService with repository

### STEP 4 — Write shared exceptions
`shared/exception/TaskNotFoundException.java` and `GlobalExceptionHandler.java`.

### STEP 5 — Compile
```
mvn compile
```
Fix any errors. $build_fix_rules

### STEP 6 — Write the test file
`$test_base/$test_file` using $test_framework.
Test ALL endpoints. Target: $coverage_target%+ line coverage.

### STEP 7 — Run tests
```
mvn test
```
Repeat until 0 failures, 0 errors.

### STEP 8 — Done
Say exactly: $completion_signal
