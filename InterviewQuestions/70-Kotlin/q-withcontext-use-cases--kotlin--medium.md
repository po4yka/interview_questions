---
id: kotlin-099
title: "When to use withContext in Kotlin coroutines? / Когда использовать withContext"
aliases: [context switching, dispatchers, withcontext, withcontext use cases]
topic: kotlin
subtopics: [coroutines, dispatchers]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, q-launch-vs-async-vs-runblocking--kotlin--medium]
created: 2025-10-12
updated: 2025-11-09
tags: [context-switching, coroutines, difficulty/medium, dispatchers, kotlin, withcontext]
---
# Вопрос (RU)

> Когда и в каких случаях следует использовать `withContext` в корутинах Kotlin по сравнению с такими построителями, как `launch` и `async`?

# Question (EN)

> When and in which scenarios should you use `withContext` in Kotlin coroutines compared to builders like `launch` and `async`?

## Ответ (RU)

Функция `withContext` — это приостанавливающий API для смены контекста корутины. Она (при необходимости) меняет контекст, выполняет блок кода и возвращает результат, оставаясь в рамках той же иерархии структурированной конкуренции (не создаёт отдельный независимый `Job`, как `launch`). Основное применение — переключение диспетчеров и выполнение операций на подходящих потоках без нарушения структурированной конкуренции.

См. также: [[c-coroutines]].

#### Базовое Использование withContext

```kotlin
import kotlinx.coroutines.*

suspend fun loadData(): String = withContext(Dispatchers.IO) {
    // Выполнение I/O операции на IO-диспетчере
    println("Загрузка на потоке: ${Thread.currentThread().name}")
    delay(1000)
    "Данные загружены"
}

fun basicWithContextExample() = runBlocking {
    println("Главный поток: ${Thread.currentThread().name}")

    val data = loadData() // Приостанавливается и (если нужно) переключается на IO-диспетчер

    println("Снова на потоке: ${Thread.currentThread().name}")
    println("Данные: $data")
}
```

#### withContext Vs Launch

```kotlin
import kotlinx.coroutines.*

fun compareWithLaunch() = runBlocking {
    println("=== withContext vs launch ===")

    // withContext: приостанавливает вызывающую корутину и возвращает результат в рамках того же Job
    val result1 = withContext(Dispatchers.IO) {
        delay(1000)
        "Результат из withContext"
    }
    println("Результат получен после возобновления: $result1")

    // launch: возвращает Job и не даёт результата напрямую
    val job = launch(Dispatchers.IO) {
        delay(1000)
        println("Результат из launch")
    }
    println("launch вернулся немедленно, всё ещё ждём...")
    job.join() // Нужно явно ждать

    // withContext подходит для последовательных операций,
    // которые должны завершиться до продолжения и/или требуют переключения диспетчера
    val data1 = withContext(Dispatchers.IO) { loadFromDatabase() }
    val data2 = withContext(Dispatchers.Default) { processData(data1) }
    withContext(Dispatchers.IO) { saveToDatabase(data2) }

    // launch подходит для fire-and-forget или конкурентной работы
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

suspend fun saveToDatabase(data: String) {
    delay(500)
}

suspend fun updateUI() = delay(100)
suspend fun logAnalytics() = delay(100)
suspend fun syncToServer() = delay(100)
```

#### withContext Vs Async

```kotlin
import kotlinx.coroutines.*
import kotlin.system.measureTimeMillis

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
    println("withContext заняло: $time1 мс") // порядка 2000 мс при последовательном выполнении

    // async: потенциально конкурентное выполнение в рамках одной области видимости
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
    // Фактическое время зависит от числа потоков в пуле;
    // при достаточных ресурсах может быть ~1000 мс
    println("async заняло: $time2 мс")

    // Используйте withContext, когда нужна одиночная приостанавливающая операция,
    // которая должна завершиться перед продолжением (последовательный поток, смена контекста).
    // Используйте async, когда есть несколько независимых операций, которые могут выполняться конкурентно.
}
```

#### Случаи Использования Переключения Диспетчера

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
        // Обновление UI-компонентов (на платформах с Main-потоком)
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

    private suspend fun fetchUserFromNetwork(id: String): User {
        delay(500)
        return User(id, "Пользователь из сети")
    }

    private fun displayUser(user: ProcessedUser) {
        println("Отображение: ${user.name}")
    }
}

data class User(val id: String, val name: String)
data class ProcessedUser(val id: String, val name: String)
```

#### Соображения Производительности

```kotlin
import kotlinx.coroutines.*
import kotlin.system.measureTimeMillis

fun performanceComparisons() = runBlocking {
    println("=== Соображения производительности ===")

    // 1. withContext использует контекст и Job родителя (как дочерняя coroutine),
    // не создавая отдельный Deferred-объект.
    val time1 = measureTimeMillis {
        repeat(10000) {
            withContext(Dispatchers.Default) {
                // Минимальные накладные расходы
            }
        }
    }
    println("withContext накладные расходы: $time1 мс")

    // 2. async + await создаёт дополнительный Job (Deferred) для каждой операции
    val time2 = measureTimeMillis {
        repeat(10000) {
            async(Dispatchers.Default) {
                // Создаёт Deferred Job
            }.await()
        }
    }
    println("async + await накладные расходы: $time2 мс")

    // 3. Ненужные переключения диспетчера
    val time3 = measureTimeMillis {
        repeat(1000) {
            withContext(Dispatchers.Default) {
                withContext(Dispatchers.Default) {
                    // При одинаковом контексте дополнительного переключения не происходит,
                    // но сам вызов withContext добавляет накладные расходы
                    val result = 1 + 1
                }
            }
        }
    }
    println("Вложенный withContext: $time3 мс")

    // 4. Правильное использование — переключать только при необходимости
    val time4 = measureTimeMillis {
        repeat(1000) {
            withContext(Dispatchers.Default) {
                val result = 1 + 1
                val result2 = 2 + 2
            }
        }
    }
    println("Одиночный withContext: $time4 мс")
}
```

#### Практические Паттерны

```kotlin
import kotlinx.coroutines.*

// Паттерн 1: Репозиторий с переключением диспетчеров
class ArticleRepository {
    private val apiService = ApiService()
    private val database = Database()

    suspend fun getArticle(id: String): Article {
        // Сначала пробуем кеш
        val cached = withContext(Dispatchers.IO) {
            database.getArticle(id)
        }

        if (cached != null) return cached

        // Получаем из сети
        val article = withContext(Dispatchers.IO) {
            apiService.fetchArticle(id)
        }

        // Сохраняем в кеш
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
suspend fun <T> runOnIO(block: suspend () -> T): T =
    withContext(Dispatchers.IO) { block() }

suspend fun <T> runOnComputation(block: suspend () -> T): T =
    withContext(Dispatchers.Default) { block() }

// Использование
suspend fun loadUserOnIO(id: String): User = runOnIO {
    // Автоматически выполняется на IO-диспетчере
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

// Вспомогательные классы
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

data class User(val id: String, val name: String)

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

#### Распространённые Ошибки

```kotlin
import kotlinx.coroutines.*
import kotlin.system.measureTimeMillis

fun commonMistakes() = runBlocking {
    // Ошибка 1: Использование withContext для параллельных операций
    // Плохо — последовательное выполнение
    val time1 = measureTimeMillis {
        val result1 = withContext(Dispatchers.IO) { delay(1000); "A" }
        val result2 = withContext(Dispatchers.IO) { delay(1000); "B" }
    }
    println("Последовательное: $time1 мс") // порядка 2000 мс

    // Хорошо — конкурентно с async (фактический параллелизм зависит от пула потоков)
    val time2 = measureTimeMillis {
        val deferred1 = async(Dispatchers.IO) { delay(1000); "A" }
        val deferred2 = async(Dispatchers.IO) { delay(1000); "B" }
        val results = awaitAll(deferred1, deferred2)
    }
    println("Конкурентное: $time2 мс")

    // Ошибка 2: Ненужные переключения диспетчера
    // Плохо
    suspend fun badExample() = withContext(Dispatchers.Default) {
        withContext(Dispatchers.Default) { // Избыточно при том же контексте
            compute()
        }
    }

    // Хорошо
    suspend fun goodExample() = withContext(Dispatchers.Default) {
        compute()
    }

    // Ошибка 3: Блокирование внутри withContext(Dispatchers.IO)
    // Плохо — блокирует поток пула IO
    suspend fun badIO() = withContext(Dispatchers.IO) {
        Thread.sleep(1000) // Блокирующий вызов!
    }

    // Хорошо — использовать приостанавливающие функции
    suspend fun goodIO() = withContext(Dispatchers.IO) {
        delay(1000) // Приостанавливающий вызов
    }

    // Ошибка 4: Использование withContext в ViewModel для fire-and-forget
    // Плохо: остаётся частью родительского Job; лишние переключения
    fun badViewModel() {
        viewModelScope.launch {
            withContext(Dispatchers.IO) {
                logEvent()
            }
        }
    }

    // Хорошо: сразу запускать на IO-диспетчере для этой работы (если не нужен результат)
    fun goodViewModel() {
        viewModelScope.launch(Dispatchers.IO) {
            logEvent()
        }
    }
}

fun compute(): Int = 42
suspend fun logEvent() = delay(100)

// Mock viewModelScope (в реальном Android-коде используйте настоящий viewModelScope
// и Main-диспетчер от Android или тестовый диспетчер)
val viewModelScope = CoroutineScope(Dispatchers.Default)
```

#### Продвинутые Паттерны withContext

```kotlin
import kotlinx.coroutines.*
import kotlin.coroutines.CoroutineContext

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
    require(times >= 1)
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
        Dispatchers.Default // например, большие коллекции с CPU-работой
    } else {
        Dispatchers.IO // пример: для небольших I/O-нагруженных задач
    }

    withContext(dispatcher) {
        block(data)
    }
}

fun demonstrateAdvancedPatterns() = runBlocking {
    // Использование таймаута с контекстом
    try {
        withContextAndTimeout(Dispatchers.IO, 2000) {
            delay(3000)
            "Result"
        }
    } catch (e: TimeoutCancellationException) {
        println("Операция завершилась по таймауту")
    }

    // Использование повторных попыток
    val result = retryOnIO {
        if (Math.random() > 0.7) "Success" else throw Exception("Failed")
    }
    println("Результат retry: $result")

    // Использование логирования
    withLogging {
        delay(1000)
        println("Выполнение работы")
    }

    // Использование пользовательского контекста
    withCustomContext(Dispatchers.Default, "DataProcessor") {
        delay(500)
        println("Обработка данных")
    }

    // Использование условного диспетчера
    withOptimalDispatcher(List(150) { it }) { data ->
        println("Обработка ${data.size} элементов")
    }
}
```

#### Тестирование withContext

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.assertEquals

class WithContextRuTest {
    @Test
    fun testWithContextSwitchesDispatcher() = runTest {
        val dispatcher = StandardTestDispatcher(testScheduler)
        val threadName = withContext(dispatcher) {
            Thread.currentThread().name
        }

        // Проверяем, что код выполнялся с переданным тестовым диспетчером.
        assert(threadName.contains("Test"))
    }

    @Test
    fun testWithContextReturnsValue() = runTest {
        val dispatcher = StandardTestDispatcher(testScheduler)
        val result = withContext(dispatcher) {
            delay(100)
            42
        }

        assertEquals(42, result)
    }

    @Test
    fun testWithContextCancellation() = runTest {
        val dispatcher = StandardTestDispatcher(testScheduler)
        val job = launch {
            try {
                withContext(dispatcher) {
                    delay(10000)
                }
            } catch (e: CancellationException) {
                println("Ожидаемая отмена")
            }
        }

        advanceTimeBy(100)
        job.cancel()
        job.join()
    }

    @Test
    fun testSequentialWithContext() = runTest {
        val dispatcher = StandardTestDispatcher(testScheduler)
        val results = mutableListOf<String>()

        withContext(dispatcher) {
            results.add("First")
        }

        withContext(dispatcher) {
            results.add("Second")
        }

        assertEquals(listOf("First", "Second"), results)
    }
}
```

## Answer (EN)

The `withContext` function is a suspending API used for changing the coroutine context. It (optionally) switches the context, executes a block of code, and returns a result while remaining in the same structured-concurrency hierarchy (it does not create an independent `Job` like `launch` does; it is part of the caller's job). Its primary use is to switch dispatchers to run work on appropriate threads without breaking structured concurrency.

See also: [[c-coroutines]].

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

    val data = loadData() // Suspends and (if needed) switches to IO dispatcher

    println("Back on thread: ${Thread.currentThread().name}")
    println("Data: $data")
}
```

#### withContext Vs Launch

```kotlin
import kotlinx.coroutines.*

fun compareWithLaunch() = runBlocking {
    println("=== withContext vs launch ===")

    // withContext: suspends caller and returns result within the same Job hierarchy
    val result1 = withContext(Dispatchers.IO) {
        delay(1000)
        "Result from withContext"
    }
    println("Got result after suspension: $result1")

    // launch: returns Job, does not produce a direct result
    val job = launch(Dispatchers.IO) {
        delay(1000)
        println("Result from launch")
    }
    println("launch returned immediately, still waiting...")
    job.join() // Need to explicitly wait

    // withContext is appropriate for sequential operations that must
    // complete before proceeding and/or require dispatcher switching
    val data1 = withContext(Dispatchers.IO) { loadFromDatabase() }
    val data2 = withContext(Dispatchers.Default) { processData(data1) }
    withContext(Dispatchers.IO) { saveToDatabase(data2) }

    // launch is appropriate for fire-and-forget or concurrent work
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

suspend fun saveToDatabase(data: String) {
    delay(500)
}

suspend fun updateUI() = delay(100)
suspend fun logAnalytics() = delay(100)
suspend fun syncToServer() = delay(100)
```

#### withContext Vs Async

```kotlin
import kotlinx.coroutines.*
import kotlin.system.measureTimeMillis

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
    println("withContext took: $time1 ms") // ~2000ms with sequential execution

    // async: potentially concurrent execution within the same scope
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
    // Actual timing depends on dispatcher threads; with enough threads may be ~1000ms
    println("async took: $time2 ms")

    // Use withContext when you need a single suspending operation that
    // must complete before moving on (sequential flow, context switch).
    // Use async when you have multiple independent operations that can run concurrently.
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
        // Update UI components (on Main-thread platforms)
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

    // 1. withContext reuses parent's context and Job (as a child),
    // without creating a separate Deferred instance.
    val time1 = measureTimeMillis {
        repeat(10000) {
            withContext(Dispatchers.Default) {
                // Minimal overhead
            }
        }
    }
    println("withContext overhead: $time1 ms")

    // 2. async + await allocates an additional Job (Deferred) per operation
    val time2 = measureTimeMillis {
        repeat(10000) {
            async(Dispatchers.Default) {
                // Creates Deferred Job
            }.await()
        }
    }
    println("async + await overhead: $time2 ms")

    // 3. Unnecessary dispatcher switches
    val time3 = measureTimeMillis {
        repeat(1000) {
            withContext(Dispatchers.Default) {
                withContext(Dispatchers.Default) {
                    // When context is identical, dispatcher won't switch threads,
                    // but extra withContext calls still add overhead
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

// Pattern 1: Repository with dispatcher switching
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
suspend fun <T> runOnIO(block: suspend () -> T): T =
    withContext(Dispatchers.IO) { block() }

suspend fun <T> runOnComputation(block: suspend () -> T): T =
    withContext(Dispatchers.Default) { block() }

// Usage
suspend fun loadUserOnIO(id: String): User = runOnIO {
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

data class User(val id: String, val name: String)

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
import kotlin.system.measureTimeMillis

fun commonMistakes() = runBlocking {
    // Mistake 1: Using withContext for parallel operations
    // Bad - sequential
    val time1 = measureTimeMillis {
        val result1 = withContext(Dispatchers.IO) { delay(1000); "A" }
        val result2 = withContext(Dispatchers.IO) { delay(1000); "B" }
    }
    println("Sequential: $time1 ms") // ~2000ms

    // Good - concurrent with async (actual parallelism depends on threads)
    val time2 = measureTimeMillis {
        val deferred1 = async(Dispatchers.IO) { delay(1000); "A" }
        val deferred2 = async(Dispatchers.IO) { delay(1000); "B" }
        val results = awaitAll(deferred1, deferred2)
    }
    println("Parallel (concurrent): $time2 ms")

    // Mistake 2: Unnecessary dispatcher switches
    // Bad
    suspend fun badExample() = withContext(Dispatchers.Default) {
        withContext(Dispatchers.Default) { // Redundant when dispatcher is the same
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
    // Bad: still part of parent Job; unnecessary nested switching
    fun badViewModel() {
        viewModelScope.launch {
            withContext(Dispatchers.IO) {
                logEvent()
            }
        }
    }

    // Good: launch directly on IO dispatcher for that work (when result is not needed)
    fun goodViewModel() {
        viewModelScope.launch(Dispatchers.IO) {
            logEvent()
        }
    }
}

fun compute(): Int = 42
suspend fun logEvent() = delay(100)

// Mock viewModelScope (in real Android code, use the actual viewModelScope
// and a Main dispatcher provided by Android or a test dispatcher)
val viewModelScope = CoroutineScope(Dispatchers.Default)
```

#### Advanced withContext Patterns

```kotlin
import kotlinx.coroutines.*
import kotlin.coroutines.CoroutineContext

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
    require(times >= 1)
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
        Dispatchers.Default // e.g. CPU-heavy processing for large collections
    } else {
        Dispatchers.IO // e.g. I/O-oriented work for smaller batches
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
        val dispatcher = StandardTestDispatcher(testScheduler)
        val threadName = withContext(dispatcher) {
            Thread.currentThread().name
        }

        // We assert that our code ran with the provided test dispatcher.
        assert(threadName.contains("Test"))
    }

    @Test
    fun testWithContextReturnsValue() = runTest {
        val dispatcher = StandardTestDispatcher(testScheduler)
        val result = withContext(dispatcher) {
            delay(100)
            42
        }

        assertEquals(42, result)
    }

    @Test
    fun testWithContextCancellation() = runTest {
        val dispatcher = StandardTestDispatcher(testScheduler)
        val job = launch {
            try {
                withContext(dispatcher) {
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
        val dispatcher = StandardTestDispatcher(testScheduler)
        val results = mutableListOf<String>()

        withContext(dispatcher) {
            results.add("First")
        }

        withContext(dispatcher) {
            results.add("Second")
        }

        assertEquals(listOf("First", "Second"), results)
    }
}
```

## Follow-ups (RU)

1. В чём разница по производительности между `withContext` и `async + await`?
2. Можно ли использовать `withContext` для вложенного переключения между `Dispatchers.Main` и `Dispatchers.IO`?
3. Как `withContext` обрабатывает исключения по сравнению с `launch` и `async`?
4. Что произойдёт, если вызвать `withContext` с тем же диспетчером, на котором вы уже находитесь?
5. Может ли `withContext` быть отменён и как распространяется отмена?
6. Как `NonCancellable` контекст влияет на поведение `withContext`?
7. В чём разница между `withContext(Dispatchers.IO)` и `runBlocking`?
8. Как измерить накладные расходы переключения диспетчера при использовании `withContext`?

## Follow-ups (EN)

1. What's the performance difference between `withContext` and `async + await`?
2. Can you use `withContext` to switch from `Dispatchers.Main` to `Dispatchers.IO` in a nested manner?
3. How does `withContext` handle exceptions compared to `launch` and `async`?
4. What happens if you call `withContext` with the same dispatcher you're already on?
5. Can `withContext` be cancelled, and how does cancellation propagate?
6. How does `NonCancellable` context affect `withContext` behavior?
7. What's the difference between `withContext(Dispatchers.IO)` and `runBlocking`?
8. How can you measure the overhead of dispatcher switching with `withContext`?

## References (RU)

- [Kotlin Coroutines Guide - Coroutine Context and Dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
- [withContext - kotlinx.coroutines API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-context.html)
- [Roman Elizarov - Blocking threads, suspending coroutines](https://medium.com/@elizarov/blocking-threads-suspending-coroutines-d33e11bf4761)
- [Android Developers - Best practices for coroutines](https://developer.android.com/kotlin/coroutines/coroutines-best-practices)

## References (EN)

- [Kotlin Coroutines Guide - Coroutine Context and Dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
- [withContext - kotlinx.coroutines API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-context.html)
- [Roman Elizarov - Blocking threads, suspending coroutines](https://medium.com/@elizarov/blocking-threads-suspending-coroutines-d33e11bf4761)
- [Android Developers - Best practices for coroutines](https://developer.android.com/kotlin/coroutines/coroutines-best-practices)

## Related Questions (RU)

- [[q-coroutine-builders-comparison--kotlin--medium]]
- [[q-structured-concurrency--kotlin--hard]]
- [[q-launch-vs-async-vs-runblocking--kotlin--medium]]

## Related Questions (EN)

- [[q-coroutine-builders-comparison--kotlin--medium]]
- [[q-structured-concurrency--kotlin--hard]]
- [[q-launch-vs-async-vs-runblocking--kotlin--medium]]
