---
id: kotlin-053
title: "supervisorScope vs coroutineScope"
aliases: ["supervisorScope vs coroutineScope"]
topic: kotlin
subtopics: [coroutines, error-handling, scopes]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en]
source: internal
source_note: Phase 1 Coroutines & Flow Advanced Questions
status: draft
moc: moc-kotlin
related: [q-coroutinescope-vs-supervisorscope--kotlin--medium, q-job-vs-supervisorjob--kotlin--medium]
created: 2025-10-11
updated: 2025-10-11
tags: [coroutines, difficulty/medium, error-handling, kotlin, scopes, supervisor]
date created: Thursday, October 16th 2025, 4:28:10 pm
date modified: Tuesday, November 25th 2025, 8:53:48 pm
---
# Question (EN)

> Compare supervisorScope and coroutineScope. When should you use each? Demonstrate how they handle independent failures differently.

---

## Answer (EN)

The key difference between `supervisorScope` and `coroutineScope` is how they react to child coroutine failures inside structured concurrency.

### coroutineScope - Fail-Fast Behavior

`coroutineScope` is fail-fast: an unhandled exception in any child cancels the scope and its other children, and the exception is rethrown from the scope.

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
Conceptually (actual interleaving may vary):
Starting coroutineScope
Caught: Task 2 failed!
Done

Task 1 and Task 3 may not complete their work because the scope is cancelled when Task 2 fails.
*/
```

### supervisorScope - Independent Failures

`supervisorScope` isolates failures of its children: a failing child does not cancel its siblings. Unhandled exceptions from the scope as a whole can still propagate to the parent.

```kotlin
suspend fun demonstrateSupervisorScope() {
    println("Starting supervisorScope")

    try {
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
    } catch (e: Exception) {
        // This will be hit if a child's exception is not handled otherwise
        println("Caught in supervisorScope: ${e.message}")
    }

    println("Done")
}

/*
Conceptually:
Starting supervisorScope
Task 1 completed
Task 3 completed
Done

Task 2 failure does not cancel Task 1 and Task 3.
Exception routing depends on whether there is a parent handler.
*/
```

### Comparison Table

| Aspect | coroutineScope | supervisorScope |
|--------|----------------|-----------------|
| **Child failure** | Cancels the scope and (typically) all other children | Only the failing child is cancelled; siblings continue |
| **Parent failure** | Cancels all children | Cancels all children |
| **Exception propagation** | Unhandled exception from scope is rethrown to parent | Unhandled exception from scope is also rethrown; difference is sibling isolation |
| **Use case** | All-or-nothing operations | Independent tasks |
| **Error handling** | Often one try-catch around the scope is enough | Usually per-child try-catch for best-effort behavior |

### When to Use Each

#### Use coroutineScope When:

1. All operations must succeed (fail-fast).
2. Operations depend on each other.
3. You want transaction-like semantics (all or nothing).

```kotlin
// Example: Loading user profile - need all data
suspend fun loadUserProfile(userId: Int): UserProfile = coroutineScope {
    val userDeferred = async { fetchUser(userId) }
    val postsDeferred = async { fetchPosts(userId) }
    val friendsDeferred = async { fetchFriends(userId) }

    // If any fails, the scope is cancelled and the exception is thrown
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

1. Tasks are independent - one failure should not cancel others.
2. You want best-effort behavior - collect what succeeds.
3. Background/auxiliary work should continue despite partial failures.

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

    // supervisorScope waits for all its children to finish
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
    // Use coroutineScope - all critical syncs must succeed
    suspend fun syncCriticalData() = coroutineScope {
        launch { syncUserProfile() }
        launch { syncSettings() }
        launch { syncPermissions() }
    }
    // On any unhandled failure, the scope is cancelled.

    // Use supervisorScope - best effort for non-critical data
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
    // Each can fail independently without cancelling siblings.
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
// Process with coroutineScope - any unhandled failure cancels the scope
suspend fun strictBatchProcess(items: List<Item>) {
    coroutineScope {
        items.forEach { item ->
            launch {
                processItem(item)
            }
        }
    }
}

// Process with supervisorScope - continue on failures
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

`CoroutineExceptionHandler` is invoked for uncaught exceptions in root coroutines of a `CoroutineScope`. It is not limited to `supervisorScope`; it works with any scope where it is part of the context.

```kotlin
val handler = CoroutineExceptionHandler { _, exception ->
    println("Caught: ${exception.message}")
}

// Root scope with handler
val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default + handler)

// Handler will see this exception
scope.launch {
    throw Exception("Task failed")
}

// Nested supervisorScope: children failures go to handler if not caught
scope.launch {
    supervisorScope {
        launch {
            throw Exception("Child failed in supervisorScope")
        }
    }
}

// Nested coroutineScope: child failure cancels the scope and propagates up;
// you can catch it or let handler see it on the parent scope.
scope.launch {
    try {
        coroutineScope {
            launch {
                throw Exception("Child failed in coroutineScope")
            }
        }
    } catch (e: Exception) {
        println("Caught around coroutineScope: ${e.message}")
    }
}
```

Key point: `CoroutineExceptionHandler` behavior is the same with `coroutineScope` and `supervisorScope`; what differs is how child failures affect siblings and scope cancellation.

### Decision Tree

```
Do all operations need to succeed?
 Yes → coroutineScope
    One unhandled failure cancels the scope and usually other children.

 No → supervisorScope
     Operations are independent
         Need all results?
            Wrap each child in try-catch

         OK with partial results?
             Collect successful results
```

### Best Practices

1. Default to coroutineScope unless you explicitly need failure isolation:
   ```kotlin
   suspend fun loadData() = coroutineScope {
       // ...
   }
   ```

2. Use supervisorScope for independent operations:
   ```kotlin
   suspend fun loadWidgets() = supervisorScope {
       // Each widget independent
   }
   ```

3. In supervisorScope, handle child failures explicitly when you don't want them to crash the whole operation:
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

4. Avoid mixing scopes unnecessarily:
   ```kotlin
   // Confusing
   coroutineScope {
       supervisorScope {
           // ...
       }
   }

   // Prefer clear intent
   supervisorScope {
       // Children are independent
   }
   ```

### Common Pitfalls

1. Assuming supervisorScope swallows exceptions automatically:
   ```kotlin
   supervisorScope {
       launch {
           throw Exception("Oops") // If not caught, will propagate to parent/handler
       }
   }
   ```

2. Using coroutineScope where failures should be isolated:
   ```kotlin
   // One widget failure can cancel all
   coroutineScope {
       launch { loadWeather() }
       launch { loadNews() }
       launch { loadStocks() }
   }

   // For independent widgets, combine supervisorScope with per-child handling
   supervisorScope {
       launch { try { loadWeather() } catch (e: Exception) { /* ... */ } }
       launch { try { loadNews() } catch (e: Exception) { /* ... */ } }
       launch { try { loadStocks() } catch (e: Exception) { /* ... */ } }
   }
   ```

3. Misunderstanding CoroutineExceptionHandler with structured concurrency:
   ```kotlin
   val handler = CoroutineExceptionHandler { _, e -> println("Caught: $e") }
   val scope = CoroutineScope(SupervisorJob() + handler)

   // Handler is used for root coroutine failures
   scope.launch { throw Exception() }

   // For coroutineScope, catch around it or rely on parent's handler
   scope.launch {
       try {
           coroutineScope {
               launch { throw Exception("Inner failure") }
           }
       } catch (e: Exception) {
           handleError(e)
       }
   }
   ```

**English Summary**: `coroutineScope` is fail-fast: an unhandled child failure cancels the scope and (typically) its siblings, and the exception is rethrown. `supervisorScope` isolates child failures so one child does not cancel others, but unhandled exceptions can still propagate to the parent. Use `coroutineScope` for all-or-nothing operations with dependencies. Use `supervisorScope` for independent tasks and partial success scenarios. Always handle exceptions inside `supervisorScope` children when you don't want them to abort the whole operation. `CoroutineExceptionHandler` works uniformly based on where it is installed in the context; it is not exclusive to `supervisorScope`.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Supervision - Kotlin Coroutines Guide](https://kotlinlang.org/docs/exception-handling.html#supervision)
- [supervisorScope - API Reference](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/supervisor-scope.html)

## Related Questions
- [[q-coroutinescope-vs-supervisorscope--kotlin--medium]]
- [[q-job-vs-supervisorjob--kotlin--medium]]
