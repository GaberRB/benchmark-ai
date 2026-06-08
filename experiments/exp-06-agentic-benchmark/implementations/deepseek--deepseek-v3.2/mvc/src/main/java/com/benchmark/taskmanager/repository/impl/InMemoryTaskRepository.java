package com.benchmark.taskmanager.repository.impl;

import com.benchmark.taskmanager.model.Task;
import com.benchmark.taskmanager.repository.TaskRepository;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

@Repository
public class InMemoryTaskRepository implements TaskRepository {
    private final Map<UUID, Task> tasks = new ConcurrentHashMap<>();

    @Override
    public List<Task> findAll() {
        return new ArrayList<>(tasks.values());
    }

    @Override
    public Task save(Task task) {
        tasks.put(task.getId(), task);
        return task;
    }

    @Override
    public Task findById(UUID id) {
        return tasks.get(id);
    }

    @Override
    public void deleteById(UUID id) {
        tasks.remove(id);
    }

    @Override
    public Task update(Task task) {
        tasks.put(task.getId(), task);
        return task;
    }
}</｜DSML｜parameter<｜DSML｜parameter name="path" string="true">src/main/java/com/benchmark/taskmanager/repository/impl/InMemoryTaskRepository.java