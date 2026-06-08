package com.benchmark.taskmanager.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record CreateTaskRequest(
    @NotBlank(message = "title is required")
    @Size(max = 200, message = "title must not exceed 200 characters")
    String title,
    
    @Size(max = 1000, message = "description must not exceed 1000 characters")
    String description
) {}