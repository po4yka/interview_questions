---
id: 20251011-010
title: "supervisorScope vs coroutineScope / supervisorScope против coroutineScope"
aliases: []

# Classification
topic: kotlin
subtopics: [coroutines, scopes, supervisor, error-handling, structured-concurrency]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Phase 1 Coroutines & Flow Advanced Questions

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-coroutinescope-vs-supervisorscope--kotlin--medium, q-job-vs-supervisorjob--kotlin--medium]

# Timestamps
created: 2025-10-11
updated: 2025-10-11

tags: [kotlin, coroutines, scopes, supervisor, error-handling, difficulty/medium]
---
# Question (EN)
> Compare supervisorScope and coroutineScope. When should you use each? Demonstrate how they handle independent failures differently.

# Вопрос (RU)
> Сравните supervisorScope и coroutineScope. Когда использовать каждый? Продемонстрируйте как они по-разному обрабатывают независимые ошибки.

---

## Answer (EN)

The key difference between `supervisorScope` and `coroutineScope` is how they handle child coroutine failures.

### coroutineScope - Fail-Fast Behavior

`coroutineScope` cancels **all children** if **any child fails**.

```kotlin
suspend fun demonstrateCoroutineScope() {
    println("Starting coroutineScope")

    try {
        coroutineScope {
            launch {
                delay(100)
                println("Task 1 completed")
            }

            launch {
                delay(50)
                throw Exception("Task 2 failed!")
            }

            launch {
                delay(200)
                println("Task 3 completed")
            }
        }
    } catch (e: Exception) {
        println("Caught: ${e.message}")
    }

    println("Done")
}

/*
Output:
Starting coroutineScope
Caught: Task 2 failed!
Done

Task 1 and Task 3 never complete - cancelled when Task 2 failed!
*/
```

### supervisorScope - Independent Failures

`supervisorScope` allows children to fail independently without affecting siblings.

```kotlin
suspend fun demonstrateSupervisorScope() {
    println("Starting supervisorScope")

    supervisorScope {
        launch {
            delay(100)
            println("Task 1 completed")
        }

        launch {
            delay(50)
            throw Exception("Task 2 failed!")
        }

        launch {
            delay(200)
            println("Task 3 completed")
        }
    }

    println("Done")
}

/*
Output:
Starting supervisorScope
Exception in thread: Task 2 failed!
Task 1 completed
Task 3 completed
Done

All tasks complete independently!
*/
```

### Comparison Table

| Aspect | coroutineScope | supervisorScope |
|--------|----------------|-----------------|
| **Child failure** | Cancels all siblings | Only failed child cancelled |
| **Parent failure** | Cancels all children | Cancels all children |
| **Exception propagation** | To parent immediately | Handled per-child |
| **Use case** | All-or-nothing operations | Independent tasks |
| **Error handling** | Single try-catch around scope | Per-task try-catch |

### When to Use Each

#### Use coroutineScope When:

1. **All operations must succeed** - Fail-fast behavior
2. **Operations depend on each other**
3. **Transaction-like semantics** - All or nothing

```kotlin
// Example: Loading user profile - need all data
suspend fun loadUserProfile(userId: Int): UserProfile = coroutineScope {
    val userDeferred = async { fetchUser(userId) }
    val postsDeferred = async { fetchPosts(userId) }
    val friendsDeferred = async { fetchFriends(userId) }

    // If any fails, cancel all and throw exception
    UserProfile(
        user = userDeferred.await(),
        posts = postsDeferred.await(),
        friends = friendsDeferred.await()
    )
}

// Usage
try {
    val profile = loadUserProfile(123)
    displayProfile(profile)
} catch (e: Exception) {
    showError("Failed to load profile")
}
```

#### Use supervisorScope When:

1. **Independent tasks** - One failure shouldn't affect others
2. **Best-effort operations** - Collect successful results
3. **Background tasks** - Continue on partial failures

```kotlin
// Example: Loading dashboard widgets - show what works
suspend fun loadDashboard(): Dashboard = supervisorScope {
    val weatherWidget = async {
        try {
            fetchWeather()
        } catch (e: Exception) {
            println("Weather failed: ${e.message}")
            WeatherWidget.UNAVAILABLE
        }
    }

    val newsWidget = async {
        try {
            fetchNews()
        } catch (e: Exception) {
            println("News failed: ${e.message}")
            NewsWidget.UNAVAILABLE
        }
    }

    val stocksWidget = async {
        try {
            fetchStocks()
        } catch (e: Exception) {
            println("Stocks failed: ${e.message}")
            StocksWidget.UNAVAILABLE
        }
    }

    // Show all widgets that loaded successfully
    Dashboard(
        weather = weatherWidget.await(),
        news = newsWidget.await(),
        stocks = stocksWidget.await()
    )
}
```

### Error Handling Patterns

#### Pattern 1: Explicit Error Handling in supervisorScope

```kotlin
suspend fun processItemsIndependently(items: List<Item>) = supervisorScope {
    val results = mutableListOf<Result>()
    val errors = mutableListOf<ItemError>()

    items.forEach { item ->
        launch {
            try {
                val result = processItem(item)
                synchronized(results) {
                    results.add(result)
                }
            } catch (e: Exception) {
                synchronized(errors) {
                    errors.add(ItemError(item.id, e))
                }
            }
        }
    }

    // Wait for all to complete
    coroutineContext[Job]?.children?.forEach { it.join() }

    ProcessingReport(
        successful = results,
        failed = errors
    )
}
```

#### Pattern 2: Collect Successful Results

```kotlin
data class PartialResult<T>(
    val successes: List<T>,
    val failures: List<Pair<String, Exception>>
)

suspend fun <T> parallelTasks(
    tasks: Map<String, suspend () -> T>
): PartialResult<T> = supervisorScope {
    val deferreds = tasks.map { (name, task) ->
        name to async {
            try {
                Result.success(task())
            } catch (e: Exception) {
                Result.failure<T>(e)
            }
        }
    }

    val results = deferreds.map { (name, deferred) ->
        name to deferred.await()
    }

    PartialResult(
        successes = results.mapNotNull { it.second.getOrNull() },
        failures = results.mapNotNull { (name, result) ->
            result.exceptionOrNull()?.let { name to it }
        }
    )
}

// Usage
val result = parallelTasks(
    mapOf(
        "API1" to { fetchFromApi1() },
        "API2" to { fetchFromApi2() },
        "API3" to { fetchFromApi3() }
    )
)

println("Successful: ${result.successes.size}")
println("Failed: ${result.failures.size}")
```

### Real-World Examples

#### Example 1: Data Synchronization

```kotlin
class SyncManager {
    // Use coroutineScope - all syncs must succeed
    suspend fun syncCriticalData() = coroutineScope {
        launch { syncUserProfile() }
        launch { syncSettings() }
        launch { syncPermissions() }
    }
    // If any fails, all are cancelled - maintain consistency

    // Use supervisorScope - best effort
    suspend fun syncOptionalData() = supervisorScope {
        launch {
            try { syncAnalytics() }
            catch (e: Exception) { /* Log and continue */ }
        }

        launch {
            try { syncCache() }
            catch (e: Exception) { /* Log and continue */ }
        }

        launch {
            try { syncPrefetch() }
            catch (e: Exception) { /* Log and continue */ }
        }
    }
    // Each can fail independently
}
```

#### Example 2: Microservices Aggregation

```kotlin
// Load from multiple services
suspend fun aggregateUserData(userId: Int): AggregatedData {
    return supervisorScope {
        val profile = async {
            try {
                userService.getProfile(userId)
            } catch (e: Exception) {
                logger.warn("Profile service failed", e)
                null
            }
        }

        val orders = async {
            try {
                orderService.getOrders(userId)
            } catch (e: Exception) {
                logger.warn("Order service failed", e)
                emptyList()
            }
        }

        val recommendations = async {
            try {
                recommendationService.getRecommendations(userId)
            } catch (e: Exception) {
                logger.warn("Recommendation service failed", e)
                emptyList()
            }
        }

        AggregatedData(
            profile = profile.await(),
            orders = orders.await(),
            recommendations = recommendations.await()
        )
    }
}
```

#### Example 3: Batch Processing

```kotlin
// Process with coroutineScope - stop on first error
suspend fun strictBatchProcess(items: List<Item>) {
    coroutineScope {
        items.forEach { item ->
            launch {
                processItem(item) // Any failure stops all
            }
        }
    }
}

// Process with supervisorScope - continue on errors
suspend fun lenientBatchProcess(items: List<Item>): BatchResult {
    return supervisorScope {
        val results = items.map { item ->
            async {
                try {
                    Result.success(processItem(item))
                } catch (e: Exception) {
                    Result.failure<ProcessedItem>(e)
                }
            }
        }.awaitAll()

        BatchResult(
            successful = results.count { it.isSuccess },
            failed = results.count { it.isFailure }
        )
    }
}
```

### CoroutineExceptionHandler

Only works with supervisorScope (independent failure handling):

```kotlin
val handler = CoroutineExceptionHandler { _, exception ->
    println("Caught: ${exception.message}")
}

// ✅ Works with supervisorScope
supervisorScope {
    launch(handler) {
        throw Exception("Task failed")
    }
    // Handler catches exception
}

// ❌ Doesn't work with coroutineScope
coroutineScope {
    launch(handler) {
        throw Exception("Task failed")
    }
    // Exception propagates to scope, handler not called
}
```

### Decision Tree

```
Do all operations need to succeed?
├─ Yes → coroutineScope
│   └─ One failure cancels all
│
└─ No → supervisorScope
    └─ Operations are independent
        ├─ Need all results?
        │   └─ Wrap each in try-catch
        │
        └─ OK with partial results?
            └─ Collect successful results
```

### Best Practices

1. **Default to coroutineScope** unless you need independent failures:
   ```kotlin
   // Most operations - use coroutineScope
   suspend fun loadData() = coroutineScope {
       // ...
   }
   ```

2. **Use supervisorScope for independent operations**:
   ```kotlin
   // Dashboard widgets - use supervisorScope
   suspend fun loadWidgets() = supervisorScope {
       // Each widget independent
   }
   ```

3. **Always handle errors in supervisorScope**:
   ```kotlin
   supervisorScope {
       launch {
           try {
               riskyOperation()
           } catch (e: Exception) {
               handleError(e)
           }
       }
   }
   ```

4. **Don't mix scopes unnecessarily**:
   ```kotlin
   // ❌ Confusing
   coroutineScope {
       supervisorScope {
           // ...
       }
   }

   // ✅ Pick one based on requirements
   supervisorScope {
       // All children independent
   }
   ```

### Common Pitfalls

1. **Not handling exceptions in supervisorScope**:
   ```kotlin
   // ❌ Exception printed but not handled
   supervisorScope {
       launch {
           throw Exception("Oops")
       }
   }

   // ✅ Explicit handling
   supervisorScope {
       launch {
           try {
               doWork()
           } catch (e: Exception) {
               handleError(e)
           }
       }
   }
   ```

2. **Using coroutineScope for independent tasks**:
   ```kotlin
   // ❌ One widget failure kills all
   coroutineScope {
       launch { loadWeather() }
       launch { loadNews() }
       launch { loadStocks() }
   }

   // ✅ Independent failures
   supervisorScope {
       launch { try { loadWeather() } catch(e: Exception) {} }
       launch { try { loadNews() } catch(e: Exception) {} }
       launch { try { loadStocks() } catch(e: Exception) {} }
   }
   ```

3. **Expecting CoroutineExceptionHandler to work with coroutineScope**:
   ```kotlin
   // ❌ Handler not called
   val handler = CoroutineExceptionHandler { _, e -> }
   coroutineScope {
       launch(handler) { throw Exception() }
   }

   // ✅ Use try-catch instead
   coroutineScope {
       try {
           launch { throw Exception() }
       } catch (e: Exception) {
           handleError(e)
       }
   }
   ```

**English Summary**: coroutineScope provides fail-fast behavior - any child failure cancels all siblings. supervisorScope allows independent failures - only the failed child is cancelled. Use coroutineScope for all-or-nothing operations where dependencies exist. Use supervisorScope for independent tasks where partial success is acceptable. Always explicitly handle exceptions in supervisorScope children. CoroutineExceptionHandler only works with supervisorScope.

## Ответ (RU)

Ключевое различие между `supervisorScope` и `coroutineScope` в том как они обрабатывают ошибки дочерних корутин.

### coroutineScope - Fail-Fast поведение

```kotlin
coroutineScope {
    launch { println("Task 1") }
    launch { throw Exception("Failed!") }
    launch { println("Task 3") }
}
// Task 1 и Task 3 отменены когда Task 2 провалилась!
```

### supervisorScope - Независимые ошибки

```kotlin
supervisorScope {
    launch { println("Task 1 completed") }
    launch { throw Exception("Failed!") }
    launch { println("Task 3 completed") }
}
// Все задачи завершаются независимо!
```

### Таблица сравнения

| Аспект | coroutineScope | supervisorScope |
|--------|----------------|-----------------|
| **Ошибка ребенка** | Отменяет всех детей | Только провалившийся отменен |
| **Ошибка родителя** | Отменяет всех детей | Отменяет всех детей |
| **Применение** | Все-или-ничего | Независимые задачи |

### Когда использовать

#### coroutineScope - Когда:

1. **Все операции должны успешно завершиться**
2. **Операции зависят друг от друга**
3. **Транзакционная семантика**

```kotlin
// Загрузка профиля - нужны все данные
suspend fun loadUserProfile(userId: Int) = coroutineScope {
    val user = async { fetchUser(userId) }
    val posts = async { fetchPosts(userId) }

    // Если любая провалится, отменить все
    UserProfile(user.await(), posts.await())
}
```

#### supervisorScope - Когда:

1. **Независимые задачи**
2. **Best-effort операции**
3. **Фоновые задачи**

```kotlin
// Загрузка виджетов - показать что работает
suspend fun loadDashboard() = supervisorScope {
    val weather = async {
        try { fetchWeather() }
        catch (e: Exception) { WeatherWidget.UNAVAILABLE }
    }

    val news = async {
        try { fetchNews() }
        catch (e: Exception) { NewsWidget.UNAVAILABLE }
    }

    Dashboard(weather.await(), news.await())
}
```

### Реальные примеры

#### Синхронизация данных

```kotlin
// coroutineScope - все синхронизации должны успешно завершиться
suspend fun syncCriticalData() = coroutineScope {
    launch { syncUserProfile() }
    launch { syncSettings() }
}

// supervisorScope - best effort
suspend fun syncOptionalData() = supervisorScope {
    launch {
        try { syncAnalytics() }
        catch (e: Exception) { /* Продолжить */ }
    }

    launch {
        try { syncCache() }
        catch (e: Exception) { /* Продолжить */ }
    }
}
```

#### Агрегация микросервисов

```kotlin
suspend fun aggregateUserData(userId: Int) = supervisorScope {
    val profile = async {
        try { userService.getProfile(userId) }
        catch (e: Exception) { null }
    }

    val orders = async {
        try { orderService.getOrders(userId) }
        catch (e: Exception) { emptyList() }
    }

    AggregatedData(
        profile = profile.await(),
        orders = orders.await()
    )
}
```

### Дерево решений

```
Все операции должны успешно завершиться?
├─ Да → coroutineScope
│   └─ Одна ошибка отменяет все
│
└─ Нет → supervisorScope
    └─ Операции независимы
```

### Лучшие практики

1. **По умолчанию coroutineScope** если не нужны независимые ошибки

2. **supervisorScope для независимых операций**:
   ```kotlin
   supervisorScope {
       launch {
           try { operation() }
           catch (e: Exception) { handle(e) }
       }
   }
   ```

3. **Всегда обрабатывайте ошибки в supervisorScope**

### Распространенные ошибки

1. **Не обработка исключений в supervisorScope**:
   ```kotlin
   // ❌ Исключение напечатано но не обработано
   supervisorScope {
       launch { throw Exception() }
   }

   // ✅ Явная обработка
   supervisorScope {
       launch {
           try { doWork() }
           catch (e: Exception) { handle(e) }
       }
   }
   ```

2. **coroutineScope для независимых задач**:
   ```kotlin
   // ❌ Одна ошибка убивает все
   coroutineScope {
       launch { loadWeather() }
       launch { loadNews() }
   }

   // ✅ Независимые ошибки
   supervisorScope {
       launch { try { loadWeather() } catch(e: Exception) {} }
       launch { try { loadNews() } catch(e: Exception) {} }
   }
   ```

**Краткое содержание**: coroutineScope обеспечивает fail-fast - любая ошибка ребенка отменяет всех детей. supervisorScope позволяет независимые ошибки - только провалившийся ребенок отменен. Используйте coroutineScope для все-или-ничего операций с зависимостями. Используйте supervisorScope для независимых задач где частичный успех приемлем. Всегда явно обрабатывайте исключения в детях supervisorScope.

---

## References
- [Supervision - Kotlin Coroutines Guide](https://kotlinlang.org/docs/exception-handling.html#supervision)
- [supervisorScope - API Reference](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/supervisor-scope.html)

## Related Questions
- [[q-coroutinescope-vs-supervisorscope--kotlin--medium]]
- [[q-job-vs-supervisorjob--kotlin--medium]]
