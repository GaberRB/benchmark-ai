# PRD — Task Manager API: Vertical Slice Architecture

## Visão Geral

Implementar a mesma Task Manager REST API especificada em `spec/task-definition.md`, mas
organizada segundo a **Vertical Slice Architecture**: o código é agrupado por **caso de uso
(slice)**, não por camada técnica.

Cada slice é auto-suficiente: contém seu próprio controller, DTO de request, DTO de
response e lógica de negócio. Slices não chamam uns aos outros. Código verdadeiramente
compartilhado (entidade, repositório) vai em `shared/`.

---

## Stack Obrigatória

- Java 21
- Spring Boot 3.2 (pom.xml já configurado em `arch-benchmark/vertical-slice/pom.xml`)
- Maven (`.\mvnw.cmd`)
- Storage in-memory (`ConcurrentHashMap`)
- JUnit 5 + Spring Boot Test
- JaCoCo (mínimo 80% de cobertura — BUILD FAILURE se < 80%)
- **MODELO OBRIGATÓRIO:** `claude-sonnet-4-6`

---

## Estrutura de Pacotes OBRIGATÓRIA

```
src/main/java/com/benchmark/taskmanager/
├── TaskManagerApplication.java
├── tasks/
│   ├── create/
│   │   ├── CreateTaskController.java    ← @RestController POST /tasks
│   │   ├── CreateTaskRequest.java       ← DTO de entrada (title, description)
│   │   └── CreateTaskUseCase.java       ← lógica de negócio para criação
│   ├── get/
│   │   ├── GetTaskController.java       ← @RestController GET /tasks/{id}
│   │   └── GetTaskUseCase.java
│   ├── update/
│   │   ├── UpdateTaskController.java    ← @RestController PUT /tasks/{id}
│   │   ├── UpdateTaskRequest.java       ← DTO de entrada (title?, description?, completed?)
│   │   └── UpdateTaskUseCase.java
│   ├── delete/
│   │   ├── DeleteTaskController.java    ← @RestController DELETE /tasks/{id}
│   │   └── DeleteTaskUseCase.java
│   ├── list/
│   │   ├── ListTasksController.java     ← @RestController GET /tasks
│   │   └── ListTasksUseCase.java
│   └── shared/
│       ├── Task.java                    ← entidade (id, title, description, completed, createdAt, updatedAt)
│       ├── TaskRepository.java          ← interface com: save, findById, findAll, deleteById
│       ├── InMemoryTaskRepository.java  ← implementação com ConcurrentHashMap (@Repository)
│       └── TaskNotFoundException.java   ← RuntimeException lançada quando ID não encontrado

src/test/java/com/benchmark/taskmanager/
├── tasks/
│   ├── create/
│   │   └── CreateTaskControllerTest.java
│   ├── get/
│   │   └── GetTaskControllerTest.java
│   ├── update/
│   │   └── UpdateTaskControllerTest.java
│   ├── delete/
│   │   └── DeleteTaskControllerTest.java
│   └── list/
│       └── ListTasksControllerTest.java
```

---

## Regras de Dependência (OBRIGATÓRIO)

```
CreateTaskController  → CreateTaskUseCase  → TaskRepository (interface)
GetTaskController     → GetTaskUseCase     → TaskRepository (interface)
UpdateTaskController  → UpdateTaskUseCase  → TaskRepository (interface)
DeleteTaskController  → DeleteTaskUseCase  → TaskRepository (interface)
ListTasksController   → ListTasksUseCase   → TaskRepository (interface)

InMemoryTaskRepository  implementa  TaskRepository
```

**Proibido:**
- Slices não chamam outros slices (CreateTaskUseCase não pode importar GetTaskUseCase)
- Controllers não acessam TaskRepository diretamente (apenas via UseCase)
- UseCases não têm anotações Spring (sem @Service — são POJOs com @Component apenas se necessário para DI)

---

## Nomenclatura Obrigatória

| Classe | Pacote | Papel |
|--------|--------|-------|
| `CreateTaskController` | tasks.create | HTTP handler POST /tasks |
| `CreateTaskRequest` | tasks.create | DTO de entrada |
| `CreateTaskUseCase` | tasks.create | Lógica de criação |
| `GetTaskController` | tasks.get | HTTP handler GET /tasks/{id} |
| `GetTaskUseCase` | tasks.get | Lógica de busca por ID |
| `UpdateTaskController` | tasks.update | HTTP handler PUT /tasks/{id} |
| `UpdateTaskRequest` | tasks.update | DTO de atualização |
| `UpdateTaskUseCase` | tasks.update | Lógica de atualização |
| `DeleteTaskController` | tasks.delete | HTTP handler DELETE /tasks/{id} |
| `DeleteTaskUseCase` | tasks.delete | Lógica de deleção |
| `ListTasksController` | tasks.list | HTTP handler GET /tasks |
| `ListTasksUseCase` | tasks.list | Lógica de listagem |
| `Task` | tasks.shared | Entidade |
| `TaskRepository` | tasks.shared | Interface de repositório |
| `InMemoryTaskRepository` | tasks.shared | Impl in-memory |
| `TaskNotFoundException` | tasks.shared | Exceção de domínio |

---

## Endpoints

| Método | Rota        | Sucesso | Erro   |
|--------|-------------|---------|--------|
| GET    | /tasks      | 200     | —      |
| POST   | /tasks      | 201     | 400    |
| GET    | /tasks/{id} | 200     | 404    |
| PUT    | /tasks/{id} | 200     | 400/404|
| DELETE | /tasks/{id} | 204     | 404    |

### Tratamento de erros

Usar `@RestControllerAdvice` em `tasks/shared/GlobalExceptionHandler.java`:
- `TaskNotFoundException` → 404 `{"error":"Task not found"}`
- `title` ausente/vazio → 400 `{"error":"title is required"}`
- `title` > 200 chars → 400 `{"error":"title must not exceed 200 characters"}`
- `description` > 1000 chars → 400 `{"error":"description must not exceed 1000 characters"}`

---

## Modelo Task

```java
// tasks/shared/Task.java
String id;          // UUID gerado no momento da criação
String title;       // obrigatório, max 200 chars
String description; // opcional, max 1000 chars
boolean completed;  // default false
String createdAt;   // ISO 8601, gerado na criação
String updatedAt;   // ISO 8601, atualizado a cada PUT
```

---

## Critérios de Aceite

- `.\mvnw.cmd compile` → BUILD SUCCESS
- `.\mvnw.cmd test` → 0 failures, 0 errors, cobertura linha ≥ 80%
- 12/12 cenários E2E passando
- Estrutura de pacotes conforme diagrama acima (sem desvios)
- Nenhum slice importa outro slice (verificar nos imports)
