# BENCHMARK KOTLIN GRADLE — MODO 1 (Agente Sequencial)

> Você é o agente responsável por executar este benchmark completo.
> Leia todos os passos antes de iniciar. Execute em ordem. Não pule etapas.
> Este arquivo conduz você do início à coleta final de métricas.
>
> **MODELO OBRIGATÓRIO:** Esta sessão deve rodar com `claude-sonnet-4-6`.
> Confirme executando: `claude --version` e verificando o modelo ativo nas configurações.

---

## PASSO 0 — Verificar Gradle instalado

```powershell
gradle --version
```

Esperado: versão 8.x ou superior. Se não estiver instalado:

```powershell
# Via Scoop (recomendado)
scoop install gradle
# Ou baixar em: https://gradle.org/install/
```

---

## PASSO 1 — Capturar Session ID atual

```powershell
Get-Content (Get-ChildItem "$env:USERPROFILE\.claude\sessions\" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName | ConvertFrom-Json | Select-Object sessionId, cwd, startedAt
```

**Guarde o `sessionId` retornado — você vai precisar dele no Passo 7.**

---

## PASSO 2 — Snapshot pré-sessão

```powershell
cd C:\Users\grios\OneDrive\Desktop\benchmark
python tools/snapshot.py --pre --language kotlin-gradle
```

Confirme que `tools/reports/snapshot_kotlin-gradle_pre_*.json` foi criado.

---

## PASSO 3 — Ler a especificação

1. `shared/task-definition.md` — Especificação funcional dos endpoints

---

## PASSO 4 — Implementar a Task Manager API em Kotlin

Trabalhe dentro do diretório `kotlin-gradle-mode-1/`.

### Stack obrigatória
- Kotlin 1.9+, Spring Boot 3.2, **Gradle (Kotlin DSL)**
- Storage in-memory (`ConcurrentHashMap`)
- JUnit 5 + Spring Boot Test
- JaCoCo para cobertura (mínimo 80%)

> O `build.gradle.kts` já está configurado. **Não crie nem modifique arquivos de build.**

### Estrutura de arquivos a criar

```
kotlin-gradle-mode-1/
├── build.gradle.kts       ← já existe, NÃO modificar
├── settings.gradle.kts    ← já existe, NÃO modificar
└── src/
    ├── main/kotlin/com/benchmark/taskmanager/
    │   ├── TaskManagerApplication.kt
    │   ├── controller/TaskController.kt
    │   ├── model/Task.kt
    │   ├── dto/CreateTaskRequest.kt
    │   ├── dto/UpdateTaskRequest.kt
    │   ├── service/TaskService.kt
    │   ├── exception/TaskNotFoundException.kt
    │   └── exception/GlobalExceptionHandler.kt
    └── test/kotlin/com/benchmark/taskmanager/
        ├── controller/TaskControllerTest.kt
        └── service/TaskServiceTest.kt
```

### Endpoints a implementar

| Método | Rota        | Sucesso | Erro    |
|--------|-------------|---------|---------|
| GET    | /tasks      | 200     | —       |
| POST   | /tasks      | 201     | 400     |
| GET    | /tasks/{id} | 200     | 404     |
| PUT    | /tasks/{id} | 200     | 400/404 |
| DELETE | /tasks/{id} | 204     | 404     |

### Modelo Task (data class)

```kotlin
data class Task(
    val id: String,           // UUID
    val title: String,        // obrigatório, max 200 chars
    val description: String?, // opcional, max 1000 chars
    val completed: Boolean = false,
    val createdAt: String,    // ISO 8601 UTC
    val updatedAt: String     // ISO 8601 UTC
)
```

### Validações obrigatórias

- `title` ausente ou vazio → 400 `{"error":"title is required"}`
- `title` > 200 chars → 400 `{"error":"title must not exceed 200 characters"}`
- `description` > 1000 chars → 400 `{"error":"description must not exceed 1000 characters"}`
- ID não encontrado → 404 `{"error":"Task not found"}`

---

## PASSO 5 — Regra de validação contínua (OBRIGATÓRIO)

**Após cada arquivo criado ou modificado**, execute:

```powershell
cd kotlin-gradle-mode-1
gradle compileKotlin
```

Se compilar com sucesso:

```powershell
gradle test
```

**Nunca avance para o próximo arquivo com build quebrado ou teste falhando.**
Cada falha corrigida é capturada como métrica automaticamente — não comente código para forçar passagem.

---

## PASSO 6 — Validação final antes dos testes E2E

```powershell
cd kotlin-gradle-mode-1
gradle compileKotlin
```
Esperado: `BUILD SUCCESSFUL`

```powershell
gradle test
```
Esperado: `BUILD SUCCESSFUL`, zero `FAILED`

```powershell
gradle jacocoTestReport
# Relatório em: build/reports/jacoco/test/html/index.html
```

```powershell
gradle check
# Falha se cobertura < 80% (configurado no build.gradle.kts)
```

---

## PASSO 7 — Testes E2E (app deve estar rodando)

### Subir o app em background

```powershell
cd kotlin-gradle-mode-1
Start-Process -NoNewWindow -FilePath "gradle" -ArgumentList "bootRun"
Start-Sleep -Seconds 25
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

### Se algum cenário falhar

Corrija o código, rode `gradle compileKotlin` e `gradle test`, reaponte o app e repita o cenário que falhou.

### Encerrar o app

```powershell
Stop-Process -Name "java" -Force -ErrorAction SilentlyContinue
```

---

## PASSO 8 — Snapshot pós-sessão e coleta de métricas

```powershell
cd C:\Users\grios\OneDrive\Desktop\benchmark
python tools/snapshot.py --post --language kotlin-gradle --session-id <SESSION-ID>
python tools/collector.py --session-id <SESSION-ID> --language kotlin-gradle
```

Confirme que `tools/reports/kotlin-gradle_*.json` foi criado.

---

## PASSO 9 — Coletar métricas de cobertura e LOC

```powershell
cd kotlin-gradle-mode-1
gradle test jacocoTestReport
# Relatório JaCoCo em: build/reports/jacoco/test/html/index.html

cd C:\Users\grios\OneDrive\Desktop\benchmark
cloc experiments/exp-01-java-vs-kotlin/kotlin-gradle-mode-1/src/main/kotlin --json | ConvertFrom-Json | Select-Object -ExpandProperty Kotlin
cloc experiments/exp-01-java-vs-kotlin/kotlin-gradle-mode-1/src/test/kotlin --json | ConvertFrom-Json | Select-Object -ExpandProperty Kotlin
```

---

## PASSO 10 — Atualizar JSON com dados manuais

Abra `tools/reports/kotlin-gradle_<timestamp>.json` e adicione:

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
    "failure_details": ["<cenários que falharam, se houver>"]
  }
}
```

---

## PASSO 11 — Gerar relatório HTML interativo

```powershell
cd C:\Users\grios\OneDrive\Desktop\benchmark
python tools/report.py
# Abre automaticamente: tools/reports/benchmark_report_<timestamp>.html
```

---

## PASSO 12 — Relatório de conclusão

```
✅ BENCHMARK KOTLIN GRADLE MODO 1 — CONCLUÍDO

Session ID: <UUID>
Arquivo de métricas: tools/reports/kotlin-gradle_<timestamp>.json

Critérios de entrega:
[ ] gradle compileKotlin — BUILD SUCCESSFUL
[ ] gradle test          — 0 failures, 0 errors
[ ] gradle check         — cobertura JaCoCo ≥ 80%
[ ] App rodou            — porta 8080 ok
[ ] E2E                  — X/12 passaram

Tokens totais:  (ver JSON)
Custo USD:      (ver JSON)
Duração sessão: (ver JSON)
```

---

## ⚠️ CRITÉRIO DE ACEITE

- `gradle compileKotlin` → BUILD SUCCESSFUL
- `gradle test` → 0 failures, 0 errors
- `gradle check` → cobertura ≥ 80%
- 12/12 cenários E2E passando
- `tools/reports/kotlin-gradle_*.json` gerado e preenchido
