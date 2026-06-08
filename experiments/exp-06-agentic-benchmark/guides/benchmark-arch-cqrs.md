# BENCHMARK — CQRS (Command Query Responsibility Segregation)

Implement the Task Manager REST API using **CQRS** in $tech_stack.
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
├── model/
│   └── Task.java
├── command/
│   ├── CreateTaskCommand.java
│   ├── UpdateTaskCommand.java
│   ├── DeleteTaskCommand.java
│   └── handler/
│       ├── CreateTaskCommandHandler.java    ← @Service
│       ├── UpdateTaskCommandHandler.java    ← @Service
│       └── DeleteTaskCommandHandler.java    ← @Service
├── query/
│   ├── GetAllTasksQuery.java
│   ├── GetTaskByIdQuery.java
│   └── handler/
│       ├── GetAllTasksQueryHandler.java     ← @Service
│       └── GetTaskByIdQueryHandler.java     ← @Service
├── store/
│   └── TaskStore.java                      ← @Repository, shared ConcurrentHashMap (write + read)
├── controller/
│   └── TaskController.java                 ← @RestController, routes to command/query handlers
├── dto/
│   ├── CreateTaskRequest.java              ← @NotBlank on title only
│   └── UpdateTaskRequest.java              ← title nullable (no @NotBlank)
└── exception/
    ├── TaskNotFoundException.java
    └── GlobalExceptionHandler.java         ← @RestControllerAdvice
```

### CQRS Rules (CRITICAL)
- **Command side** (`command/`) handles state changes — must NEVER import from `query/`
- **Query side** (`query/`) handles reads — must NEVER import from `command/`
- `TaskStore` is the shared in-memory store used by both sides
- Controller routes: POST/PUT/DELETE → command handlers; GET → query handlers

Violations detected automatically:
- `command/` importing `query/` → FAIL
- `query/` importing `command/` → FAIL

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

### STEP 1 — Write model and store
`Task.java` and `TaskStore.java` (ConcurrentHashMap, no command/query imports).

### STEP 2 — Write command handlers
`CreateTaskCommandHandler`, `UpdateTaskCommandHandler`, `DeleteTaskCommandHandler`.
Each injects `TaskStore` only — no `query/` imports.

### STEP 3 — Write query handlers
`GetAllTasksQueryHandler`, `GetTaskByIdQueryHandler`.
Each injects `TaskStore` only — no `command/` imports.

### STEP 4 — Write controller and DTOs
`TaskController` routes GET to query handlers, POST/PUT/DELETE to command handlers.

### STEP 5 — Write exceptions and main app class

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
