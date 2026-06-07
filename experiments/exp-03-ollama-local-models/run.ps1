# run.ps1 - Configura o ambiente e abre o Aider para o benchmark
# Uso: .\run.ps1                    (menu interativo)
#      .\run.ps1 -Model 2 -Arch 3   (parametros diretos)

param(
    [string]$Model = "",
    [string]$Arch  = ""
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
    Write-Host "=== EXPERIMENTO 3 - Ollama + Aider ===" -ForegroundColor Cyan
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
Write-Host "[1/3] Iniciando coletor de metricas..." -ForegroundColor Cyan
Set-Location $BASE_DIR
python tools/ollama_collector.py --start --model $MODEL_NAME --arch $ARCH_NAME

# --- Abrir Aider ---

Write-Host ""
Write-Host "[2/3] Abrindo Aider..." -ForegroundColor Cyan
Write-Host ""
Write-Host "  Mensagem para comecar no Aider:" -ForegroundColor Yellow
Write-Host "  Execute o Passo 4 do benchmark-$GUIDE_SLUG.md e implemente a Task Manager API em $ARCH_NAME." -ForegroundColor White
Write-Host ""
Write-Host "  Para fechar: /exit" -ForegroundColor DarkGray
Write-Host ""

Set-Location $IMPL_DIR

aider --model "ollama/$MODEL_NAME" `
      --read $TASK_DEF `
      --read $GUIDE `
      --no-auto-commits

# --- Coletar metricas ao fechar ---

Write-Host ""
Write-Host "[3/3] Coletando metricas finais..." -ForegroundColor Cyan
Set-Location $BASE_DIR
python tools/ollama_collector.py --collect --model $MODEL_NAME --arch $ARCH_NAME --impl-dir $IMPL_DIR

Write-Host ""
Write-Host "Pronto! Resultados em: experiments/exp-03-ollama-local-models/results/" -ForegroundColor Green
