# PRD — Task Manager API: Layered MVC Architecture

## Visão Geral

Implementar a Task Manager REST API especificada em `spec/task-definition.md` usando a
**Arquitetura Layered MVC** (Model-View-Controller em camadas): o padrão clássico do
Spring Boot, onde o código é organizado por **responsabilidade técnica** em camadas horizontais.

Esta é a arquitetura padrão gerada pelo Spring Initializr e a mais comum em projetos Java.
Serve como **referência de familiaridade** no benchmark — esperamos que a IA conheça muito bem.

```
HTTP Request
     ↓
 Controller   ← camada web (HTTP handlers, DTOs)
     ↓
  Service     ← camada de negócio (lógica, regras)
     ↓
 Repository   ← camada de dados (acesso, persistência)
     ↓
   Model      ← entidades e DTOs
```

---

## Stack Obrigatória

- Java 21
- Spring Boot 3.2 (pom.xml já configurado em `arch-benchmark/mvc/pom.xml`)
- Maven (`.\mvnw.cmd`)
- Storage in-memory (`ConcurrentHashMap`)
- JUnit 5 + Spring Boot Test
- JaCoCo (mínimo 80% de cobertura)
- **MODELO OBRIGATÓRIO:** `claude-sonnet-4-6`

---

## Estrutura de Pacotes OBRIGATÓRIA

```
src/main/java/com/benchmark/taskmanager/
├── TaskManagerApplication.java
├── controller/
│   └── TaskController.java              ← @RestController, mapeia os 5 endpoints
├── service/
│   └── TaskService.java                 ← @Service, contém toda a lógica de negócio
├── repository/
│   ├── TaskRepository.java              ← interface do repositório
│   └── InMemoryTaskRepository.java      ← @Repository, implementação ConcurrentHashMap
├── model/
│   └── Task.java                        ← entidade (id, title, description, completed, createdAt, updatedAt)
├── dto/
│   ├── CreateTaskRequest.java           ← DTO de entrada para POST
│   └── UpdateTaskRequest.java           ← DTO de entrada para PUT
└── exception/
    ├── TaskNotFoundException.java       ← RuntimeException para 404
    └── GlobalExceptionHandler.java      ← @RestControllerAdvice

src/test/java/com/benchmark/taskmanager/
├── controller/
│   └── TaskControllerTest.java
└── service/
    └── TaskServiceTest.java
```

---

## Regras de Dependência (OBRIGATÓRIO)

```
TaskController  →  TaskService  →  TaskRepository (interface)
                                          ↑
                              InMemoryTaskRepository (implementação)
```

**Lei da dependência unidirecional descendente:**
- `controller/` → depende de `service/`, `dto/`, `exception/`
- `service/` → depende de `repository/`, `model/`, `exception/`
- `repository/` → depende de `model/`
- `model/` → sem dependências internas do projeto

**Proibido:**
- `TaskController` não acessa `TaskRepository` ou `InMemoryTaskRepository` diretamente
- `TaskService` não tem anotações `@RestController` ou imports de `org.springframework.web`
- `model/Task.java` não tem lógica de negócio nem imports de `service/` ou `controller/`

---

## Nomenclatura Obrigatória

| Classe | Pacote | Anotação | Papel |
|--------|--------|----------|-------|
| `TaskController` | controller | `@RestController` | HTTP handler |
| `TaskService` | service | `@Service` | Lógica de negócio |
| `TaskRepository` | repository | — | Interface de repositório |
| `InMemoryTaskRepository` | repository | `@Repository` | Impl in-memory |
| `Task` | model | — | Entidade |
| `CreateTaskRequest` | dto | — | DTO POST |
| `UpdateTaskRequest` | dto | — | DTO PUT |
| `TaskNotFoundException` | exception | — | 404 exception |
| `GlobalExceptionHandler` | exception | `@RestControllerAdvice` | Tratamento global de erros |

---

## Endpoints

| Método | Rota        | Sucesso | Erro   |
|--------|-------------|---------|--------|
| GET    | /tasks      | 200     | —      |
| POST   | /tasks      | 201     | 400    |
| GET    | /tasks/{id} | 200     | 404    |
| PUT    | /tasks/{id} | 200     | 400/404|
| DELETE | /tasks/{id} | 204     | 404    |

### Validações

- `title` ausente ou vazio → 400 `{"error":"title is required"}`
- `title` > 200 chars → 400 `{"error":"title must not exceed 200 characters"}`
- `description` > 1000 chars → 400 `{"error":"description must not exceed 1000 characters"}`
- ID não encontrado → 404 `{"error":"Task not found"}`

---

## Modelo Task

```java
String id;          // UUID gerado na criação
String title;       // obrigatório, max 200 chars
String description; // opcional, max 1000 chars
boolean completed;  // default false
String createdAt;   // ISO 8601
String updatedAt;   // ISO 8601, atualizado a cada PUT
```

---

## Critérios de Aceite

- `.\mvnw.cmd compile` → BUILD SUCCESS
- `.\mvnw.cmd test` → 0 failures, 0 errors, cobertura linha ≥ 80%
- 12/12 cenários E2E passando
- Estrutura de pacotes conforme diagrama (controller, service, repository, model, dto, exception)
- `TaskController` não acessa `TaskRepository` diretamente (apenas via `TaskService`)
