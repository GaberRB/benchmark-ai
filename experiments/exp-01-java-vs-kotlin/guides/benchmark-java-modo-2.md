# BENCHMARK JAVA — MODO 2 (Orquestrador + Subagentes Paralelos)

> Você é o ORQUESTRADOR deste benchmark. Sua missão é decompor o trabalho em tasks
> independentes e disparar subagentes em paralelo para executá-las.
> Execute em ordem. Não pule etapas. Capture todos os session IDs.
>
> **MODELO OBRIGATÓRIO:** Esta sessão e todos os subagentes devem rodar com `claude-sonnet-4-6`.
> Ao criar cada subagente, especifique `model: claude-sonnet-4-6` no prompt.

---

## PASSO 1 — Capturar Session ID do Orquestrador

```powershell
Get-Content (Get-ChildItem "$env:USERPROFILE\.claude\sessions\" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName | ConvertFrom-Json | Select-Object sessionId, cwd, startedAt
```

**Guarde este sessionId — é o session ID do orquestrador (você).**

Anote também o timestamp de início:

```powershell
Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
```

---

## PASSO 2 — Snapshot pré-sessão

```powershell
cd C:\Users\grios\OneDrive\Desktop\benchmark
python tools/snapshot.py --pre --language java-mode2
```

---

## PASSO 3 — Ler contratos antes de decompor

Leia os arquivos abaixo **antes** de disparar qualquer subagente:

1. `.claude/spec/prd-java-task-manager-api.md`
2. `spec/task-definition.md`

---

## PASSO 4 — FASE 0: Setup e Contratos (Paralelo entre si)

Dispare os dois subagentes abaixo **em paralelo** (numa única chamada de ferramentas).
Aguarde ambos concluírem antes de avançar para a Fase 1.

### Subagente T0 — pom.xml

```
Prompt para T0:
"Você está executando a task T0 do benchmark Java Modo 2.
Crie o arquivo pom.xml em java-implementation-mode2/ para um projeto Spring Boot 3.x com:
- Java 21
- spring-boot-starter-web
- spring-boot-starter-test (JUnit 5)
- Plugin JaCoCo com mínimo 80% de cobertura de linhas
- Plugin spring-boot-maven-plugin
Group: com.benchmark | Artifact: taskmanager | Package: com.benchmark.taskmanager
Crie também TaskManagerApplication.java com @SpringBootApplication.
Ao terminar, execute: cd java-implementation-mode2 && .\mvnw.cmd compile
Reporte: SUCCESS ou FAILURE + erros encontrados."
```

### Subagente T1 — Modelo e DTOs

```
Prompt para T1:
"Você está executando a task T1 do benchmark Java Modo 2.
Crie os seguintes arquivos em java-implementation-mode2/src/main/java/com/benchmark/taskmanager/:

1. model/Task.java — campos: id (String/UUID), title (String), description (String),
   completed (boolean, default false), createdAt (String ISO8601), updatedAt (String ISO8601).
   Gere getters, setters e construtores completos.

2. dto/CreateTaskRequest.java — campos: title (String), description (String)
3. dto/UpdateTaskRequest.java — campos: title (String), description (String), completed (Boolean)

Ao terminar, execute: cd java-implementation-mode2 && .\mvnw.cmd compile
Reporte: SUCCESS ou FAILURE + erros encontrados."
```

**Após T0 e T1 concluírem com SUCCESS**, capture os session IDs:

```powershell
Get-ChildItem "$env:USERPROFILE\.claude\sessions\" |
  Sort-Object LastWriteTime -Descending | Select-Object -First 5 |
  ForEach-Object { Get-Content $_.FullName | ConvertFrom-Json | Select-Object sessionId, cwd, startedAt }
```

Anote: `SESSION_T0 = <UUID>` e `SESSION_T1 = <UUID>`

---

## PASSO 5 — FASE 1: Implementação (3 subagentes em paralelo)

Dispare os três subagentes abaixo **em paralelo**. Aguarde todos concluírem.

### Subagente T2 — TaskService

```
Prompt para T2:
"Você está executando a task T2 do benchmark Java Modo 2.
Os arquivos model/Task.java e dto/*.java já existem em java-implementation-mode2/.
Implemente java-implementation-mode2/src/main/java/com/benchmark/taskmanager/service/TaskService.java:
- Storage in-memory com ConcurrentHashMap<String, Task>
- Métodos: findAll(), findById(String id), create(CreateTaskRequest), update(String id, UpdateTaskRequest), delete(String id)
- findById e delete lançam TaskNotFoundException se não encontrar
- create: valida title obrigatório (não vazio, max 200), description (max 1000 se presente); gera UUID e timestamps ISO8601
- update: valida campos se presentes; atualiza updatedAt
Crie também exception/TaskNotFoundException.java (extends RuntimeException).
Ao terminar: cd java-implementation-mode2 && .\mvnw.cmd compile
Reporte: SUCCESS ou FAILURE + erros."
```

### Subagente T3 — TaskController

```
Prompt para T3:
"Você está executando a task T3 do benchmark Java Modo 2.
Os arquivos model/Task.java, dto/*.java já existem em java-implementation-mode2/.
O TaskService.java com os métodos findAll(), findById(), create(), update(), delete() existe ou existirá.
Implemente java-implementation-mode2/src/main/java/com/benchmark/taskmanager/controller/TaskController.java:
- @RestController @RequestMapping('/tasks')
- GET /tasks → 200, lista de Task
- POST /tasks → 201, Task criada (usa CreateTaskRequest)
- GET /tasks/{id} → 200 ou 404
- PUT /tasks/{id} → 200 ou 404 (usa UpdateTaskRequest)
- DELETE /tasks/{id} → 204 ou 404
Ao terminar: cd java-implementation-mode2 && .\mvnw.cmd compile
Reporte: SUCCESS ou FAILURE + erros."
```

### Subagente T4 — GlobalExceptionHandler

```
Prompt para T4:
"Você está executando a task T4 do benchmark Java Modo 2.
Implemente em java-implementation-mode2/src/main/java/com/benchmark/taskmanager/exception/:
1. TaskNotFoundException.java — extends RuntimeException, construtor com String message
2. GlobalExceptionHandler.java — @RestControllerAdvice
   - Trata TaskNotFoundException → ResponseEntity com status 404 e body {"error": message}
   - Trata MethodArgumentNotValidException (validação) → 400 com body {"error": message}
   - Trata genérico Exception → 400 com body {"error": message}
Ao terminar: cd java-implementation-mode2 && .\mvnw.cmd compile
Reporte: SUCCESS ou FAILURE + erros."
```

**Após T2, T3 e T4 concluírem**, capture os session IDs dos 3:

```powershell
Get-ChildItem "$env:USERPROFILE\.claude\sessions\" |
  Sort-Object LastWriteTime -Descending | Select-Object -First 8 |
  ForEach-Object { Get-Content $_.FullName | ConvertFrom-Json | Select-Object sessionId, cwd, startedAt }
```

Anote: `SESSION_T2`, `SESSION_T3`, `SESSION_T4`

Se algum subagente reportou FAILURE, corrija o problema antes de avançar.

---

## PASSO 6 — Verificação de integração (você, orquestrador)

Execute um build completo para garantir que o código dos subagentes integra corretamente:

```powershell
cd java-implementation-mode2
.\mvnw.cmd compile
```

Se houver erros de compilação (imports faltando, interfaces divergentes, etc.):
1. Identifique o conflito
2. Corrija diretamente (você é o orquestrador)
3. Reexecute `.\mvnw.cmd compile` até passar
4. Registre cada conflito como `integration_conflicts` no JSON final

---

## PASSO 7 — FASE 2: Testes Unitários (2 subagentes em paralelo)

Dispare os dois subagentes abaixo **em paralelo**. Aguarde ambos concluírem.

### Subagente T5 — Testes do TaskService

```
Prompt para T5:
"Você está executando a task T5 do benchmark Java Modo 2.
Escreva testes unitários em java-implementation-mode2/src/test/java/com/benchmark/taskmanager/service/TaskServiceTest.java
cobrindo:
- findAll() com lista vazia e com itens
- create() com dados válidos → retorna Task com ID e timestamps
- create() com title null → lança exceção
- create() com title vazio → lança exceção
- create() com title > 200 chars → lança exceção
- findById() com ID existente → retorna Task
- findById() com ID inexistente → lança TaskNotFoundException
- update() com dados válidos → atualiza campos e updatedAt
- update() com ID inexistente → lança TaskNotFoundException
- delete() com ID existente → remove
- delete() com ID inexistente → lança TaskNotFoundException
Ao terminar: cd java-implementation-mode2 && .\mvnw.cmd test
Reporte: resultado completo do .\mvnw.cmd test (quantos passaram, falharam, erros)."
```

### Subagente T6 — Testes do TaskController

```
Prompt para T6:
"Você está executando a task T6 do benchmark Java Modo 2.
Escreva testes de integração em java-implementation-mode2/src/test/java/com/benchmark/taskmanager/controller/TaskControllerTest.java
usando @SpringBootTest e MockMvc ou @WebMvcTest cobrindo:
- GET /tasks → 200, body []
- POST /tasks body válido → 201, body com id
- POST /tasks sem title → 400, body com error
- POST /tasks title vazio → 400
- GET /tasks/{id} existente → 200
- GET /tasks/{id} inexistente → 404, body com error
- PUT /tasks/{id} válido → 200, updatedAt alterado
- PUT /tasks/{id} inexistente → 404
- DELETE /tasks/{id} existente → 204
- DELETE /tasks/{id} inexistente → 404
Ao terminar: cd java-implementation-mode2 && .\mvnw.cmd test
Reporte: resultado completo do .\mvnw.cmd test."
```

**Após T5 e T6 concluírem**, capture os session IDs:

```powershell
Get-ChildItem "$env:USERPROFILE\.claude\sessions\" |
  Sort-Object LastWriteTime -Descending | Select-Object -First 10 |
  ForEach-Object { Get-Content $_.FullName | ConvertFrom-Json | Select-Object sessionId, cwd, startedAt }
```

Anote: `SESSION_T5`, `SESSION_T6`

---

## PASSO 8 — FASE 3: Integração final e E2E (você, orquestrador)

### Build e testes completos

```powershell
cd java-implementation-mode2
.\mvnw.cmd test
```

Esperado: `BUILD SUCCESS`, zero failures, cobertura ≥ 80%.
Se falhar, corrija e reexecute. Registre cada correção como `integration_fix_turns`.

### Subir o app

```powershell
Start-Process -NoNewWindow -FilePath ".\mvnw.cmd" -ArgumentList "spring-boot:run" -WorkingDirectory "java-implementation-mode2"
Start-Sleep -Seconds 20
```

### Executar os 12 cenários E2E

```powershell
$BASE = "http://localhost:8080"

$r01 = curl.exe -s -w "`n%{http_code}" "$BASE/tasks"
Write-Output "E2E-01: $($r01 -split "`n" | Select-Object -Last 1) (esperado: 200)"

$r02 = curl.exe -s -w "`n%{http_code}" -X POST "$BASE/tasks" -H "Content-Type: application/json" -d '{"title":"Test Task","description":"Desc"}'
$body02 = $r02 -split "`n" | Select-Object -First 1
$code02 = $r02 -split "`n" | Select-Object -Last 1
Write-Output "E2E-02: $code02 (esperado: 201)"
$TASK_ID = ($body02 | ConvertFrom-Json).id

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

## PASSO 9 — Anotar timestamp de fim

```powershell
Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
```

Calcule: `wall_clock_time_min = (timestamp_fim - timestamp_inicio_passo1) em minutos`

---

## PASSO 10 — Snapshot pós e coleta de métricas de todos os agentes

```powershell
cd C:\Users\grios\OneDrive\Desktop\benchmark

# Snapshot pós do orquestrador
python tools/snapshot.py --post --language java-mode2 --session-id <SESSION-ORQUESTRADOR>

# Coletar métricas de cada agente
python tools/collector.py --session-id <SESSION-ORQUESTRADOR> --language java-mode2-orchestrator
python tools/collector.py --session-id <SESSION_T0> --language java-mode2-task-T0
python tools/collector.py --session-id <SESSION_T1> --language java-mode2-task-T1
python tools/collector.py --session-id <SESSION_T2> --language java-mode2-task-T2
python tools/collector.py --session-id <SESSION_T3> --language java-mode2-task-T3
python tools/collector.py --session-id <SESSION_T4> --language java-mode2-task-T4
python tools/collector.py --session-id <SESSION_T5> --language java-mode2-task-T5
python tools/collector.py --session-id <SESSION_T6> --language java-mode2-task-T6
```

---

## PASSO 11 — Coletar LOC

```powershell
cloc java-implementation-mode2/src/main/java --json | ConvertFrom-Json | Select-Object -ExpandProperty Java
cloc java-implementation-mode2/src/test/java --json | ConvertFrom-Json | Select-Object -ExpandProperty Java
```

---

## PASSO 12 — Atualizar JSON do orquestrador com dados manuais

Abra `tools/reports/java-mode2-orchestrator_*.json` e adicione:

```json
{
  "code_quality": {
    "lines_of_code": <LOC_PRODUCAO>,
    "test_lines_of_code": <LOC_TESTES>,
    "test_coverage_line_pct": <COBERTURA_%>,
    "test_coverage_branch_pct": <COBERTURA_BRANCH_%>
  },
  "e2e": {
    "total_scenarios": 12,
    "passed": <QUANTIDADE>,
    "failed": <QUANTIDADE>,
    "failure_details": []
  },
  "mode2": {
    "wall_clock_time_min": <TEMPO_REAL>,
    "cpu_equivalent_time_min": <SOMA_TEMPOS_INDIVIDUAIS>,
    "speedup_ratio": <cpu_equivalent / wall_clock>,
    "task_count": 7,
    "tasks_parallel": 5,
    "tasks_sequential": 2,
    "task_failure_count": <TASKS_QUE_FALHARAM_1a_TENTATIVA>,
    "integration_conflicts": <CONFLITOS_ENCONTRADOS>,
    "integration_fix_turns": <TURNS_PARA_CORRIGIR>
  }
}
```

---

## PASSO 13 — Relatório de conclusão

```
✅ BENCHMARK JAVA MODO 2 — CONCLUÍDO

Session Orquestrador: <UUID>
Sessions Subagentes: T0=<UUID> T1=<UUID> T2=<UUID> T3=<UUID> T4=<UUID> T5=<UUID> T6=<UUID>

Critérios de entrega:
[ ] .\mvnw.cmd compile — BUILD SUCCESS
[ ] .\mvnw.cmd test    — 0 failures, 0 errors
[ ] Cobertura   — ≥ 80%
[ ] App rodou   — porta 8080 ok
[ ] E2E         — X/12 passaram

Wall clock time: X min | CPU equivalent: Y min | Speedup: Z x
Integration conflicts: N
Arquivos gerados: tools/reports/java-mode2-*.json (8 arquivos)
```

---

## ⚠️ CRITÉRIO DE ACEITE

- `.\mvnw.cmd compile` → BUILD SUCCESS
- `.\mvnw.cmd test` → 0 failures, 0 errors, cobertura ≥ 80%
- 12/12 cenários E2E passando
- 8 arquivos JSON de métricas gerados (orquestrador + T0 a T6)
