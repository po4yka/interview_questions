---
tags:
  - programming-languages
difficulty: medium
---

# CoroutineScope vs SupervisorScope

## Answer

Both create a new scope, but differ in error handling:

**coroutineScope {}**: If one child coroutine fails, **all siblings are cancelled**
**supervisorScope {}**: If one child coroutine fails, **others continue working independently**

### coroutineScope - Cooperative Failure

```kotlin
import kotlinx.coroutines.*

// coroutineScope: One failure cancels all
suspend fun coroutineScopeExample() = coroutineScope {
    launch {
        delay(100)
        println("Task 1")
        throw Exception("Task 1 failed!")  // Fails
    }

    launch {
        delay(200)
        println("Task 2")  // ❌ Never prints - cancelled
    }

    launch {
        delay(300)
        println("Task 3")  // ❌ Never prints - cancelled
    }
}

// Output:
// Task 1
// Exception: Task 1 failed!
// (Tasks 2 and 3 are cancelled)
```

### supervisorScope - Independent Failure

```kotlin
// supervisorScope: Failures are independent
suspend fun supervisorScopeExample() = supervisorScope {
    launch {
        delay(100)
        println("Task 1")
        throw Exception("Task 1 failed!")  // Fails
    }

    launch {
        delay(200)
        println("Task 2")  // ✅ Prints - not cancelled
    }

    launch {
        delay(300)
        println("Task 3")  // ✅ Prints - not cancelled
    }
}

// Output:
// Task 1
// Task 2  <- Still runs
// Task 3  <- Still runs
```

### When to Use Each

```kotlin
// Use coroutineScope when: Tasks depend on each other
suspend fun fetchUserData(userId: Int): UserData = coroutineScope {
    val profile = async { fetchProfile(userId) }
    val settings = async { fetchSettings(userId) }
    val friends = async { fetchFriends(userId) }

    UserData(
        profile.await(),
        settings.await(),
        friends.await()
    )
    // If any fails, all are cancelled (makes sense - we need all data)
}

// Use supervisorScope when: Tasks are independent
suspend fun loadDashboard(): DashboardData = supervisorScope {
    val news = async {
        try { fetchNews() }
        catch (e: Exception) { emptyList() }
    }

    val weather = async {
        try { fetchWeather() }
        catch (e: Exception) { Weather.Unknown }
    }

    val stocks = async {
        try { fetchStocks() }
        catch (e: Exception) { emptyList() }
    }

    DashboardData(
        news.await(),
        weather.await(),
        stocks.await()
    )
    // If one fails, others continue (independent widgets)
}
```

### Real-World Example: App Initialization

```kotlin
// Bad: Using coroutineScope for independent tasks
suspend fun badInitialization() = coroutineScope {
    launch { initializeAnalytics() }
    launch { loadUserPreferences() }
    launch { syncData() }
    // If analytics fails, everything stops! ❌
}

// Good: Using supervisorScope for independent tasks
suspend fun goodInitialization() = supervisorScope {
    launch {
        try {
            initializeAnalytics()
        } catch (e: Exception) {
            logError("Analytics init failed", e)
        }
    }

    launch {
        try {
            loadUserPreferences()
        } catch (e: Exception) {
            logError("Preferences load failed", e)
        }
    }

    launch {
        try {
            syncData()
        } catch (e: Exception) {
            logError("Sync failed", e)
        }
    }
    // Each task can fail independently ✅
}
```

### Error Propagation

```kotlin
// coroutineScope propagates exceptions
suspend fun coroutineScopePropagation() {
    try {
        coroutineScope {
            launch { throw Exception("Error!") }
        }
    } catch (e: Exception) {
        println("Caught: ${e.message}")  // ✅ Catches exception
    }
}

// supervisorScope doesn't propagate exceptions from children
suspend fun supervisorScopePropagation() {
    try {
        supervisorScope {
            launch { throw Exception("Error!") }  // Silent failure
        }
    } catch (e: Exception) {
        println("Caught: ${e.message}")  // ❌ Not caught!
    }
}

// Need exception handler in supervisorScope
suspend fun supervisorWithHandler() {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("Handler caught: ${exception.message}")
    }

    supervisorScope {
        launch(handler) {
            throw Exception("Error!")  // ✅ Caught by handler
        }
    }
}
```

### Structured Concurrency

```kotlin
// coroutineScope waits for all children
suspend fun coroutineScopeWaiting() {
    println("Start")

    coroutineScope {
        launch {
            delay(1000)
            println("Task 1")
        }
        launch {
            delay(2000)
            println("Task 2")
        }
    }

    println("End")  // Waits for both tasks to complete
}

// supervisorScope also waits for all children
suspend fun supervisorScopeWaiting() {
    println("Start")

    supervisorScope {
        launch {
            delay(1000)
            println("Task 1")
        }
        launch {
            delay(2000)
            println("Task 2")
        }
    }

    println("End")  // Waits for both tasks to complete
}
```

### Best Practices

```kotlin
class ScopeBestPractices {
    // ✅ Use coroutineScope for dependent operations
    suspend fun fetchCompleteUser(id: Int): User = coroutineScope {
        val basicInfo = async { fetchBasicInfo(id) }
        val detailedInfo = async { fetchDetailedInfo(id) }

        User(basicInfo.await(), detailedInfo.await())
        // Need both - if one fails, cancel all
    }

    // ✅ Use supervisorScope for independent operations
    suspend fun loadWidgets(): List<Widget> = supervisorScope {
        val widgets = mutableListOf<Widget>()

        launch {
            try {
                widgets.add(WeatherWidget(fetchWeather()))
            } catch (e: Exception) {
                widgets.add(WeatherWidget.Error)
            }
        }

        launch {
            try {
                widgets.add(NewsWidget(fetchNews()))
            } catch (e: Exception) {
                widgets.add(NewsWidget.Error)
            }
        }

        widgets
        // Independent widgets - one failure doesn't affect others
    }

    // ❌ Don't use supervisorScope if tasks are dependent
    suspend fun badExample() = supervisorScope {
        val userId = async { getUserId() }  // May fail silently
        val userData = async { getUserData(userId.await()) }  // Will fail if userId failed
        UserInfo(userId.await(), userData.await())
    }
}
```

### Summary Table

| Feature | coroutineScope | supervisorScope |
|---------|----------------|-----------------|
| **Error propagation** | One failure cancels all | Failures are independent |
| **Use case** | Dependent tasks | Independent tasks |
| **Exception handling** | Propagates to parent | Needs explicit handlers |
| **Waiting** | Waits for all children | Waits for all children |
| **Typical usage** | Data that must be complete | Optional/independent operations |

---

## Вопрос (RU)

В чем разница между coroutineScope и supervisorScope

## Ответ

Оба создают новый scope, но различие в обработке ошибок: coroutineScope {} – если одна дочерняя корутина упадет, отменяются все остальные. supervisorScope {} – если одна корутина упадет, остальные продолжают работу.
