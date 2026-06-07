# Setup — Experimento 3 (Ollama + Aider)

> Siga estes passos uma única vez antes de executar qualquer benchmark deste experimento.

---

## 1. Verificar Pré-requisitos

```powershell
java -version      # Exigido: Java 21+
mvn -version       # Exigido: Maven 3.9+
python --version   # Exigido: Python 3.10+
ollama --version   # Exigido: Ollama instalado
```

Se o Ollama não estiver instalado: https://ollama.com/download

---

## 2. Instalar Aider

> **Atenção**: `pip install aider-chat` falha no Python 3.14+ (sem wheels para scipy).
> Use `uv` com Python 3.12:

```powershell
# Instalar uv (caso não esteja presente)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Instalar Aider via uv com Python 3.12
uv tool install aider-chat --python 3.12

aider --version    # Esperado: aider 0.86.x
```

---

## 3. Baixar os Modelos Ollama

Execute apenas os modelos que pretende testar. Cada modelo ocupa espaço em disco e RAM:

```powershell
# Modelo 1: Deepseek Coder V2 (melhor qualidade, ~10 GB RAM)
ollama pull deepseek-coder-v2:16b

# Modelo 2: Qwen 2.5 Coder (ótimo custo-benefício, ~5 GB RAM)
ollama pull qwen2.5-coder:7b

# Modelo 3: Code Llama (baseline Meta, ~8 GB RAM)
ollama pull codellama:13b

# Modelo 4: Llama 3.1 (modelo geral — controle, ~5 GB RAM)
ollama pull llama3.1:8b
```

Verificar modelos disponíveis:
```powershell
ollama list
```

---

## 4. Criar o pom.xml Base em Cada Pasta de Implementação

> **Já feito**: `pom.xml` e `mvnw.cmd` foram copiados para todas as 28 pastas durante o setup inicial.
> Caso precise recriar, use o script abaixo:

```powershell
$base   = "C:\Users\grios\OneDrive\Desktop\benchmark"
$models = @("deepseek-coder", "qwen2.5-coder", "codellama", "llama3.1")
$archs  = @("mvc", "vertical-slice", "clean-architecture", "hexagonal", "ddd", "event-driven", "cqrs")

foreach ($model in $models) {
    foreach ($arch in $archs) {
        $dest = "$base\experiments\exp-03-ollama-local-models\implementations\$model\$arch"
        Copy-Item "$base\experiments\exp-02-arch-patterns\mvc\pom.xml"  "$dest\pom.xml"  -Force
        Copy-Item "$base\experiments\exp-02-arch-patterns\mvc\mvnw.cmd" "$dest\mvnw.cmd" -Force
    }
}
```

---

## 5. Maven Wrapper (mvnw.cmd)

Já copiado junto com o `pom.xml` no passo anterior — nada a fazer.

---

## 6. Verificar Ollama Rodando

O Ollama precisa estar ativo como servidor local antes de cada sessão Aider:

```powershell
# Verificar se está respondendo
Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing | Select-Object StatusCode
# Esperado: StatusCode 200
```

Se não estiver rodando, inicie o aplicativo Ollama ou:
```powershell
ollama serve
```

---

## 7. Verificar Aider com Ollama

Teste rápido antes do primeiro benchmark:

```powershell
cd "$base\experiments\exp-03-ollama-local-models\implementations\deepseek-coder\mvc"
aider --model ollama/deepseek-coder-v2:16b --no-auto-commits --message "Olá, você está funcionando?"
# Esperado: o modelo responde normalmente
```

---

## 8. Instalar psutil para Coleta de RAM

O `tools/ollama_collector.py` usa `psutil` para medir uso de RAM durante a sessão:

```powershell
pip install psutil
python -c "import psutil; print('psutil', psutil.__version__, '| RAM:', round(psutil.virtual_memory().total/(1024**3),1), 'GB')"
```

Verificar hardware detectado:
```powershell
cd "C:\Users\grios\OneDrive\Desktop\benchmark"
python tools/ollama_collector.py --hardware
```

---

## Pronto!

Escolha uma arquitetura e um modelo e execute o guia correspondente:

```
experiments/exp-03-ollama-local-models/guides/benchmark-mvc.md
experiments/exp-03-ollama-local-models/guides/benchmark-clean.md
...
```

> **Dica**: comece pelo MVC com o modelo que pretende testar antes de partir para arquiteturas complexas.
