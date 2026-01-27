---
id: kotlin-flow-005
title: Flow Exception Handling / Обработка исключений в Flow
aliases:
- Flow Exception Handling
- catch retry retryWhen
- Обработка ошибок Flow
topic: kotlin
subtopics:
- coroutines
- flow
- error-handling
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source: internal
status: draft
moc: moc-kotlin
related:
- c-kotlin
- c-flow
- q-catch-operator-flow--kotlin--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- coroutines
- difficulty/medium
- flow
- kotlin
- error-handling
anki_cards:
- slug: kotlin-flow-005-0-en
  language: en
  anki_id: 1769344143140
  synced_at: '2026-01-25T16:29:03.192175'
- slug: kotlin-flow-005-0-ru
  language: ru
  anki_id: 1769344143190
  synced_at: '2026-01-25T16:29:03.193907'
---
# Vopros (RU)
> Как обрабатывать исключения в Flow? Объясните операторы `catch`, `retry`, `retryWhen`.

---

# Question (EN)
> How to handle exceptions in Flow? Explain `catch`, `retry`, `retryWhen` operators.

## Otvet (RU)

### Оператор catch

`catch` перехватывает исключения из upstream (операторов выше по цепочке) и позволяет:
- Эмитировать fallback значения
- Логировать ошибки
- Преобразовывать исключения

```kotlin
flowOf(1, 2, 3)
    .map {
        if (it == 2) throw IllegalStateException("Error on 2")
        it
    }
    .catch { e ->
        // Эмитируем fallback значение
        emit(-1)
    }
    .collect { println(it) }
// 1, -1

// catch НЕ ловит исключения из collect()
flow { emit(1) }
    .catch { /* не сработает для ошибки в collect */ }
    .collect {
        throw Exception("Error in collect")  // НЕ перехватывается catch
    }
```

**Важно:** `catch` перехватывает только upstream исключения, не downstream.

### Несколько catch в цепочке

```kotlin
flow {
    emit(1)
    throw IOException("Network error")
}
.catch { e ->
    if (e is IOException) {
        emit(-1)  // Fallback для сетевых ошибок
    } else {
        throw e   // Пробрасываем дальше
    }
}
.map {
    if (it == -1) throw IllegalStateException("Invalid value")
    it * 2
}
.catch { e ->
    // Ловит IllegalStateException из map выше
    emit(0)
}
.collect { println(it) }
```

### Оператор retry

`retry` автоматически перезапускает Flow при ошибке:

```kotlin
var attempts = 0

flow {
    attempts++
    if (attempts < 3) {
        throw IOException("Attempt $attempts failed")
    }
    emit("Success on attempt $attempts")
}
.retry(retries = 3)  // Максимум 3 повторные попытки
.collect { println(it) }
// Success on attempt 3
```

#### retry с предикатом

```kotlin
flow {
    // ...
}
.retry(retries = 3) { cause ->
    // Повторять только для определённых исключений
    cause is IOException
}
```

### Оператор retryWhen

`retryWhen` даёт полный контроль над логикой повторов:

```kotlin
flow {
    emit(api.fetchData())
}
.retryWhen { cause, attempt ->
    if (cause is IOException && attempt < 3) {
        delay(1000 * (attempt + 1))  // Exponential backoff
        true  // Повторить
    } else {
        false  // Не повторять
    }
}
.collect { data -> processData(data) }
```

#### Exponential Backoff с Jitter

```kotlin
fun <T> Flow<T>.retryWithExponentialBackoff(
    maxRetries: Int = 3,
    initialDelayMs: Long = 1000,
    maxDelayMs: Long = 10000,
    factor: Double = 2.0
): Flow<T> = retryWhen { cause, attempt ->
    if (attempt < maxRetries && cause is IOException) {
        val delay = (initialDelayMs * factor.pow(attempt.toDouble()))
            .toLong()
            .coerceAtMost(maxDelayMs)
        val jitter = (0..delay / 4).random()
        delay(delay + jitter)
        true
    } else {
        false
    }
}

// Использование
apiFlow
    .retryWithExponentialBackoff(maxRetries = 5)
    .catch { emit(FallbackData) }
    .collect { data -> updateUI(data) }
```

### onCompletion

`onCompletion` вызывается при завершении Flow (успешном или с ошибкой):

```kotlin
flow {
    emit(1)
    emit(2)
    throw IOException("Error")
}
.onCompletion { cause ->
    if (cause != null) {
        println("Flow completed with error: $cause")
    } else {
        println("Flow completed successfully")
    }
}
.catch { emit(-1) }
.collect { println(it) }
// 1
// 2
// Flow completed with error: java.io.IOException: Error
// -1
```

### Практический Пример: Загрузка данных

```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Throwable) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

fun loadUserData(userId: String): Flow<Result<User>> = flow {
    emit(Result.Loading)
    val user = repository.fetchUser(userId)
    emit(Result.Success(user))
}
.retryWhen { cause, attempt ->
    val shouldRetry = cause is IOException && attempt < 3
    if (shouldRetry) {
        emit(Result.Loading)  // Показываем loading при retry
        delay(1000 * (attempt + 1))
    }
    shouldRetry
}
.catch { e ->
    emit(Result.Error(e))
}

// Использование в ViewModel
val userData: StateFlow<Result<User>> = loadUserData(userId)
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = Result.Loading
    )
```

### Обработка Ошибок в collect

Так как `catch` не ловит ошибки в `collect`, используйте:

```kotlin
// Вариант 1: try-catch в collect
flow.collect { value ->
    try {
        processValue(value)
    } catch (e: Exception) {
        handleError(e)
    }
}

// Вариант 2: onEach + launchIn
flow
    .onEach { value -> processValue(value) }
    .catch { e -> handleError(e) }
    .launchIn(scope)

// Вариант 3: collectLatest с обработкой
flow.collectLatest { value ->
    runCatching { processValue(value) }
        .onFailure { handleError(it) }
}
```

### Типичные Ошибки

```kotlin
// ОШИБКА: catch после collect не сработает
flow.collect { value ->
    throw Exception("Error")  // Не перехватится
}

// ОШИБКА: retry без ограничения может зациклиться
flow.retry()  // Бесконечные повторы!

// ПРАВИЛЬНО: всегда ограничивайте retry
flow.retry(3) { it is IOException }
```

---

## Answer (EN)

### catch Operator

`catch` intercepts exceptions from upstream (operators above in the chain) and allows:
- Emitting fallback values
- Logging errors
- Transforming exceptions

```kotlin
flowOf(1, 2, 3)
    .map {
        if (it == 2) throw IllegalStateException("Error on 2")
        it
    }
    .catch { e ->
        // Emit fallback value
        emit(-1)
    }
    .collect { println(it) }
// 1, -1

// catch does NOT catch exceptions from collect()
flow { emit(1) }
    .catch { /* won't work for error in collect */ }
    .collect {
        throw Exception("Error in collect")  // NOT caught by catch
    }
```

**Important:** `catch` only intercepts upstream exceptions, not downstream.

### Multiple catch in Chain

```kotlin
flow {
    emit(1)
    throw IOException("Network error")
}
.catch { e ->
    if (e is IOException) {
        emit(-1)  // Fallback for network errors
    } else {
        throw e   // Rethrow
    }
}
.map {
    if (it == -1) throw IllegalStateException("Invalid value")
    it * 2
}
.catch { e ->
    // Catches IllegalStateException from map above
    emit(0)
}
.collect { println(it) }
```

### retry Operator

`retry` automatically restarts Flow on error:

```kotlin
var attempts = 0

flow {
    attempts++
    if (attempts < 3) {
        throw IOException("Attempt $attempts failed")
    }
    emit("Success on attempt $attempts")
}
.retry(retries = 3)  // Maximum 3 retry attempts
.collect { println(it) }
// Success on attempt 3
```

#### retry with Predicate

```kotlin
flow {
    // ...
}
.retry(retries = 3) { cause ->
    // Retry only for specific exceptions
    cause is IOException
}
```

### retryWhen Operator

`retryWhen` gives full control over retry logic:

```kotlin
flow {
    emit(api.fetchData())
}
.retryWhen { cause, attempt ->
    if (cause is IOException && attempt < 3) {
        delay(1000 * (attempt + 1))  // Exponential backoff
        true  // Retry
    } else {
        false  // Don't retry
    }
}
.collect { data -> processData(data) }
```

#### Exponential Backoff with Jitter

```kotlin
fun <T> Flow<T>.retryWithExponentialBackoff(
    maxRetries: Int = 3,
    initialDelayMs: Long = 1000,
    maxDelayMs: Long = 10000,
    factor: Double = 2.0
): Flow<T> = retryWhen { cause, attempt ->
    if (attempt < maxRetries && cause is IOException) {
        val delay = (initialDelayMs * factor.pow(attempt.toDouble()))
            .toLong()
            .coerceAtMost(maxDelayMs)
        val jitter = (0..delay / 4).random()
        delay(delay + jitter)
        true
    } else {
        false
    }
}

// Usage
apiFlow
    .retryWithExponentialBackoff(maxRetries = 5)
    .catch { emit(FallbackData) }
    .collect { data -> updateUI(data) }
```

### onCompletion

`onCompletion` is called when Flow completes (successfully or with error):

```kotlin
flow {
    emit(1)
    emit(2)
    throw IOException("Error")
}
.onCompletion { cause ->
    if (cause != null) {
        println("Flow completed with error: $cause")
    } else {
        println("Flow completed successfully")
    }
}
.catch { emit(-1) }
.collect { println(it) }
// 1
// 2
// Flow completed with error: java.io.IOException: Error
// -1
```

### Practical Example: Data Loading

```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Throwable) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

fun loadUserData(userId: String): Flow<Result<User>> = flow {
    emit(Result.Loading)
    val user = repository.fetchUser(userId)
    emit(Result.Success(user))
}
.retryWhen { cause, attempt ->
    val shouldRetry = cause is IOException && attempt < 3
    if (shouldRetry) {
        emit(Result.Loading)  // Show loading on retry
        delay(1000 * (attempt + 1))
    }
    shouldRetry
}
.catch { e ->
    emit(Result.Error(e))
}

// Usage in ViewModel
val userData: StateFlow<Result<User>> = loadUserData(userId)
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = Result.Loading
    )
```

### Handling Errors in collect

Since `catch` doesn't catch errors in `collect`, use:

```kotlin
// Option 1: try-catch in collect
flow.collect { value ->
    try {
        processValue(value)
    } catch (e: Exception) {
        handleError(e)
    }
}

// Option 2: onEach + launchIn
flow
    .onEach { value -> processValue(value) }
    .catch { e -> handleError(e) }
    .launchIn(scope)

// Option 3: collectLatest with handling
flow.collectLatest { value ->
    runCatching { processValue(value) }
        .onFailure { handleError(it) }
}
```

### Common Mistakes

```kotlin
// WRONG: catch after collect won't work
flow.collect { value ->
    throw Exception("Error")  // Won't be caught
}

// WRONG: retry without limit can loop forever
flow.retry()  // Infinite retries!

// CORRECT: always limit retry
flow.retry(3) { it is IOException }
```

---

## Dopolnitelnye Voprosy (RU)

1. Как правильно обрабатывать CancellationException в Flow?
2. В каких случаях использовать `catch` vs `try-catch` в `collect`?
3. Как протестировать retry логику?
4. Как комбинировать `catch` и `retry` в правильном порядке?
5. Как реализовать circuit breaker паттерн с Flow?

---

## Follow-ups

1. How to properly handle CancellationException in Flow?
2. When to use `catch` vs `try-catch` in `collect`?
3. How to test retry logic?
4. How to combine `catch` and `retry` in the correct order?
5. How to implement circuit breaker pattern with Flow?

---

## Ssylki (RU)

- [[c-kotlin]]
- [[c-flow]]
- [Flow Exception Handling](https://kotlinlang.org/docs/flow.html#flow-exceptions)

---

## References

- [[c-kotlin]]
- [[c-flow]]
- [Flow Exception Handling](https://kotlinlang.org/docs/flow.html#flow-exceptions)

---

## Svyazannye Voprosy (RU)

### Sredniy Uroven
- [[q-catch-operator-flow--kotlin--medium]]
- [[q-flow-operators--flow--medium]]
- [[q-flow-completion-oncompletion--kotlin--medium]]

---

## Related Questions

### Related (Medium)
- [[q-catch-operator-flow--kotlin--medium]] - catch operator details
- [[q-flow-operators--flow--medium]] - Flow operators overview
- [[q-flow-completion-oncompletion--kotlin--medium]] - onCompletion operator
