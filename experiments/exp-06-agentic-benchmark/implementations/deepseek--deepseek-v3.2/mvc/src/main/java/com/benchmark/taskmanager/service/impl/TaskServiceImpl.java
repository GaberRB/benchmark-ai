package com.benchmark.taskmanager.service.impl;

import com.benchmark.taskmanager.dto.CreateTaskRequest;
import com.benchmark.taskmanager.dto.UpdateTaskRequest;
import com.benchmark.taskmanager.exception.TaskNotFoundException;
import com.benchmark.taskmanager.model.Task;
import com.benchmark.taskmanager.repository.TaskRepository;
import com.benchmark.taskmanager.service.TaskService;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;

@Service
public class TaskServiceImpl implements TaskService {
    private final TaskRepository taskRepository;

    public TaskServiceImpl(TaskRepository taskRepository) {
        this.taskRepository = taskRepository;
    }

    @Override
    public List<Task> getAllTasks() {
        return taskRepository.findAll();
    }

    @Override
    public Task createTask(CreateTaskRequest request) {
        Task task = Task.create(request.title(), request.description());
        return taskRepository.save(task);
    }

    @Override
    public Task getTaskById(UUID id) {
        Task task = taskRepository.findById(id);
        if (task == null) {
            throw new TaskNotFoundException("Task not found with id: " + id);
        }
        return task;
    }

    @Override
    public Task updateTask(UUID id, UpdateTaskRequest request) {
        Task task = getTaskById(id);
        
        // Validate title if provided (not null and not blank)
        if (request.title() != null && request.title().isBlank()) {
            throw new IllegalArgumentException("title cannot be blank");
        }
        
        // Validate description length if provided
        if (request.description() != null && request.description().length() > 1000) {
            throw new IllegalArgumentException("description must not exceed 1000 characters");
        }
        
        // Validate title length if provided
        if (request.title() != null && request.title().length() > 200) {
            throw new IllegalArgumentException("title must not exceed 200 characters");
        }
        
        task.update(request.title(), request.description(), request.completed());
        return taskRepository.update(task);
    }

    @Override
    public void deleteTask(UUID id) {
        // Check if task exists
        getTaskById(id);
        taskRepository.deleteById(id);
    }
}