# BENCHMARK — MVC Architecture

Implement the Task Manager REST API using the **MVC** pattern in $tech_stack.
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
├── controller/
│   └── TaskController.java          ← @RestController, @RequestMapping("/tasks")
├── model/
│   └── Task.java                    ← plain Java record or class (no Spring imports)
├── dto/
│   ├── CreateTaskRequest.java       ← @NotBlank on title only
│   └── UpdateTaskRequest.java       ← title nullable (no @NotBlank here)
├── service/
│   ├── TaskService.java             ← interface
│   └── impl/
│       └── TaskServiceImpl.java     ← @Service
├── repository/
│   ├── TaskRepository.java          ← interface
│   └── impl/
│       └── InMemoryTaskRepository.java ← @Repository, ConcurrentHashMap
└── exception/
    ├── TaskNotFoundException.java
    └── GlobalExceptionHandler.java  ← @RestControllerAdvice
```

### MVC Layer Rules
- Controller → only calls TaskService (never imports repository directly)
- Service → only calls TaskRepository (never imports controller)
- Repository → no Spring Web imports

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
Use `write_file` for each file in the list above.
Write complete file content — no placeholders, no `// TODO`.

### STEP 2 — Compile
```
mvn compile
```
If BUILD FAILURE: read error output carefully, fix the affected files, compile again.
$build_fix_rules

### STEP 3 — Write the test file
Use `write_file` to create `$test_base/$test_file`.
Use $test_framework. Cover ALL endpoints including 400 and 404 cases.
Target: $coverage_target%+ line coverage.

### STEP 4 — Run tests
```
mvn test
```
If failures: fix implementation or tests. Always re-compile before re-testing.
Repeat until BUILD SUCCESS with 0 failures and 0 errors.

### STEP 5 — Done
When `mvn test` shows BUILD SUCCESS with 0 failures:
Say exactly: $completion_signal
