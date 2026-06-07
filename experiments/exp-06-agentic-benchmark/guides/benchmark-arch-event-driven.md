# BENCHMARK — Event-Driven Architecture

Implement the Task Manager REST API using an **Event-Driven** pattern in $tech_stack.
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
├── event/
│   ├── TaskCreatedEvent.java          ← immutable event record
│   ├── TaskUpdatedEvent.java
│   └── TaskDeletedEvent.java
├── command/
│   ├── CreateTaskCommand.java
│   ├── UpdateTaskCommand.java
│   └── DeleteTaskCommand.java
├── handler/
│   ├── TaskCommandHandler.java        ← @Service, handles commands, publishes events via ApplicationEventPublisher
│   └── TaskEventHandler.java         ← @Component, @EventListener, updates repository state
├── repository/
│   └── TaskRepository.java           ← @Repository, ConcurrentHashMap
├── controller/
│   └── TaskController.java           ← @RestController, sends commands to TaskCommandHandler
├── dto/
│   ├── CreateTaskRequest.java        ← @NotBlank on title only
│   └── UpdateTaskRequest.java        ← title nullable (no @NotBlank)
└── exception/
    ├── TaskNotFoundException.java
    └── GlobalExceptionHandler.java   ← @RestControllerAdvice
```

### Event-Driven Flow
```
HTTP Request → TaskController
  → creates Command → TaskCommandHandler
    → validates + creates/updates Task
    → publishes Event via ApplicationEventPublisher
      → TaskEventHandler @EventListener
        → persists to TaskRepository
    → returns result to controller
```

Note: Spring's `ApplicationEventPublisher` is synchronous by default — this is fine for the benchmark.

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

### STEP 1 — Write model, events, commands
`Task.java`, all event records, all command records.

### STEP 2 — Write repository
`TaskRepository.java` — ConcurrentHashMap, basic CRUD.

### STEP 3 — Write handlers
`TaskCommandHandler.java` — inject `ApplicationEventPublisher` and `TaskRepository`.
`TaskEventHandler.java` — @EventListener methods that update state.

### STEP 4 — Write controller and DTOs
`TaskController.java` calls `TaskCommandHandler` methods.

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
