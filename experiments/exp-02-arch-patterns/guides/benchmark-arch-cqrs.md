# BENCHMARK ARQUITETURA — CQRS (Agente Sequencial)

> Você é o agente responsável por executar este benchmark completo.
> Leia todos os passos antes de iniciar. Execute em ordem. Não pule etapas.
>
> **MODELO OBRIGATÓRIO:** Esta sessão deve rodar com `claude-sonnet-4-6`.

---

## PASSO 1 — Capturar Session ID atual

```powershell
Get-Content (Get-ChildItem "$env:USERPROFILE\.claude\sessions\" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName | ConvertFrom-Json | Select-Object sessionId, cwd, startedAt
```

**Guarde o `sessionId` retornado.**

---

## PASSO 2 — Snapshot pré-sessão

```powershell
python metrics/snapshot.py --pre --language arch-cqrs
```

---

## PASSO 3 — Ler a especificação

1. `.claude/spec/prd-arch-cqrs.md` — PRD com separação commands/queries e assinaturas dos handlers
2. `spec/task-definition.md` — Especificação funcional dos endpoints

---

## PASSO 4 — Implementar a Task Manager API (CQRS)

Trabalhe dentro do diretório `arch-benchmark/cqrs/`.

### Conceito fundamental — CQRS

Separar **comandos** (intenções de mudar estado: create, update, delete) de **consultas**
(leituras sem efeito colateral: get, list). Cada operação tem um objeto imutável (Command/Query)
e um Handler dedicado.

O Controller **não tem lógica de negócio** — apenas cria o objeto certo e chama o handler.

**Antes de escrever qualquer código:** crie toda a estrutura de pacotes conforme abaixo.

### Estrutura de pacotes OBRIGATÓRIA

```
arch-benchmark/cqrs/src/main/java/com/benchmark/taskmanager/
├── TaskManagerApplication.java
├── commands/
│   ├── create/
│   │   ├── CreateTaskCommand.java          ← record (title, description)
│   │   └── CreateTaskHandler.java          ← @Component, handle(CreateTaskCommand) → Task
│   ├── update/
│   │   ├── UpdateTaskCommand.java          ← record (id, title, description, completed)
│   │   └── UpdateTaskHandler.java          ← @Component, handle(UpdateTaskCommand) → Task
│   └── delete/
│       ├── DeleteTaskCommand.java          ← record (id)
│       └── DeleteTaskHandler.java          ← @Component, handle(DeleteTaskCommand) → void
├── queries/
│   ├── get/
│   │   ├── GetTaskQuery.java               ← record (id)
│   │   └── GetTaskHandler.java             ← @Component, handle(GetTaskQuery) → Task
│   └── list/
│       ├── ListTasksQuery.java             ← record vazio ou classe
│       └── ListTasksHandler.java           ← @Component, handle(ListTasksQuery) → List<Task>
├── model/
│   ├── Task.java
│   ├── TaskRepository.java                 ← interface
│   └── InMemoryTaskRepository.java         ← @Repository, ConcurrentHashMap
└── api/
    ├── TaskController.java                 ← @RestController, injeta todos os Handlers
    ├── CreateTaskRequest.java              ← DTO HTTP
    ├── UpdateTaskRequest.java              ← DTO HTTP
    ├── GlobalExceptionHandler.java         ← @RestControllerAdvice
    └── TaskNotFoundException.java
```

### Como o Controller funciona

```
POST /tasks    → new CreateTaskCommand(req.title, req.description) → createHandler.handle(cmd)
PUT  /tasks/id → new UpdateTaskCommand(id, req.title, ...) → updateHandler.handle(cmd)
DEL  /tasks/id → new DeleteTaskCommand(id) → deleteHandler.handle(cmd)
GET  /tasks    → new ListTasksQuery() → listHandler.handle(query)
GET  /tasks/id → new GetTaskQuery(id) → getHandler.handle(query)
```

### Endpoints

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

## PASSO 5 — Regra de validação contínua (OBRIGATÓRIO)

```powershell
cd arch-benchmark/cqrs
.\mvnw.cmd compile
.\mvnw.cmd test
```

---

## PASSO 6 — Validação final

```powershell
cd arch-benchmark/cqrs
.\mvnw.cmd compile
.\mvnw.cmd test
```
Esperado: BUILD SUCCESS, zero falhas, cobertura ≥ 80%

---

## PASSO 7 — Testes E2E

```powershell
cd arch-benchmark/cqrs
Start-Process -NoNewWindow -FilePath ".\mvnw.cmd" -ArgumentList "spring-boot:run"
Start-Sleep -Seconds 20
```

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

```powershell
Stop-Process -Name "java" -Force -ErrorAction SilentlyContinue
```

---

## PASSO 8 — Coleta de métricas

```powershell
cd C:\Users\grios\OneDrive\Desktop\benchmark
python metrics/snapshot.py --post --language arch-cqrs --session-id <SESSION-ID>
python metrics/collector.py --session-id <SESSION-ID> --language arch-cqrs
```

---

## PASSO 9 — LOC e cobertura

```powershell
cd arch-benchmark/cqrs
.\mvnw.cmd test

cd C:\Users\grios\OneDrive\Desktop\benchmark
cloc arch-benchmark/cqrs/src/main/java --json | ConvertFrom-Json | Select-Object -ExpandProperty Java
cloc arch-benchmark/cqrs/src/test/java --json | ConvertFrom-Json | Select-Object -ExpandProperty Java
```

---

## PASSO 10 — Métricas de arquitetura

```powershell
cd arch-benchmark/cqrs/src

$fileCount = (Get-ChildItem -Recurse -Filter *.java | Measure-Object).Count
Write-Output "Arquivos .java: $fileCount"

$interfaceCount = (Get-ChildItem -Recurse -Filter *.java | Select-String "^public interface" | Measure-Object).Count
Write-Output "Interfaces: $interfaceCount"

$packageCount = (Get-ChildItem -Recurse -Directory main/java | Measure-Object).Count
Write-Output "Pacotes: $packageCount"
```

Nota de conformidade (0-10):
- Commands e Queries são `record`? (classe mutável = -2)
- `TaskController` acessa `TaskRepository` diretamente? (sim = -3)
- Command handlers importam Query handlers? (sim = -2)
- Estrutura `commands/`, `queries/`, `model/`, `api/` presente?

---

## PASSO 11 — Atualizar JSON

```json
{
  "architecture": "cqrs",
  "code_quality": {
    "lines_of_code": <LOC_PRODUCAO>,
    "test_lines_of_code": <LOC_TESTES>,
    "test_coverage_line_pct": <COBERTURA_LINHA_%>,
    "test_coverage_branch_pct": <COBERTURA_BRANCH_%>,
    "test_ratio_pct": <TEST_LOC / (PROD_LOC + TEST_LOC) * 100>
  },
  "arch_metrics": {
    "file_count": <QUANTIDADE_ARQUIVOS_JAVA>,
    "interface_count": <QUANTIDADE_INTERFACES>,
    "package_count": <QUANTIDADE_PACOTES>,
    "arch_conformance": <NOTA_0_A_10>,
    "dependency_violations": <0_OU_MAIS>
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

## PASSO 12 — Relatório de conclusão

```
✅ BENCHMARK CQRS — CONCLUÍDO

Session ID: <UUID>
Arquivo: metrics/reports/arch-cqrs_<timestamp>.json

[ ] .\mvnw.cmd compile — BUILD SUCCESS
[ ] .\mvnw.cmd test    — 0 failures, 0 errors
[ ] Cobertura          — ≥ 80%
[ ] E2E                — X/12 passaram
[ ] Commands/Queries são imutáveis (record)
[ ] Controller não acessa repositório diretamente
[ ] Conformidade       — nota X/10
```

---

## ⚠️ CRITÉRIO DE ACEITE

- `.\mvnw.cmd compile` → BUILD SUCCESS
- `.\mvnw.cmd test` → 0 failures, 0 errors, cobertura ≥ 80%
- 12/12 cenários E2E passando
- `metrics/reports/arch-cqrs_*.json` gerado e preenchido
- Commands/Queries são objetos imutáveis
- `TaskController` não acessa repositório diretamente
