---
id: lang-057
title: "Error Handling In Coroutines / Обработка ошибок в корутинах"
aliases: [Error Handling In Coroutines, Обработка ошибок в корутинах]
topic: kotlin
subtopics: [concurrency, coroutines, error-handling]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, q-how-to-create-suspend-function--programming-languages--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [coroutines, difficulty/medium, error-handling, exception-handling, kotlin]
date created: Friday, October 31st 2025, 6:29:51 pm
date modified: Tuesday, November 25th 2025, 8:53:52 pm
---
# Вопрос (RU)
> Какие известны способы обработки ошибок в корутинах?

# Question (EN)
> What methods are known for error handling in coroutines?

## Ответ (RU)

Существует несколько распространённых способов обработки ошибок в корутинах:

1. Try-catch внутри `launch`/`async` (в том числе вокруг `await()`) — локальная обработка исключений.
2. `CoroutineExceptionHandler` — обработка необработанных исключений на уровне scope для корутин типа `launch` (fire-and-forget).
3. `supervisorScope` / `SupervisorJob` — когда нужно изолировать ошибки конкретных дочерних корутин и не отменять их "соседей".
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

// Глобальный (на уровне scope) обработчик НЕобработанных исключений в launch-подобных корутинах
fun exceptionHandler() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("Caught by handler: ${exception.message}")
    }

    val scope = CoroutineScope(Job() + handler)

    scope.launch {
        throw RuntimeException("Error!")  // Не перехвачено здесь -> попадёт в CoroutineExceptionHandler
    }

    delay(100)
}

// Примечания:
// - CoroutineExceptionHandler срабатывает только для необработанных исключений в корутинах типа launch / fire-and-forget,
//   когда корутина является "корневой" для данного scope.
// - Если исключение уже перехвачено try-catch внутри корутины, до CoroutineExceptionHandler оно не дойдёт.
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

// supervisorScope: сбой одного дочернего не отменяет других дочерних
suspend fun supervisorExample() = supervisorScope {
    launch {
        throw Exception("Error 1")  // Падает только эта корутина
    }

    launch {
        delay(100)
        println("Task 2 completes")  // Всё ещё выполнится
    }
}

// Несколько независимых задач с SupervisorJobs
suspend fun loadWidgets() {
    val handler = CoroutineExceptionHandler { _, exception ->
        logError(exception)
    }

    val scope = CoroutineScope(SupervisorJob() + handler)

    scope.launch { loadWidget1() }  // Независимые дочерние задачи; падение одной не отменит остальные
    scope.launch { loadWidget2() }
    scope.launch { loadWidget3() }
}
```

// Примечания:
// - `supervisorScope` / `SupervisorJob` изолируют ошибки: необработанное исключение отменяет только упавшую дочернюю корутину,
//   но не отменяет её "соседей".
// - При этом необработанное исключение всё равно репортится наверх (например, в CoroutineExceptionHandler родительского scope).
// - Исключение в самом родителе (или вне дочерних корутин) по-прежнему может отменить весь scope.

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

    // DO: используйте CoroutineExceptionHandler на уровне scope для необработанных исключений в launch-подобных корутинах
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

## Answer (EN)

There are several ways to handle errors in coroutines:

1. Try-catch inside `launch`/`async` (including around `await()`) — local error handling.
2. `CoroutineExceptionHandler` — scope-level handler for uncaught exceptions from `launch`-like (fire-and-forget) coroutines.
3. `supervisorScope` / `SupervisorJob` — isolate failures of specific children so sibling coroutines are not cancelled.
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

// Scope-level handler for UNCAUGHT exceptions in launch-like coroutines
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
// - CoroutineExceptionHandler triggers only for uncaught exceptions in launch / fire-and-forget coroutines
//   where the coroutine is a "root" for that scope.
// - If the exception is already caught via try-catch inside the coroutine, it will NOT reach CoroutineExceptionHandler.
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

// supervisorScope: failure of one child does not cancel its siblings
suspend fun supervisorExample() = supervisorScope {
    launch {
        throw Exception("Error 1")  // Only this coroutine fails
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

    scope.launch { loadWidget1() }  // Independent children; failure in one does not cancel others
    scope.launch { loadWidget2() }
    scope.launch { loadWidget3() }
}
```

// Note:
// - `supervisorScope` / `SupervisorJob` isolate failures: an unhandled exception cancels only the failed child,
//   but does not cancel its siblings.
// - The exception is still reported upward (e.g., to the parent's CoroutineExceptionHandler).
// - An exception in the parent itself (outside child coroutines) can still cancel the entire scope.

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

    // DO: Use CoroutineExceptionHandler at scope level for uncaught exceptions in launch-like coroutines
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

## Дополнительные Вопросы (RU)

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

## Связанные Вопросы (RU)

- [[q-how-to-create-suspend-function--kotlin--medium]]

## Related Questions

- [[q-how-to-create-suspend-function--kotlin--medium]]
