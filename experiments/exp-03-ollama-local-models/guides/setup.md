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

```powershell
pip install aider-chat
aider --version    # Verificar instalação
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

Cada combinação modelo/arquitetura precisa de um projeto Maven. Copie o `pom.xml` da arquitetura equivalente do Exp-02:

```powershell
# Exemplo: copiar pom.xml do MVC para deepseek-coder/mvc
$base = "C:\Users\grios\OneDrive\Desktop\benchmark"
Copy-Item "$base\experiments\exp-02-arch-patterns\mvc\pom.xml" `
          "$base\experiments\exp-03-ollama-local-models\implementations\deepseek-coder\mvc\pom.xml"
```

> Repita para cada par (modelo, arquitetura) que for executar.

---

## 5. Instalar o Maven Wrapper

Se o `pom.xml` não incluir o Maven Wrapper (`mvnw.cmd`), copie do Exp-02:

```powershell
Copy-Item "$base\experiments\exp-02-arch-patterns\mvc\mvnw.cmd" `
          "$base\experiments\exp-03-ollama-local-models\implementations\deepseek-coder\mvc\mvnw.cmd"
```

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

## 8. (Opcional) Instalar psutil para Coleta de RAM

O `tools/ollama_collector.py` usa `psutil` para medir uso de RAM durante a sessão:

```powershell
pip install psutil
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
