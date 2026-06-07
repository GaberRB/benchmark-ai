# Experimento 3 — Modelos Locais (Ollama)

> **Variável:** modelo open-source local · **Constante:** mesma tarefa + 7 arquiteturas do Exp-02  
> **Ferramenta:** Aider + Ollama — **100% gratuito**  
> **Pergunta:** qual modelo local mais se aproxima da qualidade do Claude Sonnet? Modelos especializados em código superam os gerais?

---

## Hipótese

Modelos especializados em código (Deepseek Coder, Qwen Coder) vão superar modelos gerais (Llama 3.1) em conformidade ao PRD, cobertura de testes e número de erros de compilação.

O melhor modelo local deve atingir ≥ 80% de cobertura em pelo menos 5 das 7 arquiteturas, a custo zero.

---

## Setup

Antes de executar qualquer benchmark, siga o guia de instalação:

**[`guides/setup.md`](guides/setup.md)** — como instalar Aider, baixar os modelos Ollama e verificar o ambiente.

---

## Matriz de Experimentos

| Modelo | MVC | V-Slice | Clean | Hexagonal | DDD | Event | CQRS |
|--------|:---:|:-------:|:-----:|:---------:|:---:|:-----:|:----:|
| `deepseek-coder-v2:16b` | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| `qwen2.5-coder:7b` | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| `codellama:13b` | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| `llama3.1:8b` | ○ | ○ | ○ | ○ | ○ | ○ | ○ |

○ = pendente · ✅ = concluído · ❌ = falhou (não atingiu critério de aceite)

28 runs totais — execute incrementalmente, modelo por modelo.

---

## Guias de Execução

Cada arquitetura tem um guia no padrão dos experimentos anteriores. O **modelo é definido no topo do guia** como variável — troque conforme o modelo testado.

| Guia | Arquitetura | Guia Teórico |
|------|-------------|--------------|
| [`guides/benchmark-mvc.md`](guides/benchmark-mvc.md) | MVC | [shared/docs/arch-mvc.md](../../shared/docs/arch-mvc.md) |
| [`guides/benchmark-vertical-slice.md`](guides/benchmark-vertical-slice.md) | Vertical Slice | [shared/docs/arch-vertical-slice.md](../../shared/docs/arch-vertical-slice.md) |
| [`guides/benchmark-clean.md`](guides/benchmark-clean.md) | Clean Architecture | [shared/docs/arch-clean.md](../../shared/docs/arch-clean.md) |
| [`guides/benchmark-hexagonal.md`](guides/benchmark-hexagonal.md) | Hexagonal | [shared/docs/arch-hexagonal.md](../../shared/docs/arch-hexagonal.md) |
| [`guides/benchmark-ddd.md`](guides/benchmark-ddd.md) | DDD Tático | [shared/docs/arch-ddd.md](../../shared/docs/arch-ddd.md) |
| [`guides/benchmark-event-driven.md`](guides/benchmark-event-driven.md) | Event-Driven | [shared/docs/arch-event-driven.md](../../shared/docs/arch-event-driven.md) |
| [`guides/benchmark-cqrs.md`](guides/benchmark-cqrs.md) | CQRS | [shared/docs/arch-cqrs.md](../../shared/docs/arch-cqrs.md) |

---

## Modelos

| Modelo | Tamanho | Especialização | RAM estimada |
|--------|---------|----------------|:------------:|
| `deepseek-coder-v2:16b` | 16B | Código | ~10 GB |
| `qwen2.5-coder:7b` | 7B | Código | ~5 GB |
| `codellama:13b` | 13B | Código (Meta) | ~8 GB |
| `llama3.1:8b` | 8B | Geral | ~5 GB |

---

## Métricas Coletadas

As métricas de custo são substituídas por métricas de hardware (sem custo monetário):

| Métrica | Como medir |
|---------|----------|
| Tempo total (min) | Timestamps início/fim da sessão Aider |
| Tokens/segundo | Output speed do Ollama (logs) |
| RAM pico (GB) | `psutil` via `tools/ollama_collector.py` |
| Turnos do agente | Contagem de interações no log Aider |
| Erros de compilação | Regex `\[ERROR\]\|BUILD FAILURE` no output Maven |
| Falhas de teste | Regex `Failures: [1-9]\|FAILED` |
| Cobertura linha (%) | JaCoCo HTML report |
| LOC produção | `cloc` |
| E2E (12 cenários) | Manual (curl scripts idênticos ao Exp-02) |
| Conformidade PRD (0-10) | Checklist manual (idêntico ao Exp-02) |

---

## Estrutura de Implementações

```
implementations/
├── deepseek-coder/
│   ├── mvc/                  ← pom.xml + src/ gerado durante o run
│   ├── vertical-slice/
│   ├── clean-architecture/
│   ├── hexagonal/
│   ├── ddd/
│   ├── event-driven/
│   └── cqrs/
├── qwen2.5-coder/            ← mesmas 7 subpastas
├── codellama/                ← mesmas 7 subpastas
└── llama3.1/                 ← mesmas 7 subpastas
```

Os `src/` gerados pelo Aider são ignorados pelo git — cada um executa e gera o seu.

---

## Resultados

> Esta seção será preenchida após a execução dos experimentos.

Os JSONs de métricas ficam em `results/` (ignorado pelo git, gerado localmente).  
Use `tools/ollama_collector.py` para coletar e `tools/report.py` para gerar o dashboard HTML.

---

## Comparação com Claude Code (Exp-02)

Após completar o experimento, a comparação pode ser feita diretamente:

- **Custo**: Claude (`$2,22–$3,84`) vs Ollama (`$0,00`)
- **Tempo**: Claude (`5–9 min`) vs Ollama (a medir — depende do hardware)
- **Qualidade**: cobertura, erros e conformidade das mesmas arquiteturas
- **Conclusão esperada**: Ollama tem custo zero mas maior latência e potencialmente menor qualidade em arquiteturas complexas
