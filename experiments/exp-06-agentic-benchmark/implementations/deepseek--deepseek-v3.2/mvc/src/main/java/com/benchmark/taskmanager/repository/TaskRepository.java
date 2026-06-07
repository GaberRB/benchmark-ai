package com.benchmark.taskmanager.repository;

import com.benchmark.taskmanager.model.Task;

import java.util.List;
import java.util.UUID;

public interface TaskRepository {
    List<Task> findAll();
    Task save(Task task);
    Task findById(UUID id);
    void deleteById(UUID id);
    Task update(Task task);
}