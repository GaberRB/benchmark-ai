# Arquitetura Event-Driven

## O que é

**Event-Driven Architecture** desacopla produtores de consumidores por meio de **eventos de domínio**. Cada mutação de estado publica um evento imutável em um **EventBus**. Handlers reagem aos eventos de forma independente — o Service que publica não conhece quem vai processar.

---

## Diagrama

```
                      HTTP Request
                           │
             ┌─────────────▼─────────────┐
             │        API LAYER          │
             │     TaskController        │
             └─────────────┬─────────────┘
                           │
             ┌─────────────▼─────────────┐
             │       SERVICE LAYER       │
             │       TaskService         │
             │                           │
             │  1. opera no repository   │
             │  2. publica evento no bus │
             │                           │
             │  publish(new TaskCreated  │
             │    Event(...))            │
             └──────┬──────────┬─────────┘
                    │          │
           repositório      eventbus
                    │          │
        ┌───────────▼──┐  ┌───▼───────────────────────────────────┐
        │  REPOSITORY  │  │           EVENT BUS                   │
        │              │  │  InMemoryEventBus                     │
        │ InMemory     │  │  • Map<Class<?>, List<Handler>>       │
        │ TaskRepos.   │  │  • subscribe(eventType, handler)      │
        └──────────────┘  │  • publish(event) → invoca handlers  │
                          └──────┬──────────┬──────────┬──────────┘
                                 │          │          │
                    ┌────────────▼──┐  ┌────▼────┐  ┌─▼──────────┐
                    │   HANDLERS    │  │         │  │            │
                    │ TaskCreated   │  │ Updated │  │  Deleted   │
                    │ Handler       │  │ Handler │  │  Handler   │
                    │ loga evento   │  │ loga    │  │  loga      │
                    └───────────────┘  └─────────┘  └────────────┘

        ┌──────────────────────────────────────────────────────────┐
        │                      EVENTS                              │
        │  DomainEvent (interface)                                 │
        │    └── eventId, occurredAt, aggregateId                  │
        │                                                          │
        │  TaskCreatedEvent (record)  ← imutável                  │
        │  TaskUpdatedEvent (record)  ← imutável                  │
        │  TaskDeletedEvent (record)  ← imutável                  │
        └──────────────────────────────────────────────────────────┘
```

**Estrutura de pacotes:**

```
com.benchmark.taskmanager/
├── events/
│   ├── DomainEvent.java              ← interface
│   ├── TaskCreatedEvent.java         ← record imutável
│   ├── TaskUpdatedEvent.java         ← record imutável
│   ├── TaskDeletedEvent.java         ← record imutável
│   ├── EventHandler.java             ← @FunctionalInterface
│   ├── EventBus.java                 ← interface
│   └── InMemoryEventBus.java         ← @Component
├── handlers/
│   ├── TaskCreatedHandler.java
│   ├── TaskUpdatedHandler.java
│   └── TaskDeletedHandler.java
├── model/
│   ├── Task.java
│   └── TaskStatus.java               ← enum: PENDING, IN_PROGRESS, DONE
├── repository/
│   ├── TaskRepository.java           ← interface
│   └── InMemoryTaskRepository.java
├── service/
│   └── TaskService.java              ← publica eventos após cada operação
└── api/
    ├── TaskController.java
    ├── CreateTaskRequest.java
    ├── UpdateTaskRequest.java
    ├── TaskResponse.java
    ├── TaskNotFoundException.java
    └── GlobalExceptionHandler.java
```

---

## Fluxo de uma requisição

```
POST /tasks
    ↓
TaskController.createTask(request)
    ↓
TaskService.createTask(title, description)
    ├── 1. task = new Task(); task.setId(uuid); ...
    ├── 2. repository.save(task)
    └── 3. eventBus.publish(new TaskCreatedEvent(uuid, now, task.getId(), title, description))
                                    ↓
                        InMemoryEventBus.publish(event)
                            ↓ encontra handlers de TaskCreatedEvent
                        TaskCreatedHandler.handle(event)
                            → Logger: "Task created: {id} - {title}"
```

**Invariante:** o evento é publicado **sempre após** a persistência ter sucesso.

---

## Estrutura do EventBus

```java
// Interface (desacoplamento)
public interface EventBus {
    <T extends DomainEvent> void subscribe(Class<T> eventType, EventHandler<T> handler);
    void publish(DomainEvent event);
}

// Implementação
@Component
public class InMemoryEventBus implements EventBus {
    private final Map<Class<?>, List<EventHandler<?>>> handlers = new HashMap<>();

    @PostConstruct
    public void registerHandlers() {
        subscribe(TaskCreatedEvent.class, taskCreatedHandler);
        subscribe(TaskUpdatedEvent.class, taskUpdatedHandler);
        subscribe(TaskDeletedEvent.class, taskDeletedHandler);
    }
}
```

---

## Vantagens

- **Desacoplamento total** — Service não conhece os Handlers
- **Extensível** — adicionar um novo handler não toca no Service
- **Auditoria natural** — eventos imutáveis são um log histórico das mutações
- **Base para sistemas distribuídos** — substituir InMemoryEventBus por Kafka é só trocar o adapter

## Desvantagens

- **Rastreabilidade complexa** — fluxo não é linear, difícil de debugar
- **Over-engineering para CRUD** — para criar uma tarefa, o fluxo passa por 5 objetos
- **Handlers síncronos vs assíncronos** — no benchmark são síncronos; em produção exige decisão de design
- **Mais erros de wiring** — o registro de handlers no @PostConstruct gerou 5 erros no benchmark

## Resultado no Benchmark

| Métrica | Valor |
|---------|-------|
| 💰 Custo | **$2,22 (mais barato total)** |
| ⏱ Velocidade | 8,85 min |
| 🐛 Erros | 5 |
| 🎯 Cobertura | 90% |
| 🏗 Conformidade | 10/10 |
| ✅ E2E | 12/12 |

> **Event-Driven foi o mais barato** no total ($2,22) pelo uso intensivo de cache (94,75% hit rate).
> Depois de montar o EventBus, os handlers seguintes usaram cache pesadamente.
> 5 erros durante o desenvolvimento mas todos os 12 cenários E2E passaram ao final.
