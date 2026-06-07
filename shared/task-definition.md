# Task Definition — Task Manager API

**Versão**: 1.0  
**Usada por**: Java implementation · Kotlin implementation  
**Propósito**: Especificação idêntica para ambas as linguagens no benchmark

---

## Descrição

Implementar uma API REST para gerenciamento de tarefas com armazenamento in-memory.
A implementação deve ser **identica em comportamento** nas duas linguagens; apenas a
sintaxe e o idioma da linguagem mudam.

---

## Modelo de Dados

```json
{
  "id":          "string (UUID gerado pelo servidor)",
  "title":       "string (obrigatório, max 200 chars)",
  "description": "string (opcional, max 1000 chars)",
  "completed":   "boolean (default: false)",
  "createdAt":   "string (ISO 8601, gerado pelo servidor)",
  "updatedAt":   "string (ISO 8601, atualizado a cada PUT)"
}
```

---

## Endpoints

### GET /tasks
Retorna lista de todas as tarefas.

**Response 200**:
```json
[
  { "id": "...", "title": "...", "description": "...", "completed": false, "createdAt": "...", "updatedAt": "..." }
]
```
- Lista vazia `[]` quando não há tarefas (nunca retornar null)

---

### POST /tasks
Cria uma nova tarefa.

**Request body**:
```json
{ "title": "Minha tarefa", "description": "Opcional" }
```

**Validações**:
- `title` é obrigatório; retornar `400` se ausente ou vazio
- `title` máximo 200 caracteres; retornar `400` se exceder
- `description` máximo 1000 caracteres; retornar `400` se exceder

**Response 201** (Created):
```json
{ "id": "uuid-gerado", "title": "...", "completed": false, "createdAt": "...", "updatedAt": "..." }
```

**Response 400** (Bad Request):
```json
{ "error": "title is required" }
```

---

### GET /tasks/{id}
Busca tarefa por ID.

**Response 200**: objeto da tarefa  
**Response 404**: `{ "error": "Task not found" }`

---

### PUT /tasks/{id}
Atualiza uma tarefa existente (substituição parcial — só campos enviados são alterados).

**Request body** (todos opcionais):
```json
{ "title": "Novo título", "description": "Nova desc", "completed": true }
```

**Validações**:
- Se `title` enviado: não pode ser vazio, máximo 200 chars
- Se `description` enviada: máximo 1000 chars
- `updatedAt` deve ser atualizado automaticamente

**Response 200**: objeto da tarefa atualizado  
**Response 400**: erro de validação  
**Response 404**: tarefa não encontrada

---

### DELETE /tasks/{id}
Remove uma tarefa.

**Response 204** (No Content): sem body  
**Response 404**: `{ "error": "Task not found" }`

---

## Requisitos Não-Funcionais

| Requisito | Valor |
|---|---|
| Framework HTTP | Spring Boot 3.x (Java e Kotlin) |
| Storage | In-memory (Map/List — sem banco de dados) |
| IDs | UUID v4 gerado pelo servidor |
| Timestamps | ISO 8601 UTC |
| Content-Type | `application/json` em todas as responses |
| Cobertura de testes | ≥ 80% de linhas |
| Test runner | JUnit 5 (Java) / Kotest ou JUnit 5 (Kotlin) |

---

## Suite de Testes Mínima

A IA deve gerar testes cobrindo ao menos:

- [ ] `GET /tasks` — lista vazia
- [ ] `GET /tasks` — lista com itens
- [ ] `POST /tasks` — criação válida retorna 201 com ID
- [ ] `POST /tasks` — sem título retorna 400
- [ ] `POST /tasks` — título muito longo retorna 400
- [ ] `GET /tasks/{id}` — ID existente retorna 200
- [ ] `GET /tasks/{id}` — ID inexistente retorna 404
- [ ] `PUT /tasks/{id}` — atualização válida retorna 200
- [ ] `PUT /tasks/{id}` — ID inexistente retorna 404
- [ ] `DELETE /tasks/{id}` — ID existente retorna 204
- [ ] `DELETE /tasks/{id}` — ID inexistente retorna 404

---

## Critério de Conclusão

A sessão de benchmark encerra quando:

1. Todos os 5 endpoints respondem corretamente (testados via HTTP ou testes automatizados)
2. Suite de testes passa com ≥ 80% de cobertura
3. A aplicação sobe sem erros (`mvn spring-boot:run` ou `./gradlew bootRun`)
