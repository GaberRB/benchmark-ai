# run.ps1 - Benchmark completo Ollama + Aider
# O modelo LLM cria todos os diretorios e arquivos Java do zero.
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

# =====================================================================
# FUNCOES
# =====================================================================

function Log($msg, $color = "White") {
    $ts = Get-Date -Format "HH:mm:ss"
    Write-Host "[$ts] $msg" -ForegroundColor $color
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

    function Check($num, $expected, $code) {
        if ($code -eq $expected) {
            $script:passed++
            Log "  E2E-$num [PASS] $code" "Green"
        } else {
            $script:failures += "E2E-$num esperado=$expected obteve=$code"
            Log "  E2E-$num [FAIL] $code (esperado $expected)" "Red"
        }
    }

    $r = curl.exe -s -w "`n%{http_code}" "$BASE_URL/tasks" 2>$null
    Check "01" "200" ($r -split "`n")[-1].Trim()

    $r = curl.exe -s -w "`n%{http_code}" -X POST "$BASE_URL/tasks" -H "Content-Type: application/json" -d '{"title":"Test Task","description":"Desc"}' 2>$null
    $parts = $r -split "`n"
    Check "02" "201" $parts[-1].Trim()
    $TASK_ID = try { ($parts[0] | ConvertFrom-Json).id } catch { "unknown" }

    $r = curl.exe -s -w "`n%{http_code}" -X POST "$BASE_URL/tasks" -H "Content-Type: application/json" -d '{}' 2>$null
    Check "03" "400" ($r -split "`n")[-1].Trim()

    $r = curl.exe -s -w "`n%{http_code}" -X POST "$BASE_URL/tasks" -H "Content-Type: application/json" -d '{"title":""}' 2>$null
    Check "04" "400" ($r -split "`n")[-1].Trim()

    $r = curl.exe -s -w "`n%{http_code}" "$BASE_URL/tasks" 2>$null
    Check "05" "200" ($r -split "`n")[-1].Trim()

    $r = curl.exe -s -w "`n%{http_code}" "$BASE_URL/tasks/$TASK_ID" 2>$null
    Check "06" "200" ($r -split "`n")[-1].Trim()

    $r = curl.exe -s -w "`n%{http_code}" "$BASE_URL/tasks/id-invalido-xyz" 2>$null
    Check "07" "404" ($r -split "`n")[-1].Trim()

    $r = curl.exe -s -w "`n%{http_code}" -X PUT "$BASE_URL/tasks/$TASK_ID" -H "Content-Type: application/json" -d '{"title":"Updated","completed":true}' 2>$null
    Check "08" "200" ($r -split "`n")[-1].Trim()

    $r = curl.exe -s -w "`n%{http_code}" -X PUT "$BASE_URL/tasks/id-invalido-xyz" -H "Content-Type: application/json" -d '{"title":"X"}' 2>$null
    Check "09" "404" ($r -split "`n")[-1].Trim()

    $r = curl.exe -s -w "`n%{http_code}" -X DELETE "$BASE_URL/tasks/$TASK_ID" 2>$null
    Check "10" "204" ($r -split "`n")[-1].Trim()

    $r = curl.exe -s -w "`n%{http_code}" -X DELETE "$BASE_URL/tasks/id-invalido-xyz" 2>$null
    Check "11" "404" ($r -split "`n")[-1].Trim()

    $r = curl.exe -s -w "`n%{http_code}" "$BASE_URL/tasks/$TASK_ID" 2>$null
    Check "12" "404" ($r -split "`n")[-1].Trim()

    return @{ Passed = $passed; Failed = 12 - $passed; Failures = $failures }
}

function Get-Coverage {
    param([string]$ImplDir)
    $csv = Join-Path $ImplDir "target\site\jacoco\jacoco.csv"
    if (-not (Test-Path $csv)) { return @{ Line = 0.0; Branch = 0.0 } }
    $data = Import-Csv $csv
    $lc = ($data | Measure-Object -Property LINE_COVERED -Sum).Sum
    $lm = ($data | Measure-Object -Property LINE_MISSED  -Sum).Sum
    $bc = ($data | Measure-Object -Property BRANCH_COVERED -Sum).Sum
    $bm = ($data | Measure-Object -Property BRANCH_MISSED  -Sum).Sum
    return @{
        Line   = if (($lc+$lm) -gt 0) { [math]::Round($lc/($lc+$lm)*100,1) } else { 0.0 }
        Branch = if (($bc+$bm) -gt 0) { [math]::Round($bc/($bc+$bm)*100,1) } else { 0.0 }
    }
}

function Get-LOC {
    param([string]$ImplDir)
    $count = { param($path)
        (Get-ChildItem -Path $path -Filter "*.java" -Recurse -ErrorAction SilentlyContinue |
         Get-Content -ErrorAction SilentlyContinue |
         Where-Object { $_.Trim() -ne "" -and $_ -notmatch "^\s*//" }).Count
    }
    return @{
        Main = (& $count (Join-Path $ImplDir "src\main\java"))
        Test = (& $count (Join-Path $ImplDir "src\test\java"))
    }
}

function Update-ResultJson {
    param($JsonPath, $E2E, $Coverage, $LOC, $CompileErrors, $TestSuccess, $TotalTurns)
    if (-not (Test-Path $JsonPath)) { return }
    $json = Get-Content $JsonPath -Raw | ConvertFrom-Json
    $json.e2e.passed            = $E2E.Passed
    $json.e2e.failed            = $E2E.Failed
    $json.e2e.failure_details   = $E2E.Failures
    $json.code_quality.lines_of_code            = $LOC.Main
    $json.code_quality.test_lines_of_code       = $LOC.Test
    $json.code_quality.test_coverage_line_pct   = $Coverage.Line
    $json.code_quality.test_coverage_branch_pct = $Coverage.Branch
    $json.errors.compile_errors  = $CompileErrors
    $json.errors.test_failures   = if ($TestSuccess) { 0 } else { 1 }
    $json.iterations.total_turns = $TotalTurns
    $json | ConvertTo-Json -Depth 10 | Out-File -FilePath $JsonPath -Encoding utf8
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
# PASSO 2 - Aider cria tudo do zero (sem pre-criacao de arquivos/dirs)
# =====================================================================

Set-Location $IMPL_DIR

$attempt       = 0
$buildSuccess  = $false
$totalTurns    = 0
$compileErrors = 0

# Instrucao inicial: o modelo cria TUDO — diretorios e arquivos
$INIT_MSG = "Read benchmark-$GUIDE_SLUG.md and task-definition.md. Implement the complete Task Manager REST API from scratch in $ARCH_NAME architecture. Create ALL directories and Java source files as specified in Step 4 of the guide. The only files that exist are pom.xml and mvnw.cmd. You must create: the full src/main/java/com/benchmark/taskmanager/ package tree, all Java classes, and src/test/java tests. Requirements: Spring Boot 3.2, Java 21, all 5 endpoints (GET /tasks 200, POST /tasks 201, GET /tasks/{id} 200/404, PUT /tasks/{id} 200/400/404, DELETE /tasks/{id} 204/404), validations (missing/empty title=400 body:{error:title is required}, title>200chars=400, description>1000chars=400, unknown id=404 body:{error:Task not found}), UUID for IDs, ConcurrentHashMap. Follow the mandatory package structure exactly."

Log "[2/6] Aider criando projeto $ARCH_NAME do zero..." "Cyan"
Log "  O modelo cria todos os diretorios e arquivos Java." "DarkGray"

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
            --message $msg `
            --yes `
            --no-auto-commits

    $totalTurns++

    $javaCount = (Get-ChildItem -Path $IMPL_DIR -Filter "*.java" -Recurse -ErrorAction SilentlyContinue).Count

    if ($javaCount -eq 0 -and $attempt -eq 0) {
        Log "" "White"
        Log "  RESULTADO: nenhum arquivo Java criado." "Red"
        Log "  O modelo nao gerou codigo neste run — registrado como FAILURE." "Red"
        Log "  Isso e um resultado valido do benchmark." "Yellow"
        break
    }

    Log "  Compilando ($javaCount arquivos Java encontrados)..." "DarkGray"
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
# PASSO 3 - Testes unitarios
# =====================================================================

Log "[3/6] Testes unitarios..." "Cyan"
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
# PASSO 4 - E2E
# =====================================================================

Log "[4/6] Testes E2E (12 cenarios)..." "Cyan"
$e2eResult = @{ Passed = 0; Failed = 12; Failures = @() }
$appProcess = $null

if ($buildSuccess) {
    Log "  Subindo Spring Boot..." "DarkGray"
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
# PASSO 5 - LOC e cobertura
# =====================================================================

Log "[5/6] Calculando LOC e cobertura..." "Cyan"
$coverage = Get-Coverage -ImplDir $IMPL_DIR
$loc      = Get-LOC -ImplDir $IMPL_DIR
Log "  LOC main=$($loc.Main) test=$($loc.Test) | Cobertura linha=$($coverage.Line)% branch=$($coverage.Branch)%" "DarkGray"

# =====================================================================
# PASSO 6 - Metricas finais + JSON
# =====================================================================

Log "[6/6] Coletando metricas finais..." "Cyan"
Set-Location $BASE_DIR
python tools/ollama_collector.py --collect --model $MODEL_NAME --arch $ARCH_NAME --impl-dir $IMPL_DIR

$jsonFile = Get-ChildItem "experiments\exp-03-ollama-local-models\results" -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -like "ollama_*${ARCH_NAME}*.json" } |
            Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($jsonFile) {
    Update-ResultJson -JsonPath $jsonFile.FullName `
                      -E2E $e2eResult -Coverage $coverage -LOC $loc `
                      -CompileErrors $compileErrors -TestSuccess $testSuccess -TotalTurns $totalTurns
    Log "  JSON atualizado: $($jsonFile.Name)" "DarkGray"
}

# =====================================================================
# RESUMO
# =====================================================================

$javaCount = (Get-ChildItem -Path $IMPL_DIR -Filter "*.java" -Recurse -ErrorAction SilentlyContinue).Count

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host " RESULTADO: $MODEL_NAME / $ARCH_NAME" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host " Arquivos Java  : $javaCount" -ForegroundColor White
Write-Host " Build          : $(if ($buildSuccess) { "SUCCESS" } else { "FAILURE" })" -ForegroundColor $(if ($buildSuccess) { "Green" } else { "Red" })
Write-Host " Testes         : $(if ($testSuccess)  { "SUCCESS" } else { "FAILURE" })" -ForegroundColor $(if ($testSuccess)  { "Green" } else { "Red" })
Write-Host " E2E            : $($e2eResult.Passed)/12" -ForegroundColor $(if ($e2eResult.Passed -eq 12) { "Green" } else { "Yellow" })
Write-Host " LOC (main)     : $($loc.Main)" -ForegroundColor White
Write-Host " Cobertura      : $($coverage.Line)% linha / $($coverage.Branch)% branch" -ForegroundColor White
Write-Host " Tentativas     : $totalTurns (erros compile: $compileErrors)" -ForegroundColor White
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Preencha no JSON: tokens_per_sec, arch_conformance" -ForegroundColor Yellow
Write-Host ""
