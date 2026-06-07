# run.ps1 - Benchmark completo Ollama + Aider (implementacao + testes + E2E + metricas)
# Uso: .\run.ps1                    (menu interativo)
#      .\run.ps1 -Model 2 -Arch 3   (parametros diretos)

param(
    [string]$Model = "",
    [string]$Arch  = "",
    [int]$MaxRetries = 5
)

$BASE_DIR = "C:\Users\grios\OneDrive\Desktop\benchmark"
$PKG_BASE = "src\main\java\com\benchmark\taskmanager"

$MODELS = [ordered]@{
    "1" = @{ Name = "deepseek-coder-v2:16b"; Dir = "deepseek-coder"; Label = "Deepseek Coder V2 16B  (~9 GB)" }
    "2" = @{ Name = "qwen2.5-coder:7b";      Dir = "qwen2.5-coder";  Label = "Qwen 2.5 Coder 7B      (~5 GB)" }
    "3" = @{ Name = "codellama:13b";          Dir = "codellama";      Label = "Code Llama 13B         (~7 GB)" }
    "4" = @{ Name = "llama3.1:8b";            Dir = "llama3.1";       Label = "Llama 3.1 8B           (~5 GB)" }
}

$ARCHS = [ordered]@{
    "1" = @{ Name = "mvc";                Dir = "mvc" }
    "2" = @{ Name = "vertical-slice";     Dir = "vertical-slice" }
    "3" = @{ Name = "clean-architecture"; Dir = "clean" }
    "4" = @{ Name = "hexagonal";          Dir = "hexagonal" }
    "5" = @{ Name = "ddd";                Dir = "ddd" }
    "6" = @{ Name = "event-driven";       Dir = "event-driven" }
    "7" = @{ Name = "cqrs";              Dir = "cqrs" }
}

# =====================================================================
# FUNCOES
# =====================================================================

function Log($msg, $color = "White") {
    $ts = Get-Date -Format "HH:mm:ss"
    Write-Host "[$ts] $msg" -ForegroundColor $color
}

function New-Stubs {
    param([string]$ImplDir, [string]$ArchName)
    $pkg = $PKG_BASE
    $files = switch ($ArchName) {
        "mvc" { @(
            "$pkg\TaskManagerApplication.java",
            "$pkg\model\Task.java",
            "$pkg\dto\CreateTaskRequest.java",
            "$pkg\dto\UpdateTaskRequest.java",
            "$pkg\repository\TaskRepository.java",
            "$pkg\repository\InMemoryTaskRepository.java",
            "$pkg\service\TaskService.java",
            "$pkg\controller\TaskController.java",
            "$pkg\exception\TaskNotFoundException.java",
            "$pkg\exception\GlobalExceptionHandler.java"
        )}
        "vertical-slice" { @(
            "$pkg\TaskManagerApplication.java",
            "$pkg\tasks\Task.java",
            "$pkg\tasks\TaskRepository.java",
            "$pkg\tasks\InMemoryTaskRepository.java",
            "$pkg\tasks\CreateTask\CreateTaskRequest.java",
            "$pkg\tasks\CreateTask\CreateTaskHandler.java",
            "$pkg\tasks\GetTask\GetTaskHandler.java",
            "$pkg\tasks\ListTasks\ListTasksHandler.java",
            "$pkg\tasks\UpdateTask\UpdateTaskRequest.java",
            "$pkg\tasks\UpdateTask\UpdateTaskHandler.java",
            "$pkg\tasks\DeleteTask\DeleteTaskHandler.java",
            "$pkg\tasks\TaskController.java",
            "$pkg\tasks\GlobalExceptionHandler.java",
            "$pkg\tasks\TaskNotFoundException.java"
        )}
        "clean-architecture" { @(
            "$pkg\TaskManagerApplication.java",
            "$pkg\domain\Task.java",
            "$pkg\domain\TaskRepository.java",
            "$pkg\application\TaskService.java",
            "$pkg\application\CreateTaskCommand.java",
            "$pkg\application\UpdateTaskCommand.java",
            "$pkg\infrastructure\InMemoryTaskRepository.java",
            "$pkg\interfaces\TaskController.java",
            "$pkg\interfaces\CreateTaskRequest.java",
            "$pkg\interfaces\UpdateTaskRequest.java",
            "$pkg\interfaces\TaskNotFoundException.java",
            "$pkg\interfaces\GlobalExceptionHandler.java"
        )}
        "hexagonal" { @(
            "$pkg\TaskManagerApplication.java",
            "$pkg\domain\Task.java",
            "$pkg\application\ports\in\CreateTaskUseCase.java",
            "$pkg\application\ports\in\GetTaskUseCase.java",
            "$pkg\application\ports\in\ListTasksUseCase.java",
            "$pkg\application\ports\in\UpdateTaskUseCase.java",
            "$pkg\application\ports\in\DeleteTaskUseCase.java",
            "$pkg\application\ports\out\TaskRepository.java",
            "$pkg\application\service\TaskService.java",
            "$pkg\adapters\in\web\TaskController.java",
            "$pkg\adapters\in\web\CreateTaskRequest.java",
            "$pkg\adapters\in\web\UpdateTaskRequest.java",
            "$pkg\adapters\in\web\GlobalExceptionHandler.java",
            "$pkg\adapters\out\persistence\InMemoryTaskRepository.java",
            "$pkg\exception\TaskNotFoundException.java"
        )}
        "ddd" { @(
            "$pkg\TaskManagerApplication.java",
            "$pkg\domain\model\Task.java",
            "$pkg\domain\model\TaskId.java",
            "$pkg\domain\model\Title.java",
            "$pkg\domain\model\Description.java",
            "$pkg\domain\repository\TaskRepository.java",
            "$pkg\domain\exception\TaskNotFoundException.java",
            "$pkg\domain\exception\InvalidValueException.java",
            "$pkg\application\TaskApplicationService.java",
            "$pkg\application\dto\CreateTaskCommand.java",
            "$pkg\application\dto\UpdateTaskCommand.java",
            "$pkg\application\dto\TaskDto.java",
            "$pkg\infrastructure\persistence\InMemoryTaskRepository.java",
            "$pkg\interfaces\web\TaskController.java",
            "$pkg\interfaces\web\CreateTaskRequest.java",
            "$pkg\interfaces\web\UpdateTaskRequest.java",
            "$pkg\interfaces\web\GlobalExceptionHandler.java"
        )}
        "event-driven" { @(
            "$pkg\TaskManagerApplication.java",
            "$pkg\events\DomainEvent.java",
            "$pkg\events\TaskCreatedEvent.java",
            "$pkg\events\TaskUpdatedEvent.java",
            "$pkg\events\TaskDeletedEvent.java",
            "$pkg\events\EventHandler.java",
            "$pkg\events\EventBus.java",
            "$pkg\events\InMemoryEventBus.java",
            "$pkg\handlers\TaskCreatedHandler.java",
            "$pkg\handlers\TaskUpdatedHandler.java",
            "$pkg\handlers\TaskDeletedHandler.java",
            "$pkg\model\Task.java",
            "$pkg\model\TaskStatus.java",
            "$pkg\repository\TaskRepository.java",
            "$pkg\repository\InMemoryTaskRepository.java",
            "$pkg\service\TaskService.java",
            "$pkg\api\TaskController.java",
            "$pkg\api\CreateTaskRequest.java",
            "$pkg\api\UpdateTaskRequest.java",
            "$pkg\api\TaskResponse.java",
            "$pkg\api\TaskNotFoundException.java",
            "$pkg\api\GlobalExceptionHandler.java"
        )}
        "cqrs" { @(
            "$pkg\TaskManagerApplication.java",
            "$pkg\commands\create\CreateTaskCommand.java",
            "$pkg\commands\create\CreateTaskHandler.java",
            "$pkg\commands\update\UpdateTaskCommand.java",
            "$pkg\commands\update\UpdateTaskHandler.java",
            "$pkg\commands\delete\DeleteTaskCommand.java",
            "$pkg\commands\delete\DeleteTaskHandler.java",
            "$pkg\queries\get\GetTaskQuery.java",
            "$pkg\queries\get\GetTaskHandler.java",
            "$pkg\queries\list\ListTasksQuery.java",
            "$pkg\queries\list\ListTasksHandler.java",
            "$pkg\model\Task.java",
            "$pkg\model\TaskRepository.java",
            "$pkg\model\InMemoryTaskRepository.java",
            "$pkg\api\TaskController.java",
            "$pkg\api\CreateTaskRequest.java",
            "$pkg\api\UpdateTaskRequest.java",
            "$pkg\api\GlobalExceptionHandler.java",
            "$pkg\api\TaskNotFoundException.java"
        )}
        default { @() }
    }
    foreach ($rel in $files) {
        $full = Join-Path $ImplDir $rel
        New-Item -ItemType Directory -Force -Path (Split-Path $full -Parent) | Out-Null
        if (-not (Test-Path $full)) { "" | Out-File -FilePath $full -Encoding utf8 }
    }
    $testRoot = Join-Path $ImplDir "src\test\java\com\benchmark\taskmanager"
    New-Item -ItemType Directory -Force -Path $testRoot | Out-Null
    $testFile = Join-Path $testRoot "TaskManagerApplicationTests.java"
    if (-not (Test-Path $testFile)) { "" | Out-File -FilePath $testFile -Encoding utf8 }

    Log "  $($files.Count + 1) stub files criados." "DarkGray"
    return $files | ForEach-Object { Join-Path $ImplDir $_ }
}

function Wait-ForApp {
    param([string]$Url = "http://localhost:8080/tasks", [int]$MaxWaitSec = 60)
    Log "  Aguardando app subir (max ${MaxWaitSec}s)..." "DarkGray"
    $elapsed = 0
    while ($elapsed -lt $MaxWaitSec) {
        try {
            $r = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            if ($r.StatusCode -eq 200) { Log "  App respondendo." "DarkGray"; return $true }
        } catch {}
        Start-Sleep -Seconds 3
        $elapsed += 3
    }
    Log "  App nao subiu em ${MaxWaitSec}s." "Red"
    return $false
}

function Run-E2E {
    $BASE_URL = "http://localhost:8080"
    $passed = 0
    $failures = @()

    function Check($num, $expected, $code, $body = "") {
        if ($code -eq $expected) {
            $script:passed++
            Log "  E2E-$num [PASS] $code" "Green"
        } else {
            $script:failures += "E2E-$num esperado $expected obteve $code"
            Log "  E2E-$num [FAIL] $code (esperado $expected)" "Red"
        }
        return $body
    }

    # 01 - GET /tasks lista vazia
    $r = curl.exe -s -w "`n%{http_code}" "$BASE_URL/tasks" 2>$null
    $parts = $r -split "`n"
    Check "01" "200" $parts[-1].Trim() | Out-Null

    # 02 - POST /tasks cria tarefa
    $r = curl.exe -s -w "`n%{http_code}" -X POST "$BASE_URL/tasks" -H "Content-Type: application/json" -d '{"title":"Test Task","description":"Desc"}' 2>$null
    $parts = $r -split "`n"
    Check "02" "201" $parts[-1].Trim() | Out-Null
    $TASK_ID = try { ($parts[0] | ConvertFrom-Json).id } catch { "unknown" }

    # 03 - POST body vazio
    $r = curl.exe -s -w "`n%{http_code}" -X POST "$BASE_URL/tasks" -H "Content-Type: application/json" -d '{}' 2>$null
    Check "03" "400" ($r -split "`n")[-1].Trim() | Out-Null

    # 04 - POST title vazio
    $r = curl.exe -s -w "`n%{http_code}" -X POST "$BASE_URL/tasks" -H "Content-Type: application/json" -d '{"title":""}' 2>$null
    Check "04" "400" ($r -split "`n")[-1].Trim() | Out-Null

    # 05 - GET /tasks com 1 item
    $r = curl.exe -s -w "`n%{http_code}" "$BASE_URL/tasks" 2>$null
    Check "05" "200" ($r -split "`n")[-1].Trim() | Out-Null

    # 06 - GET /tasks/{id} existente
    $r = curl.exe -s -w "`n%{http_code}" "$BASE_URL/tasks/$TASK_ID" 2>$null
    Check "06" "200" ($r -split "`n")[-1].Trim() | Out-Null

    # 07 - GET /tasks/id-invalido
    $r = curl.exe -s -w "`n%{http_code}" "$BASE_URL/tasks/id-invalido-xyz" 2>$null
    Check "07" "404" ($r -split "`n")[-1].Trim() | Out-Null

    # 08 - PUT /tasks/{id} atualiza
    $r = curl.exe -s -w "`n%{http_code}" -X PUT "$BASE_URL/tasks/$TASK_ID" -H "Content-Type: application/json" -d '{"title":"Updated","completed":true}' 2>$null
    Check "08" "200" ($r -split "`n")[-1].Trim() | Out-Null

    # 09 - PUT /tasks/id-invalido
    $r = curl.exe -s -w "`n%{http_code}" -X PUT "$BASE_URL/tasks/id-invalido-xyz" -H "Content-Type: application/json" -d '{"title":"X"}' 2>$null
    Check "09" "404" ($r -split "`n")[-1].Trim() | Out-Null

    # 10 - DELETE /tasks/{id}
    $r = curl.exe -s -w "`n%{http_code}" -X DELETE "$BASE_URL/tasks/$TASK_ID" 2>$null
    Check "10" "204" ($r -split "`n")[-1].Trim() | Out-Null

    # 11 - DELETE /tasks/id-invalido
    $r = curl.exe -s -w "`n%{http_code}" -X DELETE "$BASE_URL/tasks/id-invalido-xyz" 2>$null
    Check "11" "404" ($r -split "`n")[-1].Trim() | Out-Null

    # 12 - GET tarefa deletada
    $r = curl.exe -s -w "`n%{http_code}" "$BASE_URL/tasks/$TASK_ID" 2>$null
    Check "12" "404" ($r -split "`n")[-1].Trim() | Out-Null

    return @{ Passed = $passed; Failed = 12 - $passed; Failures = $failures }
}

function Get-Coverage {
    param([string]$ImplDir)
    $csv = Join-Path $ImplDir "target\site\jacoco\jacoco.csv"
    if (-not (Test-Path $csv)) { return @{ Line = 0.0; Branch = 0.0 } }
    $data = Import-Csv $csv
    $covered = ($data | Measure-Object -Property LINE_COVERED -Sum).Sum
    $missed  = ($data | Measure-Object -Property LINE_MISSED  -Sum).Sum
    $total   = $covered + $missed
    $linePct = if ($total -gt 0) { [math]::Round($covered / $total * 100, 1) } else { 0.0 }

    $bcovered = ($data | Measure-Object -Property BRANCH_COVERED -Sum).Sum
    $bmissed  = ($data | Measure-Object -Property BRANCH_MISSED  -Sum).Sum
    $btotal   = $bcovered + $bmissed
    $branchPct = if ($btotal -gt 0) { [math]::Round($bcovered / $btotal * 100, 1) } else { 0.0 }

    return @{ Line = $linePct; Branch = $branchPct }
}

function Get-LOC {
    param([string]$ImplDir)
    $mainSrc = Join-Path $ImplDir "src\main\java"
    $testSrc = Join-Path $ImplDir "src\test\java"
    $mainLoc = (Get-ChildItem -Path $mainSrc -Filter "*.java" -Recurse -ErrorAction SilentlyContinue |
                Get-Content | Where-Object { $_.Trim() -ne "" -and $_ -notmatch "^\s*//" }).Count
    $testLoc = (Get-ChildItem -Path $testSrc -Filter "*.java" -Recurse -ErrorAction SilentlyContinue |
                Get-Content | Where-Object { $_.Trim() -ne "" -and $_ -notmatch "^\s*//" }).Count
    return @{ Main = $mainLoc; Test = $testLoc }
}

function Update-ResultJson {
    param($JsonPath, $E2E, $Coverage, $LOC, $CompileErrors, $TestSuccess, $TotalTurns)
    if (-not (Test-Path $JsonPath)) { return }
    $json = Get-Content $JsonPath -Raw | ConvertFrom-Json
    $json.e2e.passed          = $E2E.Passed
    $json.e2e.failed          = $E2E.Failed
    $json.e2e.failure_details = $E2E.Failures
    $json.code_quality.lines_of_code          = $LOC.Main
    $json.code_quality.test_lines_of_code     = $LOC.Test
    $json.code_quality.test_coverage_line_pct   = $Coverage.Line
    $json.code_quality.test_coverage_branch_pct = $Coverage.Branch
    $json.errors.compile_errors = $CompileErrors
    $json.errors.test_failures  = if ($TestSuccess) { 0 } else { 1 }
    $json.iterations.total_turns = $TotalTurns
    $json | ConvertTo-Json -Depth 10 | Out-File -FilePath $JsonPath -Encoding utf8
    Log "  JSON atualizado: $JsonPath" "DarkGray"
}

# =====================================================================
# SELECAO
# =====================================================================

if ($Model -eq "") {
    Write-Host ""
    Write-Host "=== EXPERIMENTO 3 - Ollama + Aider ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Escolha o modelo:" -ForegroundColor Yellow
    foreach ($k in $MODELS.Keys) { Write-Host "  $k. $($MODELS[$k].Label)" }
    Write-Host ""
    $Model = Read-Host "Numero"
}
if ($MODELS.Contains($Model)) {
    $MODEL_NAME = $MODELS[$Model].Name; $MODEL_DIR = $MODELS[$Model].Dir
} else {
    $match = $MODELS.Values | Where-Object { $_.Name -like "*$Model*" -or $_.Dir -like "*$Model*" } | Select-Object -First 1
    if ($null -eq $match) { Write-Host "Modelo invalido." -ForegroundColor Red; exit 1 }
    $MODEL_NAME = $match.Name; $MODEL_DIR = $match.Dir
}

if ($Arch -eq "") {
    Write-Host ""
    Write-Host "Escolha a arquitetura:" -ForegroundColor Yellow
    foreach ($k in $ARCHS.Keys) { Write-Host "  $k. $($ARCHS[$k].Name)" }
    Write-Host ""
    $Arch = Read-Host "Numero"
}
if ($ARCHS.Contains($Arch)) {
    $ARCH_NAME = $ARCHS[$Arch].Name; $GUIDE_SLUG = $ARCHS[$Arch].Dir
} else {
    $match = $ARCHS.Values | Where-Object { $_.Name -eq $Arch -or $_.Dir -eq $Arch -or $_.Name -like "*$Arch*" } | Select-Object -First 1
    if ($null -eq $match) { Write-Host "Arquitetura invalida." -ForegroundColor Red; exit 1 }
    $ARCH_NAME = $match.Name; $GUIDE_SLUG = $match.Dir
}

$IMPL_DIR = "$BASE_DIR\experiments\exp-03-ollama-local-models\implementations\$MODEL_DIR\$ARCH_NAME"
$GUIDE    = "$BASE_DIR\experiments\exp-03-ollama-local-models\guides\benchmark-$GUIDE_SLUG.md"
$TASK_DEF = "$BASE_DIR\shared\task-definition.md"

Write-Host ""
Write-Host "-----------------------------------------------------" -ForegroundColor DarkGray
Write-Host " Modelo : $MODEL_NAME" -ForegroundColor Green
Write-Host " Arch   : $ARCH_NAME" -ForegroundColor Green
Write-Host " Dir    : $IMPL_DIR" -ForegroundColor DarkGray
Write-Host "-----------------------------------------------------" -ForegroundColor DarkGray
Write-Host ""

# =====================================================================
# PASSO 1 - Metricas inicio
# =====================================================================

Log "[1/6] Iniciando coletor de metricas..." "Cyan"
Set-Location $BASE_DIR
python tools/ollama_collector.py --start --model $MODEL_NAME --arch $ARCH_NAME

# =====================================================================
# PASSO 2 - Criar stubs
# =====================================================================

Log "[2/6] Criando estrutura de arquivos stub..." "Cyan"
$stubFiles = New-Stubs -ImplDir $IMPL_DIR -ArchName $ARCH_NAME
$fileArgs = $stubFiles | Where-Object { Test-Path $_ } | ForEach-Object { @("--file", $_) }

# =====================================================================
# PASSO 3 - Aider implementa + loop compile
# =====================================================================

Set-Location $IMPL_DIR

$attempt       = 0
$buildSuccess  = $false
$totalTurns    = 0
$compileErrors = 0

$INIT_MSG = "Implement the complete Task Manager REST API in the $ARCH_NAME architecture. The source files are already created — implement each one fully following benchmark-$GUIDE_SLUG.md Step 4. Mandatory package structure, all 5 endpoints (GET /tasks 200, POST /tasks 201, GET /tasks/{id} 200/404, PUT /tasks/{id} 200/400/404, DELETE /tasks/{id} 204/404), all validations (empty title=400, title>200chars=400, description>1000chars=400, unknown id=404 body:{error:Task not found}). Use UUID for IDs. Store in ConcurrentHashMap. Do not leave files empty."

Log "[3/6] Aider implementando $ARCH_NAME..." "Cyan"

while ($attempt -lt $MaxRetries -and -not $buildSuccess) {
    if ($attempt -eq 0) {
        $msg = $INIT_MSG
    } else {
        $errorLines = ($lastBuildOutput | Where-Object { $_ -match "\[ERROR\]" } | Select-Object -First 20) -join "`n"
        $msg = "Fix ALL compilation errors so the project compiles successfully:`n`n$errorLines"
        Log "  Tentativa $($attempt+1)/$MaxRetries — corrigindo erros..." "Yellow"
        $compileErrors++
    }

    & aider --model "ollama/$MODEL_NAME" `
            --read $TASK_DEF `
            --read $GUIDE `
            @fileArgs `
            --message $msg `
            --yes `
            --no-auto-commits

    $totalTurns++

    Log "  Compilando..." "DarkGray"
    $lastBuildOutput = & ".\mvnw.cmd" compile 2>&1

    if ($lastBuildOutput -match "BUILD SUCCESS") {
        $buildSuccess = $true
        Log "  BUILD SUCCESS na tentativa $($attempt+1)." "Green"
    } else {
        Log "  BUILD FAILURE na tentativa $($attempt+1)." "Red"
        $attempt++
    }
}

# =====================================================================
# PASSO 4 - Testes unitarios
# =====================================================================

Log "[4/6] Rodando testes unitarios..." "Cyan"
$testSuccess = $false
if ($buildSuccess) {
    $testOutput = & ".\mvnw.cmd" test 2>&1
    if ($testOutput -match "BUILD SUCCESS") {
        $testSuccess = $true
        $summary = ($testOutput | Select-String "Tests run:" | Select-Object -Last 1).ToString()
        Log "  OK - $summary" "Green"
    } else {
        Log "  FALHA nos testes." "Red"
    }
}

# =====================================================================
# PASSO 5 - E2E
# =====================================================================

Log "[5/6] Testes E2E..." "Cyan"
$e2eResult = @{ Passed = 0; Failed = 12; Failures = @() }
$appProcess = $null

if ($buildSuccess) {
    Log "  Subindo aplicacao Spring Boot..." "DarkGray"
    $appProcess = Start-Process -NoNewWindow -PassThru -FilePath ".\mvnw.cmd" -ArgumentList "spring-boot:run"
    $appReady = Wait-ForApp

    if ($appReady) {
        $e2eResult = Run-E2E
        Log "  E2E: $($e2eResult.Passed)/12 passaram." $(if ($e2eResult.Passed -eq 12) { "Green" } else { "Yellow" })
    } else {
        Log "  App nao subiu — E2E pulado." "Red"
    }

    Stop-Process -Name "java" -Force -ErrorAction SilentlyContinue
    if ($appProcess -and -not $appProcess.HasExited) {
        Stop-Process -Id $appProcess.Id -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 3
}

# =====================================================================
# PASSO 6 - Metricas finais + atualizar JSON
# =====================================================================

Log "[6/6] Coletando metricas e atualizando JSON..." "Cyan"

$coverage = Get-Coverage -ImplDir $IMPL_DIR
$loc      = Get-LOC -ImplDir $IMPL_DIR

Set-Location $BASE_DIR
python tools/ollama_collector.py --collect --model $MODEL_NAME --arch $ARCH_NAME --impl-dir $IMPL_DIR

# Encontrar o JSON gerado e atualizar com todos os resultados
$jsonFile = Get-ChildItem "experiments\exp-03-ollama-local-models\results" |
            Where-Object { $_.Name -like "ollama_*${MODEL_DIR}*_${ARCH_NAME}_*.json" -or $_.Name -like "ollama_*$($MODEL_NAME.Replace(':','-').Replace('/','-'))_${ARCH_NAME}_*.json" } |
            Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($jsonFile) {
    Update-ResultJson -JsonPath $jsonFile.FullName `
                      -E2E $e2eResult `
                      -Coverage $coverage `
                      -LOC $loc `
                      -CompileErrors $compileErrors `
                      -TestSuccess $testSuccess `
                      -TotalTurns $totalTurns
}

# =====================================================================
# RESUMO
# =====================================================================

$javaCount = (Get-ChildItem -Path $IMPL_DIR -Filter "*.java" -Recurse -ErrorAction SilentlyContinue).Count

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host " RESULTADO FINAL: $MODEL_NAME / $ARCH_NAME" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host " Arquivos Java  : $javaCount" -ForegroundColor White
Write-Host " Build          : $(if ($buildSuccess) { "SUCCESS" } else { "FAILURE" })" -ForegroundColor $(if ($buildSuccess) { "Green" } else { "Red" })
Write-Host " Testes         : $(if ($testSuccess)  { "SUCCESS" } else { "FAILURE" })" -ForegroundColor $(if ($testSuccess)  { "Green" } else { "Red" })
Write-Host " E2E            : $($e2eResult.Passed)/12" -ForegroundColor $(if ($e2eResult.Passed -eq 12) { "Green" } else { "Yellow" })
Write-Host " LOC (main)     : $($loc.Main)" -ForegroundColor White
Write-Host " Cobertura      : $($coverage.Line)% linha / $($coverage.Branch)% branch" -ForegroundColor White
Write-Host " Tentativas     : $totalTurns (erros compile: $compileErrors)" -ForegroundColor White
if ($jsonFile) {
    Write-Host " JSON           : $($jsonFile.Name)" -ForegroundColor DarkGray
}
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Preencha manualmente no JSON: tokens_per_sec, arch_conformance" -ForegroundColor Yellow
Write-Host ""
