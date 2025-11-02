---
id: kotlin-099
title: "When to use withContext in Kotlin coroutines? / Когда использовать withContext"
aliases: [WithContext, Context Switching, Dispatchers, WithContext Use Cases]
topic: kotlin
subtopics: [coroutines, dispatchers]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-race-conditions-coroutines--kotlin--hard, q-launch-vs-async-vs-runblocking--kotlin--medium, q-kotlin-non-inheritable-class--programming-languages--easy]
created: 2025-10-12
updated: 2025-10-31
tags:
  - kotlin
  - coroutines
  - withcontext
  - dispatchers
  - context-switching
  - difficulty/medium
---
# When to use withContext in Kotlin coroutines?

## English

### Problem Statement

The `withContext` function is one of the most commonly used coroutine builders, but understanding when and why to use it over alternatives like `launch` or `async` can be confusing. What are the specific use cases for `withContext`, and how does it compare to other coroutine builders in terms of performance and behavior?

### Solution

`withContext` is a **suspending function** that switches the coroutine context, executes a block of code, and returns the result. It's primarily used for switching dispatchers to perform specific operations on appropriate threads.

#### Basic withContext Usage

```kotlin
import kotlinx.coroutines.*

suspend fun loadData(): String = withContext(Dispatchers.IO) {
    // Perform I/O operation on IO dispatcher
    println("Loading on thread: ${Thread.currentThread().name}")
    delay(1000)
    "Data loaded"
}

fun basicWithContextExample() = runBlocking {
    println("Main thread: ${Thread.currentThread().name}")

    val data = loadData() // Suspends and switches to IO dispatcher

    println("Back on thread: ${Thread.currentThread().name}")
    println("Data: $data")
}
```

#### withContext vs launch

```kotlin
import kotlinx.coroutines.*

fun compareWithLaunch() = runBlocking {
    println("=== withContext vs launch ===")

    // withContext: suspends and returns result
    val result1 = withContext(Dispatchers.IO) {
        delay(1000)
        "Result from withContext"
    }
    println("Got result immediately: $result1")

    // launch: doesn't return result, doesn't suspend parent
    val job = launch(Dispatchers.IO) {
        delay(1000)
        println("Result from launch")
    }
    println("launch returned immediately, still waiting...")
    job.join() // Need to explicitly wait

    // withContext is better for sequential operations
    val data1 = withContext(Dispatchers.IO) { loadFromDatabase() }
    val data2 = withContext(Dispatchers.Default) { processData(data1) }
    val data3 = withContext(Dispatchers.IO) { saveToDatabase(data2) }

    // launch is better for fire-and-forget
    launch { updateUI() }
    launch { logAnalytics() }
    launch { syncToServer() }
}

suspend fun loadFromDatabase(): String {
    delay(500)
    return "database data"
}

suspend fun processData(data: String): String {
    delay(500)
    return data.uppercase()
}

suspend fun saveToDatabase(data: String): Unit {
    delay(500)
}

suspend fun updateUI() = delay(100)
suspend fun logAnalytics() = delay(100)
suspend fun syncToServer() = delay(100)
```

#### withContext vs async

```kotlin
import kotlinx.coroutines.*

fun compareWithAsync() = runBlocking {
    println("=== withContext vs async ===")

    // withContext: sequential execution
    val time1 = measureTimeMillis {
        val result1 = withContext(Dispatchers.IO) {
            delay(1000)
            "First"
        }
        val result2 = withContext(Dispatchers.IO) {
            delay(1000)
            "Second"
        }
        println("Results: $result1, $result2")
    }
    println("withContext took: $time1 ms") // ~2000ms

    // async: parallel execution
    val time2 = measureTimeMillis {
        val deferred1 = async(Dispatchers.IO) {
            delay(1000)
            "First"
        }
        val deferred2 = async(Dispatchers.IO) {
            delay(1000)
            "Second"
        }
        println("Results: ${deferred1.await()}, ${deferred2.await()}")
    }
    println("async took: $time2 ms") // ~1000ms

    // Use withContext when you need sequential operations
    // Use async when you can parallelize
}
```

#### Dispatcher Switching Use Cases

```kotlin
import kotlinx.coroutines.*

class UserRepository {
    // Use case 1: I/O operations (network, database)
    suspend fun fetchUser(id: String): User = withContext(Dispatchers.IO) {
        // Network call or database query
        delay(1000) // Simulate I/O
        User(id, "John Doe")
    }

    // Use case 2: CPU-intensive operations
    suspend fun processUserData(users: List<User>): List<ProcessedUser> =
        withContext(Dispatchers.Default) {
            users.map { user ->
                // Complex computations
                ProcessedUser(user.id, user.name.uppercase())
            }
        }

    // Use case 3: UI updates (Android/Desktop)
    suspend fun updateUserUI(user: User) = withContext(Dispatchers.Main) {
        // Update UI components
        println("Updating UI with user: ${user.name}")
    }

    // Use case 4: Combining multiple dispatchers
    suspend fun loadAndDisplayUser(id: String) {
        // Start on Main (if called from UI)
        val user = withContext(Dispatchers.IO) {
            // Switch to IO for network
            fetchUserFromNetwork(id)
        }

        val processed = withContext(Dispatchers.Default) {
            // Switch to Default for processing
            processUserData(listOf(user))
        }

        withContext(Dispatchers.Main) {
            // Back to Main for UI update
            displayUser(processed.first())
        }
    }

    private suspend fun fetchUserFromNetwork(id: String): User {
        delay(500)
        return User(id, "Network User")
    }

    private fun displayUser(user: ProcessedUser) {
        println("Displaying: ${user.name}")
    }
}

data class User(val id: String, val name: String)
data class ProcessedUser(val id: String, val name: String)
```

#### Performance Considerations

```kotlin
import kotlinx.coroutines.*
import kotlin.system.measureTimeMillis

fun performanceComparisons() = runBlocking {
    println("=== Performance Considerations ===")

    // 1. withContext reuses parent's Job
    // No Job allocation overhead
    val time1 = measureTimeMillis {
        repeat(10000) {
            withContext(Dispatchers.Default) {
                // Minimal overhead
            }
        }
    }
    println("withContext overhead: $time1 ms")

    // 2. async + await has Job allocation overhead
    val time2 = measureTimeMillis {
        repeat(10000) {
            async(Dispatchers.Default) {
                // Creates Deferred job
            }.await()
        }
    }
    println("async + await overhead: $time2 ms")

    // 3. Unnecessary dispatcher switches
    val time3 = measureTimeMillis {
        repeat(1000) {
            withContext(Dispatchers.Default) {
                withContext(Dispatchers.Default) {
                    // Unnecessary switch!
                    val result = 1 + 1
                }
            }
        }
    }
    println("Nested withContext: $time3 ms")

    // 4. Proper usage - switch only when needed
    val time4 = measureTimeMillis {
        repeat(1000) {
            withContext(Dispatchers.Default) {
                val result = 1 + 1
                // Stay on same dispatcher
                val result2 = 2 + 2
            }
        }
    }
    println("Single withContext: $time4 ms")
}
```

#### Practical Patterns

```kotlin
import kotlinx.coroutines.*

// Pattern 1: Repository pattern with dispatcher switching
class ArticleRepository {
    private val apiService = ApiService()
    private val database = Database()

    suspend fun getArticle(id: String): Article {
        // Try cache first
        val cached = withContext(Dispatchers.IO) {
            database.getArticle(id)
        }

        if (cached != null) return cached

        // Fetch from network
        val article = withContext(Dispatchers.IO) {
            apiService.fetchArticle(id)
        }

        // Save to cache
        withContext(Dispatchers.IO) {
            database.saveArticle(article)
        }

        return article
    }
}

// Pattern 2: Processing pipeline
suspend fun processingPipeline(input: String): String {
    val downloaded = withContext(Dispatchers.IO) {
        downloadData(input)
    }

    val processed = withContext(Dispatchers.Default) {
        processData(downloaded)
    }

    val validated = withContext(Dispatchers.Default) {
        validateData(processed)
    }

    withContext(Dispatchers.IO) {
        saveData(validated)
    }

    return validated
}

// Pattern 3: Safe dispatcher switching
suspend fun <T> runOnIO(block: suspend () -> T): T {
    return withContext(Dispatchers.IO) {
        block()
    }
}

suspend fun <T> runOnComputation(block: suspend () -> T): T {
    return withContext(Dispatchers.Default) {
        block()
    }
}

// Usage
suspend fun loadUser(id: String): User = runOnIO {
    // Automatically runs on IO dispatcher
    fetchUserFromDatabase(id)
}

// Pattern 4: Cancellable operations
suspend fun cancellableOperation() = withContext(Dispatchers.IO) {
    repeat(10) { index ->
        ensureActive() // Check for cancellation
        println("Processing item $index")
        delay(500)
    }
}

// Pattern 5: Resource management
suspend fun <T> useResource(
    resource: Resource,
    block: suspend (Resource) -> T
): T = withContext(Dispatchers.IO) {
    try {
        resource.open()
        block(resource)
    } finally {
        resource.close()
    }
}

// Supporting classes
class ApiService {
    suspend fun fetchArticle(id: String): Article {
        delay(500)
        return Article(id, "Title", "Content")
    }
}

class Database {
    suspend fun getArticle(id: String): Article? {
        delay(100)
        return null
    }

    suspend fun saveArticle(article: Article) {
        delay(100)
    }
}

data class Article(val id: String, val title: String, val content: String)

suspend fun downloadData(input: String): String {
    delay(500)
    return "downloaded: $input"
}

suspend fun processData(data: String): String {
    delay(300)
    return "processed: $data"
}

suspend fun validateData(data: String): String {
    delay(200)
    return "validated: $data"
}

suspend fun saveData(data: String) {
    delay(300)
}

suspend fun fetchUserFromDatabase(id: String): User {
    delay(200)
    return User(id, "User $id")
}

interface Resource {
    fun open()
    fun close()
}
```

#### Common Mistakes

```kotlin
import kotlinx.coroutines.*

fun commonMistakes() = runBlocking {
    // Mistake 1: Using withContext for parallel operations
    // Bad - sequential
    val time1 = measureTimeMillis {
        val result1 = withContext(Dispatchers.IO) { delay(1000); "A" }
        val result2 = withContext(Dispatchers.IO) { delay(1000); "B" }
    }
    println("Sequential: $time1 ms") // 2000ms

    // Good - parallel with async
    val time2 = measureTimeMillis {
        val deferred1 = async(Dispatchers.IO) { delay(1000); "A" }
        val deferred2 = async(Dispatchers.IO) { delay(1000); "B" }
        val results = awaitAll(deferred1, deferred2)
    }
    println("Parallel: $time2 ms") // 1000ms

    // Mistake 2: Unnecessary dispatcher switches
    // Bad
    suspend fun badExample() = withContext(Dispatchers.Default) {
        withContext(Dispatchers.Default) { // Redundant!
            compute()
        }
    }

    // Good
    suspend fun goodExample() = withContext(Dispatchers.Default) {
        compute()
    }

    // Mistake 3: Blocking inside withContext(Dispatchers.IO)
    // Bad - blocks IO thread
    suspend fun badIO() = withContext(Dispatchers.IO) {
        Thread.sleep(1000) // Blocking call!
    }

    // Good - uses suspending function
    suspend fun goodIO() = withContext(Dispatchers.IO) {
        delay(1000) // Suspending call
    }

    // Mistake 4: Using withContext in ViewModel for fire-and-forget
    // Bad
    fun badViewModel() {
        viewModelScope.launch {
            withContext(Dispatchers.IO) {
                // This still suspends the parent
                logEvent()
            }
        }
    }

    // Good
    fun goodViewModel() {
        viewModelScope.launch(Dispatchers.IO) {
            // Directly launch on IO dispatcher
            logEvent()
        }
    }
}

fun compute(): Int = 42
suspend fun logEvent() = delay(100)

// Mock viewModelScope
val viewModelScope = CoroutineScope(Dispatchers.Main)
```

#### Advanced withContext Patterns

```kotlin
import kotlinx.coroutines.*

// Pattern 1: Timeout with withContext
suspend fun <T> withContextAndTimeout(
    context: CoroutineContext,
    timeoutMillis: Long,
    block: suspend () -> T
): T = withTimeout(timeoutMillis) {
    withContext(context) {
        block()
    }
}

// Pattern 2: Retry with dispatcher switching
suspend fun <T> retryOnIO(
    times: Int = 3,
    block: suspend () -> T
): T {
    repeat(times - 1) { attempt ->
        try {
            return withContext(Dispatchers.IO) {
                block()
            }
        } catch (e: Exception) {
            println("Attempt ${attempt + 1} failed: ${e.message}")
            delay(1000L * (attempt + 1))
        }
    }
    // Last attempt
    return withContext(Dispatchers.IO) {
        block()
    }
}

// Pattern 3: withContext with custom context elements
suspend fun withLogging(block: suspend () -> Unit) {
    val requestId = java.util.UUID.randomUUID().toString()
    withContext(CoroutineName("Request-$requestId")) {
        println("[${coroutineContext[CoroutineName]}] Starting operation")
        block()
        println("[${coroutineContext[CoroutineName]}] Completed operation")
    }
}

// Pattern 4: Combining multiple context elements
suspend fun withCustomContext(
    dispatcher: CoroutineDispatcher,
    name: String,
    block: suspend () -> Unit
) {
    withContext(dispatcher + CoroutineName(name)) {
        println("Running on ${Thread.currentThread().name} as $name")
        block()
    }
}

// Pattern 5: Conditional dispatcher switching
suspend fun <T> withOptimalDispatcher(
    data: List<T>,
    threshold: Int = 100,
    block: suspend (List<T>) -> Unit
) {
    val dispatcher = if (data.size > threshold) {
        Dispatchers.Default // CPU-intensive for large data
    } else {
        Dispatchers.IO // IO for small data
    }

    withContext(dispatcher) {
        block(data)
    }
}

fun demonstrateAdvancedPatterns() = runBlocking {
    // Using timeout with context
    try {
        withContextAndTimeout(Dispatchers.IO, 2000) {
            delay(3000)
            "Result"
        }
    } catch (e: TimeoutCancellationException) {
        println("Operation timed out")
    }

    // Using retry
    val result = retryOnIO {
        if (Math.random() > 0.7) "Success" else throw Exception("Failed")
    }
    println("Retry result: $result")

    // Using logging
    withLogging {
        delay(1000)
        println("Doing work")
    }

    // Using custom context
    withCustomContext(Dispatchers.Default, "DataProcessor") {
        delay(500)
        println("Processing data")
    }

    // Using conditional dispatcher
    withOptimalDispatcher(List(150) { it }) { data ->
        println("Processing ${data.size} items")
    }
}
```

#### Testing withContext

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.assertEquals

class WithContextTest {
    @Test
    fun testWithContextSwitchesDispatcher() = runTest {
        val threadName = withContext(Dispatchers.Default) {
            Thread.currentThread().name
        }

        assert(threadName.contains("DefaultDispatcher"))
    }

    @Test
    fun testWithContextReturnsValue() = runTest {
        val result = withContext(Dispatchers.Default) {
            delay(100)
            42
        }

        assertEquals(42, result)
    }

    @Test
    fun testWithContextCancellation() = runTest {
        val job = launch {
            try {
                withContext(Dispatchers.Default) {
                    delay(10000)
                }
            } catch (e: CancellationException) {
                println("Cancelled as expected")
            }
        }

        advanceTimeBy(100)
        job.cancel()
        job.join()
    }

    @Test
    fun testSequentialWithContext() = runTest {
        val results = mutableListOf<String>()

        withContext(Dispatchers.Default) {
            results.add("First")
        }

        withContext(Dispatchers.IO) {
            results.add("Second")
        }

        assertEquals(listOf("First", "Second"), results)
    }
}
```

### Best Practices

1. **Use withContext for sequential operations that need dispatcher switching**
   ```kotlin
   suspend fun loadUser(id: String) = withContext(Dispatchers.IO) {
       database.getUser(id)
   }
   ```

2. **Use async for parallel operations**
   ```kotlin
   suspend fun loadMultipleUsers(ids: List<String>) = coroutineScope {
       ids.map { id ->
           async(Dispatchers.IO) { database.getUser(id) }
       }.awaitAll()
   }
   ```

3. **Avoid unnecessary dispatcher switches**
   ```kotlin
   // Bad - multiple switches
   withContext(Dispatchers.IO) {
       val a = withContext(Dispatchers.Default) { compute() }
       val b = withContext(Dispatchers.Default) { compute() }
   }

   // Good - single switch
   withContext(Dispatchers.Default) {
       val a = compute()
       val b = compute()
   }
   ```

4. **Use withContext over async + await for single operations**
   ```kotlin
   // Less efficient
   val result = async(Dispatchers.IO) { loadData() }.await()

   // More efficient
   val result = withContext(Dispatchers.IO) { loadData() }
   ```

5. **Don't mix blocking and suspending calls**
   ```kotlin
   // Bad
   withContext(Dispatchers.IO) {
       Thread.sleep(1000) // Blocking!
   }

   // Good
   withContext(Dispatchers.IO) {
       delay(1000) // Suspending
   }
   ```

### Common Pitfalls

1. **Using withContext for fire-and-forget operations**
2. **Unnecessary nesting of withContext calls**
3. **Blocking the dispatcher thread**
4. **Not understanding that withContext suspends the caller**

---

## Русский

### Описание проблемы

Функция `withContext` является одним из наиболее часто используемых строителей корутин, но понимание того, когда и почему использовать её вместо альтернатив, таких как `launch` или `async`, может быть запутанным. Каковы конкретные случаи использования `withContext`, и как она сравнивается с другими строителями корутин с точки зрения производительности и поведения?

### Решение

`withContext` - это **приостанавливающая функция**, которая переключает контекст корутины, выполняет блок кода и возвращает результат. Она в основном используется для переключения диспетчеров для выполнения определённых операций на соответствующих потоках.

#### Базовое использование withContext

```kotlin
import kotlinx.coroutines.*

suspend fun loadData(): String = withContext(Dispatchers.IO) {
    // Выполнение I/O операции на IO диспетчере
    println("Загрузка на потоке: ${Thread.currentThread().name}")
    delay(1000)
    "Данные загружены"
}

fun basicWithContextExample() = runBlocking {
    println("Главный поток: ${Thread.currentThread().name}")

    val data = loadData() // Приостанавливается и переключается на IO диспетчер

    println("Обратно на потоке: ${Thread.currentThread().name}")
    println("Данные: $data")
}
```

#### withContext vs launch

```kotlin
import kotlinx.coroutines.*

fun compareWithLaunch() = runBlocking {
    println("=== withContext vs launch ===")

    // withContext: приостанавливается и возвращает результат
    val result1 = withContext(Dispatchers.IO) {
        delay(1000)
        "Результат из withContext"
    }
    println("Результат получен немедленно: $result1")

    // launch: не возвращает результат, не приостанавливает родителя
    val job = launch(Dispatchers.IO) {
        delay(1000)
        println("Результат из launch")
    }
    println("launch вернулся немедленно, всё ещё ожидание...")
    job.join() // Нужно явно ждать

    // withContext лучше для последовательных операций
    val data1 = withContext(Dispatchers.IO) { loadFromDatabase() }
    val data2 = withContext(Dispatchers.Default) { processData(data1) }
    val data3 = withContext(Dispatchers.IO) { saveToDatabase(data2) }

    // launch лучше для fire-and-forget операций
    launch { updateUI() }
    launch { logAnalytics() }
    launch { syncToServer() }
}
```

#### withContext vs async

```kotlin
import kotlinx.coroutines.*

fun compareWithAsync() = runBlocking {
    println("=== withContext vs async ===")

    // withContext: последовательное выполнение
    val time1 = measureTimeMillis {
        val result1 = withContext(Dispatchers.IO) {
            delay(1000)
            "First"
        }
        val result2 = withContext(Dispatchers.IO) {
            delay(1000)
            "Second"
        }
        println("Результаты: $result1, $result2")
    }
    println("withContext заняло: $time1 мс") // ~2000мс

    // async: параллельное выполнение
    val time2 = measureTimeMillis {
        val deferred1 = async(Dispatchers.IO) {
            delay(1000)
            "First"
        }
        val deferred2 = async(Dispatchers.IO) {
            delay(1000)
            "Second"
        }
        println("Результаты: ${deferred1.await()}, ${deferred2.await()}")
    }
    println("async заняло: $time2 мс") // ~1000мс

    // Используйте withContext для последовательных операций
    // Используйте async для параллельных операций
}
```

#### Случаи использования переключения диспетчера

```kotlin
import kotlinx.coroutines.*

class UserRepository {
    // Случай 1: I/O операции (сеть, база данных)
    suspend fun fetchUser(id: String): User = withContext(Dispatchers.IO) {
        // Сетевой вызов или запрос к базе данных
        delay(1000) // Имитация I/O
        User(id, "Иван Иванов")
    }

    // Случай 2: CPU-интенсивные операции
    suspend fun processUserData(users: List<User>): List<ProcessedUser> =
        withContext(Dispatchers.Default) {
            users.map { user ->
                // Сложные вычисления
                ProcessedUser(user.id, user.name.uppercase())
            }
        }

    // Случай 3: Обновления UI (Android/Desktop)
    suspend fun updateUserUI(user: User) = withContext(Dispatchers.Main) {
        // Обновление UI компонентов
        println("Обновление UI пользователя: ${user.name}")
    }

    // Случай 4: Комбинирование нескольких диспетчеров
    suspend fun loadAndDisplayUser(id: String) {
        // Начало на Main (если вызвано из UI)
        val user = withContext(Dispatchers.IO) {
            // Переключение на IO для сети
            fetchUserFromNetwork(id)
        }

        val processed = withContext(Dispatchers.Default) {
            // Переключение на Default для обработки
            processUserData(listOf(user))
        }

        withContext(Dispatchers.Main) {
            // Обратно на Main для обновления UI
            displayUser(processed.first())
        }
    }
}
```

#### Соображения производительности

```kotlin
import kotlinx.coroutines.*
import kotlin.system.measureTimeMillis

fun performanceComparisons() = runBlocking {
    println("=== Соображения производительности ===")

    // 1. withContext переиспользует Job родителя
    // Нет накладных расходов на выделение Job
    val time1 = measureTimeMillis {
        repeat(10000) {
            withContext(Dispatchers.Default) {
                // Минимальные накладные расходы
            }
        }
    }
    println("withContext накладные расходы: $time1 мс")

    // 2. async + await имеет накладные расходы на выделение Job
    val time2 = measureTimeMillis {
        repeat(10000) {
            async(Dispatchers.Default) {
                // Создаёт Deferred job
            }.await()
        }
    }
    println("async + await накладные расходы: $time2 мс")

    // 3. Ненужные переключения диспетчера
    val time3 = measureTimeMillis {
        repeat(1000) {
            withContext(Dispatchers.Default) {
                withContext(Dispatchers.Default) {
                    // Ненужное переключение!
                    val result = 1 + 1
                }
            }
        }
    }
    println("Вложенный withContext: $time3 мс")

    // 4. Правильное использование - переключать только при необходимости
    val time4 = measureTimeMillis {
        repeat(1000) {
            withContext(Dispatchers.Default) {
                val result = 1 + 1
                // Остаться на том же диспетчере
                val result2 = 2 + 2
            }
        }
    }
    println("Одиночный withContext: $time4 мс")
}
```

#### Практические паттерны

```kotlin
import kotlinx.coroutines.*

// Паттерн 1: Паттерн репозитория с переключением диспетчера
class ArticleRepository {
    private val apiService = ApiService()
    private val database = Database()

    suspend fun getArticle(id: String): Article {
        // Сначала попробовать кеш
        val cached = withContext(Dispatchers.IO) {
            database.getArticle(id)
        }

        if (cached != null) return cached

        // Получить из сети
        val article = withContext(Dispatchers.IO) {
            apiService.fetchArticle(id)
        }

        // Сохранить в кеш
        withContext(Dispatchers.IO) {
            database.saveArticle(article)
        }

        return article
    }
}

// Паттерн 2: Конвейер обработки
suspend fun processingPipeline(input: String): String {
    val downloaded = withContext(Dispatchers.IO) {
        downloadData(input)
    }

    val processed = withContext(Dispatchers.Default) {
        processData(downloaded)
    }

    val validated = withContext(Dispatchers.Default) {
        validateData(processed)
    }

    withContext(Dispatchers.IO) {
        saveData(validated)
    }

    return validated
}

// Паттерн 3: Безопасное переключение диспетчера
suspend fun <T> runOnIO(block: suspend () -> T): T {
    return withContext(Dispatchers.IO) {
        block()
    }
}

suspend fun <T> runOnComputation(block: suspend () -> T): T {
    return withContext(Dispatchers.Default) {
        block()
    }
}

// Использование
suspend fun loadUser(id: String): User = runOnIO {
    // Автоматически выполняется на IO диспетчере
    fetchUserFromDatabase(id)
}

// Паттерн 4: Отменяемые операции
suspend fun cancellableOperation() = withContext(Dispatchers.IO) {
    repeat(10) { index ->
        ensureActive() // Проверка на отмену
        println("Обработка элемента $index")
        delay(500)
    }
}

// Паттерн 5: Управление ресурсами
suspend fun <T> useResource(
    resource: Resource,
    block: suspend (Resource) -> T
): T = withContext(Dispatchers.IO) {
    try {
        resource.open()
        block(resource)
    } finally {
        resource.close()
    }
}
```

#### Распространённые ошибки

```kotlin
import kotlinx.coroutines.*

fun commonMistakes() = runBlocking {
    // Ошибка 1: Использование withContext для параллельных операций
    // Плохо - последовательное
    val time1 = measureTimeMillis {
        val result1 = withContext(Dispatchers.IO) { delay(1000); "A" }
        val result2 = withContext(Dispatchers.IO) { delay(1000); "B" }
    }
    println("Последовательное: $time1 мс") // 2000мс

    // Хорошо - параллельное с async
    val time2 = measureTimeMillis {
        val deferred1 = async(Dispatchers.IO) { delay(1000); "A" }
        val deferred2 = async(Dispatchers.IO) { delay(1000); "B" }
        val results = awaitAll(deferred1, deferred2)
    }
    println("Параллельное: $time2 мс") // 1000мс

    // Ошибка 2: Ненужные переключения диспетчера
    // Плохо
    suspend fun badExample() = withContext(Dispatchers.Default) {
        withContext(Dispatchers.Default) { // Избыточно!
            compute()
        }
    }

    // Хорошо
    suspend fun goodExample() = withContext(Dispatchers.Default) {
        compute()
    }

    // Ошибка 3: Блокирование внутри withContext(Dispatchers.IO)
    // Плохо - блокирует IO поток
    suspend fun badIO() = withContext(Dispatchers.IO) {
        Thread.sleep(1000) // Блокирующий вызов!
    }

    // Хорошо - использует приостанавливающую функцию
    suspend fun goodIO() = withContext(Dispatchers.IO) {
        delay(1000) // Приостанавливающий вызов
    }

    // Ошибка 4: Использование withContext в ViewModel для fire-and-forget
    // Плохо
    fun badViewModel() {
        viewModelScope.launch {
            withContext(Dispatchers.IO) {
                // Это всё ещё приостанавливает родителя
                logEvent()
            }
        }
    }

    // Хорошо
    fun goodViewModel() {
        viewModelScope.launch(Dispatchers.IO) {
            // Напрямую запускаем на IO диспетчере
            logEvent()
        }
    }
}
```

#### Продвинутые паттерны withContext

```kotlin
import kotlinx.coroutines.*

// Паттерн 1: Таймаут с withContext
suspend fun <T> withContextAndTimeout(
    context: CoroutineContext,
    timeoutMillis: Long,
    block: suspend () -> T
): T = withTimeout(timeoutMillis) {
    withContext(context) {
        block()
    }
}

// Паттерн 2: Повторные попытки с переключением диспетчера
suspend fun <T> retryOnIO(
    times: Int = 3,
    block: suspend () -> T
): T {
    repeat(times - 1) { attempt ->
        try {
            return withContext(Dispatchers.IO) {
                block()
            }
        } catch (e: Exception) {
            println("Попытка ${attempt + 1} не удалась: ${e.message}")
            delay(1000L * (attempt + 1))
        }
    }
    // Последняя попытка
    return withContext(Dispatchers.IO) {
        block()
    }
}

// Паттерн 3: withContext с пользовательскими элементами контекста
suspend fun withLogging(block: suspend () -> Unit) {
    val requestId = java.util.UUID.randomUUID().toString()
    withContext(CoroutineName("Request-$requestId")) {
        println("[${coroutineContext[CoroutineName]}] Начало операции")
        block()
        println("[${coroutineContext[CoroutineName]}] Операция завершена")
    }
}

// Паттерн 4: Комбинирование нескольких элементов контекста
suspend fun withCustomContext(
    dispatcher: CoroutineDispatcher,
    name: String,
    block: suspend () -> Unit
) {
    withContext(dispatcher + CoroutineName(name)) {
        println("Выполняется на ${Thread.currentThread().name} как $name")
        block()
    }
}

// Паттерн 5: Условное переключение диспетчера
suspend fun <T> withOptimalDispatcher(
    data: List<T>,
    threshold: Int = 100,
    block: suspend (List<T>) -> Unit
) {
    val dispatcher = if (data.size > threshold) {
        Dispatchers.Default // CPU-интенсивно для больших данных
    } else {
        Dispatchers.IO // IO для малых данных
    }

    withContext(dispatcher) {
        block(data)
    }
}
```

### Лучшие практики

1. **Используйте withContext для последовательных операций, требующих переключения диспетчера**
   ```kotlin
   suspend fun loadUser(id: String) = withContext(Dispatchers.IO) {
       database.getUser(id)
   }
   ```

2. **Используйте async для параллельных операций**
   ```kotlin
   suspend fun loadMultipleUsers(ids: List<String>) = coroutineScope {
       ids.map { id ->
           async(Dispatchers.IO) { database.getUser(id) }
       }.awaitAll()
   }
   ```

3. **Избегайте ненужных переключений диспетчера**
   ```kotlin
   // Плохо - множественные переключения
   withContext(Dispatchers.IO) {
       val a = withContext(Dispatchers.Default) { compute() }
       val b = withContext(Dispatchers.Default) { compute() }
   }

   // Хорошо - одно переключение
   withContext(Dispatchers.Default) {
       val a = compute()
       val b = compute()
   }
   ```

4. **Используйте withContext вместо async + await для одиночных операций**
   ```kotlin
   // Менее эффективно
   val result = async(Dispatchers.IO) { loadData() }.await()

   // Более эффективно
   val result = withContext(Dispatchers.IO) { loadData() }
   ```

5. **Не смешивайте блокирующие и приостанавливающие вызовы**
   ```kotlin
   // Плохо
   withContext(Dispatchers.IO) {
       Thread.sleep(1000) // Блокирование!
   }

   // Хорошо
   withContext(Dispatchers.IO) {
       delay(1000) // Приостановка
   }
   ```

### Распространённые ошибки

1. **Использование withContext для операций "запустил и забыл"** - используйте launch вместо этого
2. **Ненужная вложенность вызовов withContext** - объедините переключения диспетчера
3. **Блокировка потока диспетчера** - используйте приостанавливающие функции вместо блокирующих
4. **Непонимание того, что withContext приостанавливает вызывающую сторону** - для параллелизма используйте async

---

## Follow-ups

1. What's the performance difference between withContext and async + await?
2. Can you use withContext to switch from Dispatchers.Main to Dispatchers.IO in a nested manner?
3. How does withContext handle exceptions compared to launch and async?
4. What happens if you call withContext with the same dispatcher you're already on?
5. Can withContext be cancelled, and how does cancellation propagate?
6. How does NonCancellable context affect withContext behavior?
7. What's the difference between withContext(Dispatchers.IO) and runBlocking?
8. How can you measure the overhead of dispatcher switching with withContext?

## References

- [Kotlin Coroutines Guide - Coroutine Context and Dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
- [withContext - kotlinx.coroutines API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-context.html)
- [Roman Elizarov - Blocking threads, suspending coroutines](https://medium.com/@elizarov/blocking-threads-suspending-coroutines-d33e11bf4761)
- [Android Developers - Best practices for coroutines](https://developer.android.com/kotlin/coroutines/coroutines-best-practices)

## Related Questions

- [[q-coroutine-builders-comparison--kotlin--medium]]
- [[q-coroutine-dispatchers--kotlin--medium]]
- [[q-dispatchers-unconfined--kotlin--medium]]
- [[q-structured-concurrency--kotlin--hard]]
- [[q-coroutine-performance--kotlin--hard]]
- [[q-async-await--kotlin--medium]]
