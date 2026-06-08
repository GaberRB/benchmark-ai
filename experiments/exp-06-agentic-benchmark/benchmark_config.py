"""Configuração do projeto Task Manager API para o exp-06."""

import os
from dataclasses import dataclass, field

# Auto-detectar caminho base
import pathlib
_HERE = pathlib.Path(__file__).parent
_BASE = _HERE.parent.parent  # benchmark/

EXP_DIR = str(_HERE)

TASK_DEFINITION_PATH = str(_BASE / "shared" / "task-definition.md")


@dataclass
class BenchmarkConfig:
    # ===== Diretórios =====
    exp_dir: str = EXP_DIR
    guides_dir: str = str(_HERE / "guides")
    task_definition_path: str = TASK_DEFINITION_PATH

    # ===== Limites do loop agentico =====
    max_tokens_per_turn: int = 8192
    max_build_failures: int = 10       # max de mvn compile falhando
    max_test_failures: int = 10        # max de mvn test falhando
    max_e2e_failures: int = 10         # max de verificações E2E falhando consecutivamente

    # ===== Tech Stack =====
    tech_stack: str = "Java 21, Spring Boot 3.2"
    base_package: str = "com.benchmark.taskmanager"
    test_framework: str = "@SpringBootTest + MockMvc"
    storage_desc: str = "UUID IDs stored in ConcurrentHashMap (no database, in-memory only)"
    coverage_target: int = 80

    # ===== Regras de domínio =====
    endpoints_desc: str = (
        "GET /tasks → 200, "
        "POST /tasks → 201 or 400, "
        "GET /tasks/{id} → 200 or 404, "
        "PUT /tasks/{id} → 200 or 404, "
        "DELETE /tasks/{id} → 204 or 404"
    )

    validation_rules: str = (
        "Use jakarta.validation.constraints (NOT javax). "
        "@NotBlank on title field of CreateTaskRequest only."
    )

    build_fix_rules: str = (
        "(1) DO NOT change existing interface signatures in TaskService.java or "
        "TaskRepository.java — only fix implementation classes. "
        "(2) Use jakarta.validation.constraints NOT javax. "
        "(3) pom.xml already has spring-boot-starter-validation — do not add it again. "
        "(4) Write COMPLETE file content, no placeholders."
    )

    partial_update_rules: str = (
        "PUT PARTIAL UPDATE RULE: UpdateTaskRequest.title is nullable (null = keep existing value). "
        "@NotBlank rejects BOTH null and blank — NEVER use @NotBlank on UpdateTaskRequest. "
        "Instead add in the controller PUT method: "
        "if (request.title() != null && request.title().isBlank()) { "
        "return ResponseEntity.badRequest().body(Map.of(\"error\", \"title cannot be blank\")); }"
    )

    e2e_rules: str = (
        "(1) @Valid on controller params + @NotBlank on title DTO field → returns 400. "
        "(2) Any non-existent or invalid UUID → throws TaskNotFoundException → "
        "GlobalExceptionHandler returns 404 JSON. "
        "(3) POST needs title, null/empty = 400. "
        "(4) DELETE returns 204 (no body). "
        "(5) Never return 400 for ID not found, always 404."
    )

    # ===== Modelos =====
    models: list = field(default_factory=lambda: [
        {"name": "deepseek/deepseek-chat",             "dir": "deepseek-v3",     "label": "DeepSeek V3",         "price_in": 0.14,  "price_out": 0.28,  "tool_use": True},
        {"name": "qwen/qwen-2.5-coder-32b-instruct",  "dir": "qwen-coder-32b",  "label": "Qwen 2.5 Coder 32B",  "price_in": 0.10,  "price_out": 0.20,  "tool_use": False},
        {"name": "google/gemini-2.0-flash-001",        "dir": "gemini-flash",    "label": "Gemini 2.0 Flash",    "price_in": 0.075, "price_out": 0.30,  "tool_use": True},
        {"name": "meta-llama/llama-3.3-70b-instruct", "dir": "llama-3.3-70b",   "label": "Llama 3.3 70B",       "price_in": 0.10,  "price_out": 0.20,  "tool_use": True},
        {"name": "anthropic/claude-sonnet-4-5",        "dir": "claude-sonnet",   "label": "Claude Sonnet 4.5",   "price_in": 3.00,  "price_out": 15.00, "tool_use": True},
    ])

    # ===== Arquiteturas =====
    architectures: list = field(default_factory=lambda: [
        "mvc",
        "vertical-slice",
        "clean-architecture",
        "hexagonal",
        "ddd",
        "event-driven",
        "cqrs",
    ])

    # ===== Arquivos por arquitetura =====
    arch_prod_files: dict = field(default_factory=lambda: {
        "mvc": (
            "TaskManagerApplication.java, controller/TaskController.java, "
            "model/Task.java, dto/CreateTaskRequest.java, dto/UpdateTaskRequest.java, "
            "service/TaskService.java, service/impl/TaskServiceImpl.java, "
            "repository/TaskRepository.java, repository/impl/InMemoryTaskRepository.java, "
            "exception/TaskNotFoundException.java, exception/GlobalExceptionHandler.java"
        ),
        "vertical-slice": (
            "TaskManagerApplication.java, task/TaskController.java, task/Task.java, "
            "task/CreateTaskRequest.java, task/UpdateTaskRequest.java, "
            "task/TaskService.java, task/InMemoryTaskRepository.java, "
            "shared/exception/TaskNotFoundException.java, shared/exception/GlobalExceptionHandler.java"
        ),
        "clean-architecture": (
            "TaskManagerApplication.java, domain/entity/Task.java, "
            "domain/port/in/TaskUseCase.java, domain/port/out/TaskRepositoryPort.java, "
            "application/service/TaskApplicationService.java, "
            "infrastructure/adapter/web/TaskController.java, "
            "infrastructure/adapter/web/dto/CreateTaskRequest.java, "
            "infrastructure/adapter/web/dto/UpdateTaskRequest.java, "
            "infrastructure/adapter/persistence/InMemoryTaskRepository.java, "
            "infrastructure/config/BeanConfig.java, "
            "shared/exception/TaskNotFoundException.java, shared/exception/GlobalExceptionHandler.java"
        ),
        "hexagonal": (
            "TaskManagerApplication.java, domain/model/Task.java, "
            "domain/port/in/TaskUseCase.java, domain/port/out/TaskRepositoryPort.java, "
            "domain/service/TaskServiceImpl.java, "
            "adapter/in/web/TaskController.java, "
            "adapter/in/web/dto/CreateTaskRequest.java, "
            "adapter/in/web/dto/UpdateTaskRequest.java, "
            "adapter/out/persistence/InMemoryTaskRepository.java, "
            "config/AppConfig.java, "
            "shared/exception/TaskNotFoundException.java, shared/exception/GlobalExceptionHandler.java"
        ),
        "ddd": (
            "TaskManagerApplication.java, domain/model/Task.java, "
            "domain/valueobject/TaskId.java, domain/repository/TaskRepository.java, "
            "application/service/TaskApplicationService.java, "
            "application/dto/CreateTaskCommand.java, application/dto/UpdateTaskCommand.java, "
            "infrastructure/persistence/InMemoryTaskRepositoryImpl.java, "
            "interfaces/rest/TaskController.java, "
            "interfaces/rest/dto/CreateTaskRequest.java, "
            "interfaces/rest/dto/UpdateTaskRequest.java, "
            "shared/exception/TaskNotFoundException.java, shared/exception/GlobalExceptionHandler.java"
        ),
        "event-driven": (
            "TaskManagerApplication.java, model/Task.java, "
            "event/TaskCreatedEvent.java, event/TaskUpdatedEvent.java, "
            "event/TaskDeletedEvent.java, "
            "command/CreateTaskCommand.java, command/UpdateTaskCommand.java, "
            "command/DeleteTaskCommand.java, "
            "handler/TaskCommandHandler.java, handler/TaskEventHandler.java, "
            "repository/TaskRepository.java, controller/TaskController.java, "
            "dto/CreateTaskRequest.java, dto/UpdateTaskRequest.java, "
            "exception/TaskNotFoundException.java, exception/GlobalExceptionHandler.java"
        ),
        "cqrs": (
            "TaskManagerApplication.java, model/Task.java, "
            "command/CreateTaskCommand.java, command/UpdateTaskCommand.java, "
            "command/DeleteTaskCommand.java, "
            "command/handler/CreateTaskCommandHandler.java, "
            "command/handler/UpdateTaskCommandHandler.java, "
            "command/handler/DeleteTaskCommandHandler.java, "
            "query/GetAllTasksQuery.java, query/GetTaskByIdQuery.java, "
            "query/handler/GetAllTasksQueryHandler.java, "
            "query/handler/GetTaskByIdQueryHandler.java, "
            "store/TaskStore.java, controller/TaskController.java, "
            "dto/CreateTaskRequest.java, dto/UpdateTaskRequest.java, "
            "exception/TaskNotFoundException.java, exception/GlobalExceptionHandler.java"
        ),
    })

    arch_test_file: dict = field(default_factory=lambda: {
        "mvc":                "TaskControllerTest.java",
        "vertical-slice":     "task/TaskControllerTest.java",
        "clean-architecture": "infrastructure/adapter/web/TaskControllerTest.java",
        "hexagonal":          "adapter/in/web/TaskControllerTest.java",
        "ddd":                "interfaces/rest/TaskControllerTest.java",
        "event-driven":       "controller/TaskControllerTest.java",
        "cqrs":               "controller/TaskControllerTest.java",
    })


# Instância padrão
config = BenchmarkConfig()
