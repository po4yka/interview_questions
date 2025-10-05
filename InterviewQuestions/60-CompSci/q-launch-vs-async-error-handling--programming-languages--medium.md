---
tags:
  - programming-languages
difficulty: medium
---

# Error Handling Differences: Launch vs Async

## Answer

Yes, **errors (Exceptions) are handled differently** in launch and async:

**launch:**
- Exceptions are thrown immediately
- Exception propagates to parent CoroutineScope
- Without try-catch or exception handler, crashes parent scope
- Can be caught with CoroutineExceptionHandler

**async:**
- Exceptions are stored in Deferred<T>
- Not thrown until await() is called
- Can be caught with try-catch around await()
- Allows selective error handling

### launch - Immediate Exception Propagation

```kotlin
import kotlinx.coroutines.*

// launch throws exception immediately
fun launchErrorExample() = runBlocking {
    try {
        val job = launch {
            delay(100)
            throw RuntimeException("Error in launch")
        }
        job.join()
    } catch (e: Exception) {
        // ❌ Won't catch here!
        println("Caught: ${e.message}")
    }
    // Exception propagates to parent scope
}

// Exception crashes the parent scope
fun launchCrash() = runBlocking {
    launch {
        throw RuntimeException("Crash!")  // Crashes runBlocking
    }

    delay(1000)
    println("This won't print")  // Never reached
}
```

### async - Deferred Exception

```kotlin
// async stores exception in Deferred
fun asyncErrorExample() = runBlocking {
    val deferred = async {
        delay(100)
        throw RuntimeException("Error in async")
    }

    try {
        deferred.await()  // ✅ Exception thrown here
    } catch (e: Exception) {
        println("Caught: ${e.message}")  // ✅ Catches here!
    }

    println("Program continues")  // Continues execution
}

// Multiple async with selective error handling
suspend fun selectiveErrorHandling() = coroutineScope {
    val result1 = async { fetchData1() }
    val result2 = async { fetchData2() }  // May fail
    val result3 = async { fetchData3() }

    val data1 = result1.await()  // Get first result

    val data2 = try {
        result2.await()  // May throw
    } catch (e: Exception) {
        "Fallback data"  // Use fallback
    }

    val data3 = result3.await()  // Get third result

    CombinedData(data1, data2, data3)
}
```

### Error Handling Comparison

```kotlin
fun compareErrorHandling() = runBlocking {
    println("=== launch error ===")
    try {
        launch {
            throw Exception("Launch error")
        }.join()
    } catch (e: Exception) {
        println("Outer catch: ${e.message}")  // ❌ Not caught
    }

    println("\n=== async error ===")
    try {
        async {
            throw Exception("Async error")
        }.await()
    } catch (e: Exception) {
        println("Outer catch: ${e.message}")  // ✅ Caught!
    }
}
```

### launch with CoroutineExceptionHandler

```kotlin
// Proper error handling for launch
fun launchWithHandler() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("Caught by handler: ${exception.message}")
    }

    val scope = CoroutineScope(Job() + handler)

    scope.launch {
        throw RuntimeException("Error")  // Caught by handler
    }

    delay(100)
    println("Scope still alive")
}

// Example with multiple coroutines
fun multipleWithHandler() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("Handler caught: ${exception.message}")
    }

    launch(handler) {
        launch {
            throw Exception("Error 1")  // Caught
        }
    }

    launch(handler) {
        launch {
            throw Exception("Error 2")  // Caught
        }
    }

    delay(100)
}
```

### Real-World Example: Data Loading

```kotlin
class DataViewModel {
    // Using launch - needs exception handler
    fun loadDataWithLaunch() {
        val handler = CoroutineExceptionHandler { _, exception ->
            _error.value = exception.message
            _loading.value = false
        }

        viewModelScope.launch(handler) {
            _loading.value = true
            val data = repository.fetchData()  // May throw
            _data.value = data
            _loading.value = false
        }
    }

    // Using async - can use try-catch
    fun loadDataWithAsync() {
        viewModelScope.launch {
            _loading.value = true

            try {
                val data = async { repository.fetchData() }.await()
                _data.value = data
            } catch (e: Exception) {
                _error.value = e.message
            } finally {
                _loading.value = false
            }
        }
    }
}
```

### Parallel Error Handling

```kotlin
// async allows per-task error handling
suspend fun parallelWithErrors() = coroutineScope {
    val result1 = async { fetchData1() }
    val result2 = async { fetchData2() }
    val result3 = async { fetchData3() }

    val data1 = try {
        result1.await()
    } catch (e: Exception) {
        Data("Error: ${e.message}")
    }

    val data2 = try {
        result2.await()
    } catch (e: Exception) {
        Data("Error: ${e.message}")
    }

    val data3 = try {
        result3.await()
    } catch (e: Exception) {
        Data("Error: ${e.message}")
    }

    CombinedData(data1, data2, data3)  // All results available
}

// launch - one error cancels all
fun launchParallel() = runBlocking {
    launch {
        launch {
            delay(100)
            throw Exception("Error")  // Cancels siblings
        }

        launch {
            delay(200)
            println("Task 2")  // Won't print
        }

        launch {
            delay(300)
            println("Task 3")  // Won't print
        }
    }
}
```

### supervisorScope for Independent Errors

```kotlin
// supervisorScope: Errors don't affect siblings
suspend fun supervisorExample() = supervisorScope {
    // With launch
    launch {
        throw Exception("Error 1")  // Only this fails
    }

    launch {
        delay(100)
        println("Task 2 completes")  // ✅ Still runs
    }
}

// With async in supervisorScope
suspend fun supervisorAsync() = supervisorScope {
    val result1 = async {
        throw Exception("Error 1")
    }

    val result2 = async {
        delay(100)
        "Success"
    }

    val data1 = try {
        result1.await()
    } catch (e: Exception) {
        "Failed"
    }

    val data2 = result2.await()  // ✅ Succeeds

    Pair(data1, data2)  // ("Failed", "Success")
}
```

### Best Practices

```kotlin
class ErrorHandlingBestPractices {
    // ✅ DO: Use try-catch with async.await()
    suspend fun good1() = coroutineScope {
        try {
            val result = async { riskyOperation() }.await()
            process(result)
        } catch (e: Exception) {
            handleError(e)
        }
    }

    // ✅ DO: Use CoroutineExceptionHandler with launch
    fun good2() = viewModelScope.launch {
        val handler = CoroutineExceptionHandler { _, exception ->
            handleError(exception)
        }

        withContext(handler) {
            riskyOperation()
        }
    }

    // ✅ DO: Use supervisorScope for independent tasks
    suspend fun good3() = supervisorScope {
        launch { task1() }  // Errors don't affect task2
        launch { task2() }
    }

    // ❌ DON'T: Expect to catch launch errors with try-catch
    suspend fun bad1() {
        try {
            launch {
                throw Exception("Error")
            }.join()
        } catch (e: Exception) {
            // ❌ Won't catch!
        }
    }

    // ❌ DON'T: Use async without handling await() errors
    suspend fun bad2() {
        val result = async { riskyOperation() }.await()  // ❌ Uncaught error
        process(result)
    }
}
```

### Summary Table

| Feature | launch | async |
|---------|--------|-------|
| **Error timing** | Immediate | On await() |
| **Propagation** | To parent scope | Stored in Deferred |
| **Catch with try-catch** | No (around launch) | Yes (around await) |
| **Exception handler** | CoroutineExceptionHandler | Not needed |
| **Scope cancellation** | Cancels siblings | Only if await() throws |
| **Selective handling** | No | Yes |
| **Best for** | Fire-and-forget | Operations with results |

---

## Вопрос (RU)

Есть ли отличия между launch и async в обработке ошибок

## Ответ

Да, ошибки (Exceptions) обрабатываются по-разному в launch и async! Ошибки в `launch` – падают сразу. Launch сразу выбрасывает исключение, и если нет try-catch, корутина завершает родительский CoroutineScope. В `async` ошибка не выбрасывается сразу, а сохраняется в Deferred<T>. Она появится только при вызове await().
