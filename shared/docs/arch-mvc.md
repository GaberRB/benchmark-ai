# Arquitetura MVC — Layered MVC

## O que é

O padrão **Layered MVC** organiza o código em **camadas horizontais**, cada uma com uma responsabilidade distinta. É o padrão padrão do Spring Boot e o mais comum em tutoriais e projetos Java no mundo.

---

## Diagrama

```
┌─────────────────────────────────────────────┐
│              HTTP Request                   │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│           CONTROLLER LAYER                  │
│  TaskController.java                        │
│  • recebe e valida a requisição HTTP        │
│  • chama o Service                          │
│  • retorna a resposta HTTP                  │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│            SERVICE LAYER                    │
│  TaskService.java                           │
│  • contém a lógica de negócio               │
│  • orquestra chamadas ao repositório        │
│  • lança exceções de domínio                │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│          REPOSITORY LAYER                   │
│  TaskRepository (interface)                 │
│  InMemoryTaskRepository (implementação)     │
│  • abstrai o acesso aos dados               │
└─────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│              MODEL                          │
│  Task.java        — entidade de dados       │
│  CreateTaskRequest — DTO de entrada         │
│  UpdateTaskRequest — DTO de atualização     │
└─────────────────────────────────────────────┘
```

**Estrutura de pacotes:**

```
com.benchmark.taskmanager/
├── controller/
│   └── TaskController.java
├── service/
│   └── TaskService.java
├── repository/
│   ├── TaskRepository.java
│   └── InMemoryTaskRepository.java
├── model/
│   └── Task.java
├── dto/
│   ├── CreateTaskRequest.java
│   └── UpdateTaskRequest.java
└── exception/
    ├── TaskNotFoundException.java
    └── GlobalExceptionHandler.java
```

---

## Regra de Dependência

```
Controller  →  Service  →  Repository  →  Model
```

Cada camada só conhece a camada imediatamente abaixo. O Controller nunca acessa o Repository diretamente.

---

## Vantagens

- **Curva de aprendizado mínima** — todo desenvolvedor Java conhece esse padrão
- **Tooling excelente** — Spring Boot, Spring Data, Spring MVC foram feitos para isso
- **Menos boilerplate** — menos arquivos, menos interfaces, menos abstrações
- **IA implementa bem** — alta densidade nos dados de treinamento → menos erros, menos tokens

## Desvantagens

- **Service vira um "god class"** em projetos grandes — regras de negócio de todo o domínio acumulam no mesmo lugar
- **Difícil de testar em isolamento** — Service geralmente depende diretamente de classes concretas
- **Sem fronteiras explícitas** — nada impede um Controller de injetar um Repository

## Resultado no Benchmark

| Métrica | Valor |
|---------|-------|
| 💰 Custo | $1,73 (2º mais barato) |
| ⏱ Velocidade | 6,3 min |
| 🐛 Erros | 5 |
| 🎯 Cobertura | 93% |
| 🏗 Conformidade | 10/10 |
| ✅ E2E | 12/12 |

> **Por que MVC foi barato?** A IA reconhece esse padrão quase de memória — poucos tokens de
> raciocínio, código direto. Output: apenas 27.550 tokens contra 107k do Vertical Slice.
