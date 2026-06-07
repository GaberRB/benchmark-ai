# BENCHMARK OLLAMA — CQRS (Command Query Responsibility Segregation) (Aider)

> Você é o agente Aider responsável por executar este benchmark completo.
> Leia todos os passos antes de iniciar. Execute em ordem. Não pule etapas.
>
> **CONFIGURE AS VARIÁVEIS ABAIXO ANTES DE INICIAR:**

```powershell
$MODEL     = "deepseek-coder-v2:16b"   # trocar: qwen2.5-coder:7b | codellama:13b | llama3.1:8b
$MODEL_DIR = "deepseek-coder"           # trocar: qwen2.5-coder | codellama | llama3.1
$ARCH      = "cqrs"
$BASE_DIR  = "C:\Users\grios\OneDrive\Desktop\benchmark"
$IMPL_DIR  = "$BASE_DIR\experiments\exp-03-ollama-local-models\implementations\$MODEL_DIR\$ARCH"
```

---

## PASSO 1 — Verificar modelo disponível no Ollama

```powershell
ollama list
# Confirme que $MODEL aparece. Se não: ollama pull $MODEL
```

---

## PASSO 2 — Iniciar coleta de métricas

```powershell
cd $BASE_DIR
python tools/ollama_collector.py --start --model $MODEL --arch $ARCH
```

---

## PASSO 3 — Iniciar sessão Aider

```powershell
cd $IMPL_DIR
aider --model ollama/$MODEL `
      --read "$BASE_DIR\shared\task-definition.md" `
      --read "$BASE_DIR\experiments\exp-03-ollama-local-models\spec\prd.md" `
      --no-auto-commits
```

---

## PASSO 4 — Implementar a Task Manager API (CQRS)

### Conceito fundamental — CQRS

Separar **comandos** (intenções de mudar estado: create, update, delete) de **consultas**
(leituras sem efeito colateral: get, list). Cada operação tem um objeto imutável (Command/Query)
e um Handler dedicado.

O Controller **não tem lógica de negócio** — apenas cria o objeto certo e chama o handler.

**Antes de escrever qualquer código:** crie toda a estrutura de pacotes.

### Estrutura de pacotes OBRIGATÓRIA

```
src/main/java/com/benchmark/taskmanager/
├── TaskManagerApplication.java
├── commands/
│   ├── create/
│   │   ├── CreateTaskCommand.java          ← record (title, description)
│   │   └── CreateTaskHandler.java          ← @Component, handle(CreateTaskCommand) → Task
│   ├── update/
│   │   ├── UpdateTaskCommand.java          ← record (id, title, description, completed)
│   │   └── UpdateTaskHandler.java
│   └── delete/
│       ├── DeleteTaskCommand.java          ← record (id)
│       └── DeleteTaskHandler.java
├── queries/
│   ├── get/
│   │   ├── GetTaskQuery.java               ← record (id)
│   │   └── GetTaskHandler.java
│   └── list/
│       ├── ListTasksQuery.java
│       └── ListTasksHandler.java
├── model/
│   ├── Task.java
│   ├── TaskRepository.java                 ← interface
│   └── InMemoryTaskRepository.java         ← @Repository, ConcurrentHashMap
└── api/
    ├── TaskController.java                 ← @RestController, injeta todos os Handlers
    ├── CreateTaskRequest.java
    ├── UpdateTaskRequest.java
    ├── GlobalExceptionHandler.java
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

### Validações obrigatórias

- `title` ausente ou vazio → 400 `{"error":"title is required"}`
- `title` > 200 chars → 400 `{"error":"title must not exceed 200 characters"}`
- `description` > 1000 chars → 400 `{"error":"description must not exceed 1000 characters"}`
- ID não encontrado → 404 `{"error":"Task not found"}`

---

## PASSO 5 — Regra de validação contínua (OBRIGATÓRIO)

```powershell
cd $IMPL_DIR
.\mvnw.cmd compile
.\mvnw.cmd test
```

---

## PASSO 6 — Validação final

```powershell
cd $IMPL_DIR
.\mvnw.cmd compile
.\mvnw.cmd test
```

Esperado: `BUILD SUCCESS`, zero falhas, cobertura ≥ 80%

---

## PASSO 7 — Testes E2E

```powershell
cd $IMPL_DIR
Start-Process -NoNewWindow -FilePath ".\mvnw.cmd" -ArgumentList "spring-boot:run"
Start-Sleep -Seconds 20
```

```powershell
$BASE = "http://localhost:8080"

$r01 = curl.exe -s -w "`n%{http_code}" "$BASE/tasks"
Write-Output "E2E-01: $($r01 -split "`n" | Select-Object -Last 1) (esperado: 200)"

$r02 = curl.exe -s -w "`n%{http_code}" -X POST "$BASE/tasks" -H "Content-Type: application/json" -d '{"title":"Test Task","description":"Desc"}'
$body02 = $r02 -split "`n" | Select-Object -First 1
Write-Output "E2E-02: $($r02 -split "`n" | Select-Object -Last 1) (esperado: 201)"
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

```powershell
Stop-Process -Name "java" -Force -ErrorAction SilentlyContinue
```

---

## PASSO 8 — Coleta de métricas finais

```powershell
cd $BASE_DIR
python tools/ollama_collector.py --collect --model $MODEL --arch $ARCH --impl-dir $IMPL_DIR
```

---

## PASSO 9 — LOC e cobertura

```powershell
cloc $IMPL_DIR\src\main\java --json | ConvertFrom-Json | Select-Object -ExpandProperty Java
cloc $IMPL_DIR\src\test\java --json | ConvertFrom-Json | Select-Object -ExpandProperty Java
```

---

## PASSO 10 — Conformidade arquitetural

```powershell
cd $IMPL_DIR\src
$fileCount = (Get-ChildItem -Recurse -Filter *.java | Measure-Object).Count
$interfaceCount = (Get-ChildItem -Recurse -Filter *.java | Select-String "^public interface" | Measure-Object).Count
Write-Output "Arquivos: $fileCount | Interfaces: $interfaceCount"

# Verificar que Controller não tem lógica de negócio
Select-String -Path (Get-ChildItem -Recurse -Filter TaskController.java).FullName -Pattern "if|for|while|switch"
# Deve ter poucas ou nenhuma ocorrência
```

Nota de conformidade (0-10):
- Pacotes `commands/` e `queries/` existem? (não = -2 cada)
- Cada operação tem Command/Query + Handler separado? (faltando = -1 cada)
- Controller tem lógica de negócio (if/for além de validação HTTP básica)? (sim = -2)
- Commands e Queries são objetos imutáveis (records ou final fields)? (não = -2)

---

## ⚠️ CRITÉRIO DE ACEITE

- `.\mvnw.cmd compile` → BUILD SUCCESS
- `.\mvnw.cmd test` → 0 failures, 0 errors, cobertura ≥ 80%
- 12/12 cenários E2E passando
- Pacotes `commands/` e `queries/` com handlers separados por operação
- Controller delega para handlers sem lógica própria
- JSON de métricas gerado
