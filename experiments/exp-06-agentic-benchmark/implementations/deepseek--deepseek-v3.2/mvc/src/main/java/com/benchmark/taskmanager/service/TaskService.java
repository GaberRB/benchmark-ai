package com.benchmark.taskmanager.service;

import com.benchmark.taskmanager.dto.CreateTaskRequest;
import com.benchmark.taskmanager.dto.UpdateTaskRequest;
import com.benchmark.taskmanager.model.Task;

import java.util.List;
import java.util.UUID;

public interface TaskService {
    List<Task> getAllTasks();
    Task createTask(CreateTaskRequest request);
    Task getTaskById(UUID id);
    Task updateTask(UUID id, UpdateTaskRequest request);
    void deleteTask(UUID id);
}