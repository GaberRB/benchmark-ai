# BENCHMARK ARQUITETURA — VERTICAL SLICE (Agente Sequencial)

> Você é o agente responsável por executar este benchmark completo.
> Leia todos os passos antes de iniciar. Execute em ordem. Não pule etapas.
> Este arquivo conduz você do início à coleta final de métricas.
>
> **MODELO OBRIGATÓRIO:** Esta sessão deve rodar com `claude-sonnet-4-6`.
> Confirme executando: `claude --version` e verificando o modelo ativo.

---

## PASSO 1 — Capturar Session ID atual

```powershell
Get-Content (Get-ChildItem "$env:USERPROFILE\.claude\sessions\" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName | ConvertFrom-Json | Select-Object sessionId, cwd, startedAt
```

**Guarde o `sessionId` retornado — você vai precisar dele no Passo 8.**

---

## PASSO 2 — Snapshot pré-sessão

A partir da raiz do benchmark (`C:\Users\grios\OneDrive\Desktop\benchmark`):

```powershell
python metrics/snapshot.py --pre --language arch-vertical-slice
```

Confirme que o arquivo `metrics/reports/snapshot_arch-vertical-slice_pre_*.json` foi criado.

---

## PASSO 3 — Ler a especificação

Leia os dois arquivos abaixo antes de implementar qualquer código:

1. `.claude/spec/prd-arch-vertical-slice.md` — PRD completo com estrutura de pacotes, regras e nomenclatura obrigatória
2. `spec/task-definition.md` — Especificação funcional dos endpoints

---

## PASSO 4 — Implementar a Task Manager API (Vertical Slice)

Trabalhe dentro do diretório `arch-benchmark/vertical-slice/`.

### Conceito fundamental — Vertical Slice

Cada operação (Create, Get, Update, Delete, List) é um "slice" com seu próprio pacote.
O slice contém tudo que precisa: controller, DTO, use case.
**Slices não chamam uns aos outros.** Código compartilhado vai em `tasks/shared/`.

### Estrutura de pacotes OBRIGATÓRIA (crie antes do código)

```
arch-benchmark/vertical-slice/src/main/java/com/benchmark/taskmanager/
├── TaskManagerApplication.java
└── tasks/
    ├── create/
    │   ├── CreateTaskController.java    ← POST /tasks
    │   ├── CreateTaskRequest.java
    │   └── CreateTaskUseCase.java
    ├── get/
    │   ├── GetTaskController.java       ← GET /tasks/{id}
    │   └── GetTaskUseCase.java
    ├── update/
    │   ├── UpdateTaskController.java    ← PUT /tasks/{id}
    │   ├── UpdateTaskRequest.java
    │   └── UpdateTaskUseCase.java
    ├── delete/
    │   ├── DeleteTaskController.java    ← DELETE /tasks/{id}
    │   └── DeleteTaskUseCase.java
    ├── list/
    │   ├── ListTasksController.java     ← GET /tasks
    │   └── ListTasksUseCase.java
    └── shared/
        ├── Task.java
        ├── TaskRepository.java          ← interface
        ├── InMemoryTaskRepository.java  ← @Repository, ConcurrentHashMap
        ├── TaskNotFoundException.java
        └── GlobalExceptionHandler.java  ← @RestControllerAdvice
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

**Após cada arquivo criado ou modificado**, execute:

```powershell
cd arch-benchmark/vertical-slice
.\mvnw.cmd compile
```

Se compilar com sucesso:

```powershell
.\mvnw.cmd test
```

**Nunca avance para o próximo arquivo com build quebrado ou teste falhando.**

---

## PASSO 6 — Validação final antes dos testes E2E

```powershell
cd arch-benchmark/vertical-slice
.\mvnw.cmd compile
```
Esperado: `BUILD SUCCESS`

```powershell
.\mvnw.cmd test
```
Esperado: `BUILD SUCCESS`, zero `Failures`, zero `Errors`, cobertura ≥ 80%

---

## PASSO 7 — Testes E2E (app deve estar rodando)

### Subir o app em background

```powershell
cd arch-benchmark/vertical-slice
Start-Process -NoNewWindow -FilePath ".\mvnw.cmd" -ArgumentList "spring-boot:run"
Start-Sleep -Seconds 20
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

```powershell
cd C:\Users\grios\OneDrive\Desktop\benchmark
python metrics/snapshot.py --post --language arch-vertical-slice --session-id <SESSION-ID>
python metrics/collector.py --session-id <SESSION-ID> --language arch-vertical-slice
```

Confirme que `metrics/reports/arch-vertical-slice_*.json` foi criado.

---

## PASSO 9 — Coletar métricas de cobertura e LOC

```powershell
cd arch-benchmark/vertical-slice
.\mvnw.cmd test

cd C:\Users\grios\OneDrive\Desktop\benchmark
cloc arch-benchmark/vertical-slice/src/main/java --json | ConvertFrom-Json | Select-Object -ExpandProperty Java
cloc arch-benchmark/vertical-slice/src/test/java --json | ConvertFrom-Json | Select-Object -ExpandProperty Java
```

---

## PASSO 10 — Coletar métricas de arquitetura

Execute na pasta `arch-benchmark/vertical-slice/src/`:

```powershell
cd arch-benchmark/vertical-slice/src

# Contagem de arquivos .java
$fileCount = (Get-ChildItem -Recurse -Filter *.java | Measure-Object).Count
Write-Output "Arquivos .java: $fileCount"

# Contagem de interfaces
$interfaceCount = (Get-ChildItem -Recurse -Filter *.java | Select-String "^public interface" | Measure-Object).Count
Write-Output "Interfaces: $interfaceCount"

# Contagem de pacotes (subpastas)
$packageCount = (Get-ChildItem -Recurse -Directory main/java | Measure-Object).Count
Write-Output "Pacotes: $packageCount"
```

Após verificar o código gerado, atribua uma **nota de conformidade (0-10)**:
- 10 = estrutura de pacotes exatamente como o PRD, sem desvios
- 7-9 = pequenos desvios (nomes ligeiramente diferentes, mas padrão respeitado)
- 4-6 = estrutura parcialmente correta (misturou com padrão layered)
- 0-3 = ignorou o padrão (fez layered puro, sem slices)

Verificar: há algum slice importando outro slice? (se sim, `dependency_violations > 0`)

---

## PASSO 11 — Atualizar JSON com dados manuais

Abra `metrics/reports/arch-vertical-slice_<timestamp>.json` e adicione:

```json
{
  "architecture": "vertical-slice",
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
✅ BENCHMARK VERTICAL SLICE — CONCLUÍDO

Session ID: <UUID>
Arquivo de métricas: metrics/reports/arch-vertical-slice_<timestamp>.json

Critérios de entrega:
[ ] .\mvnw.cmd compile — BUILD SUCCESS
[ ] .\mvnw.cmd test    — 0 failures, 0 errors
[ ] Cobertura          — ≥ 80%
[ ] App rodou          — porta 8080 ok
[ ] E2E                — X/12 passaram
[ ] Conformidade       — nota X/10

Tokens totais:    (ver JSON)
Custo USD:        (ver JSON)
Duração sessão:   (ver JSON)
Arquivos criados: (ver arch_metrics)
```

---

## ⚠️ CRITÉRIO DE ACEITE

A sessão só está concluída quando:

- `.\mvnw.cmd compile` → BUILD SUCCESS
- `.\mvnw.cmd test` → 0 failures, 0 errors, cobertura ≥ 80%
- 12/12 cenários E2E passando
- `metrics/reports/arch-vertical-slice_*.json` gerado e preenchido
- Estrutura de pacotes conforme PRD (slices separados, sem mistura de camadas)
