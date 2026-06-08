# BENCHMARK JAVA GRADLE — MODO 1 (Agente Sequencial)

> Você é o agente responsável por executar este benchmark completo.
> Leia todos os passos antes de iniciar. Execute em ordem. Não pule etapas.
> Este arquivo conduz você do início à coleta final de métricas.
>
> **MODELO OBRIGATÓRIO:** Esta sessão deve rodar com `claude-sonnet-4-6`.
> Confirme executando: `claude --version` e verificando o modelo ativo nas configurações.

---

## PASSO 0 — Verificar Gradle instalado

```powershell
./gradlew.bat --version
```

Esperado: versão 8.x ou superior. Se não estiver instalado:

```powershell
# Via Scoop (recomendado)
scoop install gradle
# Ou baixar em: https://gradle.org/install/
```

---

## PASSO 1 — Capturar Session ID atual

Execute o comando abaixo para descobrir o session ID desta sessão Claude Code:

```powershell
Get-Content (Get-ChildItem "$env:USERPROFILE\.claude\sessions\" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName | ConvertFrom-Json | Select-Object sessionId, cwd, startedAt
```

**Guarde o `sessionId` retornado — você vai precisar dele no Passo 7.**

---

## PASSO 2 — Snapshot pré-sessão

A partir da raiz do benchmark (`C:\Users\grios\OneDrive\Desktop\benchmark`):

```powershell
python tools/snapshot.py --pre --language java-gradle
```

Confirme que o arquivo `tools/reports/snapshot_java-gradle_pre_*.json` foi criado.

---

## PASSO 3 — Ler a especificação

Leia os dois arquivos abaixo antes de implementar qualquer código:

1. `shared/task-definition.md` — Especificação funcional dos endpoints

---

## PASSO 4 — Implementar a Task Manager API em Java

Trabalhe dentro do diretório `java-gradle-mode-1/`.

### Stack obrigatória
- Java 21, Spring Boot 3.2, **Gradle**
- Storage in-memory (`ConcurrentHashMap`)
- JUnit 5 + Spring Boot Test
- JaCoCo para cobertura (mínimo 80%)

> O `build.gradle` já está configurado. **Não crie nem modifique arquivos de build.**

### Estrutura de arquivos a criar

```
java-gradle-mode-1/
├── build.gradle       ← já existe, NÃO modificar
├── settings.gradle    ← já existe, NÃO modificar
└── src/
    ├── main/java/com/benchmark/taskmanager/
    │   ├── TaskManagerApplication.java
    │   ├── controller/TaskController.java
    │   ├── model/Task.java
    │   ├── dto/CreateTaskRequest.java
    │   ├── dto/UpdateTaskRequest.java
    │   ├── service/TaskService.java
    │   ├── exception/TaskNotFoundException.java
    │   └── exception/GlobalExceptionHandler.java
    └── test/java/com/benchmark/taskmanager/
        ├── controller/TaskControllerTest.java
        └── service/TaskServiceTest.java
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

## PASSO 5 — Regra de validação contínua (OBRIGATÓRIO)

**Após cada arquivo criado ou modificado**, execute:

```powershell
cd java-gradle-mode-1
./gradlew.bat compileJava
```

Se compilar com sucesso:

```powershell
./gradlew.bat test
```

**Nunca avance para o próximo arquivo com build quebrado ou teste falhando.**
Cada falha corrigida é capturada como métrica automaticamente — não comente código para forçar passagem.

---

## PASSO 6 — Validação final antes dos testes E2E

Execute a sequência completa:

```powershell
cd java-gradle-mode-1
./gradlew.bat compileJava
```
Esperado: `BUILD SUCCESSFUL`

```powershell
./gradlew.bat test
```
Esperado: `BUILD SUCCESSFUL`, zero `FAILED`

```powershell
./gradlew.bat jacocoTestReport
# Relatório em: build/reports/jacoco/test/html/index.html
```

```powershell
./gradlew.bat check
# Falha se cobertura < 80% (configurado no build.gradle)
```

---

## PASSO 7 — Testes E2E (app deve estar rodando)

### Subir o app em background

```powershell
cd java-gradle-mode-1
Start-Process -NoNewWindow -FilePath ".gradlew.bat" -ArgumentList "bootRun"
# Aguardar ~15 segundos até o log mostrar "Started TaskManagerApplication"
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

### Se algum cenário falhar

Corrija o código, rode `./gradlew.bat compileJava` e `./gradlew.bat test`, reaponte o app e repita o cenário que falhou.
**Não avance para o Passo 8 com E2E falhando.**

### Encerrar o app

```powershell
Stop-Process -Name "java" -Force -ErrorAction SilentlyContinue
```

---

## PASSO 8 — Snapshot pós-sessão e coleta de métricas

Volte para a raiz do benchmark e execute (substituindo `<SESSION-ID>` pelo valor do Passo 1):

```powershell
cd C:\Users\grios\OneDrive\Desktop\benchmark
python tools/snapshot.py --post --language java-gradle --session-id <SESSION-ID>
python tools/collector.py --session-id <SESSION-ID> --language java-gradle
```

Confirme que `tools/reports/java-gradle_*.json` foi criado.

---

## PASSO 9 — Coletar métricas de cobertura e LOC

```powershell
cd java-gradle-mode-1

# Gerar relatório JaCoCo
./gradlew.bat test jacocoTestReport

# Relatório completo em: build/reports/jacoco/test/html/index.html

# Contar LOC
cd C:\Users\grios\OneDrive\Desktop\benchmark
cloc experiments/exp-01-java-vs-kotlin/java-gradle-mode-1/src/main/java --json | ConvertFrom-Json | Select-Object -ExpandProperty Java
cloc experiments/exp-01-java-vs-kotlin/java-gradle-mode-1/src/test/java --json | ConvertFrom-Json | Select-Object -ExpandProperty Java
```

---

## PASSO 10 — Atualizar JSON com dados manuais

Abra o arquivo `tools/reports/java-gradle_<timestamp>.json` e adicione/atualize os campos:

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
    "failure_details": [
      "<descrever cenários que falharam, se houver>"
    ]
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

Ao finalizar, reporte o seguinte resumo:

```
✅ BENCHMARK JAVA GRADLE MODO 1 — CONCLUÍDO

Session ID: <UUID>
Arquivo de métricas: tools/reports/java-gradle_<timestamp>.json

Critérios de entrega:
[ ] ./gradlew.bat compileJava — BUILD SUCCESSFUL
[ ] ./gradlew.bat test        — 0 failures, 0 errors
[ ] ./gradlew.bat check       — cobertura ≥ 80%
[ ] App rodou          — porta 8080 ok
[ ] E2E                — X/12 passaram

Tokens totais:    (ver JSON)
Custo USD:        (ver JSON)
Duração sessão:   (ver JSON)
```

---

## ⚠️ CRITÉRIO DE ACEITE

A sessão só está concluída quando:

- `./gradlew.bat compileJava` → BUILD SUCCESSFUL
- `./gradlew.bat test` → 0 failures, 0 errors
- `./gradlew.bat check` → cobertura ≥ 80%
- 12/12 cenários E2E passando
- `tools/reports/java-gradle_*.json` gerado e preenchido
