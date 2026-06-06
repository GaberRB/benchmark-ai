# Benchmark — Arquitetura Event-Driven

Este guia mede o custo e qualidade de usar Claude para implementar uma Task Manager API
seguindo **Event-Driven Architecture** (Domain Events + EventBus + Handlers desacoplados).

---

## Pré-requisitos

- [ ] Java 21 instalado (`java -version`)
- [ ] Maven disponível (`mvn -version`)
- [ ] Python 3.10+ com `requests` (`pip install requests`)
- [ ] Claude Code CLI autenticado

---

## Passo 1 — Preparar o diretório

```powershell
cd arch-benchmark\event-driven
```

Se existir `src/` de uma execução anterior, remova:
```powershell
Remove-Item -Recurse -Force src -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force target -ErrorAction SilentlyContinue
```

---

## Passo 2 — Verificar o pom.xml

```powershell
Get-Content pom.xml | Select-String "artifactId"
# Deve mostrar: task-manager-event-driven
```

---

## Passo 3 — Abrir nova sessão Claude Code

```powershell
claude
```

**Anote o Session ID** exibido no início da sessão (formato: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`).

---

## Passo 4 — Prompt de implementação

Cole o prompt abaixo **exatamente** na sessão Claude:

```
Leia o PRD em .claude/spec/prd-arch-event-driven.md e implemente a Task Manager API
completa usando Event-Driven Architecture no diretório arch-benchmark/event-driven/.

Requisitos obrigatórios:
1. Crie TODA a estrutura de pacotes definida no PRD antes de escrever código
2. Domain Events devem ser Java records imutáveis implementando DomainEvent
3. EventBus deve ser uma interface — implemente InMemoryEventBus manualmente (SEM ApplicationEventPublisher do Spring)
4. TaskService injeta EventBus como interface, não InMemoryEventBus diretamente
5. TaskService NÃO conhece os handlers — publica para o bus e pronto
6. Cada operação de mutação (create/update/delete) publica exatamente 1 evento APÓS o sucesso
7. Handlers são registrados no InMemoryEventBus via @PostConstruct
8. Testes com cobertura JaCoCo mínima de 80% (BUILD FAILURE se menor)
9. Ao terminar, rode: .\mvnw.cmd test

Confirme o BUILD SUCCESS antes de encerrar.
```

---

## Passo 5 — Aguardar e monitorar

Aguarde a implementação completa. O Claude deve:
1. Criar a estrutura de pacotes
2. Implementar todas as classes
3. Rodar `mvnw.cmd test` e confirmar `BUILD SUCCESS`

Se ocorrer BUILD FAILURE, deixe o Claude corrigir até obter sucesso.

---

## Passo 6 — Verificar cobertura JaCoCo

Após BUILD SUCCESS:
```powershell
Get-Content target\site\jacoco\index.html | Select-String "Total"
```

---

## Passo 7 — Contar métricas de código

```powershell
# Linhas de código (LOC) — somente src/main
(Get-Content (Get-ChildItem -Recurse -Path src\main -Filter *.java) | Measure-Object -Line).Lines

# Número de arquivos Java
(Get-ChildItem -Recurse -Filter *.java -Path src\main | Measure-Object).Count

# Número de interfaces
(Select-String -Path (Get-ChildItem -Recurse -Filter *.java -Path src\main).FullName -Pattern "^public interface").Count

# Número de pacotes (subdiretórios de src/main/java)
(Get-ChildItem -Recurse -Directory -Path src\main\java | Measure-Object).Count
```

---

## Passo 8 — Executar testes E2E

Inicie a aplicação em segundo plano:
```powershell
Start-Process -NoNewWindow .\mvnw.cmd -ArgumentList "spring-boot:run" -PassThru
Start-Sleep -Seconds 15
```

Execute os 12 cenários E2E:
```powershell
# 1. Criar tarefa
$r1 = Invoke-RestMethod -Uri http://localhost:8080/tasks -Method POST -ContentType "application/json" -Body '{"title":"Tarefa EDA 1","description":"Event-Driven test"}'
Write-Host "1. CREATE: $($r1.id)"

# 2. Listar (deve ter 1)
$list = Invoke-RestMethod -Uri http://localhost:8080/tasks -Method GET
Write-Host "2. LIST count: $($list.Count)"

# 3. Buscar por ID
$r3 = Invoke-RestMethod -Uri "http://localhost:8080/tasks/$($r1.id)" -Method GET
Write-Host "3. GET: $($r3.title)"

# 4. Atualizar
$r4 = Invoke-RestMethod -Uri "http://localhost:8080/tasks/$($r1.id)" -Method PUT -ContentType "application/json" -Body '{"title":"Tarefa EDA Atualizada","description":"Updated","completed":false}'
Write-Host "4. UPDATE: $($r4.title)"

# 5. Completar tarefa
$r5 = Invoke-RestMethod -Uri "http://localhost:8080/tasks/$($r1.id)" -Method PUT -ContentType "application/json" -Body '{"title":"Tarefa EDA Atualizada","description":"Updated","completed":true}'
Write-Host "5. COMPLETE: status=$($r5.status)"

# 6. Criar segunda tarefa
$r6 = Invoke-RestMethod -Uri http://localhost:8080/tasks -Method POST -ContentType "application/json" -Body '{"title":"Tarefa EDA 2","description":"Second task"}'
Write-Host "6. CREATE 2: $($r6.id)"

# 7. Listar (deve ter 2)
$list2 = Invoke-RestMethod -Uri http://localhost:8080/tasks -Method GET
Write-Host "7. LIST count: $($list2.Count)"

# 8. Deletar primeira tarefa
Invoke-RestMethod -Uri "http://localhost:8080/tasks/$($r1.id)" -Method DELETE
Write-Host "8. DELETE: OK"

# 9. Listar (deve ter 1)
$list3 = Invoke-RestMethod -Uri http://localhost:8080/tasks -Method GET
Write-Host "9. LIST after delete: $($list3.Count)"

# 10. GET em ID inexistente — espera 404
try {
    Invoke-RestMethod -Uri "http://localhost:8080/tasks/id-inexistente" -Method GET
    Write-Host "10. 404 FALHOU — deveria ter dado erro"
} catch { Write-Host "10. 404 OK: $($_.Exception.Response.StatusCode)" }

# 11. POST sem título — espera 400
try {
    Invoke-RestMethod -Uri http://localhost:8080/tasks -Method POST -ContentType "application/json" -Body '{"description":"sem titulo"}'
    Write-Host "11. 400 FALHOU — deveria ter dado erro"
} catch { Write-Host "11. 400 OK: $($_.Exception.Response.StatusCode)" }

# 12. Verificar se evento foi logado após criação (smoke test)
# Checar se os handlers estão funcionando: olhar o console do servidor
# Se o servidor logou "Task created: <id>" → handler funcionou
Write-Host "12. HANDLER LOG: verifique o console do servidor por 'Task created:'"
```

Pare o servidor:
```powershell
Stop-Process -Name "java" -Force -ErrorAction SilentlyContinue
```

---

## Passo 9 — Coletar métricas de tokens

```powershell
python ..\..\metrics\collector.py `
  --session-id SEU_SESSION_ID_AQUI `
  --language java `
  --architecture event-driven `
  --output ..\..\metrics\reports\arch-event-driven.json
```

> Substitua `SEU_SESSION_ID_AQUI` pelo Session ID anotado no Passo 3.

---

## Passo 10 — Preencher métricas arquiteturais no JSON

Abra `metrics/reports/arch-event-driven.json` e adicione/atualize a seção `arch_metrics`:

```json
"arch_metrics": {
  "file_count": 0,
  "interface_count": 0,
  "package_count": 0,
  "arch_conformance": 0,
  "dependency_violations": 0
}
```

**Como pontuar `arch_conformance` (0-10):**
Consulte a tabela de conformidade no PRD (`prd-arch-event-driven.md`).
Cada item marcado ☑ vale 1 ponto. Anote a soma.

**Pontos de atenção para `dependency_violations`:**
- `TaskService` conheceu handlers diretamente? (+1)
- EventBus usou `ApplicationEventPublisher`? (+1)
- Events com campos mutáveis? (+1)
- Evento publicado antes da persistência? (+1)

---

## Passo 11 — Salvar JSON final

Estrutura esperada do JSON:
```json
{
  "meta": {
    "session_id": "...",
    "language": "java",
    "architecture": "event-driven",
    "timestamp": "..."
  },
  "tokens": {
    "input": 0,
    "output": 0,
    "cache_creation": 0,
    "cache_read": 0
  },
  "cost": {
    "total_usd": 0.0
  },
  "speed": {
    "total_duration_seconds": 0,
    "tokens_per_second": 0
  },
  "iterations": {
    "total": 0,
    "with_errors": 0,
    "error_rate": 0.0
  },
  "errors": {
    "compile": 0,
    "test": 0,
    "runtime": 0
  },
  "code_quality": {
    "loc": 0,
    "test_loc": 0,
    "coverage_pct": 0.0
  },
  "arch_metrics": {
    "file_count": 0,
    "interface_count": 0,
    "package_count": 0,
    "arch_conformance": 0,
    "dependency_violations": 0
  },
  "e2e": {
    "total": 12,
    "passed": 0,
    "failed": 0
  }
}
```

---

## Passo 12 — Gerar relatório atualizado

```powershell
python ..\..\metrics\report.py --mode arch
```

O HTML será salvo em `metrics/reports/arch_report_<timestamp>.html`.

---

## Checklist Final

- [ ] BUILD SUCCESS com cobertura ≥ 80%
- [ ] 12 cenários E2E executados e anotados
- [ ] `arch-event-driven.json` salvo em `metrics/reports/`
- [ ] `arch_conformance` preenchido com base no checklist do PRD
- [ ] `dependency_violations` verificado manualmente
- [ ] Handlers logaram eventos no console do servidor
- [ ] Relatório HTML gerado
