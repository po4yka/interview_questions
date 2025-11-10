---
id: lang-057
title: "Error Handling In Coroutines / Обработка ошибок в корутинах"
aliases: [Error Handling In Coroutines, Обработка ошибок в корутинах]
topic: kotlin
subtopics: [coroutines, concurrency, error-handling]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-coroutines, q-how-to-create-suspend-function--programming-languages--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [coroutines, difficulty/medium, error-handling, exception-handling, kotlin]
---
# Вопрос (RU)
> Какие известны способы обработки ошибок в корутинах?

## Ответ (RU)

Существует несколько распространённых способов обработки ошибок в корутинах:

1. Try-catch внутри `launch`/`async` (в том числе вокруг `await()`) — локальная обработка исключений.
2. `CoroutineExceptionHandler` — обработка необработанных исключений на уровне scope для корутин типа `launch`.
3. `supervisorScope` / `SupervisorJob` — когда нужно изолировать ошибки и не отменять "соседние" корутины.
4. Использование `Result<T>` — обёртка результата для явной, функциональной обработки ошибок.

### Метод 1: Try-Catch

```kotlin
import kotlinx.coroutines.*

// Внутри launch
fun tryCatchInLaunch() = runBlocking {
    launch {
        try {
            riskyOperation()
        } catch (e: Exception) {
            println("Caught in launch: ${e.message}")
        }
    }
}

// Внутри async (локальная обработка внутри async)
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

// Вокруг await() (исключение пробрасывается при await)
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

### Метод 2: CoroutineExceptionHandler

```kotlin
import kotlinx.coroutines.*

// Глобальный (на уровне scope) обработчик необработанных исключений в launch
fun exceptionHandler() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("Caught by handler: ${exception.message}")
    }

    val scope = CoroutineScope(Job() + handler)

    scope.launch {
        throw RuntimeException("Error!")  // Необработанное здесь -> попадёт в CoroutineExceptionHandler
    }

    delay(100)
}

// Примечания:
// - CoroutineExceptionHandler обрабатывает необработанные исключения из launch и других fire-and-forget корутин.
// - Для async исключения сохраняются и выбрасываются при await(), поэтому их нужно ловить через try-catch вокруг await().

// Пример в Android ViewModel
class MyViewModel : ViewModel() {
    private val exceptionHandler = CoroutineExceptionHandler { _, exception ->
        _error.value = exception.message
    }

    fun loadData() {
        viewModelScope.launch(exceptionHandler) {
            val data = repository.fetchData()  // Может бросить исключение
            _data.value = data
        }
    }
}
```

### Метод 3: supervisorScope / SupervisorJob

```kotlin
import kotlinx.coroutines.*

// supervisorScope: сбой одного потомка не отменяет других
suspend fun supervisorExample() = supervisorScope {
    launch {
        throw Exception("Error 1")  // Падает только эта корутина
    }

    launch {
        delay(100)
        println("Task 2 completes")  // Всё ещё выполнится
    }
}

// Несколько независимых задач с SupervisorJob
suspend fun loadWidgets() {
    val handler = CoroutineExceptionHandler { _, exception ->
        logError(exception)
    }

    val scope = CoroutineScope(SupervisorJob() + handler)

    scope.launch { loadWidget1() }  // Независимые задачи
    scope.launch { loadWidget2() }
    scope.launch { loadWidget3() }
}
```

// Примечания:
// - `supervisorScope` / `SupervisorJob` предотвращают отмену "соседних" корутин при падении одной.
// - Необработанное исключение в родительском scope (или не обработанное дочерней корутиной) всё ещё может отменить этот scope.

### Метод 4: Тип Result

```kotlin
// Обёртка результата в тип Result
suspend fun safeOperation(): Result<String> {
    return try {
        Result.success(riskyOperation())
    } catch (e: Exception) {
        Result.failure(e)
    }
}

// Использование
suspend fun useResult() {
    safeOperation()
        .onSuccess { data -> println("Success: $data") }
        .onFailure { error -> println("Error: ${error.message}") }
}
```

### Рекомендации (Best Practices)

```kotlin
class ErrorHandlingBestPractices {
    // DO: используйте try-catch для локальной обработки
    suspend fun good1() {
        try {
            riskyOperation()
        } catch (e: Exception) {
            handleError(e)
        }
    }

    // DO: используйте CoroutineExceptionHandler на уровне scope для необработанных исключений в launch
    fun good2() {
        val handler = CoroutineExceptionHandler { _, e -> logError(e) }
        CoroutineScope(SupervisorJob() + handler).launch {
            // Work
        }
    }

    // DO: используйте supervisorScope / SupervisorJob для независимых задач
    suspend fun good3() = supervisorScope {
        launch { task1() }  // Ошибка здесь не отменит task2
        launch { task2() }
    }

    // DON'T: не "глотайте" исключения тихо
    suspend fun bad1() {
        try {
            riskyOperation()
        } catch (e: Exception) {
            // Тихое игнорирование ошибки — плохо
        }
    }
}
```

---

# Question (EN)
> What methods are known for error handling in coroutines?

## Answer (EN)

There are several ways to handle errors in coroutines:

1. Try-catch inside `launch`/`async` (including around `await()`) — local error handling.
2. `CoroutineExceptionHandler` — scope-level handler for uncaught exceptions from `launch`-like coroutines.
3. `supervisorScope` / `SupervisorJob` — isolate failures so sibling coroutines are not cancelled.
4. `Result<T>` — wrap results in `Result` for explicit, functional-style error handling.

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

// Inside async (local handling inside async)
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

// Around await() (exception surfaces on await)
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
import kotlinx.coroutines.*

// Global-like exception handler for uncaught exceptions in launch
fun exceptionHandler() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("Caught by handler: ${exception.message}")
    }

    val scope = CoroutineScope(Job() + handler)

    scope.launch {
        throw RuntimeException("Error!")  // Uncaught here -> handled by CoroutineExceptionHandler
    }

    delay(100)
}

// Note:
// - CoroutineExceptionHandler handles uncaught exceptions from launch and other fire-and-forget coroutines.
// - For async, exceptions are captured and rethrown on await(), so they must be handled via try-catch around await().

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

### Method 3: supervisorScope / SupervisorJob

```kotlin
import kotlinx.coroutines.*

// supervisorScope: one child failure doesn't cancel its siblings
suspend fun supervisorExample() = supervisorScope {
    launch {
        throw Exception("Error 1")  // Fails only this child
    }

    launch {
        delay(100)
        println("Task 2 completes")  // Still runs
    }
}

// Multiple independent tasks with SupervisorJob
suspend fun loadWidgets() {
    val handler = CoroutineExceptionHandler { _, exception ->
        logError(exception)
    }

    val scope = CoroutineScope(SupervisorJob() + handler)

    scope.launch { loadWidget1() }  // Independent
    scope.launch { loadWidget2() }  // Independent
    scope.launch { loadWidget3() }  // Independent
}
```

// Note:
// - supervisorScope / SupervisorJob prevent failure of one child from cancelling siblings.
// - An unhandled exception in the parent itself (or not handled by a child) still can cancel that scope.

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
    // DO: Use try-catch for local handling
    suspend fun good1() {
        try {
            riskyOperation()
        } catch (e: Exception) {
            handleError(e)
        }
    }

    // DO: Use CoroutineExceptionHandler at scope level for uncaught exceptions in launch coroutines
    fun good2() {
        val handler = CoroutineExceptionHandler { _, e -> logError(e) }
        CoroutineScope(SupervisorJob() + handler).launch {
            // Work
        }
    }

    // DO: Use supervisorScope / SupervisorJob for independent tasks
    suspend fun good3() = supervisorScope {
        launch { task1() }  // Failure here doesn't cancel task2
        launch { task2() }
    }

    // DON'T: Swallow exceptions silently
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

## Дополнительные вопросы (RU)

- В чём ключевые отличия этой модели обработки ошибок от Java?
- Когда бы вы применили эти подходы на практике?
- Каковы распространённые ошибки и подводные камни при обработке ошибок в корутинах?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- [[c-coroutines]]
- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [[c-kotlin]]
- [[c-coroutines]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные вопросы (RU)

- [[q-how-to-create-suspend-function--programming-languages--medium]]

## Related Questions

- [[q-how-to-create-suspend-function--programming-languages--medium]]
