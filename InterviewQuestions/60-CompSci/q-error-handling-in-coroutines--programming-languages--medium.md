---
id: 20251012-1227111131
title: "Error Handling In Coroutines"
topic: computer-science
difficulty: medium
status: draft
moc: moc-cs
related: [q-data-sealed-classes-why--programming-languages--medium, q-hashmap-how-it-works--programming-languages--medium, q-where-to-call-suspend-functions--programming-languages--medium]
created: 2025-10-15
tags: [programming-languages]
date created: Saturday, October 4th 2025, 10:56:46 am
date modified: Sunday, October 26th 2025, 11:57:38 am
---

# Error Handling Methods in Coroutines

# Question (EN)
> What methods are known for error handling in coroutines?

# Вопрос (RU)
> Какие известны способы обработки ошибок в корутинах?

---

## Answer (EN)

There are several ways to handle errors in coroutines:

1. **Try-catch inside launch/async**: Local error handling
2. **CoroutineExceptionHandler**: Global exception handler for uncaught exceptions
3. **supervisorScope**: Prevent error propagation to sibling coroutines
4. **Result type**: Wrap results in Result<T> for functional error handling

### Method 1: Try-Catch

```kotlin
import kotlinx.coroutines.*

// Inside launch
fun tryCatchInLaunch() = runBlocking {
    launch {
        try {
            riskyOperation()
        } catch (e: Exception) {
            println("Caught in launch: ${e.message}")
        }
    }
}

// Inside async
suspend fun tryCatchInAsync() = coroutineScope {
    val result = async {
        try {
            riskyOperation()
        } catch (e: Exception) {
            "Fallback value"
        }
    }.await()

    println("Result: $result")
}

// Around await()
suspend fun tryCatchAroundAwait() = coroutineScope {
    val deferred = async { riskyOperation() }

    val result = try {
        deferred.await()
    } catch (e: Exception) {
        "Fallback value"
    }

    println("Result: $result")
}
```

### Method 2: CoroutineExceptionHandler

```kotlin
// Global exception handler
fun exceptionHandler() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("Caught by handler: ${exception.message}")
    }

    val scope = CoroutineScope(Job() + handler)

    scope.launch {
        throw RuntimeException("Error!")  // Caught by handler
    }

    delay(100)
}

// In Android ViewModel
class MyViewModel : ViewModel() {
    private val exceptionHandler = CoroutineExceptionHandler { _, exception ->
        _error.value = exception.message
    }

    fun loadData() {
        viewModelScope.launch(exceptionHandler) {
            val data = repository.fetchData()  // May throw
            _data.value = data
        }
    }
}
```

### Method 3: supervisorScope

```kotlin
// Prevent error propagation
suspend fun supervisorExample() = supervisorScope {
    launch {
        throw Exception("Error 1")  // Only this fails
    }

    launch {
        delay(100)
        println("Task 2 completes")  // Still runs
    }
}

// Multiple independent tasks
suspend fun loadWidgets() = supervisorScope {
    val handler = CoroutineExceptionHandler { _, exception ->
        logError(exception)
    }

    launch(handler) { loadWidget1() }  // Independent
    launch(handler) { loadWidget2() }  // Independent
    launch(handler) { loadWidget3() }  // Independent
}
```

### Method 4: Result Type

```kotlin
// Wrap in Result type
suspend fun safeOperation(): Result<String> {
    return try {
        Result.success(riskyOperation())
    } catch (e: Exception) {
        Result.failure(e)
    }
}

// Usage
suspend fun useResult() {
    safeOperation()
        .onSuccess { data -> println("Success: $data") }
        .onFailure { error -> println("Error: ${error.message}") }
}
```

### Best Practices

```kotlin
class ErrorHandlingBestPractices {
    // - DO: Use try-catch for local handling
    suspend fun good1() {
        try {
            riskyOperation()
        } catch (e: Exception) {
            handleError(e)
        }
    }

    // - DO: Use CoroutineExceptionHandler at scope level
    fun good2() {
        val handler = CoroutineExceptionHandler { _, e -> logError(e) }
        CoroutineScope(SupervisorJob() + handler).launch {
            // Work
        }
    }

    // - DO: Use supervisorScope for independent tasks
    suspend fun good3() = supervisorScope {
        launch { task1() }  // Errors don't affect task2
        launch { task2() }
    }

    // - DON'T: Swallow exceptions silently
    suspend fun bad1() {
        try {
            riskyOperation()
        } catch (e: Exception) {
            // Silent failure - bad!
        }
    }
}
```

---

## Ответ (RU)

1. Try-catch внутри launch {} или async {} – локальная обработка ошибок.\",

## Related Questions

- [[q-data-sealed-classes-why--programming-languages--medium]]
- [[q-hashmap-how-it-works--programming-languages--medium]]
- [[q-where-to-call-suspend-functions--programming-languages--medium]]
