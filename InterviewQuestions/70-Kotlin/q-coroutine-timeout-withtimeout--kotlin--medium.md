---
id: "20251012-150006"
title: "How to handle timeouts in coroutines: withTimeout vs withTimeoutOrNull"
description: "Comprehensive guide to timeout handling in Kotlin coroutines, covering withTimeout, withTimeoutOrNull, TimeoutCancellationException, and practical patterns"
tags: ["kotlin", "coroutines", "timeout", "cancellation", "error-handling", "difficulty/medium"]
topic: "kotlin"
subtopics: ["coroutines", "timeout", "cancellation", "error-handling"]
moc: "moc-kotlin"
status: "draft"
date_created: "2025-10-12"
date_updated: "2025-10-12"
---

# How to handle timeouts in coroutines: withTimeout vs withTimeoutOrNull

## English

### Problem Statement

When working with coroutines, operations may take longer than expected, leading to poor user experience or resource waste. How do we implement timeouts effectively using `withTimeout` and `withTimeoutOrNull`, and what are the differences between them?

### Solution

**`withTimeout`** throws `TimeoutCancellationException` if the operation exceeds the specified time. **`withTimeoutOrNull`** returns `null` instead of throwing an exception, providing a more graceful fallback.

#### Basic Usage

```kotlin
import kotlinx.coroutines.*

fun basicTimeouts() = runBlocking {
    println("=== withTimeout ===")

    // withTimeout throws exception on timeout
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
        // Cleanup or fallback
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
| Use case | Critical operations that must complete | Optional operations with fallback |
| Error handling | try-catch required | Elvis operator (?:) |
| Code clarity | Explicit error | Implicit with null check |

#### Practical Examples

```kotlin
import kotlinx.coroutines.*

// Example 1: User authentication with timeout
suspend fun authenticateUser(credentials: Credentials): AuthResult {
    return try {
        withTimeout(10000) {
            val token = callAuthService(credentials)
            AuthResult.Success(token)
        }
    } catch (e: TimeoutCancellationException) {
        AuthResult.Timeout
    } catch (e: Exception) {
        AuthResult.Error(e.message ?: "Unknown error")
    }
}

// Example 2: Optional feature loading
suspend fun loadOptionalFeature(): Feature? {
    return withTimeoutOrNull(2000) {
        fetchFeatureConfig()
    }
}

// Example 3: Database query with timeout
suspend fun queryDatabase(query: String): List<Result> {
    return withTimeoutOrNull(5000) {
        executeQuery(query)
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

1. **Use withTimeout for critical operations**
2. **Use withTimeoutOrNull for optional operations**
3. **Set reasonable timeout values based on operation type**
4. **Always provide fallback for withTimeoutOrNull**
5. **Consider user experience when choosing timeout duration**

---

## Русский

### Описание проблемы

При работе с корутинами операции могут занимать больше времени, чем ожидается, что приводит к плохому пользовательскому опыту или потере ресурсов. Как эффективно реализовать таймауты, используя `withTimeout` и `withTimeoutOrNull`, и в чём различия между ними?

[Full translation sections...]

---

## Follow-up Questions

1. What happens to the coroutine after a timeout occurs?
2. Can you recover partial results before timeout?
3. How does withTimeout interact with cancellation?
4. What's the overhead of using timeout functions?
5. Can you nest multiple withTimeout calls?
6. How do you test code with timeouts?
7. What's the difference between timeout and manual cancellation?
8. How does withTimeout handle finally blocks?

## References

- [Kotlin Coroutines Guide - Cancellation and Timeouts](https://kotlinlang.org/docs/cancellation-and-timeouts.html)
- [withTimeout - kotlinx.coroutines API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-timeout.html)
- [TimeoutCancellationException](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-timeout-cancellation-exception/)

## Related Questions

- [[q-coroutine-cancellation--kotlin--medium]]
- [[q-coroutine-exception-handling--kotlin--hard]]
- [[q-withcontext-use-cases--kotlin--medium]]
- [[q-structured-concurrency--kotlin--hard]]
