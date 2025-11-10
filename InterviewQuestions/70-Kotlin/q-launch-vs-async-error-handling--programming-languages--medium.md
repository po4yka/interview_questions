---
id: lang-031
title: "Launch Vs Async Error Handling / Launch против Async Обработка"
aliases: ["Launch Vs Async Error Handling", "Launch против Async Error Обработка"]
topic: kotlin
subtopics: [c-coroutines, c-structured-concurrency, c-kotlin]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-coroutines, q-suspend-function-suspension-mechanism--programming-languages--hard, q-what-is-job-object--programming-languages--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [coroutines, difficulty/medium, error-handling, exception-handling, kotlin]
---

# Вопрос (RU)
> Обрабатываются ли ошибки по-разному в launch и async?

---

# Question (EN)
> Are errors handled differently in launch and async?

## Ответ (RU)

Да, ошибки (exceptions) в `launch` и `async` ведут себя по-разному с точки зрения:
- когда исключение наблюдается;
- как оно распространяется по иерархии корутин;
- как это связано со структурированной конкуррентностью ([[c-structured-concurrency]]).

Ключевые моменты:
- В `launch` неперехваченные исключения считаются сбоем корутины и по умолчанию являются "unhandled" (если не перехвачены внутри корутины или через `CoroutineExceptionHandler`). В дочерних корутинах `launch` исключение обычно отменяет родительский scope (если это не supervisor).
- В `async` исключения сохраняются внутри `Deferred<T>` и повторно выбрасываются только при вызове `await()`. Если `await()` никогда не вызывается, исключение может остаться необработанным.

### Launch - распространение исключений

```kotlin
import kotlinx.coroutines.*

// launch: исключение сообщается, когда корутина завершается с ошибкой
fun launchErrorExample() = runBlocking {
    try {
        val job = launch {
            delay(100)
            throw RuntimeException("Error in launch")
        }
        job.join()
    } catch (e: Exception) {
        // Здесь для дочернего launch не поймаем:
        // исключение обрабатывается механизмом родительского контекста
        println("Caught: ${e.message}")
    }
    // Сбой дочернего launch репортится в родительский scope
}

// Исключение в дочернем launch отменяет родительский scope (если это не supervisor)
fun launchCrash() = runBlocking {
    launch {
        throw RuntimeException("Crash!")  // Ошибка в дочерней корутине; отменяет runBlocking
    }

    delay(1000)
    println("This won't print")  // Не будет выполнено из-за отмены
}
```

### Async - исключения в Deferred

```kotlin
import kotlinx.coroutines.*

// async сохраняет исключение в Deferred и выбрасывает его при await()
fun asyncErrorExample() = runBlocking {
    val deferred = async {
        delay(100)
        throw RuntimeException("Error in async")
    }

    try {
        deferred.await()  // Исключение выбрасывается здесь
    } catch (e: Exception) {
        println("Caught: ${e.message}")  // Обрабатывается здесь
    }

    println("Program continues")  // Продолжаем выполнение
}

// Несколько async с выборочной обработкой ошибок
suspend fun selectiveErrorHandling() = coroutineScope {
    val result1 = async { fetchData1() }
    val result2 = async { fetchData2() }  // Может завершиться с ошибкой
    val result3 = async { fetchData3() }

    val data1 = result1.await()

    val data2 = try {
        result2.await()  // Может выбросить
    } catch (e: Exception) {
        "Fallback data"
    }

    val data3 = result3.await()

    CombinedData(data1, data2, data3)
}
```

### Сравнение обработки ошибок

```kotlin
import kotlinx.coroutines.*

fun compareErrorHandling() = runBlocking {
    println("=== launch error ===")
    try {
        launch {
            throw Exception("Launch error")
        }.join()
    } catch (e: Exception) {
        // Для дочернего launch внешний try-catch НЕ видит исключение.
        println("Outer catch: ${e.message}")  // Не будет достигнуто, исключение обрабатывается контекстом родителя
    }

    println("\n=== async error ===")
    try {
        async {
            throw Exception("Async error")
        }.await()
    } catch (e: Exception) {
        // Для async исключение перекидывается на await() и может быть поймано здесь.
        println("Outer catch: ${e.message}")  // Будет поймано
    }
}
```

### Launch с CoroutineExceptionHandler

```kotlin
import kotlinx.coroutines.*

// Корректная обработка ошибок в launch с использованием CoroutineExceptionHandler
fun launchWithHandler() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("Caught by handler: ${exception.message}")
    }

    // Установим handler в контекст корутины
    val scope = CoroutineScope(Job() + handler)

    scope.launch {
        throw RuntimeException("Error")  // Будет перехвачено handler
    }

    delay(100)
    println("Scope still alive")
}

// Пример с несколькими корутинами и handler на родительском launch
fun multipleWithHandler() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("Handler caught: ${exception.message}")
    }

    // Handler должен быть в контексте корутины, где исключение остаётся неперехваченным
    launch(handler) {
        launch {
            throw Exception("Error 1")  // Поднимется и будет пойман handler родительского launch
        }
    }

    launch(handler) {
        launch {
            throw Exception("Error 2")  // Аналогично
        }
    }

    delay(100)
}
```

### Практический пример: загрузка данных

```kotlin
import kotlinx.coroutines.*

class DataViewModel {
    private val _loading = MutableStateFlow(false)
    private val _data = MutableStateFlow<Data?>(null)
    private val _error = MutableStateFlow<String?>(null)

    // Используем launch: обрабатываем ошибки через CoroutineExceptionHandler или try-catch внутри
    fun loadDataWithLaunch() {
        val handler = CoroutineExceptionHandler { _, exception ->
            _error.value = exception.message
            _loading.value = false
        }

        viewModelScope.launch(handler) {
            _loading.value = true
            val data = repository.fetchData()  // Может бросить исключение
            _data.value = data
            _loading.value = false
        }
    }

    // Используем async: обрабатываем через try-catch вокруг await()
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

### Параллельная обработка ошибок

```kotlin
import kotlinx.coroutines.*

// async позволяет обрабатывать ошибки для каждой задачи отдельно через await()
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

    CombinedData(data1, data2, data3)
}

// launch в обычном scope: одна необработанная ошибка отменяет соседние задачи (structured concurrency)
fun launchParallel() = runBlocking {
    launch {
        launch {
            delay(100)
            throw Exception("Error")  // Отменяет родителя и, следовательно, всех детей
        }

        launch {
            delay(200)
            println("Task 2")  // Не выполнится
        }

        launch {
            delay(300)
            println("Task 3")  // Не выполнится
        }
    }
}
```

### supervisorScope для независимых ошибок

```kotlin
import kotlinx.coroutines.*

// supervisorScope: сбой одной дочерней корутины не отменяет остальных
suspend fun supervisorExample() = supervisorScope {
    launch {
        throw Exception("Error 1")  // Падает только эта корутина
    }

    launch {
        delay(100)
        println("Task 2 completes")  // Всё ещё выполнится
    }
}

// Использование async в supervisorScope
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

    val data2 = result2.await()  // Успешно

    Pair(data1, data2)  // ("Failed", "Success")
}
```

### Рекомендации (Best Practices)

```kotlin
import kotlinx.coroutines.*

class ErrorHandlingBestPractices {
    // Делайте: оборачивайте async.await() в try-catch
    suspend fun good1() = coroutineScope {
        try {
            val result = async { riskyOperation() }.await()
            process(result)
        } catch (e: Exception) {
            handleError(e)
        }
    }

    // Делайте: используйте CoroutineExceptionHandler с launch в контексте корутины
    fun good2() = runBlocking {
        val handler = CoroutineExceptionHandler { _, exception ->
            handleError(exception)
        }

        launch(handler) {
            riskyOperation()
        }
    }

    // Делайте: используйте supervisorScope для независимых задач
    suspend fun good3() = supervisorScope {
        launch { task1() }  // Ошибки в task1 не отменяют task2
        launch { task2() }
    }

    // Не делайте: не рассчитывайте поймать ошибки дочернего launch внешним try-catch вот так
    suspend fun bad1() = coroutineScope {
        try {
            launch {
                throw Exception("Error")
            }.join()
        } catch (e: Exception) {
            // Не будет поймано: исключение репортится в родительский контекст
        }
    }

    // Не делайте: не используйте async без обработки ошибок await()
    suspend fun bad2() = coroutineScope {
        val result = async { riskyOperation() }.await()  // Если бросает, это должно быть обработано вызывающим кодом или этим scope
        process(result)
    }

    // Заглушки для полноты примера
    private suspend fun riskyOperation(): Int = 42
    private fun process(result: Int) {}
    private fun handleError(e: Throwable) {}
    private suspend fun task1() {}
    private suspend fun task2() {}
}
```

### Сводная таблица

| Feature | launch | async |
|---------|--------|-------|
| Error timing | Reported when coroutine fails (for unhandled exceptions) | Rethrown on await() |
| Propagation | To parent scope; cancels parent/siblings (non-supervisor) | Stored in Deferred; observed on await() |
| Catch with try-catch | Not around launch(...) for child failures; must catch inside the coroutine | Yes, around await() |
| Exception handler | Use CoroutineExceptionHandler in context | Usually handled via await()/try-catch; handler applies if installed in context |
| Scope cancellation | Failure cancels parent and siblings (non-supervisor) | Cancellation depends on how parent handles the failure from await() |
| Selective handling | Limited | Yes, per Deferred via await() |
| Best for | Fire-and-forget / structured side effects | Operations with results, fine-grained error handling |

## Answer (EN)

Yes, errors (exceptions) behave differently in launch and async, especially regarding:
- when the exception is observed;
- how it propagates through the coroutine hierarchy;
- how it interacts with structured concurrency ([[c-structured-concurrency]]).

Key points:
- In `launch`, uncaught exceptions are treated as failures of the coroutine and, by default, are "unhandled" (unless caught inside the coroutine or handled via `CoroutineExceptionHandler`). For child coroutines, the exception cancels the parent scope (unless it's a supervisor).
- In `async`, exceptions are captured in the `Deferred<T>` and are rethrown only when `await()` is called. If `await()` is never called, the exception may effectively remain unobserved.

### Launch - Exception Propagation

```kotlin
import kotlinx.coroutines.*

// launch: exception is reported when the coroutine fails
fun launchErrorExample() = runBlocking {
    try {
        val job = launch {
            delay(100)
            throw RuntimeException("Error in launch")
        }
        job.join()
    } catch (e: Exception) {
        // Won't catch here for this child launch:
        // the exception is handled by the parent context's machinery
        println("Caught: ${e.message}")
    }
    // The failure of the child launch is reported to the parent scope
}

// Exception in a child launch cancels the parent scope (non-supervisor)
fun launchCrash() = runBlocking {
    launch {
        throw RuntimeException("Crash!")  // Fails this child; cancels runBlocking
    }

    delay(1000)
    println("This won't print")  // Not reached due to cancellation
}
```

### Async - Deferred Exception

```kotlin
import kotlinx.coroutines.*

// async stores exception in Deferred and rethrows on await()
fun asyncErrorExample() = runBlocking {
    val deferred = async {
        delay(100)
        throw RuntimeException("Error in async")
    }

    try {
        deferred.await()  // Exception is thrown here
    } catch (e: Exception) {
        println("Caught: ${e.message}")  // Caught here
    }

    println("Program continues")  // Continues execution
}

// Multiple async with selective error handling
suspend fun selectiveErrorHandling() = coroutineScope {
    val result1 = async { fetchData1() }
    val result2 = async { fetchData2() }  // May fail
    val result3 = async { fetchData3() }

    val data1 = result1.await()

    val data2 = try {
        result2.await()  // May throw
    } catch (e: Exception) {
        "Fallback data"
    }

    val data3 = result3.await()

    CombinedData(data1, data2, data3)
}
```

### Error Handling Comparison

```kotlin
import kotlinx.coroutines.*

fun compareErrorHandling() = runBlocking {
    println("=== launch error ===")
    try {
        launch {
            throw Exception("Launch error")
        }.join()
    } catch (e: Exception) {
        // For a child launch, this outer try-catch does NOT see the exception.
        println("Outer catch: ${e.message}")  // Not reached because exception is handled by parent context
    }

    println("\n=== async error ===")
    try {
        async {
            throw Exception("Async error")
        }.await()
    } catch (e: Exception) {
        // For async, exception is rethrown on await() and can be caught here.
        println("Outer catch: ${e.message}")  // Caught
    }
}
```

### Launch with CoroutineExceptionHandler

```kotlin
import kotlinx.coroutines.*

// Proper error handling for launch using CoroutineExceptionHandler
fun launchWithHandler() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("Caught by handler: ${exception.message}")
    }

    // Install handler in the context of the launched coroutine
    val scope = CoroutineScope(Job() + handler)

    scope.launch {
        throw RuntimeException("Error")  // Caught by handler
    }

    delay(100)
    println("Scope still alive")
}

// Example with multiple coroutines using a handler on the parent launch
fun multipleWithHandler() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("Handler caught: ${exception.message}")
    }

    // Handler must be in the context of the coroutine where the exception is unhandled
    launch(handler) {
        launch {
            throw Exception("Error 1")  // Propagates up and is caught by handler on parent launch
        }
    }

    launch(handler) {
        launch {
            throw Exception("Error 2")  // Propagates up and is caught by handler on parent launch
        }
    }

    delay(100)
}
```

### Real-World Example: Data Loading

```kotlin
import kotlinx.coroutines.*

class DataViewModel {
    private val _loading = MutableStateFlow(false)
    private val _data = MutableStateFlow<Data?>(null)
    private val _error = MutableStateFlow<String?>(null)

    // Using launch - use CoroutineExceptionHandler or try-catch inside
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

    // Using async - handle via try-catch around await()
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
import kotlinx.coroutines.*

// async allows per-task error handling via await()
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

    CombinedData(data1, data2, data3)
}

// launch in a regular scope: one unhandled error cancels siblings (structured concurrency)
fun launchParallel() = runBlocking {
    launch {
        launch {
            delay(100)
            throw Exception("Error")  // Cancels parent of these children and thus siblings
        }

        launch {
            delay(200)
            println("Task 2")  // Won't print due to cancellation
        }

        launch {
            delay(300)
            println("Task 3")  // Won't print due to cancellation
        }
    }
}
```

### supervisorScope for Independent Errors

```kotlin
import kotlinx.coroutines.*

// supervisorScope: child failures don't cancel siblings
suspend fun supervisorExample() = supervisorScope {
    launch {
        throw Exception("Error 1")  // Only this child fails
    }

    launch {
        delay(100)
        println("Task 2 completes")  // Still runs
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

    val data2 = result2.await()  // Succeeds

    Pair(data1, data2)  // ("Failed", "Success")
}
```

### Best Practices

```kotlin
import kotlinx.coroutines.*

class ErrorHandlingBestPractices {
    // DO: Use try-catch around async.await()
    suspend fun good1() = coroutineScope {
        try {
            val result = async { riskyOperation() }.await()
            process(result)
        } catch (e: Exception) {
            handleError(e)
        }
    }

    // DO: Use CoroutineExceptionHandler with launch by installing it in the coroutine context
    fun good2() = runBlocking {
        val handler = CoroutineExceptionHandler { _, exception ->
            handleError(exception)
        }

        launch(handler) {
            riskyOperation()
        }
    }

    // DO: Use supervisorScope for independent tasks
    suspend fun good3() = supervisorScope {
        launch { task1() }  // Errors in task1 don't cancel task2
        launch { task2() }
    }

    // DON'T: Expect to catch child launch errors with outer try-catch like this
    suspend fun bad1() = coroutineScope {
        try {
            launch {
                throw Exception("Error")
            }.join()
        } catch (e: Exception) {
            // Won't catch: exception is reported to parent context instead
        }
    }

    // DON'T: Use async without handling await() errors
    suspend fun bad2() = coroutineScope {
        val result = async { riskyOperation() }.await()  // If it throws, must be caught by caller or this scope
        process(result)
    }

    // Placeholder implementations to keep the snippet self-contained
    private suspend fun riskyOperation(): Int = 42
    private fun process(result: Int) {}
    private fun handleError(e: Throwable) {}
    private suspend fun task1() {}
    private suspend fun task2() {}
}
```

### Summary Table

| Feature | launch | async |
|---------|--------|-------|
| Error timing | Reported when coroutine fails (for unhandled exceptions) | Rethrown on await() |
| Propagation | To parent scope; cancels parent/siblings (non-supervisor) | Stored in Deferred; observed on await() |
| Catch with try-catch | Not around launch(...) for child failures; must catch inside the coroutine | Yes, around await() |
| Exception handler | Use CoroutineExceptionHandler in context | Usually handled via await()/try-catch; handler applies if installed in context |
| Scope cancellation | Failure cancels parent and siblings (non-supervisor) | Cancellation depends on how parent handles the failure from await() |
| Selective handling | Limited | Yes, per Deferred via await() |
| Best for | Fire-and-forget / structured side effects | Operations with results, fine-grained error handling |

## Дополнительные вопросы (RU)

- В чем ключевые отличия по сравнению с обработкой исключений в Java?
- Когда на практике стоит предпочесть `launch` или `async` для обработки ошибок?
- Как избежать типичных ошибок при обработке исключений в корутинах?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные вопросы (RU)

- [[q-suspend-function-suspension-mechanism--programming-languages--hard]]
- [[q-what-is-job-object--programming-languages--medium]]

## Related Questions

- [[q-suspend-function-suspension-mechanism--programming-languages--hard]]
- [[q-what-is-job-object--programming-languages--medium]]
