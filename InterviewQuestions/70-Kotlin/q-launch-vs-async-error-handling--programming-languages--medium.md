---
id: lang-031
title: "Launch Vs Async Error Handling / Launch против Async: обработка ошибок"
aliases: ["Launch Vs Async Error Handling", "Launch против Async Обработка"]
topic: kotlin
subtopics: [coroutines]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-concurrency, q-suspend-function-suspension-mechanism--programming-languages--hard, q-what-is-job-object--programming-languages--medium]
created: 2024-10-15
updated: 2025-11-11
tags: [kotlin, coroutines, difficulty/medium, error-handling, exception-handling]
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
- как это связано со структурированной конкуррентностью ([[c-concurrency]]).

Ключевые моменты:
- В `launch` неперехваченные исключения считаются сбоем корутины и по умолчанию являются "unhandled" (если не перехвачены внутри корутины или через `CoroutineExceptionHandler`). У дочерних корутин `launch` исключение по умолчанию отменяет родительский scope и всех "соседей" (если это не supervisor).
- В `async` исключения сохраняются внутри `Deferred<T>` и повторно выбрасываются только при вызове `await()`. В составе структурированной иерархии, если родитель отменяется из-за других ошибок, соответствующие `async` также отменяются, и их исключения могут проявиться как `CancellationException` при `await()`. Для корневых `async` (например, созданных в `GlobalScope`) ситуация другая: непойманное исключение ведет себя как в root-корутинах `launch` и обрабатывается как "unhandled" через `CoroutineExceptionHandler`.

### Launch - распространение исключений

```kotlin
import kotlinx.coroutines.*

// launch: неперехваченные исключения в корутине считаются её сбоем
// и передаются вверх по иерархии (отменяя родителя, если это обычный Job)
fun launchErrorExample() = runBlocking {
    val job = launch {
        delay(100)
        throw RuntimeException("Error in launch")
    }

    try {
        job.join() // join() пробрасывает CancellationException, если родительский scope отменён
    } catch (e: CancellationException) {
        println("Parent cancelled due to child failure: ${e.message}")
    }
    // Само исключение логируется/обрабатывается механизмом родительского контекста
}

// Исключение в дочернем launch отменяет родительский scope (если это не supervisor)
fun launchCrash() = runBlocking {
    launch {
        throw RuntimeException("Crash!")  // Ошибка в дочерней корутине; отменяет runBlocking
    }

    delay(1000)
    println("This won't print")  // Не будет выполнено из-за отмены runBlocking
}
```

### Async - исключения в Deferred

```kotlin
import kotlinx.coroutines.*

// async в рамках структурированной конкуррентности сохраняет исключение в Deferred
// и повторно выбрасывает его при await() для наблюдающей стороны
fun asyncErrorExample() = runBlocking {
    val deferred = async {
        delay(100)
        throw RuntimeException("Error in async")
    }

    try {
        deferred.await()  // Исключение выбрасывается здесь для наблюдателя
    } catch (e: Exception) {
        println("Caught: ${e.message}")
    }

    println("Program continues")
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
        val job = launch {
            throw Exception("Launch error")
        }
        job.join()
    } catch (e: CancellationException) {
        // Для дочерних launch- корутин ошибка обычно проявляется как отмена родителя,
        // и эту отмену (CancellationException) можно наблюдать через join().
        println("Observed cancellation from child failure: ${e.message}")
    }

    println("\n=== async error ===")
    try {
        async {
            throw Exception("Async error")
        }.await()
    } catch (e: Exception) {
        // Для async исключение напрямую перекидывается на await() и обрабатывается здесь.
        println("Outer catch: ${e.message}")
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

    // Важно: CoroutineExceptionHandler срабатывает только для неперехваченных исключений
    // в корутинах верхнего уровня (root coroutines) для данного контекста
    val scope = CoroutineScope(Job() + handler)

    scope.launch {
        throw RuntimeException("Error")  // Будет перехвачено handler как root coroutine
    }

    delay(100)
    println("Scope still alive")
}

// Пример с несколькими корутинами и handler на корневом launch
fun multipleWithHandler() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("Handler caught: ${exception.message}")
    }

    // Handler должен быть в контексте корневой корутины, где исключение остаётся неперехваченным
    launch(handler) {
        launch {
            throw Exception("Error 1")  // Поднимется и будет пойман handler корневого launch
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
    // Делайте: оборачивайте async.await() в try-catch (в этом же scope или уровнем выше)
    suspend fun good1() = coroutineScope {
        try {
            val result = async { riskyOperation() }.await()
            process(result)
        } catch (e: Exception) {
            handleError(e)
        }
    }

    // Делайте: используйте CoroutineExceptionHandler с launch в контексте корневых корутин,
    // где исключение может остаться неперехваченным
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

    // Не делайте: игнорировать тот факт, что ошибки дочерних launch проявляются как отмена родителя;
    // полагайтесь на обработку через CancellationException, внутренние try-catch или handler там,
    // где это уместно.
    suspend fun bad1() = coroutineScope {
        try {
            val job = launch {
                throw Exception("Error")
            }
            job.join()
        } catch (e: Exception) {
            // В реальных сценариях предпочтительнее обрабатывать ошибку внутри корутины
            // или через CoroutineExceptionHandler для root-coroutines.
        }
    }

    // Не делайте: не создавайте async без осознанной обработки исключений при await()
    // (либо в этом scope, либо у вызывающего кода); и не используйте async там, где не нужна конкуррентность.
    suspend fun bad2() = coroutineScope {
        val result = async { riskyOperation() }.await()  // Если бросает, это должно быть обработано этим или внешним scope
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
| Error timing | Неперехваченное исключение немедленно завершает корутину и инициирует отмену родителя/handler | Исключение хранится в Deferred и наблюдается при await(); в root-async без await ведет себя как unhandled |
| Propagation | К родителю; отменяет родителя/"соседей" (non-supervisor) | Вверх по цепочке при await(); в supervisorScope не отменяет соседей автоматически |
| Catch with try-catch | Обычно: внутри корутины или через наблюдаемую отмену (CancellationException) и CoroutineExceptionHandler | Да, вокруг await() |
| Exception handler | Используется для root-coroutines launch | Обычно не нужен: ошибки обрабатываются через await(); для root-async без await применяется handler |
| Scope cancellation | Сбой отменяет родителя и детей (non-supervisor) | Зависит от того, как родитель обрабатывает исключения из await() |
| Selective handling | Ограничена структурой | Да, по каждому Deferred отдельно |
| Best for | Fire-and-forget / структурированные сайд-эффекты | Операции с результатом, тонкая настройка обработки ошибок |

## Answer (EN)

Yes, errors (exceptions) behave differently in `launch` and `async`, especially regarding:
- when the exception is observed;
- how it propagates through the coroutine hierarchy;
- how it interacts with structured concurrency ([[c-concurrency]]).

Key points:
- In `launch`, uncaught exceptions are treated as failures of the coroutine and, by default, are "unhandled" (unless caught inside the coroutine or handled via `CoroutineExceptionHandler`). For child `launch` coroutines, the exception typically cancels the parent scope and siblings (unless it's a supervisor).
- In `async`, exceptions are captured in the `Deferred<T>` and are rethrown when `await()` is called by the observing code. Within structured concurrency, if the parent is cancelled due to other failures, the corresponding `async` are cancelled and their failures may surface as `CancellationException` on `await()`. For root `async` coroutines (e.g., in `GlobalScope`), an unobserved exception behaves like in root `launch` coroutines and is handled as "unhandled" via `CoroutineExceptionHandler`.

### Launch - Exception Propagation

```kotlin
import kotlinx.coroutines.*

// launch: uncaught exceptions in a coroutine are treated as its failure
// and propagate up, cancelling the parent if it's a regular Job
fun launchErrorExample() = runBlocking {
    val job = launch {
        delay(100)
        throw RuntimeException("Error in launch")
    }

    try {
        job.join() // join() can throw CancellationException if parent scope is cancelled
    } catch (e: CancellationException) {
        println("Parent cancelled due to child failure: ${e.message}")
    }
    // The original exception is logged/handled by the parent context machinery
}

// Exception in a child launch cancels the parent scope (non-supervisor)
fun launchCrash() = runBlocking {
    launch {
        throw RuntimeException("Crash!")  // Fails this child; cancels runBlocking
    }

    delay(1000)
    println("This won't print")  // Not reached due to runBlocking cancellation
}
```

### Async - Deferred Exception

```kotlin
import kotlinx.coroutines.*

// async within structured concurrency stores the exception in Deferred
// and rethrows it on await() for the observer
fun asyncErrorExample() = runBlocking {
    val deferred = async {
        delay(100)
        throw RuntimeException("Error in async")
    }

    try {
        deferred.await()  // Exception is thrown here for the observer
    } catch (e: Exception) {
        println("Caught: ${e.message}")
    }

    println("Program continues")
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
        val job = launch {
            throw Exception("Launch error")
        }
        job.join()
    } catch (e: CancellationException) {
        // For child launch coroutines, the failure usually manifests as parent cancellation,
        // which you can observe as CancellationException when joining.
        println("Observed cancellation from child failure: ${e.message}")
    }

    println("\n=== async error ===")
    try {
        async {
            throw Exception("Async error")
        }.await()
    } catch (e: Exception) {
        // For async, the exception is rethrown on await() and can be caught here.
        println("Outer catch: ${e.message}")
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

    // CoroutineExceptionHandler is invoked only for uncaught exceptions in
    // root coroutines of this context
    val scope = CoroutineScope(Job() + handler)

    scope.launch {
        throw RuntimeException("Error")  // Caught by handler as a root coroutine
    }

    delay(100)
    println("Scope still alive")
}

// Example with multiple coroutines using a handler on the root launch
fun multipleWithHandler() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("Handler caught: ${exception.message}")
    }

    // Handler must be installed in the context of the root coroutine
    launch(handler) {
        launch {
            throw Exception("Error 1")  // Propagates and is caught by handler on root launch
        }
    }

    launch(handler) {
        launch {
            throw Exception("Error 2")  // Same behavior
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

    // Using launch - handle errors via CoroutineExceptionHandler or try-catch inside
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
            throw Exception("Error")  // Cancels this parent and thus its children
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
import kotlinx.coroutines.*

// supervisorScope: a failing child does not cancel its siblings
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
    // DO: Wrap async.await() in try-catch (either here or at the appropriate caller level)
    suspend fun good1() = coroutineScope {
        try {
            val result = async { riskyOperation() }.await()
            process(result)
        } catch (e: Exception) {
            handleError(e)
        }
    }

    // DO: Use CoroutineExceptionHandler with launch in the context of root coroutines
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

    // DON'T: Ignore that child launch failures surface as parent cancellation;
    // handle via CancellationException observation, internal try-catch, or a handler where appropriate.
    suspend fun bad1() = coroutineScope {
        try {
            val job = launch {
                throw Exception("Error")
            }
            job.join()
        } catch (e: Exception) {
            // In real code, prefer handling inside the coroutine or via CoroutineExceptionHandler
            // for root coroutines rather than relying solely on this pattern.
        }
    }

    // DON'T: Create async without a clear plan for handling await() exceptions
    // (either in this scope or by the caller); and avoid async when you don't need concurrency.
    suspend fun bad2() = coroutineScope {
        val result = async { riskyOperation() }.await()  // If this throws, it must be handled here or above
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
| Error timing | Uncaught exception immediately fails the coroutine and triggers parent cancellation/handler | Exception stored in Deferred and observed on await(); root async without await behaves as unhandled |
| Propagation | To parent; cancels parent/siblings (non-supervisor) | Via await() up the call chain; in supervisorScope doesn't auto-cancel siblings |
| Catch with try-catch | Commonly inside coroutine or via observing CancellationException/handler | Yes, around await() |
| Exception handler | Use CoroutineExceptionHandler for root launch coroutines | Typically handle via await(); handler applies for root async with unobserved failures |
| Scope cancellation | Failure cancels parent and children (non-supervisor) | Depends on how parent handles exceptions from await() |
| Selective handling | Limited by structure | Yes, per Deferred |
| Best for | Fire-and-forget / structured side effects | Result-returning operations with fine-grained error handling |

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
