# BENCHMARK — Vertical Slice Architecture

Implement the Task Manager REST API using the **Vertical Slice** pattern in $tech_stack.
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
├── task/                            ← everything task-related lives here
│   ├── TaskController.java          ← @RestController, @RequestMapping("/tasks")
│   ├── Task.java                    ← model
│   ├── CreateTaskRequest.java       ← @NotBlank on title only
│   ├── UpdateTaskRequest.java       ← title nullable (no @NotBlank)
│   ├── TaskService.java             ← business logic (can be interface+impl or single class)
│   └── InMemoryTaskRepository.java  ← ConcurrentHashMap storage
└── shared/
    └── exception/
        ├── TaskNotFoundException.java
        └── GlobalExceptionHandler.java ← @RestControllerAdvice
```

### Vertical Slice Principle
All classes related to the "task" feature live inside `task/`.
No cross-feature imports. Shared utilities go in `shared/`.

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

### STEP 1 — Write all production Java files
Use `write_file` for each file. Complete content only — no placeholders.

### STEP 2 — Compile
```
mvn compile
```
If BUILD FAILURE: fix errors and compile again.
$build_fix_rules

### STEP 3 — Write the test file
Use `write_file` to create `$test_base/$test_file`.
Use $test_framework. Test ALL endpoints including validation (400) and not-found (404) cases.
Target: $coverage_target%+ line coverage.

### STEP 4 — Run tests
```
mvn test
```
Fix any failures. Re-compile before re-testing. Repeat until 0 failures, 0 errors.

### STEP 5 — Done
Say exactly: $completion_signal
