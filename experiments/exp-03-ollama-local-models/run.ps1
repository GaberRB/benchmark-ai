# run.ps1 - Benchmark Ollama + Aider (auto mode com stub files)
# Uso: .\run.ps1                    (menu interativo)
#      .\run.ps1 -Model 2 -Arch 3   (parametros diretos)

param(
    [string]$Model = "",
    [string]$Arch  = "",
    [int]$MaxRetries = 5
)

$BASE_DIR = "C:\Users\grios\OneDrive\Desktop\benchmark"
$PKG_BASE = "src\main\java\com\benchmark\taskmanager"
$PKG_DECL = "com.benchmark.taskmanager"

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
    "7" = @{ Name = "cqrs";               Dir = "cqrs" }
}

# --- Funcao: criar stub files por arquitetura ---
function New-Stubs {
    param([string]$ImplDir, [string]$ArchName)

    $pkg = $PKG_BASE
    $root = Join-Path $ImplDir $pkg

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

    $created = @()
    foreach ($rel in $files) {
        $full = Join-Path $ImplDir $rel
        $dir  = Split-Path $full -Parent
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
        if (-not (Test-Path $full)) {
            "" | Out-File -FilePath $full -Encoding utf8
            $created += $full
        }
    }

    # Tambem criar src/test/java/com/benchmark/taskmanager/
    $testRoot = Join-Path $ImplDir "src\test\java\com\benchmark\taskmanager"
    New-Item -ItemType Directory -Force -Path $testRoot | Out-Null
    $testFile = Join-Path $testRoot "TaskManagerApplicationTests.java"
    if (-not (Test-Path $testFile)) {
        "" | Out-File -FilePath $testFile -Encoding utf8
        $created += $testFile
    }

    Write-Host "  $($created.Count) stub files criados." -ForegroundColor DarkGray
    return $files | ForEach-Object { Join-Path $ImplDir $_ }
}

# --- Selecionar modelo ---

if ($Model -eq "") {
    Write-Host ""
    Write-Host "=== EXPERIMENTO 3 - Ollama + Aider (auto mode) ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Escolha o modelo:" -ForegroundColor Yellow
    foreach ($k in $MODELS.Keys) { Write-Host "  $k. $($MODELS[$k].Label)" }
    Write-Host ""
    $Model = Read-Host "Numero"
}

if ($MODELS.Contains($Model)) {
    $MODEL_NAME = $MODELS[$Model].Name
    $MODEL_DIR  = $MODELS[$Model].Dir
} else {
    $match = $MODELS.Values | Where-Object { $_.Name -like "*$Model*" -or $_.Dir -like "*$Model*" } | Select-Object -First 1
    if ($null -eq $match) { Write-Host "Modelo invalido: $Model" -ForegroundColor Red; exit 1 }
    $MODEL_NAME = $match.Name; $MODEL_DIR = $match.Dir
}

# --- Selecionar arquitetura ---

if ($Arch -eq "") {
    Write-Host ""
    Write-Host "Escolha a arquitetura:" -ForegroundColor Yellow
    foreach ($k in $ARCHS.Keys) { Write-Host "  $k. $($ARCHS[$k].Name)" }
    Write-Host ""
    $Arch = Read-Host "Numero"
}

if ($ARCHS.Contains($Arch)) {
    $ARCH_NAME  = $ARCHS[$Arch].Name
    $GUIDE_SLUG = $ARCHS[$Arch].Dir
} else {
    $match = $ARCHS.Values | Where-Object { $_.Name -eq $Arch -or $_.Dir -eq $Arch -or $_.Name -like "*$Arch*" } | Select-Object -First 1
    if ($null -eq $match) { Write-Host "Arquitetura invalida: $Arch" -ForegroundColor Red; exit 1 }
    $ARCH_NAME = $match.Name; $GUIDE_SLUG = $match.Dir
}

# --- Caminhos ---

$IMPL_DIR = "$BASE_DIR\experiments\exp-03-ollama-local-models\implementations\$MODEL_DIR\$ARCH_NAME"
$GUIDE    = "$BASE_DIR\experiments\exp-03-ollama-local-models\guides\benchmark-$GUIDE_SLUG.md"
$TASK_DEF = "$BASE_DIR\shared\task-definition.md"

Write-Host ""
Write-Host "-----------------------------------------------------" -ForegroundColor DarkGray
Write-Host " Modelo : $MODEL_NAME" -ForegroundColor Green
Write-Host " Arch   : $ARCH_NAME" -ForegroundColor Green
Write-Host " Dir    : $IMPL_DIR" -ForegroundColor DarkGray
Write-Host "-----------------------------------------------------" -ForegroundColor DarkGray

# --- Iniciar coleta de metricas ---

Write-Host ""
Write-Host "[1/4] Iniciando coletor de metricas..." -ForegroundColor Cyan
Set-Location $BASE_DIR
python tools/ollama_collector.py --start --model $MODEL_NAME --arch $ARCH_NAME

# --- Criar stub files ---

Write-Host ""
Write-Host "[2/4] Criando estrutura de arquivos..." -ForegroundColor Cyan
$stubFiles = New-Stubs -ImplDir $IMPL_DIR -ArchName $ARCH_NAME

# Montar argumentos --file para o Aider
$fileArgs = $stubFiles | Where-Object { Test-Path $_ } | ForEach-Object { @("--file", $_) }

# --- Loop: Aider implementa + compile + corrige ---

Set-Location $IMPL_DIR

$attempt       = 0
$buildSuccess  = $false
$totalTurns    = 0
$compileErrors = 0

$INIT_MSG = "Implement the complete Task Manager REST API in the $ARCH_NAME architecture. All the source files are already created and listed above — implement each one fully. Follow benchmark-$GUIDE_SLUG.md Step 4 exactly: mandatory package structure, all 5 endpoints, all validations. Do not leave any file empty or with placeholder comments."

Write-Host ""
Write-Host "[3/4] Aider implementando $ARCH_NAME (auto mode)..." -ForegroundColor Cyan

while ($attempt -lt $MaxRetries -and -not $buildSuccess) {

    if ($attempt -eq 0) {
        $msg = $INIT_MSG
    } else {
        $errorLines = ($lastBuildOutput | Where-Object { $_ -match "\[ERROR\]" } | Select-Object -First 20) -join "`n"
        $msg = "Fix ALL compilation errors so the project builds successfully:`n`n$errorLines"
        Write-Host "  Tentativa $($attempt+1): corrigindo erros..." -ForegroundColor Yellow
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

    # Checar se os arquivos foram preenchidos (pelo menos o Application)
    $appFile = Join-Path $IMPL_DIR "$PKG_BASE\TaskManagerApplication.java"
    $appContent = if (Test-Path $appFile) { Get-Content $appFile -Raw } else { "" }
    if ($appContent.Trim().Length -lt 50 -and $attempt -eq 0) {
        Write-Host "  AVISO: arquivos ainda vazios apos primeira tentativa." -ForegroundColor Red
        Write-Host "  O modelo pode nao estar gerando codigo. Verifique o output do Aider." -ForegroundColor Yellow
    }

    Write-Host "  Compilando..." -ForegroundColor DarkGray
    $lastBuildOutput = & ".\mvnw.cmd" compile 2>&1

    if ($lastBuildOutput -match "BUILD SUCCESS") {
        $buildSuccess = $true
        Write-Host "  BUILD SUCCESS na tentativa $($attempt+1)." -ForegroundColor Green
    } else {
        Write-Host "  BUILD FAILURE na tentativa $($attempt+1)." -ForegroundColor Red
        $attempt++
    }
}

# --- Testes unitarios ---

$testSuccess = $false
if ($buildSuccess) {
    Write-Host "  Rodando testes..." -ForegroundColor DarkGray
    $testOutput = & ".\mvnw.cmd" test 2>&1
    if ($testOutput -match "BUILD SUCCESS") {
        $testSuccess = $true
        $summary = $testOutput | Select-String "Tests run:" | Select-Object -Last 1
        Write-Host "  TESTES OK - $summary" -ForegroundColor Green
    } else {
        Write-Host "  FALHA nos testes." -ForegroundColor Red
    }
}

# --- Coleta de metricas finais ---

Write-Host ""
Write-Host "[4/4] Coletando metricas finais..." -ForegroundColor Cyan
Set-Location $BASE_DIR
python tools/ollama_collector.py --collect --model $MODEL_NAME --arch $ARCH_NAME --impl-dir $IMPL_DIR

# --- Resumo ---

$javaCount = (Get-ChildItem -Path $IMPL_DIR -Filter "*.java" -Recurse -ErrorAction SilentlyContinue).Count

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host " RESULTADO: $MODEL_NAME / $ARCH_NAME" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host " Arquivos Java : $javaCount" -ForegroundColor White
Write-Host " Build         : $(if ($buildSuccess) { "SUCCESS" } else { "FAILURE" })" -ForegroundColor $(if ($buildSuccess) { "Green" } else { "Red" })
Write-Host " Testes        : $(if ($testSuccess)  { "SUCCESS" } else { "FAILURE" })" -ForegroundColor $(if ($testSuccess)  { "Green" } else { "Red" })
Write-Host " Tentativas    : $totalTurns (erros compile: $compileErrors)" -ForegroundColor White
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Resultados em: experiments/exp-03-ollama-local-models/results/" -ForegroundColor Green
Write-Host "Preencha no JSON: tokens_per_sec, arch_conformance, e2e (12 cenarios)" -ForegroundColor Yellow
Write-Host ""
