---
id: kotlin-244
title: "How to handle timeouts in coroutines: withTimeout vs withTimeoutOrNull / Таймауты в корутинах"
aliases: [Coroutine Timeouts, Таймауты в корутинах]
topic: kotlin
difficulty: medium
original_language: en
language_tags: [en, ru]
question_kind: theory
status: draft
created: "2025-10-12"
updated: "2025-11-09"
tags: ["cancellation", "coroutines", "difficulty/medium", "error-handling", "kotlin", "timeout"]
description: "Comprehensive guide to timeout handling in Kotlin coroutines, covering withTimeout, withTimeoutOrNull, TimeoutCancellationException, and practical patterns"
moc: moc-kotlin
related: [c-kotlin, c-coroutines, c-structured-concurrency]
subtopics: [coroutines, timeout]
---

# Вопрос (RU)

> Как обрабатывать таймауты в корутинах Kotlin: когда использовать `withTimeout`, а когда `withTimeoutOrNull`, в чём их различия и как применять их на практике?

# Question (EN)

> How to handle timeouts in Kotlin coroutines: when to use `withTimeout` vs `withTimeoutOrNull`, what are their differences, and how to apply them in practice?

## Ответ (RU)

### Описание Проблемы

При работе с корутинами операции могут занимать больше времени, чем ожидается, что приводит к плохому пользовательскому опыту или потере ресурсов. Как эффективно реализовать таймауты, используя `withTimeout` и `withTimeoutOrNull`, и в чём различия между ними?

### Решение

`withTimeout` и `withTimeoutOrNull` запускают suspend-блок и отменяют его, если он не завершился за указанное время.

- `withTimeout` выбрасывает `TimeoutCancellationException`, если операция превышает указанное время.
- `withTimeoutOrNull` возвращает `null` вместо выбрасывания исключения, обеспечивая более мягкое резервное поведение.

`TimeoutCancellationException` является подклассом `CancellationException`, поэтому таймаут трактуется как обычный сигнал отмены в корутинах и в рамках структурированной конкуррентности.

#### Базовое Использование

```kotlin
import kotlinx.coroutines.*

fun basicTimeouts() = runBlocking {
    println("=== withTimeout ===")

    // withTimeout выбрасывает TimeoutCancellationException при таймауте
    try {
        withTimeout(1000) {
            delay(2000) // Занимает больше времени, чем таймаут
            "Result"
        }
    } catch (e: TimeoutCancellationException) {
        println("Операция превысила таймаут!")
    }

    println("\n=== withTimeoutOrNull ===")

    // withTimeoutOrNull возвращает null при таймауте
    val result = withTimeoutOrNull(1000) {
        delay(2000)
        "Result"
    }
    println("Результат: $result") // null

    // Успешная операция
    val success = withTimeoutOrNull(2000) {
        delay(1000)
        "Success"
    }
    println("Результат: $success") // "Success"
}
```

#### Обработка Исключений

```kotlin
import kotlinx.coroutines.*

fun exceptionHandling() = runBlocking {
    // withTimeout распространяет TimeoutCancellationException
    try {
        val result = withTimeout(1000) {
            performLongOperation()
        }
        println("Результат: $result")
    } catch (e: TimeoutCancellationException) {
        println("Таймаут: ${e.message}")
        // Очистка или резервное поведение (finally-блоки внутри всё равно выполнятся)
    }

    // withTimeoutOrNull не выбрасывает, возвращает null
    val result2 = withTimeoutOrNull(1000) {
        performLongOperation()
    } ?: "Значение по умолчанию"
    println("Результат с резервным значением: $result2")
}

suspend fun performLongOperation(): String {
    delay(5000)
    return "Результат длительной операции"
}
```

#### Паттерны Для Сетевых Запросов

```kotlin
import kotlinx.coroutines.*

class ApiClient {
    // Паттерн 1: withTimeout для критических операций
    suspend fun fetchCriticalData(id: String): Data {
        return withTimeout(5000) {
            performNetworkRequest(id)
        }
    }

    // Паттерн 2: withTimeoutOrNull с резервным вариантом
    suspend fun fetchDataWithFallback(id: String): Data {
        return withTimeoutOrNull(5000) {
            performNetworkRequest(id)
        } ?: loadFromCache(id)
    }

    // Паттерн 3: Несколько попыток с таймаутом
    suspend fun fetchWithRetry(id: String, attempts: Int = 3): Data? {
        repeat(attempts) { attempt ->
            val result = withTimeoutOrNull(3000) {
                performNetworkRequest(id)
            }
            if (result != null) return result
            println("Попытка ${attempt + 1} превысила таймаут")
            delay(1000)
        }
        return null
    }

    private suspend fun performNetworkRequest(id: String): Data {
        delay(4000) // Имитация сетевого запроса
        return Data(id, "Данные из сети")
    }

    private suspend fun loadFromCache(id: String): Data {
        delay(100)
        return Data(id, "Кэшированные данные")
    }
}

data class Data(val id: String, val content: String)
```

#### Таблица Сравнения

| Аспект | withTimeout | withTimeoutOrNull |
|--------|-------------|-------------------|
| Возврат при таймауте | Выбрасывает TimeoutCancellationException | Возвращает null |
| Случай использования | Критические операции, которые должны явно завершиться или провалиться | Опциональные операции с резервным вариантом |
| Обработка ошибок | Требуется try-catch (или дать отмене распространиться) | Оператор Elvis (?:) / проверка на null |
| Ясность кода | Явный таймаут как ошибка | Неявный через nullable-результат |

#### Практические Примеры

```kotlin
import kotlinx.coroutines.*

// Пример 1: Аутентификация пользователя с таймаутом
suspend fun authenticateUser(credentials: Credentials): AuthResult {
    return try {
        withTimeout(10000) {
            val token = callAuthService(credentials) // здесь завершается до истечения таймаута
            AuthResult.Success(token)
        }
    } catch (e: TimeoutCancellationException) {
        AuthResult.Timeout
    } catch (e: Exception) {
        AuthResult.Error(e.message ?: "Неизвестная ошибка")
    }
}

// Пример 2: Загрузка опциональной функциональности (настроен так, чтобы продемонстрировать таймаут)
suspend fun loadOptionalFeature(): Feature? {
    return withTimeoutOrNull(2000) {
        fetchFeatureConfig() // 3000мс > 2000мс -> вернёт null в этом примере
    }
}

// Пример 3: Запрос к базе данных с таймаутом (настроен так, чтобы продемонстрировать таймаут)
suspend fun queryDatabase(query: String): List<Result> {
    return withTimeoutOrNull(5000) {
        executeQuery(query) // 6000мс > 5000мс -> таймаут, вернёт null
    } ?: emptyList()
}

// Пример 4: Несколько параллельных операций с индивидуальными таймаутами
suspend fun loadDashboard(): Dashboard = coroutineScope {
    val weather = async {
        withTimeoutOrNull(2000) { fetchWeather() }
    }
    val news = async {
        withTimeoutOrNull(3000) { fetchNews() }
    }
    val stocks = async {
        withTimeoutOrNull(1000) { fetchStocks() }
    }

    Dashboard(
        weather = weather.await() ?: "Погода недоступна",
        news = news.await() ?: "Новости недоступны",
        stocks = stocks.await() ?: "Котировки недоступны"
    )
}

data class Credentials(val username: String, val password: String)
sealed class AuthResult {
    data class Success(val token: String) : AuthResult()
    object Timeout : AuthResult()
    data class Error(val message: String) : AuthResult()
}

data class Feature(val name: String, val enabled: Boolean)
data class Result(val id: String, val data: String)
data class Dashboard(val weather: String, val news: String, val stocks: String)

suspend fun callAuthService(credentials: Credentials): String {
    delay(5000)
    return "token123"
}

suspend fun fetchFeatureConfig(): Feature {
    delay(3000)
    return Feature("premium", true)
}

suspend fun executeQuery(query: String): List<Result> {
    delay(6000)
    return listOf(Result("1", "data"))
}

suspend fun fetchWeather(): String {
    delay(1500)
    return "Солнечно, 22°C"
}

suspend fun fetchNews(): String {
    delay(2500)
    return "Последние новости"
}

suspend fun fetchStocks(): String {
    delay(800)
    return "AAPL: $150"
}
```

### Лучшие Практики

1. Используйте `withTimeout` для критических операций, которые должны либо завершиться за дедлайн, либо явно упасть.
2. Используйте `withTimeoutOrNull` для опциональных/некритичных операций, когда можно продолжить без результата.
3. Устанавливайте разумные значения таймаута, учитывая тип операции, условия сети и пользовательский опыт.
4. Всегда предоставляйте резервный вариант для `withTimeoutOrNull` (значение по умолчанию, кэш, пропуск функциональности).
5. Помните, что `TimeoutCancellationException` — это форма отмены: блок и его дочерние корутины будут отменены, `finally`-блоки выполняются.
6. Таймауты кооперативны и проверяются в точках приостановки; длительные CPU-связанные задачи без suspension не будут прерваны без дополнительной поддержки отмены.
7. `withTimeout`/`withTimeoutOrNull` не меняют диспетчер: они наследуют контекст родительской корутины.

## Answer (EN)

### Problem Statement

When working with coroutines, operations may take longer than expected, leading to poor user experience or resource waste. How do we implement timeouts effectively using `withTimeout` and `withTimeoutOrNull`, and what are the differences between them?

### Solution

`withTimeout` and `withTimeoutOrNull` run a suspendable block and cancel it if it does not complete within the given time.

- `withTimeout` throws `TimeoutCancellationException` if the operation exceeds the specified time.
- `withTimeoutOrNull` returns `null` instead of throwing an exception, providing a more graceful fallback.

`TimeoutCancellationException` is a subclass of `CancellationException`, so timeout is treated as a normal cancellation signal by coroutines and structured concurrency.

#### Basic Usage

```kotlin
import kotlinx.coroutines.*

fun basicTimeouts() = runBlocking {
    println("=== withTimeout ===")

    // withTimeout throws TimeoutCancellationException on timeout
    try {
        withTimeout(1000) {
            delay(2000) // Takes longer than timeout
            "Result"
        }
    } catch (e: TimeoutCancellationException) {
        println("Operation timed out!")
    }

    println("\n=== withTimeoutOrNull ===")

    // withTimeoutOrNull returns null on timeout
    val result = withTimeoutOrNull(1000) {
        delay(2000)
        "Result"
    }
    println("Result: $result") // null

    // Successful operation
    val success = withTimeoutOrNull(2000) {
        delay(1000)
        "Success"
    }
    println("Result: $success") // "Success"
}
```

#### Exception Handling

```kotlin
import kotlinx.coroutines.*

fun exceptionHandling() = runBlocking {
    // withTimeout propagates TimeoutCancellationException
    try {
        val result = withTimeout(1000) {
            performLongOperation()
        }
        println("Result: $result")
    } catch (e: TimeoutCancellationException) {
        println("Timeout: ${e.message}")
        // Cleanup or fallback (finally blocks inside will still run)
    }

    // withTimeoutOrNull doesn't throw, returns null
    val result2 = withTimeoutOrNull(1000) {
        performLongOperation()
    } ?: "Default value"
    println("Result with fallback: $result2")
}

suspend fun performLongOperation(): String {
    delay(5000)
    return "Long operation result"
}
```

#### Network Request Patterns

```kotlin
import kotlinx.coroutines.*

class ApiClient {
    // Pattern 1: withTimeout for critical operations
    suspend fun fetchCriticalData(id: String): Data {
        return withTimeout(5000) {
            performNetworkRequest(id)
        }
    }

    // Pattern 2: withTimeoutOrNull with fallback
    suspend fun fetchDataWithFallback(id: String): Data {
        return withTimeoutOrNull(5000) {
            performNetworkRequest(id)
        } ?: loadFromCache(id)
    }

    // Pattern 3: Multiple attempts with timeout
    suspend fun fetchWithRetry(id: String, attempts: Int = 3): Data? {
        repeat(attempts) { attempt ->
            val result = withTimeoutOrNull(3000) {
                performNetworkRequest(id)
            }
            if (result != null) return result
            println("Attempt ${attempt + 1} timed out")
            delay(1000)
        }
        return null
    }

    private suspend fun performNetworkRequest(id: String): Data {
        delay(4000) // Simulate network request
        return Data(id, "Network data")
    }

    private suspend fun loadFromCache(id: String): Data {
        delay(100)
        return Data(id, "Cached data")
    }
}

data class Data(val id: String, val content: String)
```

#### Comparison Table

| Aspect | withTimeout | withTimeoutOrNull |
|--------|-------------|-------------------|
| Return on timeout | Throws TimeoutCancellationException | Returns null |
| Use case | Critical operations that must complete or fail explicitly | Optional operations with fallback |
| Error handling | try-catch required (or let it propagate as cancellation) | Elvis operator (?:) / null check |
| Code clarity | Explicit timeout failure | Implicit via nullable result |

#### Practical Examples

```kotlin
import kotlinx.coroutines.*

// Example 1: User authentication with timeout
suspend fun authenticateUser(credentials: Credentials): AuthResult {
    return try {
        withTimeout(10000) {
            val token = callAuthService(credentials) // here completes before timeout
            AuthResult.Success(token)
        }
    } catch (e: TimeoutCancellationException) {
        AuthResult.Timeout
    } catch (e: Exception) {
        AuthResult.Error(e.message ?: "Unknown error")
    }
}

// Example 2: Optional feature loading (configured to show a timeout scenario)
suspend fun loadOptionalFeature(): Feature? {
    return withTimeoutOrNull(2000) {
        fetchFeatureConfig() // 3000ms > 2000ms -> returns null in this example
    }
}

// Example 3: Database query with timeout (configured to show a timeout scenario)
suspend fun queryDatabase(query: String): List<Result> {
    return withTimeoutOrNull(5000) {
        executeQuery(query) // 6000ms > 5000ms -> times out, returns null
    } ?: emptyList()
}

// Example 4: Multiple parallel operations with individual timeouts
suspend fun loadDashboard(): Dashboard = coroutineScope {
    val weather = async {
        withTimeoutOrNull(2000) { fetchWeather() }
    }
    val news = async {
        withTimeoutOrNull(3000) { fetchNews() }
    }
    val stocks = async {
        withTimeoutOrNull(1000) { fetchStocks() }
    }

    Dashboard(
        weather = weather.await() ?: "Weather unavailable",
        news = news.await() ?: "News unavailable",
        stocks = stocks.await() ?: "Stocks unavailable"
    )
}

data class Credentials(val username: String, val password: String)
sealed class AuthResult {
    data class Success(val token: String) : AuthResult()
    object Timeout : AuthResult()
    data class Error(val message: String) : AuthResult()
}

data class Feature(val name: String, val enabled: Boolean)
data class Result(val id: String, val data: String)
data class Dashboard(val weather: String, val news: String, val stocks: String)

suspend fun callAuthService(credentials: Credentials): String {
    delay(5000)
    return "token123"
}

suspend fun fetchFeatureConfig(): Feature {
    delay(3000)
    return Feature("premium", true)
}

suspend fun executeQuery(query: String): List<Result> {
    delay(6000)
    return listOf(Result("1", "data"))
}

suspend fun fetchWeather(): String {
    delay(1500)
    return "Sunny, 72°F"
}

suspend fun fetchNews(): String {
    delay(2500)
    return "Latest news"
}

suspend fun fetchStocks(): String {
    delay(800)
    return "AAPL: $150"
}
```

### Best Practices

1. Use `withTimeout` for critical operations that must either complete within the deadline or fail explicitly.
2. Use `withTimeoutOrNull` for optional/non-critical operations where you can proceed without a result.
3. Set reasonable timeout values based on operation type, environment, and UX expectations.
4. Always provide a fallback for `withTimeoutOrNull` (e.g., default value, cache, or skipping the feature).
5. Remember that `TimeoutCancellationException` is a form of cancellation: it will cancel the timed-out block and its children, and `finally` blocks still run.
6. Timeouts are cooperative and checked at suspension points; long CPU-bound work without suspension will not be interrupted unless you make it cancellable.
7. `withTimeout`/`withTimeoutOrNull` do not change dispatcher; they inherit the parent coroutine context.

## Дополнительные вопросы (RU)

1. Что происходит с корутиной после срабатывания таймаута? (Тело и дочерние корутины отменяются через `TimeoutCancellationException`, родитель может продолжить работу, если не рассматривает это как фатальную ошибку.)
2. Можно ли получить частичные результаты до таймаута?
3. Как `withTimeout` взаимодействует с отменой корутин?
4. Какова стоимость использования функций таймаута?
5. Можно ли вкладывать несколько вызовов `withTimeout`?
6. Как тестировать код с таймаутами?
7. В чём разница между таймаутом и ручной отменой?
8. Как `withTimeout` обрабатывает `finally`-блоки? (Они всё равно выполняются при отмене/таймауте.)

## Follow-ups

1. What happens to the coroutine after a timeout occurs? (The timed block and its children are cancelled with `TimeoutCancellationException`; parent can continue unless it treats it as fatal.)
2. Can you recover partial results before timeout?
3. How does `withTimeout` interact with cancellation?
4. What is the overhead of using timeout functions?
5. Can you nest multiple `withTimeout` calls?
6. How do you test code with timeouts?
7. What is the difference between timeout and manual cancellation?
8. How does `withTimeout` handle `finally` blocks? (They still execute on cancellation/timeout.)

## Ссылки (RU)

- [Kotlin Coroutines Guide - Cancellation and Timeouts](https://kotlinlang.org/docs/cancellation-and-timeouts.html)
- [withTimeout - kotlinx.coroutines API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-timeout.html)
- [TimeoutCancellationException](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-timeout-cancellation-exception/)
- [[c-coroutines]]

## References

- [Kotlin Coroutines Guide - Cancellation and Timeouts](https://kotlinlang.org/docs/cancellation-and-timeouts.html)
- [withTimeout - kotlinx.coroutines API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-timeout.html)
- [TimeoutCancellationException](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-timeout-cancellation-exception/)
- [[c-coroutines]]

## Связанные вопросы (RU)

- [[q-coroutine-exception-handling--kotlin--medium]]
- [[q-withcontext-use-cases--kotlin--medium]]
- [[q-structured-concurrency--kotlin--hard]]

## Related Questions

- [[q-coroutine-exception-handling--kotlin--medium]]
- [[q-withcontext-use-cases--kotlin--medium]]
- [[q-structured-concurrency--kotlin--hard]]
