# Setup — Aider + OpenRouter

## 1. Instalar Aider

```powershell
uv tool install aider-chat
# ou
pip install aider-chat
```

Verificar versão esperada (≥ 0.86):

```powershell
aider --version
```

## 2. Configurar OpenRouter API Key

Crie um arquivo `.env` neste diretório (`exp-07-aider-benchmark/.env`) com:

```
OPENROUTER_API_KEY=sk-or-...
```

Ou copie do exp-06:

```powershell
Copy-Item ..\exp-06-agentic-benchmark\.env .\.env
```

> A chave também é aceita via variável de ambiente: `$env:OPENROUTER_API_KEY = "sk-or-..."`

## 3. Instalar dependências Python

```powershell
pip install -r requirements.txt
# ou
uv pip install -r requirements.txt
```

## 4. Verificar Maven disponível

```powershell
mvn --version
```

Esperado: Apache Maven 3.8+ com Java 21+.

## 5. Rodar o benchmark

```powershell
python main.py
```

O script:
1. Exibe tabela de modelos disponíveis
2. Você seleciona modelo + arquitetura
3. Copia o `pom.xml` de exp-06 para o diretório de implementação
4. Lança o Aider com `--auto-test` (Aider roda `mvn compile && mvn test` automaticamente após cada mudança)
5. Após o Aider terminar, roda verificação independente (build + tests + 12 E2E cenários)
6. Salva o resultado em `results/exp07_<modelo>_<arch>_<timestamp>.json`

## Modelos disponíveis

| Modelo | ID Aider | Custo estimado por run |
|--------|----------|----------------------|
| Claude Sonnet 4.5 | `openrouter/anthropic/claude-sonnet-4.5` | ~$1–5 |
| Claude Sonnet 4.6 | `openrouter/anthropic/claude-sonnet-4.6` | ~$1–5 |
| DeepSeek V3 | `openrouter/deepseek/deepseek-chat` | ~$0.10–0.50 |
| DeepSeek V3.2 | `openrouter/deepseek/deepseek-v3.2` | ~$0.10–0.50 |
| Gemini 2.5 Flash | `openrouter/google/gemini-2.5-flash` | ~$0.05–0.30 |
| Devstral 25/12 | `openrouter/mistralai/devstral-2512` | ~$0.10–0.50 |

> Todos são confirmados na lista oficial de modelos OpenRouter do Aider (`aider --list-models openrouter`).
