# BENCHMARK — Domain-Driven Design (DDD)

Implement the Task Manager REST API using **DDD** in $tech_stack.
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
```

### DDD Rules (CRITICAL)
- `domain/` is the innermost layer: ZERO imports from Spring Web, infrastructure, or interfaces
- `application/` orchestrates the domain — calls domain objects and domain repository interface
- `infrastructure/` implements domain interfaces — no domain logic here
- `interfaces/rest/` adapts HTTP to application commands — calls `TaskApplicationService`

Violations detected automatically:
- `domain/` importing `org.springframework.web` → FAIL
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

### STEP 1 — Write the domain layer
`Task.java`, `TaskId.java`, `TaskRepository.java` — pure domain, no Spring.

### STEP 2 — Write the application layer
`TaskApplicationService.java`, `CreateTaskCommand.java`, `UpdateTaskCommand.java`.

### STEP 3 — Write infrastructure
`InMemoryTaskRepositoryImpl.java` — implements domain `TaskRepository`.

### STEP 4 — Write the interfaces layer
`TaskController.java`, `CreateTaskRequest.java`, `UpdateTaskRequest.java`.

### STEP 5 — Write shared exceptions and main app class

### STEP 6 — Compile
```
mvn compile
```
Fix any errors. $build_fix_rules

### STEP 7 — Write the test file
`$test_base/$test_file` using $test_framework.
Target: $coverage_target%+ line coverage.

### STEP 8 — Run tests
```
mvn test
```
Repeat until 0 failures, 0 errors.

### STEP 9 — Done
Say exactly: $completion_signal
