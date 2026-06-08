# BENCHMARK JAVA QUARKUS — GRADLE MODO 1 (Agente Sequencial)

> Você é o agente responsável por executar este benchmark completo.
> Leia todos os passos antes de iniciar. Execute em ordem. Não pule etapas.
> Este arquivo conduz você do início à coleta final de métricas.
>
> **MODELO OBRIGATÓRIO:** Esta sessão deve rodar com `claude-sonnet-4-6`.
> Confirme executando: `claude --version` e verificando o modelo ativo nas configurações.
>
> **FRAMEWORK:** Quarkus 3.8.3 — NÃO Spring Boot.
> **BUILD TOOL:** Gradle — NÃO Maven.
> Use JAX-RS (`jakarta.ws.rs.*`) para REST e CDI (`@ApplicationScoped`, `@Inject`) para injeção.

---

## PASSO 1 — Capturar Session ID atual

Execute o comando abaixo para descobrir o session ID desta sessão Claude Code:

```powershell
Get-Content (Get-ChildItem "$env:USERPROFILE\.claude\sessions\" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName | ConvertFrom-Json | Select-Object sessionId, cwd, startedAt
```

**Guarde o `sessionId` retornado — você vai precisar dele no Passo 7.**

---

## PASSO 0 — Verificar Gradle instalado

```powershell
cd experiments/exp-01-java-vs-kotlin/java-quarkus-gradle-mode-1
.\gradlew.bat --version
```

Esperado: Gradle 8.x. Se não funcionar, verifique se o arquivo `gradlew.bat` e a pasta `gradle/wrapper/` existem no diretório.

---

## PASSO 2 — Snapshot pré-sessão

A partir da raiz do benchmark (`C:\Users\grios\OneDrive\Desktop\benchmark`):

```powershell
python tools/snapshot.py --pre --language java-quarkus-gradle
```

Confirme que o arquivo `tools/reports/snapshot_java-quarkus-gradle_pre_*.json` foi criado.

---

## PASSO 3 — Ler a especificação

Leia o arquivo abaixo antes de implementar qualquer código:

`shared/task-definition.md` — Especificação funcional dos endpoints (5 endpoints CRUD, modelo Task, validações)

---

## PASSO 4 — Implementar a Task Manager API com Quarkus

Trabalhe dentro do diretório `experiments/exp-01-java-vs-kotlin/java-quarkus-gradle-mode-1/`.

O `build.gradle` já está configurado — **não modifique**.
O `settings.gradle` já está configurado — **não modifique**.
O `gradle.properties` já está configurado — **não modifique**.
O `src/main/resources/application.properties` já está configurado — **não modifique**.

### Stack obrigatória

- Java 21, **Quarkus 3.8.3**, Gradle
- REST via **JAX-RS** (`jakarta.ws.rs.*`) — NÃO Spring MVC
- DI via **CDI** (`@ApplicationScoped`, `@Inject`) — NÃO Spring
- Storage in-memory (`ConcurrentHashMap`)
- **JUnit 5 + `@QuarkusTest` + RestAssured** para testes
- `quarkus-jacoco` para cobertura (mínimo 80%)

### Estrutura de arquivos a criar

```
java-quarkus-gradle-mode-1/
├── build.gradle                     ← JÁ EXISTE — não modifique
├── settings.gradle                  ← JÁ EXISTE — não modifique
├── gradle.properties                ← JÁ EXISTE — não modifique
├── gradlew.bat                      ← JÁ EXISTE
├── gradle/wrapper/                  ← JÁ EXISTE
└── src/
    ├── main/
    │   ├── java/com/benchmark/taskmanager/
    │   │   ├── model/Task.java
    │   │   ├── dto/CreateTaskRequest.java
    │   │   ├── dto/UpdateTaskRequest.java
    │   │   ├── repository/TaskRepository.java
    │   │   ├── repository/impl/InMemoryTaskRepository.java
    │   │   ├── service/TaskService.java
    │   │   ├── service/impl/TaskServiceImpl.java
    │   │   ├── resource/TaskResource.java
    │   │   └── exception/
    │   │       ├── TaskNotFoundException.java
    │   │       ├── TaskNotFoundExceptionMapper.java
    │   │       └── ValidationExceptionMapper.java
    │   └── resources/
    │       └── application.properties  ← JÁ EXISTE — não modifique
    └── test/java/com/benchmark/taskmanager/
        └── TaskResourceTest.java
```

### Endpoints a implementar

| Método | Rota        | Sucesso | Erro   |
|--------|-------------|---------|--------|
| GET    | /tasks      | 200     | —      |
| POST   | /tasks      | 201     | 400    |
| GET    | /tasks/{id} | 200     | 404    |
| PUT    | /tasks/{id} | 200     | 400/404|
| DELETE | /tasks/{id} | 204     | 404    |

### Modelo Task

```java
{ id (UUID), title (max 200, obrigatório), description (max 1000, opcional),
  completed (boolean, default false), createdAt (ISO 8601), updatedAt (ISO 8601) }
```

### Validações obrigatórias

- `title` ausente ou vazio → 400 `{"error":"title is required"}`
- `title` > 200 chars → 400 `{"error":"title must not exceed 200 characters"}`
- `description` > 1000 chars → 400 `{"error":"description must not exceed 1000 characters"}`
- ID não encontrado → 404 `{"error":"Task not found"}`

---

## REFERÊNCIA DE IMPLEMENTAÇÃO QUARKUS

Esta seção mostra os padrões obrigatórios de cada classe. Use como guia de escrita.
O código é idêntico à variante Maven — apenas os comandos de build mudam.

### model/Task.java

```java
package com.benchmark.taskmanager.model;

import java.time.Instant;
import java.util.UUID;

public class Task {
    private String id;
    private String title;
    private String description;
    private boolean completed;
    private String createdAt;
    private String updatedAt;

    public Task() {}

    public static Task create(String title, String description) {
        Task task = new Task();
        task.id = UUID.randomUUID().toString();
        task.title = title;
        task.description = description;
        task.completed = false;
        String now = Instant.now().toString();
        task.createdAt = now;
        task.updatedAt = now;
        return task;
    }

    // getters e setters obrigatórios para serialização Jackson
}
```

### dto/CreateTaskRequest.java

```java
package com.benchmark.taskmanager.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class CreateTaskRequest {
    @NotBlank(message = "title is required")
    @Size(max = 200, message = "title must not exceed 200 characters")
    private String title;

    @Size(max = 1000, message = "description must not exceed 1000 characters")
    private String description;

    // getters e setters
}
```

### dto/UpdateTaskRequest.java

```java
package com.benchmark.taskmanager.dto;

import jakarta.validation.constraints.Size;

public class UpdateTaskRequest {
    @Size(max = 200, message = "title must not exceed 200 characters")
    private String title;

    @Size(max = 1000, message = "description must not exceed 1000 characters")
    private String description;

    private Boolean completed;

    // getters e setters
}
```

### repository/TaskRepository.java + impl/InMemoryTaskRepository.java

```java
// TaskRepository.java
package com.benchmark.taskmanager.repository;
import com.benchmark.taskmanager.model.Task;
import java.util.List;
import java.util.Optional;

public interface TaskRepository {
    List<Task> findAll();
    Optional<Task> findById(String id);
    Task save(Task task);
    void deleteById(String id);
    boolean existsById(String id);
}

// InMemoryTaskRepository.java
package com.benchmark.taskmanager.repository.impl;
import com.benchmark.taskmanager.model.Task;
import com.benchmark.taskmanager.repository.TaskRepository;
import jakarta.enterprise.context.ApplicationScoped;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@ApplicationScoped
public class InMemoryTaskRepository implements TaskRepository {
    private final Map<String, Task> store = new ConcurrentHashMap<>();
    @Override public List<Task> findAll() { return new ArrayList<>(store.values()); }
    @Override public Optional<Task> findById(String id) { return Optional.ofNullable(store.get(id)); }
    @Override public Task save(Task task) { store.put(task.getId(), task); return task; }
    @Override public void deleteById(String id) { store.remove(id); }
    @Override public boolean existsById(String id) { return store.containsKey(id); }
}
```

### service/TaskService.java + impl/TaskServiceImpl.java

```java
// TaskService.java
package com.benchmark.taskmanager.service;
import com.benchmark.taskmanager.dto.*;
import com.benchmark.taskmanager.model.Task;
import java.util.List;

public interface TaskService {
    List<Task> findAll();
    Task findById(String id);
    Task create(CreateTaskRequest request);
    Task update(String id, UpdateTaskRequest request);
    void delete(String id);
}

// TaskServiceImpl.java
package com.benchmark.taskmanager.service.impl;
import com.benchmark.taskmanager.dto.*;
import com.benchmark.taskmanager.exception.TaskNotFoundException;
import com.benchmark.taskmanager.model.Task;
import com.benchmark.taskmanager.repository.TaskRepository;
import com.benchmark.taskmanager.service.TaskService;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import java.time.Instant;
import java.util.List;

@ApplicationScoped
public class TaskServiceImpl implements TaskService {
    @Inject TaskRepository taskRepository;

    @Override public List<Task> findAll() { return taskRepository.findAll(); }

    @Override public Task findById(String id) {
        return taskRepository.findById(id).orElseThrow(() -> new TaskNotFoundException("Task not found"));
    }

    @Override public Task create(CreateTaskRequest req) {
        return taskRepository.save(Task.create(req.getTitle(), req.getDescription()));
    }

    @Override public Task update(String id, UpdateTaskRequest req) {
        Task task = findById(id);
        if (req.getTitle() != null) {
            if (req.getTitle().isBlank()) throw new IllegalArgumentException("title is required");
            task.setTitle(req.getTitle());
        }
        if (req.getDescription() != null) task.setDescription(req.getDescription());
        if (req.getCompleted() != null) task.setCompleted(req.getCompleted());
        task.setUpdatedAt(Instant.now().toString());
        return taskRepository.save(task);
    }

    @Override public void delete(String id) {
        if (!taskRepository.existsById(id)) throw new TaskNotFoundException("Task not found");
        taskRepository.deleteById(id);
    }
}
```

### resource/TaskResource.java

```java
package com.benchmark.taskmanager.resource;

import com.benchmark.taskmanager.dto.CreateTaskRequest;
import com.benchmark.taskmanager.dto.UpdateTaskRequest;
import com.benchmark.taskmanager.model.Task;
import com.benchmark.taskmanager.service.TaskService;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.validation.Valid;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import java.util.List;

@Path("/tasks")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@ApplicationScoped
public class TaskResource {

    @Inject
    TaskService taskService;

    @GET
    public List<Task> listAll() { return taskService.findAll(); }

    @POST
    public Response create(@Valid CreateTaskRequest request) {
        return Response.status(201).entity(taskService.create(request)).build();
    }

    @GET
    @Path("/{id}")
    public Task findById(@PathParam("id") String id) { return taskService.findById(id); }

    @PUT
    @Path("/{id}")
    public Task update(@PathParam("id") String id, UpdateTaskRequest request) {
        return taskService.update(id, request);
    }

    @DELETE
    @Path("/{id}")
    public Response delete(@PathParam("id") String id) {
        taskService.delete(id);
        return Response.noContent().build();
    }
}
```

### exception/TaskNotFoundException.java + mappers

```java
// TaskNotFoundException.java
package com.benchmark.taskmanager.exception;
public class TaskNotFoundException extends RuntimeException {
    public TaskNotFoundException(String message) { super(message); }
}

// TaskNotFoundExceptionMapper.java
package com.benchmark.taskmanager.exception;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.ext.ExceptionMapper;
import jakarta.ws.rs.ext.Provider;
import java.util.Map;

@Provider
public class TaskNotFoundExceptionMapper implements ExceptionMapper<TaskNotFoundException> {
    @Override
    public Response toResponse(TaskNotFoundException e) {
        return Response.status(404).entity(Map.of("error", e.getMessage())).build();
    }
}

// ValidationExceptionMapper.java
package com.benchmark.taskmanager.exception;
import jakarta.validation.ConstraintViolationException;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.ext.ExceptionMapper;
import jakarta.ws.rs.ext.Provider;
import java.util.Map;

@Provider
public class ValidationExceptionMapper implements ExceptionMapper<ConstraintViolationException> {
    @Override
    public Response toResponse(ConstraintViolationException e) {
        String message = e.getConstraintViolations().stream()
            .map(v -> v.getMessage()).findFirst().orElse("Validation error");
        return Response.status(400).entity(Map.of("error", message)).build();
    }
}
```

### test/TaskResourceTest.java

```java
package com.benchmark.taskmanager;

import io.quarkus.test.junit.QuarkusTest;
import io.restassured.http.ContentType;
import org.junit.jupiter.api.Test;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.*;

@QuarkusTest
public class TaskResourceTest {

    @Test void testListEmpty() {
        given().when().get("/tasks").then().statusCode(200);
    }

    @Test void testCreateTask() {
        given().contentType(ContentType.JSON)
            .body("{\"title\":\"Test Task\",\"description\":\"Desc\"}")
            .when().post("/tasks").then().statusCode(201)
            .body("id", notNullValue()).body("title", equalTo("Test Task"));
    }

    @Test void testCreateWithoutTitle() {
        given().contentType(ContentType.JSON).body("{}")
            .when().post("/tasks").then().statusCode(400);
    }

    @Test void testGetById() {
        String id = given().contentType(ContentType.JSON)
            .body("{\"title\":\"Find Me\"}").when().post("/tasks")
            .then().statusCode(201).extract().path("id");
        given().when().get("/tasks/" + id).then().statusCode(200).body("id", equalTo(id));
    }

    @Test void testGetNotFound() {
        given().when().get("/tasks/id-invalido-xyz").then().statusCode(404);
    }

    @Test void testUpdate() {
        String id = given().contentType(ContentType.JSON)
            .body("{\"title\":\"Original\"}").when().post("/tasks")
            .then().statusCode(201).extract().path("id");
        given().contentType(ContentType.JSON)
            .body("{\"title\":\"Updated\",\"completed\":true}")
            .when().put("/tasks/" + id).then().statusCode(200)
            .body("title", equalTo("Updated")).body("completed", equalTo(true));
    }

    @Test void testUpdateNotFound() {
        given().contentType(ContentType.JSON).body("{\"title\":\"X\"}")
            .when().put("/tasks/id-invalido-xyz").then().statusCode(404);
    }

    @Test void testDelete() {
        String id = given().contentType(ContentType.JSON)
            .body("{\"title\":\"Delete Me\"}").when().post("/tasks")
            .then().statusCode(201).extract().path("id");
        given().when().delete("/tasks/" + id).then().statusCode(204);
    }

    @Test void testDeleteNotFound() {
        given().when().delete("/tasks/id-invalido-xyz").then().statusCode(404);
    }

    @Test void testTitleTooLong() {
        given().contentType(ContentType.JSON)
            .body("{\"title\":\"" + "A".repeat(201) + "\"}")
            .when().post("/tasks").then().statusCode(400);
    }

    @Test void testListWithItems() {
        given().contentType(ContentType.JSON).body("{\"title\":\"List Test\"}")
            .when().post("/tasks").then().statusCode(201);
        given().when().get("/tasks").then().statusCode(200).body("size()", greaterThan(0));
    }
}
```

---

## PASSO 5 — Regra de validação contínua (OBRIGATÓRIO)

**Após cada arquivo criado ou modificado**, execute:

```powershell
cd experiments/exp-01-java-vs-kotlin/java-quarkus-gradle-mode-1
.\gradlew.bat compileJava
```

Se compilar com sucesso, rode os testes:

```powershell
.\gradlew.bat test
```

**Nunca avance para o próximo arquivo com build quebrado ou teste falhando.**

---

## PASSO 6 — Validação final antes dos testes E2E

```powershell
cd experiments/exp-01-java-vs-kotlin/java-quarkus-gradle-mode-1
.\gradlew.bat compileJava
```
Esperado: `BUILD SUCCESSFUL`

```powershell
.\gradlew.bat test
```
Esperado: `BUILD SUCCESSFUL`, zero `Failures`, zero `Errors`

```powershell
# Verificar cobertura — o relatório JaCoCo fica em:
# build/reports/jacoco/test/html/index.html
# build/reports/jacoco/test/jacocoTestReport.csv
# Cobertura de linha deve ser >= 80%
```

---

## PASSO 7 — Testes E2E (app deve estar rodando)

### Compilar e subir o app

```powershell
cd experiments/exp-01-java-vs-kotlin/java-quarkus-gradle-mode-1
.\gradlew.bat build -x test
```

Depois suba a aplicação:

```powershell
Start-Process -NoNewWindow -FilePath "java" -ArgumentList "-jar", "build/quarkus-app/quarkus-run.jar"
# Aguardar ~10 segundos até o log mostrar "Listening on: http://0.0.0.0:8080"
Start-Sleep -Seconds 15
```

### Executar os 12 cenários E2E

```powershell
$BASE = "http://localhost:8080"

# E2E-01: Listar tarefas (lista vazia) — esperado: 200
$r01 = curl.exe -s -w "`n%{http_code}" "$BASE/tasks"
Write-Output "E2E-01: $($r01 -split "`n" | Select-Object -Last 1) (esperado: 200)"

# E2E-02: Criar tarefa válida — esperado: 201
$r02 = curl.exe -s -w "`n%{http_code}" -X POST "$BASE/tasks" -H "Content-Type: application/json" -d '{"title":"Test Task","description":"Desc"}'
$body02 = $r02 -split "`n" | Select-Object -First 1
$code02 = $r02 -split "`n" | Select-Object -Last 1
Write-Output "E2E-02: $code02 (esperado: 201)"
$TASK_ID = ($body02 | ConvertFrom-Json).id
Write-Output "Task ID capturado: $TASK_ID"

# E2E-03: Criar sem title — esperado: 400
$r03 = curl.exe -s -w "`n%{http_code}" -X POST "$BASE/tasks" -H "Content-Type: application/json" -d '{}'
Write-Output "E2E-03: $($r03 -split "`n" | Select-Object -Last 1) (esperado: 400)"

# E2E-04: Criar com title vazio — esperado: 400
$r04 = curl.exe -s -w "`n%{http_code}" -X POST "$BASE/tasks" -H "Content-Type: application/json" -d '{"title":""}'
Write-Output "E2E-04: $($r04 -split "`n" | Select-Object -Last 1) (esperado: 400)"

# E2E-05: Listar com itens — esperado: 200
$r05 = curl.exe -s -w "`n%{http_code}" "$BASE/tasks"
Write-Output "E2E-05: $($r05 -split "`n" | Select-Object -Last 1) (esperado: 200)"

# E2E-06: Buscar por ID existente — esperado: 200
$r06 = curl.exe -s -w "`n%{http_code}" "$BASE/tasks/$TASK_ID"
Write-Output "E2E-06: $($r06 -split "`n" | Select-Object -Last 1) (esperado: 200)"

# E2E-07: Buscar por ID inexistente — esperado: 404
$r07 = curl.exe -s -w "`n%{http_code}" "$BASE/tasks/id-invalido-xyz"
Write-Output "E2E-07: $($r07 -split "`n" | Select-Object -Last 1) (esperado: 404)"

# E2E-08: Atualizar tarefa válida — esperado: 200
$r08 = curl.exe -s -w "`n%{http_code}" -X PUT "$BASE/tasks/$TASK_ID" -H "Content-Type: application/json" -d '{"title":"Updated","completed":true}'
Write-Output "E2E-08: $($r08 -split "`n" | Select-Object -Last 1) (esperado: 200)"

# E2E-09: Atualizar ID inexistente — esperado: 404
$r09 = curl.exe -s -w "`n%{http_code}" -X PUT "$BASE/tasks/id-invalido-xyz" -H "Content-Type: application/json" -d '{"title":"X"}'
Write-Output "E2E-09: $($r09 -split "`n" | Select-Object -Last 1) (esperado: 404)"

# E2E-10: Deletar tarefa existente — esperado: 204
$r10 = curl.exe -s -w "`n%{http_code}" -X DELETE "$BASE/tasks/$TASK_ID"
Write-Output "E2E-10: $($r10 -split "`n" | Select-Object -Last 1) (esperado: 204)"

# E2E-11: Deletar ID inexistente — esperado: 404
$r11 = curl.exe -s -w "`n%{http_code}" -X DELETE "$BASE/tasks/id-invalido-xyz"
Write-Output "E2E-11: $($r11 -split "`n" | Select-Object -Last 1) (esperado: 404)"

# E2E-12: Confirmar que tarefa deletada não existe — esperado: 404
$r12 = curl.exe -s -w "`n%{http_code}" "$BASE/tasks/$TASK_ID"
Write-Output "E2E-12: $($r12 -split "`n" | Select-Object -Last 1) (esperado: 404)"
```

### Encerrar o app

```powershell
Stop-Process -Name "java" -Force -ErrorAction SilentlyContinue
```

---

## PASSO 8 — Snapshot pós-sessão e coleta de métricas

Volte para a raiz do benchmark e execute (substituindo `<SESSION-ID>` pelo valor do Passo 1):

```powershell
cd C:\Users\grios\OneDrive\Desktop\benchmark
python tools/snapshot.py --post --language java-quarkus-gradle --session-id <SESSION-ID>
python tools/collector.py --session-id <SESSION-ID> --language java-quarkus-gradle
```

Confirme que `tools/reports/java-quarkus-gradle_*.json` foi criado.

---

## PASSO 9 — Coletar métricas de cobertura e LOC

```powershell
# Relatório JaCoCo Gradle:
# build/reports/jacoco/test/html/index.html
# build/reports/jacoco/test/jacocoTestReport.csv

# Contar LOC
cd C:\Users\grios\OneDrive\Desktop\benchmark
cloc experiments/exp-01-java-vs-kotlin/java-quarkus-gradle-mode-1/src/main/java --json | ConvertFrom-Json | Select-Object -ExpandProperty Java
cloc experiments/exp-01-java-vs-kotlin/java-quarkus-gradle-mode-1/src/test/java --json | ConvertFrom-Json | Select-Object -ExpandProperty Java
```

---

## PASSO 10 — Atualizar JSON com dados manuais

Abra o arquivo `tools/reports/java-quarkus-gradle_<timestamp>.json` e adicione/atualize:

```json
{
  "code_quality": {
    "lines_of_code": <LOC_PRODUCAO>,
    "test_lines_of_code": <LOC_TESTES>,
    "test_coverage_line_pct": <COBERTURA_LINHA_%>,
    "test_coverage_branch_pct": <COBERTURA_BRANCH_%>,
    "test_ratio_pct": <TEST_LOC / (PROD_LOC + TEST_LOC) * 100>
  },
  "e2e": {
    "total_scenarios": 12,
    "passed": <QUANTIDADE_PASSOU>,
    "failed": <QUANTIDADE_FALHOU>,
    "failure_details": []
  }
}
```

---

## PASSO 11 — Gerar relatório HTML interativo

```powershell
cd C:\Users\grios\OneDrive\Desktop\benchmark
python tools/report.py
```

---

## PASSO 12 — Relatório de conclusão

```
✅ BENCHMARK JAVA QUARKUS GRADLE MODO 1 — CONCLUÍDO

Session ID: <UUID>
Arquivo de métricas: tools/reports/java-quarkus-gradle_<timestamp>.json

Critérios de entrega:
[ ] .\gradlew.bat compileJava  — BUILD SUCCESSFUL
[ ] .\gradlew.bat test         — 0 failures, 0 errors
[ ] Cobertura                  — ≥ 80%
[ ] App rodou                  — porta 8080 ok
[ ] E2E                        — X/12 passaram

Tokens totais:    (ver JSON)
Custo USD:        (ver JSON)
Duração sessão:   (ver JSON)
```

---

## ⚠️ CRITÉRIO DE ACEITE

A sessão só está concluída quando:

- `.\gradlew.bat compileJava` → BUILD SUCCESSFUL
- `.\gradlew.bat test` → 0 failures, 0 errors, cobertura ≥ 80%
- 12/12 cenários E2E passando
- `tools/reports/java-quarkus-gradle_*.json` gerado e preenchido

---

## ⚠️ ERROS COMUNS COM QUARKUS + GRADLE

| Sintoma | Causa | Solução |
|---------|-------|---------|
| `@PathVariable` não resolve | Anotação Spring, não JAX-RS | Use `@PathParam("id") String id` |
| `@GetMapping` não resolve | Anotação Spring MVC | Use `@GET` + `@Path("/tasks")` |
| `@Service` não resolve | Anotação Spring | Use `@ApplicationScoped` |
| `@Autowired` não resolve | Anotação Spring | Use `@Inject` |
| `@RestControllerAdvice` não resolve | Anotação Spring | Use `@Provider` + `ExceptionMapper<T>` |
| 404 em todos os endpoints | `@Path` ausente na classe | Adicione `@Path("/tasks")` na classe Resource |
| 415 Unsupported Media Type | `@Consumes` ausente | Adicione `@Consumes(MediaType.APPLICATION_JSON)` |
| Validação não retorna 400 | `@Valid` ausente | Adicione `@Valid` antes do parâmetro no POST |
| Cobertura não gerada | `quarkus-jacoco` ausente | Já incluído no `build.gradle` |
| `build/quarkus-app/` não existe | Build não rodou | Execute `.\gradlew.bat build -x test` antes |
