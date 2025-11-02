---
id: lang-090
title: "What Is CoroutineScope / Что такое CoroutineScope"
aliases: [What Is CoroutineScope, Что такое CoroutineScope]
topic: programming-languages
subtopics: [coroutines, lifecycle, scope-management]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-programming-languages
related: [q-hot-vs-cold-flows--programming-languages--medium, q-template-method-pattern--design-patterns--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [coroutines, difficulty/medium, kotlin, programming-languages, scope]
date created: Saturday, October 4th 2025, 10:52:06 am
date modified: Saturday, November 1st 2025, 5:43:23 pm
---

# What is CoroutineScope?

# Question (EN)
> What is CoroutineScope?

# Вопрос (RU)
> Что такое CoroutineScope?

---

## Answer (EN)

**CoroutineScope** is an area/context in which coroutines execute in Kotlin. It defines the coroutine lifecycle and allows cancelling them when the scope finishes.

**Common scopes:**
- **GlobalScope**: Lives for the entire app lifetime, but rarely used (can cause leaks)
- **viewModelScope**: In ViewModel, cancelled when ViewModel is destroyed
- **lifecycleScope**: In Activity/Fragment, cancelled when UI is destroyed

CoroutineScope provides structured concurrency - when scope is cancelled, all child coroutines are automatically cancelled.

### Basic Concept

```kotlin
import kotlinx.coroutines.*

// CoroutineScope defines where coroutines run and their lifecycle
fun main() = runBlocking {  // Creates a scope
    // All coroutines in this scope
    launch {
        println("Coroutine 1")
    }

    launch {
        println("Coroutine 2")
    }

    // When scope ends, all coroutines are cancelled
}
```

### Creating Custom Scope

```kotlin
// Custom scope with specific lifecycle
class MyManager {
    private val scope = CoroutineScope(
        SupervisorJob() + Dispatchers.Default
    )

    fun startWork() {
        scope.launch {
            // Work is tied to scope lifecycle
            performTask()
        }
    }

    fun cleanup() {
        scope.cancel()  // Cancels all coroutines
    }
}
```

### Common Scopes

```kotlin
// 1. GlobalScope - application lifetime
GlobalScope.launch {
    // Runs for entire app lifetime
    // WARNING: Use with caution - can cause memory leaks
}

// 2. viewModelScope (Android)
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            // Cancelled when ViewModel is cleared
            val data = repository.fetchData()
            _uiState.value = data
        }
    }
}

// 3. lifecycleScope (Android)
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // Cancelled when Activity is destroyed
            collectData()
        }
    }
}

// 4. coroutineScope builder
suspend fun performTask() = coroutineScope {
    // Creates a scope for structured concurrency
    launch { subtask1() }
    launch { subtask2() }
    // Waits for all children to complete
}
```

### Scope Hierarchy

```kotlin
fun scopeHierarchy() = runBlocking {  // Parent scope
    launch {  // Child scope 1
        println("Child 1")
        launch {  // Grandchild
            println("Grandchild 1")
        }
    }

    launch {  // Child scope 2
        println("Child 2")
    }

    // When parent is cancelled, all children are cancelled
}
```

### Structured Concurrency

```kotlin
// All children must complete before parent completes
suspend fun structuredConcurrency() = coroutineScope {
    launch {
        delay(1000)
        println("Task 1 done")
    }

    launch {
        delay(2000)
        println("Task 2 done")
    }

    println("All tasks completed")  // Printed after both tasks
}
```

### Real-World Examples

```kotlin
// Android ViewModel
class UserViewModel : ViewModel() {
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            try {
                val userList = userRepository.getUsers()
                _users.value = userList
            } catch (e: Exception) {
                // Handle error
            }
        }
        // Automatically cancelled when ViewModel is cleared
    }
}

// Android Fragment
class UserFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        lifecycleScope.launch {
            viewModel.users.collect { users ->
                updateUI(users)
            }
        }
        // Automatically cancelled when Fragment is destroyed
    }
}

// Custom Service
class DataSyncService : Service() {
    private val serviceScope = CoroutineScope(
        SupervisorJob() + Dispatchers.IO
    )

    fun startSync() {
        serviceScope.launch {
            while (isActive) {
                syncData()
                delay(60_000)  // Sync every minute
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        serviceScope.cancel()  // Clean up
    }
}
```

### Scope Cancellation

```kotlin
fun scopeCancellation() = runBlocking {
    val job = launch {
        repeat(5) { i ->
            println("Job $i")
            delay(500)
        }
    }

    delay(1200)
    job.cancel()  // Cancel specific job
    println("Job cancelled")
}

// Cancel entire scope
fun cancelScope() {
    val scope = CoroutineScope(Dispatchers.Default)

    scope.launch { task1() }
    scope.launch { task2() }
    scope.launch { task3() }

    // Later...
    scope.cancel()  // Cancels all coroutines in scope
}
```

### Exception Handling in Scope

```kotlin
// SupervisorJob: Children failures don't affect siblings
val supervisorScope = CoroutineScope(SupervisorJob())

supervisorScope.launch {
    launch {
        throw Exception("Child 1 failed")  // Only this child fails
    }

    launch {
        delay(1000)
        println("Child 2 still running")  // Continues to run
    }
}

// Regular Job: One child failure cancels all siblings
val regularScope = CoroutineScope(Job())

regularScope.launch {
    launch {
        throw Exception("Child 1 failed")  // Fails
    }

    launch {
        delay(1000)
        println("Child 2")  // Never prints - cancelled
    }
}
```

### Best Practices

```kotlin
class ScopeBestPractices {
    // - DO: Use lifecycle-aware scopes in Android
    class GoodViewModel : ViewModel() {
        fun loadData() {
            viewModelScope.launch {  // Tied to ViewModel lifecycle
                fetchData()
            }
        }
    }

    // - DON'T: Use GlobalScope in Android
    class BadViewModel : ViewModel() {
        fun loadData() {
            GlobalScope.launch {  // Leaks when ViewModel is cleared
                fetchData()
            }
        }
    }

    // - DO: Create custom scope with proper cleanup
    class GoodManager {
        private val scope = CoroutineScope(SupervisorJob())

        fun start() {
            scope.launch { work() }
        }

        fun cleanup() {
            scope.cancel()  // Clean up resources
        }
    }

    // - DON'T: Create scope without cleanup mechanism
    class BadManager {
        private val scope = CoroutineScope(Dispatchers.Default)

        fun start() {
            scope.launch { work() }
        }
        // No cleanup - potential leak
    }
}
```

### Scope Context

```kotlin
// Scope with specific context
val ioScope = CoroutineScope(Dispatchers.IO + Job())

ioScope.launch {
    // Runs on IO dispatcher
    performIOOperation()
}

// Scope with exception handler
val handler = CoroutineExceptionHandler { _, exception ->
    println("Caught $exception")
}

val scopeWithHandler = CoroutineScope(
    Dispatchers.Default + SupervisorJob() + handler
)

scopeWithHandler.launch {
    throw Exception("Error")  // Caught by handler
}
```

### Testing with Scopes

```kotlin
class MyRepositoryTest {
    @Test
    fun testDataFetch() = runTest {  // Test scope
        val repository = MyRepository()

        val result = repository.fetchData()

        assertEquals(expected, result)
    }
}
```

### Summary

**CoroutineScope:**
- Defines coroutine lifecycle
- Enables structured concurrency
- Provides automatic cleanup
- Prevents resource leaks
- Manages parent-child relationships

**Key Points:**
- Always tie scopes to component lifecycle
- Use `viewModelScope` in ViewModels
- Use `lifecycleScope` in Activities/Fragments
- Avoid `GlobalScope` unless necessary
- Cancel scopes to prevent leaks

---


## Ответ (RU)

Это область, в которой выполняются корутины в Kotlin. Определяет жизненный цикл корутин и позволяет отменять их при завершении scope. GlobalScope – живет все время работы приложения, но редко используется. viewModelScope – в ViewModel, отменяется при уничтожении ViewModel. lifecycleScope – в Activity/Fragment, отменяется при уничтожении UI.

## Related Questions

- [[q-template-method-pattern--design-patterns--medium]]
- [[q-hot-vs-cold-flows--programming-languages--medium]]
