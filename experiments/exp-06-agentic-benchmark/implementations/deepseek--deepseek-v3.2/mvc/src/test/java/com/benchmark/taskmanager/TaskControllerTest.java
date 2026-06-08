package com.benchmark.taskmanager;

import com.benchmark.taskmanager.dto.CreateTaskRequest;
import com.benchmark.taskmanager.dto.UpdateTaskRequest;
import com.benchmark.taskmanager.exception.TaskNotFoundException;
import com.benchmark.taskmanager.model.Task;
import com.benchmark.taskmanager.service.TaskService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.UUID;

import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.is;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class TaskControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private TaskService taskService;

    @Autowired
    private ObjectMapper objectMapper;

    private UUID taskId;
    private Task task;

    @BeforeEach
    void setUp() {
        taskId = UUID.randomUUID();
        LocalDateTime now = LocalDateTime.now();
        task = new Task(taskId, "Test Task", "Test Description", false, now, now);
    }

    @Test
    void getAllTasks_EmptyList() throws Exception {
        when(taskService.getAllTasks()).thenReturn(Collections.emptyList());

        mockMvc.perform(get("/tasks"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(0)));
    }

    @Test
    void getAllTasks_WithItems() throws Exception {
        when(taskService.getAllTasks()).thenReturn(Arrays.asList(task));

        mockMvc.perform(get("/tasks"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].id", is(taskId.toString())))
                .andExpect(jsonPath("$[0].title", is("Test Task")));
    }

    @Test
    void createTask_ValidRequest_Returns201() throws Exception {
        CreateTaskRequest request = new CreateTaskRequest("New Task", "New Description");
        Task createdTask = Task.create(request.title(), request.description());
        when(taskService.createTask(any(CreateTaskRequest.class))).thenReturn(createdTask);

        mockMvc.perform(post("/tasks")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").exists())
                .andExpect(jsonPath("$.title", is("New Task")))
                .andExpect(jsonPath("$.completed", is(false)));
    }

    @Test
    void createTask_MissingTitle_Returns400() throws Exception {
        CreateTaskRequest request = new CreateTaskRequest("", "Description");

        mockMvc.perform(post("/tasks")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").exists());
    }

    @Test
    void createTask_TitleTooLong_Returns400() throws Exception {
        // Create a string with 201 'a' characters
        StringBuilder longTitleBuilder = new StringBuilder();
        for (int i = 0; i < 201; i++) {
            longTitleBuilder.append('a');
        }
        String longTitle = longTitleBuilder.toString();
        CreateTaskRequest request = new CreateTaskRequest(longTitle, "Description");

        mockMvc.perform(post("/tasks")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").exists());
    }

    @Test
    void getTaskById_ExistingId_Returns200() throws Exception {
        when(taskService.getTaskById(taskId)).thenReturn(task);

        mockMvc.perform(get("/tasks/{id}", taskId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id", is(taskId.toString())))
                .andExpect(jsonPath("$.title", is("Test Task")));
    }

    @Test
    void getTaskById_NonExistentId_Returns404() throws Exception {
        when(taskService.getTaskById(any(UUID.class)))
                .thenThrow(new TaskNotFoundException("Task not found"));

        mockMvc.perform(get("/tasks/{id}", UUID.randomUUID()))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.error", is("Task not found")));
    }

    @Test
    void updateTask_ValidRequest_Returns200() throws Exception {
        UpdateTaskRequest request = new UpdateTaskRequest("Updated Task", "Updated Description", true);
        Task updatedTask = new Task(taskId, "Updated Task", "Updated Description", true, 
                                   LocalDateTime.now(), LocalDateTime.now());
        
        when(taskService.updateTask(eq(taskId), any(UpdateTaskRequest.class))).thenReturn(updatedTask);

        mockMvc.perform(put("/tasks/{id}", taskId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.title", is("Updated Task")))
                .andExpect(jsonPath("$.completed", is(true)));
    }

    @Test
    void updateTask_NonExistentId_Returns404() throws Exception {
        UpdateTaskRequest request = new UpdateTaskRequest("Updated Task", "Updated Description", true);
        
        when(taskService.updateTask(any(UUID.class), any(UpdateTaskRequest.class)))
                .thenThrow(new TaskNotFoundException("Task not found"));

        mockMvc.perform(put("/tasks/{id}", UUID.randomUUID())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.error", is("Task not found")));
    }

    @Test
    void deleteTask_ExistingId_Returns204() throws Exception {
        doNothing().when(taskService).deleteTask(taskId);

        mockMvc.perform(delete("/tasks/{id}", taskId))
                .andExpect(status().isNoContent());
        
        verify(taskService, times(1)).deleteTask(taskId);
    }

    @Test
    void deleteTask_NonExistentId_Returns404() throws Exception {
        doThrow(new TaskNotFoundException("Task not found"))
                .when(taskService).deleteTask(any(UUID.class));

        mockMvc.perform(delete("/tasks/{id}", UUID.randomUUID()))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.error", is("Task not found")));
    }

    @Test
    void createTask_DescriptionTooLong_Returns400() throws Exception {
        // Create a string with 1001 'a' characters
        StringBuilder longDescriptionBuilder = new StringBuilder();
        for (int i = 0; i < 1001; i++) {
            longDescriptionBuilder.append('a');
        }
        String longDescription = longDescriptionBuilder.toString();
        CreateTaskRequest request = new CreateTaskRequest("Valid Title", longDescription);

        mockMvc.perform(post("/tasks")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").exists());
    }
}