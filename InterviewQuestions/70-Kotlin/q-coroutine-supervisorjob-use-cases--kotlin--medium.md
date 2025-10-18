---
id: "20251012-150003"
title: "SupervisorJob: when and why to use it?"
topic: kotlin
difficulty: medium
status: draft
created: "2025-10-12"
tags: ["kotlin", "coroutines", "supervisorjob", "error-handling", "job", "difficulty/medium"]
description: "Comprehensive guide to SupervisorJob in Kotlin coroutines, covering independent failure handling, comparison with regular Job, and real-world use cases in Android development"
moc: moc-kotlin
related: [q-delegation-by-keyword--kotlin--medium, q-flow-performance--kotlin--hard, q-dispatchers-unconfined--kotlin--medium]
subtopics: ["coroutines", "supervisorjob", "error-handling", "job"]
---
# SupervisorJob: when and why to use it?

## English

### Problem Statement

In structured concurrency, when a child coroutine fails, it normally cancels its parent and all siblings. However, sometimes we want independent failure handling where one coroutine's failure doesn't affect others. When should we use SupervisorJob instead of a regular Job, and what are the real-world use cases, especially in Android development?

### Solution

**SupervisorJob** is a special implementation of Job where the failure of a child doesn't affect the parent or other children. Each child is supervised independently.

#### Regular Job vs SupervisorJob

```kotlin
import kotlinx.coroutines.*

fun compareJobTypes() = runBlocking {
    println("=== Regular Job ===")

    // Regular Job: child failure cancels parent and siblings
    val regularJob = launch {
        launch {
            delay(500)
            println("Regular: Child 1 completed")
        }

        launch {
            delay(200)
            throw RuntimeException("Regular: Child 2 failed!")
        }

        launch {
            delay(1000)
            println("Regular: Child 3 completed") // Never executes
        }

        delay(2000)
        println("Regular: Parent completed") // Never executes
    }

    delay(1500)
    println("Regular job cancelled: ${regularJob.isCancelled}")

    println("\n=== SupervisorJob ===")

    // SupervisorJob: child failure is independent
    val supervisorJob = SupervisorJob()
    val scope = CoroutineScope(supervisorJob + Dispatchers.Default)

    scope.launch {
        delay(500)
        println("Supervisor: Child 1 completed")
    }

    scope.launch {
        delay(200)
        throw RuntimeException("Supervisor: Child 2 failed!")
    }

    scope.launch {
        delay(1000)
        println("Supervisor: Child 3 completed") // Executes successfully
    }

    delay(1500)
    println("Supervisor job cancelled: ${supervisorJob.isCancelled}")

    scope.cancel()
}
```

#### Creating SupervisorJob

```kotlin
import kotlinx.coroutines.*

fun supervisorJobCreation() = runBlocking {
    // Method 1: Standalone SupervisorJob
    val supervisorJob = SupervisorJob()
    val scope = CoroutineScope(Dispatchers.Default + supervisorJob)

    scope.launch {
        println("Child 1")
    }

    scope.launch {
        println("Child 2")
    }

    delay(100)
    scope.cancel()

    // Method 2: supervisorScope builder
    supervisorScope {
        launch {
            delay(500)
            println("supervisorScope: Child 1")
        }

        launch {
            throw RuntimeException("supervisorScope: Child 2 failed")
        }

        launch {
            delay(1000)
            println("supervisorScope: Child 3") // Still executes
        }

        delay(1500)
    }

    // Method 3: CoroutineScope with SupervisorJob
    val customScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    customScope.launch {
        println("Custom scope child")
    }

    delay(100)
    customScope.cancel()
}
```

#### Exception Handling with SupervisorJob

```kotlin
import kotlinx.coroutines.*

fun supervisorExceptionHandling() = runBlocking {
    println("=== Exception Handling ===")

    // SupervisorJob + CoroutineExceptionHandler
    val exceptionHandler = CoroutineExceptionHandler { context, exception ->
        println("Caught exception: ${exception.message}")
    }

    val supervisorJob = SupervisorJob()
    val scope = CoroutineScope(
        supervisorJob + Dispatchers.Default + exceptionHandler
    )

    // Child 1: Succeeds
    scope.launch {
        delay(500)
        println("Child 1 completed successfully")
    }

    // Child 2: Fails - exception caught by handler
    scope.launch {
        delay(200)
        throw RuntimeException("Child 2 failed!")
    }

    // Child 3: Still executes
    scope.launch {
        delay(1000)
        println("Child 3 completed successfully")
    }

    delay(1500)
    scope.cancel()

    println("\n=== Without Exception Handler ===")

    // Without handler: exceptions are printed to stderr
    val supervisorJob2 = SupervisorJob()
    val scope2 = CoroutineScope(supervisorJob2 + Dispatchers.Default)

    scope2.launch {
        throw RuntimeException("Unhandled exception!")
    }

    delay(500)
    scope2.cancel()
}
```

#### supervisorScope vs coroutineScope

```kotlin
import kotlinx.coroutines.*

suspend fun compareScopeBuilders() {
    println("=== coroutineScope ===")

    try {
        coroutineScope {
            launch {
                delay(500)
                println("coroutineScope: Child 1")
            }

            launch {
                delay(200)
                throw RuntimeException("coroutineScope: Failed")
            }

            launch {
                delay(1000)
                println("coroutineScope: Child 3") // Never executes
            }
        }
    } catch (e: RuntimeException) {
        println("coroutineScope caught exception: ${e.message}")
    }

    println("\n=== supervisorScope ===")

    try {
        supervisorScope {
            launch {
                delay(500)
                println("supervisorScope: Child 1")
            }

            launch {
                delay(200)
                throw RuntimeException("supervisorScope: Failed")
            }

            launch {
                delay(1000)
                println("supervisorScope: Child 3") // Still executes
            }

            delay(1500) // Wait for children
        }
    } catch (e: RuntimeException) {
        println("supervisorScope caught exception: ${e.message}")
    }
}
```

#### Android Use Cases

```kotlin
import kotlinx.coroutines.*
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope

// Use Case 1: ViewModel with independent operations
class UserProfileViewModel : ViewModel() {
    // Using viewModelScope which has SupervisorJob by default

    fun loadUserProfile(userId: String) {
        // Load user info
        viewModelScope.launch {
            try {
                val user = loadUser(userId)
                // Update UI
            } catch (e: Exception) {
                // Handle error
            }
        }

        // Load user posts (independent operation)
        viewModelScope.launch {
            try {
                val posts = loadUserPosts(userId)
                // Update UI
            } catch (e: Exception) {
                // Handle error - doesn't affect user info loading
            }
        }

        // Load user friends (independent operation)
        viewModelScope.launch {
            try {
                val friends = loadUserFriends(userId)
                // Update UI
            } catch (e: Exception) {
                // Handle error - doesn't affect other operations
            }
        }
    }

    private suspend fun loadUser(userId: String): User {
        delay(500)
        return User(userId, "John")
    }

    private suspend fun loadUserPosts(userId: String): List<Post> {
        delay(300)
        return emptyList()
    }

    private suspend fun loadUserFriends(userId: String): List<User> {
        delay(400)
        return emptyList()
    }
}

// Use Case 2: Repository with background sync
class DataRepository {
    private val supervisorJob = SupervisorJob()
    private val scope = CoroutineScope(Dispatchers.IO + supervisorJob)

    fun startBackgroundSync() {
        // Sync users
        scope.launch {
            try {
                syncUsers()
            } catch (e: Exception) {
                // Log error, don't stop other syncs
            }
        }

        // Sync posts
        scope.launch {
            try {
                syncPosts()
            } catch (e: Exception) {
                // Log error, don't stop other syncs
            }
        }

        // Sync comments
        scope.launch {
            try {
                syncComments()
            } catch (e: Exception) {
                // Log error, don't stop other syncs
            }
        }
    }

    fun stopSync() {
        scope.cancel()
    }

    private suspend fun syncUsers() {
        delay(1000)
        println("Users synced")
    }

    private suspend fun syncPosts() {
        delay(800)
        println("Posts synced")
    }

    private suspend fun syncComments() {
        delay(600)
        println("Comments synced")
    }
}

// Use Case 3: Dashboard with multiple widgets
class DashboardViewModel : ViewModel() {
    private val exceptionHandler = CoroutineExceptionHandler { _, exception ->
        println("Widget failed: ${exception.message}")
        // Show partial UI with error indicators
    }

    fun loadDashboard() {
        // Each widget loads independently
        viewModelScope.launch(exceptionHandler) {
            loadWeatherWidget()
        }

        viewModelScope.launch(exceptionHandler) {
            loadNewsWidget()
        }

        viewModelScope.launch(exceptionHandler) {
            loadStocksWidget()
        }

        viewModelScope.launch(exceptionHandler) {
            loadCalendarWidget()
        }
    }

    private suspend fun loadWeatherWidget() {
        delay(500)
        // throw Exception("Weather service unavailable")
        println("Weather widget loaded")
    }

    private suspend fun loadNewsWidget() {
        delay(300)
        println("News widget loaded")
    }

    private suspend fun loadStocksWidget() {
        delay(400)
        println("Stocks widget loaded")
    }

    private suspend fun loadCalendarWidget() {
        delay(200)
        println("Calendar widget loaded")
    }
}

data class User(val id: String, val name: String)
data class Post(val id: String, val title: String)
```

#### Advanced Patterns

```kotlin
import kotlinx.coroutines.*

// Pattern 1: Retry with SupervisorJob
class RetryableScope {
    private val supervisorJob = SupervisorJob()
    private val scope = CoroutineScope(Dispatchers.Default + supervisorJob)

    fun <T> launchWithRetry(
        maxRetries: Int = 3,
        block: suspend () -> T
    ): Job {
        return scope.launch {
            var lastException: Exception? = null

            repeat(maxRetries) { attempt ->
                try {
                    block()
                    return@launch // Success
                } catch (e: Exception) {
                    lastException = e
                    println("Attempt ${attempt + 1} failed: ${e.message}")
                    delay(1000L * (attempt + 1))
                }
            }

            // All retries failed
            throw lastException ?: Exception("All retries failed")
        }
    }

    fun cancel() {
        scope.cancel()
    }
}

// Pattern 2: Supervised child scopes
suspend fun supervisedChildren() = supervisorScope {
    // Each child has its own supervisor
    launch {
        supervisorScope {
            launch { println("Grandchild 1.1") }
            launch {
                throw RuntimeException("Grandchild 1.2 failed")
            }
            launch {
                delay(500)
                println("Grandchild 1.3")
            }
            delay(1000)
        }
    }

    launch {
        supervisorScope {
            launch { println("Grandchild 2.1") }
            launch { println("Grandchild 2.2") }
            delay(500)
        }
    }

    delay(1500)
}

// Pattern 3: Fallback mechanism
class DataLoader {
    private val supervisorJob = SupervisorJob()
    private val scope = CoroutineScope(Dispatchers.IO + supervisorJob)

    suspend fun loadWithFallback(): String {
        val primaryJob = scope.async {
            loadFromPrimarySource()
        }

        val fallbackJob = scope.async {
            delay(2000) // Wait before trying fallback
            loadFromFallbackSource()
        }

        return try {
            primaryJob.await()
        } catch (e: Exception) {
            println("Primary failed, using fallback")
            fallbackJob.await()
        }
    }

    private suspend fun loadFromPrimarySource(): String {
        delay(1000)
        throw Exception("Primary source failed")
    }

    private suspend fun loadFromFallbackSource(): String {
        delay(500)
        return "Fallback data"
    }

    fun cleanup() {
        scope.cancel()
    }
}

// Pattern 4: Partial results collection
suspend fun collectPartialResults(): List<String> = supervisorScope {
    val jobs = List(5) { index ->
        async {
            delay(index * 100L)
            if (index == 2) throw Exception("Job $index failed")
            "Result $index"
        }
    }

    val results = mutableListOf<String>()
    jobs.forEach { job ->
        try {
            results.add(job.await())
        } catch (e: Exception) {
            println("Skipping failed job: ${e.message}")
        }
    }

    results
}

fun demonstrateAdvancedPatterns() = runBlocking {
    // Retry pattern
    val retryScope = RetryableScope()
    retryScope.launchWithRetry {
        if (Math.random() > 0.5) throw Exception("Random failure")
        println("Operation succeeded")
    }
    delay(5000)
    retryScope.cancel()

    // Supervised children
    supervisedChildren()

    // Fallback mechanism
    val loader = DataLoader()
    val data = loader.loadWithFallback()
    println("Loaded: $data")
    loader.cleanup()

    // Partial results
    val results = collectPartialResults()
    println("Collected results: $results")
}
```

#### SupervisorJob Lifecycle Management

```kotlin
import kotlinx.coroutines.*

class ManagedSupervisorScope {
    private var supervisorJob: CompletableJob? = null
    private var scope: CoroutineScope? = null

    fun start() {
        supervisorJob = SupervisorJob()
        scope = CoroutineScope(Dispatchers.Default + supervisorJob!!)
    }

    fun launchTask(block: suspend CoroutineScope.() -> Unit): Job {
        return scope?.launch(block = block)
            ?: throw IllegalStateException("Scope not started")
    }

    suspend fun stop() {
        supervisorJob?.cancelAndJoin()
        supervisorJob = null
        scope = null
    }

    fun isActive(): Boolean = supervisorJob?.isActive == true

    suspend fun stopAndRestart() {
        stop()
        start()
    }
}

fun demonstrateLifecycleManagement() = runBlocking {
    val managedScope = ManagedSupervisorScope()

    managedScope.start()

    managedScope.launchTask {
        delay(500)
        println("Task 1 completed")
    }

    managedScope.launchTask {
        delay(1000)
        println("Task 2 completed")
    }

    delay(1500)
    managedScope.stop()

    println("Scope stopped, restarting...")
    managedScope.start()

    managedScope.launchTask {
        println("New task after restart")
    }

    delay(500)
    managedScope.stop()
}
```

#### Testing SupervisorJob

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.*

class SupervisorJobTest {
    @Test
    fun testIndependentFailures() = runTest {
        val supervisorJob = SupervisorJob()
        val scope = CoroutineScope(supervisorJob + StandardTestDispatcher(testScheduler))

        var job1Completed = false
        var job2Failed = false
        var job3Completed = false

        scope.launch {
            delay(500)
            job1Completed = true
        }

        scope.launch {
            delay(200)
            job2Failed = true
            throw RuntimeException("Job 2 failed")
        }

        scope.launch {
            delay(1000)
            job3Completed = true
        }

        advanceTimeBy(1500)

        assertTrue(job1Completed)
        assertTrue(job2Failed)
        assertTrue(job3Completed)

        scope.cancel()
    }

    @Test
    fun testSupervisorScopeVsCoroutineScope() = runTest {
        // supervisorScope continues despite child failure
        var supervisorCompleted = false
        supervisorScope {
            launch {
                throw RuntimeException("Child failed")
            }
            delay(500)
            supervisorCompleted = true
        }

        assertTrue(supervisorCompleted)

        // coroutineScope fails if child fails
        var coroutineCompleted = false
        try {
            coroutineScope {
                launch {
                    throw RuntimeException("Child failed")
                }
                delay(500)
                coroutineCompleted = true
            }
        } catch (e: RuntimeException) {
            // Expected
        }

        assertFalse(coroutineCompleted)
    }

    @Test
    fun testExceptionHandlerWithSupervisorJob() = runTest {
        val exceptions = mutableListOf<Throwable>()
        val handler = CoroutineExceptionHandler { _, exception ->
            exceptions.add(exception)
        }

        val supervisorJob = SupervisorJob()
        val scope = CoroutineScope(
            supervisorJob + StandardTestDispatcher(testScheduler) + handler
        )

        scope.launch {
            throw RuntimeException("Error 1")
        }

        scope.launch {
            delay(100)
            throw RuntimeException("Error 2")
        }

        advanceTimeBy(500)

        assertEquals(2, exceptions.size)

        scope.cancel()
    }
}
```

### Best Practices

1. **Use SupervisorJob for independent operations**
   ```kotlin
   // Good: Independent network calls
   viewModelScope.launch { loadUsers() }
   viewModelScope.launch { loadPosts() }
   viewModelScope.launch { loadComments() }
   ```

2. **Always provide CoroutineExceptionHandler with SupervisorJob**
   ```kotlin
   val handler = CoroutineExceptionHandler { _, exception ->
       // Handle exception
   }
   val scope = CoroutineScope(SupervisorJob() + handler)
   ```

3. **Use supervisorScope for scoped supervision**
   ```kotlin
   suspend fun loadData() = supervisorScope {
       // Children fail independently
   }
   ```

4. **Don't use SupervisorJob for dependent operations**
   ```kotlin
   // Bad: These are sequential and dependent
   supervisorScope {
       val user = loadUser()
       val profile = loadProfile(user)
       val settings = loadSettings(profile)
   }

   // Good: Use regular coroutineScope
   coroutineScope {
       val user = loadUser()
       val profile = loadProfile(user)
       val settings = loadSettings(profile)
   }
   ```

5. **Cancel SupervisorJob explicitly**
   ```kotlin
   class MyScope {
       private val job = SupervisorJob()
       private val scope = CoroutineScope(job)

       fun cleanup() {
           job.cancel() // Don't forget to cancel!
       }
   }
   ```

### Common Pitfalls

1. **Forgetting exception handler with SupervisorJob**
   - Exceptions are lost without handler
2. **Using SupervisorJob for sequential operations**
   - Breaks error propagation
3. **Not cancelling SupervisorJob**
   - Resource leaks
4. **Expecting automatic error propagation**
   - Must handle errors in each child

---

## Русский

### Описание проблемы

В структурированном параллелизме, когда дочерняя корутина падает с ошибкой, она обычно отменяет родителя и всех siblings. Однако иногда нам нужна независимая обработка ошибок, где сбой одной корутины не влияет на другие. Когда следует использовать SupervisorJob вместо обычного Job, и каковы реальные случаи использования, особенно в Android-разработке?

### Решение

**SupervisorJob** - это специальная реализация Job, где сбой дочерней корутины не влияет на родителя или других потомков. Каждый потомок контролируется независимо.

#### Обычный Job vs SupervisorJob

```kotlin
import kotlinx.coroutines.*

fun compareJobTypes() = runBlocking {
    println("=== Обычный Job ===")

    // Обычный Job: сбой потомка отменяет родителя и siblings
    val regularJob = launch {
        launch {
            delay(500)
            println("Regular: Потомок 1 завершен")
        }

        launch {
            delay(200)
            throw RuntimeException("Regular: Потомок 2 упал!")
        }

        launch {
            delay(1000)
            println("Regular: Потомок 3 завершен") // Никогда не выполнится
        }

        delay(2000)
        println("Regular: Родитель завершен") // Никогда не выполнится
    }

    delay(1500)
    println("Regular job отменен: ${regularJob.isCancelled}")

    println("\n=== SupervisorJob ===")

    // SupervisorJob: сбой потомка независим
    val supervisorJob = SupervisorJob()
    val scope = CoroutineScope(supervisorJob + Dispatchers.Default)

    scope.launch {
        delay(500)
        println("Supervisor: Потомок 1 завершен")
    }

    scope.launch {
        delay(200)
        throw RuntimeException("Supervisor: Потомок 2 упал!")
    }

    scope.launch {
        delay(1000)
        println("Supervisor: Потомок 3 завершен") // Успешно выполнится
    }

    delay(1500)
    println("Supervisor job отменен: ${supervisorJob.isCancelled}")

    scope.cancel()
}
```

#### Создание SupervisorJob

```kotlin
import kotlinx.coroutines.*

fun supervisorJobCreation() = runBlocking {
    // Способ 1: Отдельный SupervisorJob
    val supervisorJob = SupervisorJob()
    val scope = CoroutineScope(Dispatchers.Default + supervisorJob)

    scope.launch {
        println("Потомок 1")
    }

    scope.launch {
        println("Потомок 2")
    }

    delay(100)
    scope.cancel()

    // Способ 2: supervisorScope builder
    supervisorScope {
        launch {
            delay(500)
            println("supervisorScope: Потомок 1")
        }

        launch {
            throw RuntimeException("supervisorScope: Потомок 2 упал")
        }

        launch {
            delay(1000)
            println("supervisorScope: Потомок 3") // Все равно выполнится
        }

        delay(1500)
    }

    // Способ 3: CoroutineScope с SupervisorJob
    val customScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    customScope.launch {
        println("Потомок custom scope")
    }

    delay(100)
    customScope.cancel()
}
```

#### Обработка исключений с SupervisorJob

```kotlin
import kotlinx.coroutines.*

fun supervisorExceptionHandling() = runBlocking {
    println("=== Обработка исключений ===")

    // SupervisorJob + CoroutineExceptionHandler
    val exceptionHandler = CoroutineExceptionHandler { context, exception ->
        println("Перехвачено исключение: ${exception.message}")
    }

    val supervisorJob = SupervisorJob()
    val scope = CoroutineScope(
        supervisorJob + Dispatchers.Default + exceptionHandler
    )

    // Потомок 1: Успешен
    scope.launch {
        delay(500)
        println("Потомок 1 успешно завершен")
    }

    // Потомок 2: Падает - исключение перехватывается handler'ом
    scope.launch {
        delay(200)
        throw RuntimeException("Потомок 2 упал!")
    }

    // Потомок 3: Все равно выполняется
    scope.launch {
        delay(1000)
        println("Потомок 3 успешно завершен")
    }

    delay(1500)
    scope.cancel()

    println("\n=== Без Exception Handler ===")

    // Без handler'а: исключения выводятся в stderr
    val supervisorJob2 = SupervisorJob()
    val scope2 = CoroutineScope(supervisorJob2 + Dispatchers.Default)

    scope2.launch {
        throw RuntimeException("Необработанное исключение!")
    }

    delay(500)
    scope2.cancel()
}
```

#### supervisorScope vs coroutineScope

```kotlin
import kotlinx.coroutines.*

suspend fun compareScopeBuilders() {
    println("=== coroutineScope ===")

    try {
        coroutineScope {
            launch {
                delay(500)
                println("coroutineScope: Потомок 1")
            }

            launch {
                delay(200)
                throw RuntimeException("coroutineScope: Упал")
            }

            launch {
                delay(1000)
                println("coroutineScope: Потомок 3") // Никогда не выполнится
            }
        }
    } catch (e: RuntimeException) {
        println("coroutineScope перехватил исключение: ${e.message}")
    }

    println("\n=== supervisorScope ===")

    try {
        supervisorScope {
            launch {
                delay(500)
                println("supervisorScope: Потомок 1")
            }

            launch {
                delay(200)
                throw RuntimeException("supervisorScope: Упал")
            }

            launch {
                delay(1000)
                println("supervisorScope: Потомок 3") // Все равно выполнится
            }

            delay(1500) // Ждем потомков
        }
    } catch (e: RuntimeException) {
        println("supervisorScope перехватил исключение: ${e.message}")
    }
}
```

#### Случаи использования в Android

```kotlin
import kotlinx.coroutines.*
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope

// Случай 1: ViewModel с независимыми операциями
class UserProfileViewModel : ViewModel() {
    // Используем viewModelScope, который имеет SupervisorJob по умолчанию

    fun loadUserProfile(userId: String) {
        // Загружаем информацию о пользователе
        viewModelScope.launch {
            try {
                val user = loadUser(userId)
                // Обновляем UI
            } catch (e: Exception) {
                // Обрабатываем ошибку
            }
        }

        // Загружаем посты пользователя (независимая операция)
        viewModelScope.launch {
            try {
                val posts = loadUserPosts(userId)
                // Обновляем UI
            } catch (e: Exception) {
                // Обрабатываем ошибку - не влияет на загрузку информации о пользователе
            }
        }

        // Загружаем друзей пользователя (независимая операция)
        viewModelScope.launch {
            try {
                val friends = loadUserFriends(userId)
                // Обновляем UI
            } catch (e: Exception) {
                // Обрабатываем ошибку - не влияет на другие операции
            }
        }
    }

    private suspend fun loadUser(userId: String): User {
        delay(500)
        return User(userId, "John")
    }

    private suspend fun loadUserPosts(userId: String): List<Post> {
        delay(300)
        return emptyList()
    }

    private suspend fun loadUserFriends(userId: String): List<User> {
        delay(400)
        return emptyList()
    }
}

// Случай 2: Repository с фоновой синхронизацией
class DataRepository {
    private val supervisorJob = SupervisorJob()
    private val scope = CoroutineScope(Dispatchers.IO + supervisorJob)

    fun startBackgroundSync() {
        // Синхронизация пользователей
        scope.launch {
            try {
                syncUsers()
            } catch (e: Exception) {
                // Логируем ошибку, не останавливаем другие синхронизации
            }
        }

        // Синхронизация постов
        scope.launch {
            try {
                syncPosts()
            } catch (e: Exception) {
                // Логируем ошибку, не останавливаем другие синхронизации
            }
        }

        // Синхронизация комментариев
        scope.launch {
            try {
                syncComments()
            } catch (e: Exception) {
                // Логируем ошибку, не останавливаем другие синхронизации
            }
        }
    }

    fun stopSync() {
        scope.cancel()
    }

    private suspend fun syncUsers() {
        delay(1000)
        println("Пользователи синхронизированы")
    }

    private suspend fun syncPosts() {
        delay(800)
        println("Посты синхронизированы")
    }

    private suspend fun syncComments() {
        delay(600)
        println("Комментарии синхронизированы")
    }
}

// Случай 3: Dashboard с несколькими виджетами
class DashboardViewModel : ViewModel() {
    private val exceptionHandler = CoroutineExceptionHandler { _, exception ->
        println("Виджет упал: ${exception.message}")
        // Показываем частичный UI с индикаторами ошибок
    }

    fun loadDashboard() {
        // Каждый виджет загружается независимо
        viewModelScope.launch(exceptionHandler) {
            loadWeatherWidget()
        }

        viewModelScope.launch(exceptionHandler) {
            loadNewsWidget()
        }

        viewModelScope.launch(exceptionHandler) {
            loadStocksWidget()
        }

        viewModelScope.launch(exceptionHandler) {
            loadCalendarWidget()
        }
    }

    private suspend fun loadWeatherWidget() {
        delay(500)
        // throw Exception("Сервис погоды недоступен")
        println("Виджет погоды загружен")
    }

    private suspend fun loadNewsWidget() {
        delay(300)
        println("Виджет новостей загружен")
    }

    private suspend fun loadStocksWidget() {
        delay(400)
        println("Виджет акций загружен")
    }

    private suspend fun loadCalendarWidget() {
        delay(200)
        println("Виджет календаря загружен")
    }
}

data class User(val id: String, val name: String)
data class Post(val id: String, val title: String)
```

#### Продвинутые паттерны

```kotlin
import kotlinx.coroutines.*

// Паттерн 1: Retry с SupervisorJob
class RetryableScope {
    private val supervisorJob = SupervisorJob()
    private val scope = CoroutineScope(Dispatchers.Default + supervisorJob)

    fun <T> launchWithRetry(
        maxRetries: Int = 3,
        block: suspend () -> T
    ): Job {
        return scope.launch {
            var lastException: Exception? = null

            repeat(maxRetries) { attempt ->
                try {
                    block()
                    return@launch // Успех
                } catch (e: Exception) {
                    lastException = e
                    println("Попытка ${attempt + 1} не удалась: ${e.message}")
                    delay(1000L * (attempt + 1))
                }
            }

            // Все попытки не удались
            throw lastException ?: Exception("Все попытки не удались")
        }
    }

    fun cancel() {
        scope.cancel()
    }
}

// Паттерн 2: Надзираемые дочерние scope'ы
suspend fun supervisedChildren() = supervisorScope {
    // Каждый потомок имеет свой supervisor
    launch {
        supervisorScope {
            launch { println("Внук 1.1") }
            launch {
                throw RuntimeException("Внук 1.2 упал")
            }
            launch {
                delay(500)
                println("Внук 1.3")
            }
            delay(1000)
        }
    }

    launch {
        supervisorScope {
            launch { println("Внук 2.1") }
            launch { println("Внук 2.2") }
            delay(500)
        }
    }

    delay(1500)
}

// Паттерн 3: Механизм запасного варианта
class DataLoader {
    private val supervisorJob = SupervisorJob()
    private val scope = CoroutineScope(Dispatchers.IO + supervisorJob)

    suspend fun loadWithFallback(): String {
        val primaryJob = scope.async {
            loadFromPrimarySource()
        }

        val fallbackJob = scope.async {
            delay(2000) // Ждем перед попыткой запасного варианта
            loadFromFallbackSource()
        }

        return try {
            primaryJob.await()
        } catch (e: Exception) {
            println("Основной источник упал, используем запасной")
            fallbackJob.await()
        }
    }

    private suspend fun loadFromPrimarySource(): String {
        delay(1000)
        throw Exception("Основной источник упал")
    }

    private suspend fun loadFromFallbackSource(): String {
        delay(500)
        return "Данные запасного варианта"
    }

    fun cleanup() {
        scope.cancel()
    }
}

// Паттерн 4: Сбор частичных результатов
suspend fun collectPartialResults(): List<String> = supervisorScope {
    val jobs = List(5) { index ->
        async {
            delay(index * 100L)
            if (index == 2) throw Exception("Job $index упал")
            "Результат $index"
        }
    }

    val results = mutableListOf<String>()
    jobs.forEach { job ->
        try {
            results.add(job.await())
        } catch (e: Exception) {
            println("Пропускаем упавший job: ${e.message}")
        }
    }

    results
}

fun demonstrateAdvancedPatterns() = runBlocking {
    // Retry паттерн
    val retryScope = RetryableScope()
    retryScope.launchWithRetry {
        if (Math.random() > 0.5) throw Exception("Случайный сбой")
        println("Операция успешна")
    }
    delay(5000)
    retryScope.cancel()

    // Надзираемые потомки
    supervisedChildren()

    // Механизм запасного варианта
    val loader = DataLoader()
    val data = loader.loadWithFallback()
    println("Загружено: $data")
    loader.cleanup()

    // Частичные результаты
    val results = collectPartialResults()
    println("Собранные результаты: $results")
}
```

#### Управление жизненным циклом SupervisorJob

```kotlin
import kotlinx.coroutines.*

class ManagedSupervisorScope {
    private var supervisorJob: CompletableJob? = null
    private var scope: CoroutineScope? = null

    fun start() {
        supervisorJob = SupervisorJob()
        scope = CoroutineScope(Dispatchers.Default + supervisorJob!!)
    }

    fun launchTask(block: suspend CoroutineScope.() -> Unit): Job {
        return scope?.launch(block = block)
            ?: throw IllegalStateException("Scope не запущен")
    }

    suspend fun stop() {
        supervisorJob?.cancelAndJoin()
        supervisorJob = null
        scope = null
    }

    fun isActive(): Boolean = supervisorJob?.isActive == true

    suspend fun stopAndRestart() {
        stop()
        start()
    }
}

fun demonstrateLifecycleManagement() = runBlocking {
    val managedScope = ManagedSupervisorScope()

    managedScope.start()

    managedScope.launchTask {
        delay(500)
        println("Задача 1 завершена")
    }

    managedScope.launchTask {
        delay(1000)
        println("Задача 2 завершена")
    }

    delay(1500)
    managedScope.stop()

    println("Scope остановлен, перезапускаем...")
    managedScope.start()

    managedScope.launchTask {
        println("Новая задача после перезапуска")
    }

    delay(500)
    managedScope.stop()
}
```

#### Тестирование SupervisorJob

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.*

class SupervisorJobTest {
    @Test
    fun testIndependentFailures() = runTest {
        val supervisorJob = SupervisorJob()
        val scope = CoroutineScope(supervisorJob + StandardTestDispatcher(testScheduler))

        var job1Completed = false
        var job2Failed = false
        var job3Completed = false

        scope.launch {
            delay(500)
            job1Completed = true
        }

        scope.launch {
            delay(200)
            job2Failed = true
            throw RuntimeException("Job 2 упал")
        }

        scope.launch {
            delay(1000)
            job3Completed = true
        }

        advanceTimeBy(1500)

        assertTrue(job1Completed)
        assertTrue(job2Failed)
        assertTrue(job3Completed)

        scope.cancel()
    }

    @Test
    fun testSupervisorScopeVsCoroutineScope() = runTest {
        // supervisorScope продолжает работу несмотря на сбой потомка
        var supervisorCompleted = false
        supervisorScope {
            launch {
                throw RuntimeException("Потомок упал")
            }
            delay(500)
            supervisorCompleted = true
        }

        assertTrue(supervisorCompleted)

        // coroutineScope падает, если падает потомок
        var coroutineCompleted = false
        try {
            coroutineScope {
                launch {
                    throw RuntimeException("Потомок упал")
                }
                delay(500)
                coroutineCompleted = true
            }
        } catch (e: RuntimeException) {
            // Ожидаемо
        }

        assertFalse(coroutineCompleted)
    }

    @Test
    fun testExceptionHandlerWithSupervisorJob() = runTest {
        val exceptions = mutableListOf<Throwable>()
        val handler = CoroutineExceptionHandler { _, exception ->
            exceptions.add(exception)
        }

        val supervisorJob = SupervisorJob()
        val scope = CoroutineScope(
            supervisorJob + StandardTestDispatcher(testScheduler) + handler
        )

        scope.launch {
            throw RuntimeException("Ошибка 1")
        }

        scope.launch {
            delay(100)
            throw RuntimeException("Ошибка 2")
        }

        advanceTimeBy(500)

        assertEquals(2, exceptions.size)

        scope.cancel()
    }
}
```

### Лучшие практики

1. **Используйте SupervisorJob для независимых операций**
   ```kotlin
   // Хорошо: Независимые сетевые вызовы
   viewModelScope.launch { loadUsers() }
   viewModelScope.launch { loadPosts() }
   viewModelScope.launch { loadComments() }
   ```

2. **Всегда предоставляйте CoroutineExceptionHandler с SupervisorJob**
   ```kotlin
   val handler = CoroutineExceptionHandler { _, exception ->
       // Обрабатываем исключение
   }
   val scope = CoroutineScope(SupervisorJob() + handler)
   ```

3. **Используйте supervisorScope для scope'd supervision**
   ```kotlin
   suspend fun loadData() = supervisorScope {
       // Потомки падают независимо
   }
   ```

4. **Не используйте SupervisorJob для зависимых операций**
   ```kotlin
   // Плохо: Это последовательные и зависимые операции
   supervisorScope {
       val user = loadUser()
       val profile = loadProfile(user)
       val settings = loadSettings(profile)
   }

   // Хорошо: Используйте обычный coroutineScope
   coroutineScope {
       val user = loadUser()
       val profile = loadProfile(user)
       val settings = loadSettings(profile)
   }
   ```

5. **Отменяйте SupervisorJob явно**
   ```kotlin
   class MyScope {
       private val job = SupervisorJob()
       private val scope = CoroutineScope(job)

       fun cleanup() {
           job.cancel() // Не забудьте отменить!
       }
   }
   ```

### Частые ошибки

1. **Забывание exception handler'а с SupervisorJob**
   - Исключения теряются без handler'а
2. **Использование SupervisorJob для последовательных операций**
   - Нарушает распространение ошибок
3. **Неотмена SupervisorJob**
   - Утечки ресурсов
4. **Ожидание автоматического распространения ошибок**
   - Нужно обрабатывать ошибки в каждом потомке

---

## Follow-ups

1. Can you use both regular Job and SupervisorJob in the same coroutine hierarchy?
2. What happens if the parent scope has SupervisorJob but a child creates a regular Job?
3. How does SupervisorJob affect exception propagation in nested scopes?
4. What's the difference between SupervisorJob() and Job() in terms of completion behavior?
5. Can supervisorScope throw exceptions to its caller?
6. How do you test code that uses SupervisorJob effectively?
7. What's the performance impact of using SupervisorJob vs regular Job?
8. When should you use supervisorScope vs creating a CoroutineScope with SupervisorJob?

## References

- [Kotlin Coroutines Guide - Exception Handling](https://kotlinlang.org/docs/exception-handling.html)
- [SupervisorJob - kotlinx.coroutines API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-supervisor-job.html)
- [Android Developers - viewModelScope](https://developer.android.com/topic/libraries/architecture/coroutines)
- [Roman Elizarov - Exceptions in coroutines](https://medium.com/@elizarov/exceptions-in-coroutines-ce8da1ec060c)

## Related Questions

- [[q-coroutine-job-lifecycle--kotlin--medium]]
- [[q-coroutine-parent-child-relationship--kotlin--medium]]
- [[q-coroutine-exception-handling--kotlin--hard]]
- [[q-coroutine-context-elements--kotlin--hard]]
- [[q-structured-concurrency--kotlin--hard]]
