"""Configuração dos modelos e arquiteturas para o exp-07 Aider benchmark."""

MODELS = [
    {
        "aider_model": "openrouter/anthropic/claude-sonnet-4.5",
        "dir": "claude-sonnet-4.5",
        "label": "Claude Sonnet 4.5",
        "price_in": 3.00,
        "price_out": 15.00,
    },
    {
        "aider_model": "openrouter/anthropic/claude-sonnet-4.6",
        "dir": "claude-sonnet-4.6",
        "label": "Claude Sonnet 4.6",
        "price_in": 3.00,
        "price_out": 15.00,
    },
    {
        "aider_model": "openrouter/deepseek/deepseek-chat",
        "dir": "deepseek-v3",
        "label": "DeepSeek V3",
        "price_in": 0.14,
        "price_out": 0.28,
    },
    {
        "aider_model": "openrouter/deepseek/deepseek-v3.2",
        "dir": "deepseek-v3.2",
        "label": "DeepSeek V3.2",
        "price_in": 0.14,
        "price_out": 0.28,
    },
    {
        "aider_model": "openrouter/google/gemini-2.5-flash",
        "dir": "gemini-2.5-flash",
        "label": "Gemini 2.5 Flash",
        "price_in": 0.075,
        "price_out": 0.30,
    },
    {
        "aider_model": "openrouter/mistralai/devstral-2512",
        "dir": "devstral-2512",
        "label": "Devstral 25/12",
        "price_in": 0.10,
        "price_out": 0.30,
    },
]

ARCHITECTURES = [
    "mvc",
    "vertical-slice",
    "clean-architecture",
    "hexagonal",
    "ddd",
    "event-driven",
    "cqrs",
]

# Pacote base Java (usado nos guias e na verificação de arquitetura)
JAVA_PACKAGE = "com/benchmark/taskmanager"
JAVA_PACKAGE_DOT = "com.benchmark.taskmanager"
