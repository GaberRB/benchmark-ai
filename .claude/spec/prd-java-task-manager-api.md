# PRD — Java: Task Manager API

**Versão**: 2.0  
**Data**: 2026-06-04  
**Linguagem**: Java 21  
**Sessão**: `java-implementation/`  
**Benchmark master**: `prd-ai-benchmark-java-vs-kotlin.md`

---

## ⚠️ MANDATO DO AGENTE CODIFICADOR

> Este bloco define as regras inegociáveis que o agente que executar esta sessão deve seguir.
> **Não há exceções. A sessão só termina quando todos os critérios abaixo estão 100% satisfeitos.**

### Regra 1 — Validar após cada mudança

Após **qualquer** alteração de código (novo arquivo, nova classe, novo método, mudança de
configuração), o agente **deve obrigatoriamente** executar:

```bash
mvn compile
```

Se compilar com sucesso:

```bash
mvn test
```

**Nunca avançar para a próxima tarefa com build quebrado ou teste falhando.**
Cada falha deve ser corrigida antes de prosseguir. Isso é intencional — as falhas
e as tentativas de correção são parte das métricas do benchmark.

### Regra 2 — Registrar falhas explicitamente

Cada vez que `mvn compile` ou `mvn test` falhar, o agente deve:

1. Identificar a causa raiz do erro na saída do compilador/test runner
2. Corrigi-la na mesma sequência de turns
3. Rodar novamente até passar

O número de falhas acumuladas durante a sessão é capturado automaticamente
pelo `metrics/collector.py` via telemetria. **Não pule erros, não comente código
quebrado para fazer o build passar.**

### Regra 3 — Entrega 100% funcional obrigatória

A sessão **não pode ser declarada concluída** sem que todos os itens abaixo estejam verdes:

- [ ] `mvn compile` — BUILD SUCCESS, zero erros
- [ ] `mvn test` — BUILD SUCCESS, zero failures, zero errors
- [ ] Cobertura JaCoCo ≥ 80% de linhas
- [ ] `mvn spring-boot:run` — aplicação sobe na porta 8080 sem erros
- [ ] Todos os testes E2E passam (ver Seção 8)

**Se qualquer item falhar, a sessão continua até ser resolvida.**

---

## 1. Objetivo desta Sessão

Implementar a Task Manager API em **Java com Spring Boot 3.x**, seguindo exatamente a
especificação em `spec/task-definition.md`, de forma que os dados de tokens, erros e
velocidade coletados possam ser comparados de forma justa com a sessão Kotlin.

---

## 2. Stack Técnica

| Componente      | Tecnologia                         |
|-----------------|------------------------------------|
| Linguagem       | Java 21                            |
| Framework HTTP  | Spring Boot 3.x (spring-web)       |
| Build tool      | Maven (pom.xml)                    |
| Testes unitários | JUnit 5 + Spring Boot Test        |
| Testes E2E      | curl (HTTP calls contra app rodando) |
| Cobertura       | JaCoCo Maven Plugin                |
| Storage         | In-memory (`ConcurrentHashMap`)    |
| IDs             | `UUID.randomUUID()`                |
| Timestamps      | `Instant.now()` → ISO 8601         |

---

## 3. Especificação Funcional

Seguir **integralmente** o arquivo `spec/task-definition.md`.

| Método | Rota        | Status de sucesso | Status de erro |
|--------|-------------|-------------------|----------------|
| GET    | /tasks      | 200               | —              |
| POST   | /tasks      | 201               | 400            |
| GET    | /tasks/{id} | 200               | 404            |
| PUT    | /tasks/{id} | 200               | 400, 404       |
| DELETE | /tasks/{id} | 204               | 404            |

---

## 4. Modelo de Dados

```java
public class Task {
    private String id;           // UUID
    private String title;        // obrigatório, max 200 chars
    private String description;  // opcional, max 1000 chars
    private boolean completed;   // default false
    private String createdAt;    // ISO 8601 UTC
    private String updatedAt;    // ISO 8601 UTC
}
```

---

## 5. Estrutura de Projeto Esperada

```
java-implementation/
├── pom.xml
└── src/
    ├── main/
    │   └── java/com/benchmark/taskmanager/
    │       ├── TaskManagerApplication.java
    │       ├── controller/
    │       │   └── TaskController.java
    │       ├── model/
    │       │   └── Task.java
    │       ├── dto/
    │       │   ├── CreateTaskRequest.java
    │       │   └── UpdateTaskRequest.java
    │       ├── service/
    │       │   └── TaskService.java
    │       └── exception/
    │           ├── TaskNotFoundException.java
    │           └── GlobalExceptionHandler.java
    └── test/
        └── java/com/benchmark/taskmanager/
            ├── controller/
            │   └── TaskControllerTest.java
            └── service/
                └── TaskServiceTest.java
```

---

## 6. Requisitos de Implementação

### 6.1 Validações obrigatórias

- `title` ausente ou vazio → HTTP 400, body `{ "error": "title is required" }`
- `title` > 200 chars → HTTP 400, body `{ "error": "title must not exceed 200 characters" }`
- `description` > 1000 chars → HTTP 400, body `{ "error": "description must not exceed 1000 characters" }`
- ID não encontrado → HTTP 404, body `{ "error": "Task not found" }`

### 6.2 Configuração JaCoCo (pom.xml)

```xml
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <executions>
        <execution>
            <goals><goal>prepare-agent</goal></goals>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals><goal>report</goal></goals>
        </execution>
        <execution>
            <id>check</id>
            <goals><goal>check</goal></goals>
            <configuration>
                <rules>
                    <rule>
                        <limits>
                            <limit>
                                <counter>LINE</counter>
                                <value>COVEREDRATIO</value>
                                <minimum>0.80</minimum>
                            </limit>
                        </limits>
                    </rule>
                </rules>
            </configuration>
        </execution>
    </executions>
</plugin>
```

### 6.3 Comandos de validação (executar após cada mudança)

```bash
# Passo 1 — compilar
mvn compile

# Passo 2 — testar (só executar se passo 1 passou)
mvn test

# Relatório de cobertura disponível em: target/site/jacoco/index.html
```

---

## 7. Suite de Testes Unitários

O agente deve gerar **e garantir que passam** os seguintes testes antes de avançar:

- [ ] `GET /tasks` — retorna `[]` com status 200 quando lista vazia
- [ ] `GET /tasks` — retorna lista com tarefas criadas, status 200
- [ ] `POST /tasks` — body válido → 201, response contém `id` UUID e `createdAt`
- [ ] `POST /tasks` — sem `title` → 400, body `{ "error": "title is required" }`
- [ ] `POST /tasks` — `title` com 201 chars → 400
- [ ] `GET /tasks/{id}` — ID existente → 200 com objeto completo
- [ ] `GET /tasks/{id}` — ID inexistente → 404, body `{ "error": "Task not found" }`
- [ ] `PUT /tasks/{id}` — dados válidos → 200, `updatedAt` diferente de `createdAt`
- [ ] `PUT /tasks/{id}` — `completed: true` → 200, campo `completed` é `true`
- [ ] `PUT /tasks/{id}` — ID inexistente → 404
- [ ] `DELETE /tasks/{id}` — ID existente → 204, sem body
- [ ] `DELETE /tasks/{id}` — ID inexistente → 404

**O agente não deve declarar os testes unitários concluídos enquanto `mvn test` reportar
qualquer `Failures` ou `Errors`.**

---

## 8. Testes E2E (Obrigatórios — app deve estar rodando)

Após `mvn test` passar com 100% de testes verdes, o agente deve:

**Passo 1** — Subir a aplicação em background:

```bash
mvn spring-boot:run &
# Aguardar log: "Started TaskManagerApplication in X seconds"
```

**Passo 2** — Executar todos os cenários E2E com curl:

```bash
BASE="http://localhost:8080"

# E2E-01: Listar tarefas (lista vazia)
curl -s -o /tmp/e2e01.json -w "%{http_code}" $BASE/tasks
# Esperado: 200, body []

# E2E-02: Criar tarefa válida
curl -s -o /tmp/e2e02.json -w "%{http_code}" -X POST $BASE/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Task","description":"Desc"}'
# Esperado: 201, body com id, title, completed=false, createdAt, updatedAt
TASK_ID=$(cat /tmp/e2e02.json | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

# E2E-03: Criar tarefa sem title
curl -s -o /tmp/e2e03.json -w "%{http_code}" -X POST $BASE/tasks \
  -H "Content-Type: application/json" \
  -d '{}'
# Esperado: 400, body {"error":"title is required"}

# E2E-04: Criar tarefa com title vazio
curl -s -o /tmp/e2e04.json -w "%{http_code}" -X POST $BASE/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":""}'
# Esperado: 400

# E2E-05: Listar tarefas (com itens)
curl -s -o /tmp/e2e05.json -w "%{http_code}" $BASE/tasks
# Esperado: 200, body com array contendo a tarefa criada

# E2E-06: Buscar tarefa por ID (existente)
curl -s -o /tmp/e2e06.json -w "%{http_code}" $BASE/tasks/$TASK_ID
# Esperado: 200, objeto completo

# E2E-07: Buscar tarefa por ID (inexistente)
curl -s -o /tmp/e2e07.json -w "%{http_code}" $BASE/tasks/id-que-nao-existe
# Esperado: 404, body {"error":"Task not found"}

# E2E-08: Atualizar tarefa (válido)
curl -s -o /tmp/e2e08.json -w "%{http_code}" -X PUT $BASE/tasks/$TASK_ID \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated Title","completed":true}'
# Esperado: 200, title atualizado, completed=true, updatedAt != createdAt

# E2E-09: Atualizar tarefa (ID inexistente)
curl -s -o /tmp/e2e09.json -w "%{http_code}" -X PUT $BASE/tasks/id-que-nao-existe \
  -H "Content-Type: application/json" \
  -d '{"title":"X"}'
# Esperado: 404

# E2E-10: Deletar tarefa (existente)
curl -s -o /tmp/e2e10.json -w "%{http_code}" -X DELETE $BASE/tasks/$TASK_ID
# Esperado: 204, sem body

# E2E-11: Deletar tarefa (inexistente)
curl -s -o /tmp/e2e11.json -w "%{http_code}" -X DELETE $BASE/tasks/id-que-nao-existe
# Esperado: 404

# E2E-12: Confirmar que tarefa deletada não existe mais
curl -s -o /tmp/e2e12.json -w "%{http_code}" $BASE/tasks/$TASK_ID
# Esperado: 404
```

**Passo 3** — Verificar resultados. Para cada cenário que não retornou o status esperado,
o agente deve:
1. Identificar o problema
2. Corrigir o código
3. Recompilar (`mvn compile`)
4. Reexecutar os testes unitários (`mvn test`)
5. Resubir o app e repetir o cenário E2E que falhou

**Passo 4** — Encerrar o app:

```bash
# Matar o processo Spring Boot
pkill -f "spring-boot:run" 2>/dev/null || kill $(lsof -t -i:8080) 2>/dev/null
```

### Métricas E2E a registrar

| Cenário | Status esperado | Status obtido | Passou? |
|---------|----------------|---------------|---------|
| E2E-01  | 200            |               |         |
| E2E-02  | 201            |               |         |
| E2E-03  | 400            |               |         |
| E2E-04  | 400            |               |         |
| E2E-05  | 200            |               |         |
| E2E-06  | 200            |               |         |
| E2E-07  | 404            |               |         |
| E2E-08  | 200            |               |         |
| E2E-09  | 404            |               |         |
| E2E-10  | 204            |               |         |
| E2E-11  | 404            |               |         |
| E2E-12  | 404            |               |         |
| **Total falhas E2E** | — | — | **/12** |

---

## 9. Critério de Conclusão da Sessão

A sessão Java só está concluída quando **todos** os itens abaixo forem verificados:

| # | Critério | Comando de validação | Status |
|---|----------|----------------------|--------|
| 1 | Compilação sem erros | `mvn compile` → BUILD SUCCESS | [ ] |
| 2 | Todos os testes unitários passam | `mvn test` → 0 failures, 0 errors | [ ] |
| 3 | Cobertura ≥ 80% | JaCoCo report → Line coverage ≥ 80% | [ ] |
| 4 | App sobe sem erros | `mvn spring-boot:run` → porta 8080 ok | [ ] |
| 5 | Todos os 12 cenários E2E passam | curl scripts → 0 falhas | [ ] |

**Se qualquer item estiver com `[ ]` ao final, a sessão não está concluída.**

---

## 10. Captura de Métricas — Checklist Obrigatório

### Antes de iniciar a sessão

```powershell
cd C:\Users\grios\OneDrive\Desktop\benchmark
python metrics/snapshot.py --pre --language java
```

Abrir Claude Code **dentro de `java-implementation/`**:

```powershell
cd java-implementation
claude
```

### Ao concluir a sessão

1. Anotar o Session ID exibido no terminal do Claude Code
2. Fechar a sessão Claude Code

```powershell
cd C:\Users\grios\OneDrive\Desktop\benchmark
python metrics/snapshot.py --post --language java --session-id <UUID>
python metrics/collector.py --session-id <UUID> --language java
```

3. Executar cobertura e LOC:

```powershell
cd java-implementation
mvn test
# Anotar Line coverage % e Branch coverage % de target/site/jacoco/index.html
cloc src/main/java --json
cloc src/test/java --json
```

---

## 11. Dados a Registrar Manualmente

Após a sessão, atualizar o JSON de saída do `collector.py` com:

```json
{
  "code_quality": {
    "lines_of_code": 0,
    "test_lines_of_code": 0,
    "test_coverage_line_pct": 0.0,
    "test_coverage_branch_pct": 0.0,
    "test_ratio_pct": 0.0
  },
  "e2e": {
    "total_scenarios": 12,
    "passed": 0,
    "failed": 0,
    "failure_details": []
  }
}
```

---

## 12. Modo 2 — Execução com Subagentes Paralelos

> Esta seção descreve como executar a sessão Java no **Modo 2**, onde um agente orquestrador
> decompõe o trabalho em tasks independentes que subagentes executam em paralelo.
> Executar **depois** do Modo 1 para permitir comparação direta.

### 12.1 Decomposição de Tasks

O orquestrador deve gerar tasks seguindo as fases abaixo. Tasks na mesma fase não têm
interdependências entre si e podem ser enviadas a subagentes em paralelo.

#### Fase 0 — Contratos (Sequential — base para todas as tasks)

| Task | Descrição | Arquivo(s) alvo |
|------|-----------|-----------------|
| T0 | Criar `pom.xml` com todas as dependências e plugins (Spring Boot, JUnit 5, JaCoCo) | `pom.xml` |
| T1 | Criar modelo `Task.java` e DTOs (`CreateTaskRequest.java`, `UpdateTaskRequest.java`) | `model/`, `dto/` |

> T0 e T1 podem rodar em paralelo entre si. Todas as phases seguintes dependem de T1.

#### Fase 1 — Implementação (Parallel — rodam simultaneamente)

| Task | Descrição | Arquivo(s) alvo | Depende de |
|------|-----------|-----------------|------------|
| T2 | Implementar `TaskService.java` com storage in-memory | `service/TaskService.java` | T1 |
| T3 | Implementar `TaskController.java` com todos os 5 endpoints | `controller/TaskController.java` | T1 |
| T4 | Implementar `TaskNotFoundException.java` e `GlobalExceptionHandler.java` | `exception/` | T1 |

> T2, T3 e T4 rodam em paralelo. T3 usa a **interface** de T2, não sua implementação —
> o orquestrador deve definir o contrato do service antes de disparar T3.

#### Fase 2 — Testes Unitários (Parallel — rodam simultaneamente)

| Task | Descrição | Arquivo(s) alvo | Depende de |
|------|-----------|-----------------|------------|
| T5 | Escrever testes unitários para `TaskService` (todos os cenários da Seção 7) | `service/TaskServiceTest.java` | T2 |
| T6 | Escrever testes unitários para `TaskController` (todos os cenários da Seção 7) | `controller/TaskControllerTest.java` | T3, T4 |

> T5 e T6 rodam em paralelo. Cada subagente deve rodar `mvn test` ao final e garantir
> que todos os seus testes passam antes de retornar.

#### Fase 3 — Integração e E2E (Sequential — orquestrador)

| Task | Descrição |
|------|-----------|
| T7 | Orquestrador integra o código, resolve conflitos, roda `mvn test` completo e executa os 12 cenários E2E da Seção 8 |

### 12.2 Regras para Subagentes

Cada subagente que receber uma task deve:

1. Ler os arquivos de contrato relevantes (modelo, interfaces) antes de implementar
2. Ao finalizar: rodar `mvn compile` e, se aplicável, `mvn test`
3. Reportar ao orquestrador: status (sucesso/falha), arquivos criados, erros encontrados
4. **Não declarar conclusão com build quebrado**

### 12.3 Prompt Base para o Orquestrador

```
Você é o orquestrador de uma sessão de benchmark Java.
Sua missão:
1. Ler o PRD em .claude/spec/prd-java-task-manager-api.md
2. Ler a spec em spec/task-definition.md
3. Decompor o trabalho nas tasks da Seção 12.1 deste PRD
4. Executar tasks da Fase 0 sequencialmente
5. Disparar tasks da Fase 1 em paralelo (subagentes simultâneos)
6. Aguardar conclusão de todas as tasks da Fase 1
7. Disparar tasks da Fase 2 em paralelo (subagentes simultâneos)
8. Aguardar conclusão, então executar Fase 3 (integração + E2E)
9. Entregar a aplicação 100% funcional conforme critérios da Seção 9
```

### 12.4 Métricas a Capturar no Modo 2

Além de todas as métricas do Modo 1, registrar:

| Métrica | Como capturar |
|---|---|
| `orchestration_tokens` | session_id do agente orquestrador via `collector.py` |
| `tokens_per_task[T0..T6]` | session_id de cada subagente via `collector.py` |
| `wall_clock_time_min` | timestamp início do T0 até fim do T7 |
| `cpu_equivalent_time_min` | soma dos tempos individuais de cada task |
| `speedup_ratio` | `cpu_equivalent / wall_clock` |
| `task_failure_count` | tasks que falharam na primeira tentativa (subagente reportou erro) |
| `integration_conflicts` | erros encontrados pelo orquestrador na Fase 3 |
| `integration_fix_turns` | turns do orquestrador para resolver conflitos pós-integração |
| `context_duplication_tokens` | tokens dos subagentes gastos relendo spec/modelo (cada um lê do zero) |

### 12.5 Captura de Métricas — Modo 2

```powershell
# Antes de iniciar o orquestrador
python metrics/snapshot.py --pre --language java-mode2

# Ao concluir (anotar session_id do orquestrador E de cada subagente)
python metrics/snapshot.py --post --language java-mode2 --session-id <UUID-orquestrador>

# Coletar métricas do orquestrador
python metrics/collector.py --session-id <UUID-orquestrador> --language java-mode2-orchestrator

# Coletar métricas de cada subagente
python metrics/collector.py --session-id <UUID-T2> --language java-mode2-task-T2
python metrics/collector.py --session-id <UUID-T3> --language java-mode2-task-T3
# ... repetir para cada task
```

---

## 13. Fora de Escopo desta Sessão

- Banco de dados externo
- Autenticação / autorização
- Deploy / containerização
- Swagger / OpenAPI (opcional — não conta no benchmark)
- Lombok (opcional — a IA decide)
