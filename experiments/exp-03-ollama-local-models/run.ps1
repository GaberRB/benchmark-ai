# run.ps1 - Configura o ambiente e roda o Aider em auto mode
# Uso: .\run.ps1                    (menu interativo)
#      .\run.ps1 -Model 2 -Arch 3   (parametros diretos)

param(
    [string]$Model = "",
    [string]$Arch  = "",
    [int]$MaxRetries = 5
)

$BASE_DIR = "C:\Users\grios\OneDrive\Desktop\benchmark"

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

# --- Loop: Aider auto mode + compile + corrigir erros ---

Set-Location $IMPL_DIR

$attempt      = 0
$buildSuccess = $false
$totalTurns   = 0
$compileErrors = 0

$INIT_MSG = "Read benchmark-$GUIDE_SLUG.md carefully. Implement the complete Task Manager REST API following Step 4 exactly: create all required packages and Java files, implement all 5 endpoints (GET /tasks, POST /tasks returning 201, GET /tasks/{id}, PUT /tasks/{id}, DELETE /tasks/{id} returning 204), apply all validations (title required 400, title max 200 chars, description max 1000 chars, ID not found 404). Follow the mandatory package structure shown in the guide."

Write-Host ""
Write-Host "[2/4] Aider implementando $ARCH_NAME (auto mode)..." -ForegroundColor Cyan

while ($attempt -lt $MaxRetries -and -not $buildSuccess) {

    if ($attempt -eq 0) {
        $msg = $INIT_MSG
    } else {
        $errorLines = ($lastBuildOutput | Where-Object { $_ -match "\[ERROR\]" } | Select-Object -First 20) -join "`n"
        $msg = "Fix these compilation errors:`n$errorLines"
        Write-Host "  Tentativa $($attempt+1): enviando erros para correcao..." -ForegroundColor Yellow
        $compileErrors++
    }

    aider --model "ollama/$MODEL_NAME" `
          --read $TASK_DEF `
          --read $GUIDE `
          --message $msg `
          --yes `
          --no-auto-commits

    $totalTurns++

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

Write-Host ""
Write-Host "[3/4] Rodando testes..." -ForegroundColor Cyan

$testSuccess = $false
if ($buildSuccess) {
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

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host " RESULTADO: $MODEL_NAME / $ARCH_NAME" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host " Build     : $(if ($buildSuccess) { 'SUCCESS' } else { 'FAILURE' })" -ForegroundColor $(if ($buildSuccess) { "Green" } else { "Red" })
Write-Host " Testes    : $(if ($testSuccess)  { 'SUCCESS' } else { 'FAILURE' })" -ForegroundColor $(if ($testSuccess)  { "Green" } else { "Red" })
Write-Host " Tentativas: $totalTurns (erros de compile: $compileErrors)" -ForegroundColor White
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Resultados em: experiments/exp-03-ollama-local-models/results/" -ForegroundColor Green
Write-Host "Preencha manualmente no JSON: tokens_per_sec, arch_conformance, e2e" -ForegroundColor Yellow
Write-Host ""
