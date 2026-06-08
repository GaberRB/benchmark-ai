# BENCHMARK KOTLIN QUARKUS — MAVEN MODO 1 (Agente Sequencial)

> Você é o agente responsável por executar este benchmark completo.
> Leia todos os passos antes de iniciar. Execute em ordem. Não pule etapas.
> Este arquivo conduz você do início à coleta final de métricas.
>
> **MODELO OBRIGATÓRIO:** Esta sessão deve rodar com `claude-sonnet-4-6`.
> Confirme executando: `claude --version` e verificando o modelo ativo nas configurações.
>
> **LINGUAGEM:** Kotlin · **FRAMEWORK:** Quarkus 3.8.3 · **BUILD:** Maven
> Use JAX-RS (`jakarta.ws.rs.*`) para REST e CDI (`@ApplicationScoped`, `@Inject`) para injeção.

> ⛔ **ESCOPO RESTRITO — LEIA ANTES DE QUALQUER AÇÃO**
> - Você deve trabalhar **EXCLUSIVAMENTE** no diretório `kotlin-quarkus-maven-mode-1/`
> - **NÃO leia, NÃO explore e NÃO referencie** nenhum outro diretório de implementação
> - **NÃO crie** guias, arquivos de configuração ou diretórios fora de `kotlin-quarkus-maven-mode-1/src/`
> - Se você encontrar outros experimentos no filesystem, **ignore-os completamente**
> - Escreva **apenas arquivos `.kt`** — não crie arquivos `.java`

---

## PASSO 1 — Capturar Session ID atual

```powershell
Get-Content (Get-ChildItem "$env:USERPROFILE\.claude\sessions\" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName | ConvertFrom-Json | Select-Object sessionId, cwd, startedAt
```

**Guarde o `sessionId` retornado — você vai precisar dele no Passo 7.**

---

## PASSO 2 — Snapshot pré-sessão

```powershell
python tools/snapshot.py --pre --language kotlin-quarkus-maven
```

---

## PASSO 3 — Ler a especificação

`shared/task-definition.md` — especificação dos 5 endpoints CRUD, modelo Task, validações.

---

## PASSO 4 — Implementar a Task Manager API em Kotlin + Quarkus

Trabalhe dentro de `experiments/exp-01-java-vs-kotlin/kotlin-quarkus-maven-mode-1/`.

O `pom.xml` e `application.properties` já estão configurados — **não modifique**.

### Stack obrigatória

- Kotlin 1.9.22, **Quarkus 3.8.3**, Maven
- REST via **JAX-RS** (`jakarta.ws.rs.*`) — NÃO Spring MVC
- DI via **CDI** (`@ApplicationScoped`, `@Inject`) — NÃO Spring
- Storage in-memory (`ConcurrentHashMap`)
- `@QuarkusTest` + RestAssured para testes
- `quarkus-jacoco` para cobertura (mínimo 80%)

### Estrutura de arquivos a criar

```
kotlin-quarkus-maven-mode-1/
├── pom.xml                          ← JÁ EXISTE — não modifique
└── src/
    ├── main/
    │   ├── kotlin/com/benchmark/taskmanager/
    │   │   ├── model/Task.kt
    │   │   ├── dto/CreateTaskRequest.kt
    │   │   ├── dto/UpdateTaskRequest.kt
    │   │   ├── repository/TaskRepository.kt
    │   │   ├── repository/impl/InMemoryTaskRepository.kt
    │   │   ├── service/TaskService.kt
    │   │   ├── service/impl/TaskServiceImpl.kt
    │   │   ├── resource/TaskResource.kt
    │   │   └── exception/
    │   │       ├── TaskNotFoundException.kt
    │   │       ├── TaskNotFoundExceptionMapper.kt
    │   │       └── ValidationExceptionMapper.kt
    │   └── resources/
    │       └── application.properties  ← JÁ EXISTE — não modifique
    └── test/kotlin/com/benchmark/taskmanager/
        └── TaskResourceTest.kt
```

### Endpoints a implementar

| Método | Rota        | Sucesso | Erro    |
|--------|-------------|---------|---------|
| GET    | /tasks      | 200     | —       |
| POST   | /tasks      | 201     | 400     |
| GET    | /tasks/{id} | 200     | 404     |
| PUT    | /tasks/{id} | 200     | 400/404 |
| DELETE | /tasks/{id} | 204     | 404     |

### Validações

- `title` ausente ou vazio → 400 `{"error":"title is required"}`
- `title` > 200 chars → 400 `{"error":"title must not exceed 200 characters"}`
- `description` > 1000 chars → 400 `{"error":"description must not exceed 1000 characters"}`
- ID não encontrado → 404 `{"error":"Task not found"}`

---

## REFERÊNCIA DE IMPLEMENTAÇÃO KOTLIN + QUARKUS

### model/Task.kt

```kotlin
package com.benchmark.taskmanager.model

import java.time.Instant
import java.util.UUID

data class Task(
    val id: String = UUID.randomUUID().toString(),
    var title: String,
    var description: String? = null,
    var completed: Boolean = false,
    val createdAt: String = Instant.now().toString(),
    var updatedAt: String = Instant.now().toString()
)
```

### dto/CreateTaskRequest.kt

```kotlin
package com.benchmark.taskmanager.dto

import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.Size

data class CreateTaskRequest(
    @field:NotBlank(message = "title is required")
    @field:Size(max = 200, message = "title must not exceed 200 characters")
    val title: String? = null,

    @field:Size(max = 1000, message = "description must not exceed 1000 characters")
    val description: String? = null
)
```

### dto/UpdateTaskRequest.kt

```kotlin
package com.benchmark.taskmanager.dto

import jakarta.validation.constraints.Size

data class UpdateTaskRequest(
    @field:Size(max = 200, message = "title must not exceed 200 characters")
    val title: String? = null,

    @field:Size(max = 1000, message = "description must not exceed 1000 characters")
    val description: String? = null,

    val completed: Boolean? = null
)
```

### repository/TaskRepository.kt

```kotlin
package com.benchmark.taskmanager.repository

import com.benchmark.taskmanager.model.Task

interface TaskRepository {
    fun findAll(): List<Task>
    fun findById(id: String): Task?
    fun save(task: Task): Task
    fun deleteById(id: String)
    fun existsById(id: String): Boolean
}
```

### repository/impl/InMemoryTaskRepository.kt

```kotlin
package com.benchmark.taskmanager.repository.impl

import com.benchmark.taskmanager.model.Task
import com.benchmark.taskmanager.repository.TaskRepository
import jakarta.enterprise.context.ApplicationScoped
import java.util.concurrent.ConcurrentHashMap

@ApplicationScoped
class InMemoryTaskRepository : TaskRepository {
    private val store = ConcurrentHashMap<String, Task>()

    override fun findAll(): List<Task> = store.values.toList()
    override fun findById(id: String): Task? = store[id]
    override fun save(task: Task): Task { store[task.id] = task; return task }
    override fun deleteById(id: String) { store.remove(id) }
    override fun existsById(id: String): Boolean = store.containsKey(id)
}
```

### service/TaskService.kt

```kotlin
package com.benchmark.taskmanager.service

import com.benchmark.taskmanager.dto.CreateTaskRequest
import com.benchmark.taskmanager.dto.UpdateTaskRequest
import com.benchmark.taskmanager.model.Task

interface TaskService {
    fun findAll(): List<Task>
    fun findById(id: String): Task
    fun create(request: CreateTaskRequest): Task
    fun update(id: String, request: UpdateTaskRequest): Task
    fun delete(id: String)
}
```

### service/impl/TaskServiceImpl.kt

```kotlin
package com.benchmark.taskmanager.service.impl

import com.benchmark.taskmanager.dto.CreateTaskRequest
import com.benchmark.taskmanager.dto.UpdateTaskRequest
import com.benchmark.taskmanager.exception.TaskNotFoundException
import com.benchmark.taskmanager.model.Task
import com.benchmark.taskmanager.repository.TaskRepository
import com.benchmark.taskmanager.service.TaskService
import jakarta.enterprise.context.ApplicationScoped
import jakarta.inject.Inject
import java.time.Instant

@ApplicationScoped
class TaskServiceImpl : TaskService {

    @Inject
    lateinit var taskRepository: TaskRepository

    override fun findAll(): List<Task> = taskRepository.findAll()

    override fun findById(id: String): Task =
        taskRepository.findById(id) ?: throw TaskNotFoundException("Task not found")

    override fun create(request: CreateTaskRequest): Task =
        taskRepository.save(Task(title = request.title!!, description = request.description))

    override fun update(id: String, request: UpdateTaskRequest): Task {
        val task = findById(id)
        request.title?.let {
            if (it.isBlank()) throw IllegalArgumentException("title is required")
            task.title = it
        }
        request.description?.let { task.description = it }
        request.completed?.let { task.completed = it }
        task.updatedAt = Instant.now().toString()
        return taskRepository.save(task)
    }

    override fun delete(id: String) {
        if (!taskRepository.existsById(id)) throw TaskNotFoundException("Task not found")
        taskRepository.deleteById(id)
    }
}
```

### resource/TaskResource.kt

```kotlin
package com.benchmark.taskmanager.resource

import com.benchmark.taskmanager.dto.CreateTaskRequest
import com.benchmark.taskmanager.dto.UpdateTaskRequest
import com.benchmark.taskmanager.service.TaskService
import jakarta.enterprise.context.ApplicationScoped
import jakarta.inject.Inject
import jakarta.validation.Valid
import jakarta.ws.rs.*
import jakarta.ws.rs.core.MediaType
import jakarta.ws.rs.core.Response

@Path("/tasks")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@ApplicationScoped
class TaskResource {

    @Inject
    lateinit var taskService: TaskService

    @GET
    fun listAll() = taskService.findAll()

    @POST
    fun create(@Valid request: CreateTaskRequest): Response =
        Response.status(201).entity(taskService.create(request)).build()

    @GET
    @Path("/{id}")
    fun findById(@PathParam("id") id: String) = taskService.findById(id)

    @PUT
    @Path("/{id}")
    fun update(@PathParam("id") id: String, request: UpdateTaskRequest) =
        taskService.update(id, request)

    @DELETE
    @Path("/{id}")
    fun delete(@PathParam("id") id: String): Response {
        taskService.delete(id)
        return Response.noContent().build()
    }
}
```

### exception/TaskNotFoundException.kt

```kotlin
package com.benchmark.taskmanager.exception

class TaskNotFoundException(message: String) : RuntimeException(message)
```

### exception/TaskNotFoundExceptionMapper.kt

```kotlin
package com.benchmark.taskmanager.exception

import jakarta.ws.rs.core.Response
import jakarta.ws.rs.ext.ExceptionMapper
import jakarta.ws.rs.ext.Provider

@Provider
class TaskNotFoundExceptionMapper : ExceptionMapper<TaskNotFoundException> {
    override fun toResponse(e: TaskNotFoundException): Response =
        Response.status(404).entity(mapOf("error" to e.message)).build()
}
```

### exception/ValidationExceptionMapper.kt

```kotlin
package com.benchmark.taskmanager.exception

import jakarta.validation.ConstraintViolationException
import jakarta.ws.rs.core.Response
import jakarta.ws.rs.ext.ExceptionMapper
import jakarta.ws.rs.ext.Provider

@Provider
class ValidationExceptionMapper : ExceptionMapper<ConstraintViolationException> {
    override fun toResponse(e: ConstraintViolationException): Response {
        val message = e.constraintViolations.firstOrNull()?.message ?: "Validation error"
        return Response.status(400).entity(mapOf("error" to message)).build()
    }
}
```

### test/TaskResourceTest.kt

```kotlin
package com.benchmark.taskmanager

import io.quarkus.test.junit.QuarkusTest
import io.restassured.RestAssured.given
import io.restassured.http.ContentType
import org.hamcrest.Matchers.*
import org.junit.jupiter.api.Test

@QuarkusTest
class TaskResourceTest {

    @Test fun `GET tasks returns 200`() {
        given().`when`().get("/tasks").then().statusCode(200)
    }

    @Test fun `POST task returns 201 with id`() {
        given().contentType(ContentType.JSON)
            .body("""{"title":"Test Task","description":"Desc"}""")
            .`when`().post("/tasks").then().statusCode(201)
            .body("id", notNullValue()).body("title", equalTo("Test Task"))
    }

    @Test fun `POST without title returns 400`() {
        given().contentType(ContentType.JSON).body("{}")
            .`when`().post("/tasks").then().statusCode(400)
    }

    @Test fun `POST with empty title returns 400`() {
        given().contentType(ContentType.JSON).body("""{"title":""}""")
            .`when`().post("/tasks").then().statusCode(400)
    }

    @Test fun `GET tasks list has items after create`() {
        given().contentType(ContentType.JSON).body("""{"title":"List Test"}""")
            .`when`().post("/tasks").then().statusCode(201)
        given().`when`().get("/tasks").then().statusCode(200).body("size()", greaterThan(0))
    }

    @Test fun `GET task by id returns 200`() {
        val id = given().contentType(ContentType.JSON).body("""{"title":"Find Me"}""")
            .`when`().post("/tasks").then().statusCode(201).extract().path<String>("id")
        given().`when`().get("/tasks/$id").then().statusCode(200).body("id", equalTo(id))
    }

    @Test fun `GET non-existent task returns 404`() {
        given().`when`().get("/tasks/id-invalido-xyz").then().statusCode(404)
    }

    @Test fun `PUT task returns 200 updated`() {
        val id = given().contentType(ContentType.JSON).body("""{"title":"Original"}""")
            .`when`().post("/tasks").then().statusCode(201).extract().path<String>("id")
        given().contentType(ContentType.JSON)
            .body("""{"title":"Updated","completed":true}""")
            .`when`().put("/tasks/$id").then().statusCode(200)
            .body("title", equalTo("Updated")).body("completed", equalTo(true))
    }

    @Test fun `PUT non-existent task returns 404`() {
        given().contentType(ContentType.JSON).body("""{"title":"X"}""")
            .`when`().put("/tasks/id-invalido-xyz").then().statusCode(404)
    }

    @Test fun `DELETE task returns 204`() {
        val id = given().contentType(ContentType.JSON).body("""{"title":"Delete Me"}""")
            .`when`().post("/tasks").then().statusCode(201).extract().path<String>("id")
        given().`when`().delete("/tasks/$id").then().statusCode(204)
    }

    @Test fun `DELETE non-existent task returns 404`() {
        given().`when`().delete("/tasks/id-invalido-xyz").then().statusCode(404)
    }

    @Test fun `POST with title too long returns 400`() {
        given().contentType(ContentType.JSON)
            .body("""{"title":"${"A".repeat(201)}"}""")
            .`when`().post("/tasks").then().statusCode(400)
    }
}
```

---

## PASSO 5 — Regra de validação contínua (OBRIGATÓRIO)

**Após cada arquivo criado ou modificado**, execute:

```powershell
cd experiments/exp-01-java-vs-kotlin/kotlin-quarkus-maven-mode-1
.\mvnw.cmd compile
```

Se compilar com sucesso:

```powershell
.\mvnw.cmd test
```

**Nunca avance com build ou teste falhando.**

---

## PASSO 6 — Validação final

```powershell
cd experiments/exp-01-java-vs-kotlin/kotlin-quarkus-maven-mode-1
.\mvnw.cmd compile
```
Esperado: `BUILD SUCCESS`

```powershell
.\mvnw.cmd test
```
Esperado: `BUILD SUCCESS`, zero `Failures`, zero `Errors`, cobertura ≥ 80%

---

## PASSO 7 — Testes E2E

### Subir o app

```powershell
cd experiments/exp-01-java-vs-kotlin/kotlin-quarkus-maven-mode-1
.\mvnw.cmd package -DskipTests
Start-Process -NoNewWindow -FilePath "java" -ArgumentList "-jar", "target/quarkus-app/quarkus-run.jar"
Start-Sleep -Seconds 15
```

### 12 cenários E2E

```powershell
$BASE = "http://localhost:8080"

$r01 = curl.exe -s -w "`n%{http_code}" "$BASE/tasks"
Write-Output "E2E-01: $($r01 -split "`n" | Select-Object -Last 1) (esperado: 200)"

$r02 = curl.exe -s -w "`n%{http_code}" -X POST "$BASE/tasks" -H "Content-Type: application/json" -d '{"title":"Test Task","description":"Desc"}'
$body02 = $r02 -split "`n" | Select-Object -First 1
$code02 = $r02 -split "`n" | Select-Object -Last 1
Write-Output "E2E-02: $code02 (esperado: 201)"
$TASK_ID = ($body02 | ConvertFrom-Json).id
Write-Output "Task ID capturado: $TASK_ID"

$r03 = curl.exe -s -w "`n%{http_code}" -X POST "$BASE/tasks" -H "Content-Type: application/json" -d '{}'
Write-Output "E2E-03: $($r03 -split "`n" | Select-Object -Last 1) (esperado: 400)"

$r04 = curl.exe -s -w "`n%{http_code}" -X POST "$BASE/tasks" -H "Content-Type: application/json" -d '{"title":""}'
Write-Output "E2E-04: $($r04 -split "`n" | Select-Object -Last 1) (esperado: 400)"

$r05 = curl.exe -s -w "`n%{http_code}" "$BASE/tasks"
Write-Output "E2E-05: $($r05 -split "`n" | Select-Object -Last 1) (esperado: 200)"

$r06 = curl.exe -s -w "`n%{http_code}" "$BASE/tasks/$TASK_ID"
Write-Output "E2E-06: $($r06 -split "`n" | Select-Object -Last 1) (esperado: 200)"

$r07 = curl.exe -s -w "`n%{http_code}" "$BASE/tasks/id-invalido-xyz"
Write-Output "E2E-07: $($r07 -split "`n" | Select-Object -Last 1) (esperado: 404)"

$r08 = curl.exe -s -w "`n%{http_code}" -X PUT "$BASE/tasks/$TASK_ID" -H "Content-Type: application/json" -d '{"title":"Updated","completed":true}'
Write-Output "E2E-08: $($r08 -split "`n" | Select-Object -Last 1) (esperado: 200)"

$r09 = curl.exe -s -w "`n%{http_code}" -X PUT "$BASE/tasks/id-invalido-xyz" -H "Content-Type: application/json" -d '{"title":"X"}'
Write-Output "E2E-09: $($r09 -split "`n" | Select-Object -Last 1) (esperado: 404)"

$r10 = curl.exe -s -w "`n%{http_code}" -X DELETE "$BASE/tasks/$TASK_ID"
Write-Output "E2E-10: $($r10 -split "`n" | Select-Object -Last 1) (esperado: 204)"

$r11 = curl.exe -s -w "`n%{http_code}" -X DELETE "$BASE/tasks/id-invalido-xyz"
Write-Output "E2E-11: $($r11 -split "`n" | Select-Object -Last 1) (esperado: 404)"

$r12 = curl.exe -s -w "`n%{http_code}" "$BASE/tasks/$TASK_ID"
Write-Output "E2E-12: $($r12 -split "`n" | Select-Object -Last 1) (esperado: 404)"
```

### Encerrar o app

```powershell
Stop-Process -Name "java" -Force -ErrorAction SilentlyContinue
```

---

## PASSO 8 — Coleta de métricas

```powershell
cd C:\Users\grios\OneDrive\Desktop\benchmark
python tools/snapshot.py --post --language kotlin-quarkus-maven --session-id <SESSION-ID>
python tools/collector.py --session-id <SESSION-ID> --language kotlin-quarkus-maven
```

---

## PASSO 9 — LOC e cobertura

```powershell
# Relatório JaCoCo: target/site/jacoco/index.html
# CSV: target/site/jacoco/jacoco.csv

cloc experiments/exp-01-java-vs-kotlin/kotlin-quarkus-maven-mode-1/src/main/kotlin --json | ConvertFrom-Json | Select-Object -ExpandProperty Kotlin
cloc experiments/exp-01-java-vs-kotlin/kotlin-quarkus-maven-mode-1/src/test/kotlin --json | ConvertFrom-Json | Select-Object -ExpandProperty Kotlin
```

---

## PASSO 10 — Atualizar JSON com dados manuais

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

## PASSO 11 — Relatório HTML

```powershell
cd C:\Users\grios\OneDrive\Desktop\benchmark
python tools/report.py
```

---

## PASSO 12 — Relatório de conclusão

```
✅ BENCHMARK KOTLIN QUARKUS MAVEN MODO 1 — CONCLUÍDO

Session ID: <UUID>
Arquivo: tools/reports/kotlin-quarkus-maven_<timestamp>.json

[ ] .\mvnw.cmd compile  — BUILD SUCCESS
[ ] .\mvnw.cmd test     — 0 failures, cobertura ≥ 80%
[ ] App rodou           — porta 8080 ok
[ ] E2E                 — X/12 passaram
```

---

## ⚠️ CRITÉRIO DE ACEITE

- `.\mvnw.cmd compile` → BUILD SUCCESS
- `.\mvnw.cmd test` → 0 failures, cobertura ≥ 80%
- 12/12 E2E passando
- JSON gerado e preenchido

---

## ⚠️ ERROS COMUNS KOTLIN + QUARKUS

| Sintoma | Causa | Solução |
|---------|-------|---------|
| `@field:` ausente nas validações | Kotlin redireciona anotações ao campo com `@field:` | Use `@field:NotBlank`, `@field:Size` nos DTOs |
| `lateinit var` em services | Inject em Kotlin requer `lateinit var`, não `val` | Declare `@Inject lateinit var service: TaskService` |
| CDI falha em classe `final` | Kotlin fecha classes por padrão | O `pom.xml` já configura `all-open` — não modifique |
| `@PathVariable` não resolve | Anotação Spring, não JAX-RS | Use `@PathParam("id") id: String` |
| `@GetMapping` não resolve | Anotação Spring MVC | Use `@GET` + `@Path("/tasks")` |
| `@Service` não resolve | Anotação Spring | Use `@ApplicationScoped` |
| `@Autowired` não resolve | Anotação Spring | Use `@Inject` |
| 404 em todos os endpoints | `@Path` ausente na classe | Adicione `@Path("/tasks")` na classe Resource |
| Validação não retorna 400 | `@Valid` ausente no parâmetro | Adicione `@Valid` antes do parâmetro no POST |
