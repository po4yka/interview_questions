---
id: kotlin-238
title: "Comparison of all coroutine builders / Сравнение всех builders корутин"
aliases: [Coroutine Builders Comparison, Сравнение coroutine builders]
topic: kotlin
difficulty: medium
status: draft
created: "2025-10-12"
updated: "2025-11-09"
question_kind: theory
original_language: en
language_tags: [en, ru]
subtopics: [builders, coroutines]
tags: ["async", "builders", "coroutines", "difficulty/medium", "kotlin", "launch", "runblocking"]
description: "Comprehensive comparison of Kotlin coroutine builders covering return types, blocking vs suspending behavior, use cases, and performance implications"
moc: moc-kotlin
related: [c-kotlin, c-coroutines, q-dispatcher-performance--kotlin--hard]
---

# Вопрос (RU)

> Сравните основные builders корутин в Kotlin: `launch`, `async`, `runBlocking`, `withContext`, `coroutineScope`, `supervisorScope` — по возвращаемым типам, блокирующему/приостанавливающему поведению, обработке исключений, структурной конкуррентности и основным вариантам использования.

## Ответ (RU)

Ниже приведено детальное сравнение всех основных builders корутин Kotlin с примерами, фокусом на структурной конкуррентности, обработке исключений, блокирующем поведении и производительности. См. также [[c-coroutines]].

### Краткая справочная таблица

| Строитель | Возвращает | Сам является suspend-функцией | Блокирующий | Обработка исключений | Случай использования |
|-----------|------------|-------------------------------|-------------|----------------------|----------------------|
| `launch` | `Job` | Нет (вызывается из корутины/suspend/`runBlocking`) | Нет | Необработанное исключение сразу репортится и отменяет родителя | Операции «запустил и забыл», фоновые задачи |
| `async` | `Deferred<T>` | Нет (вызывается из корутины/suspend/`runBlocking`) | Нет | Исключение сохраняется и выбрасывается при `await()` | Параллельные вычисления с результатом |
| `runBlocking` | `T` | Нет | Да (блокирует поток до завершения) | Исключения выбрасываются наружу блока | Мост между блокирующим и suspend-кодом (main, тесты) |
| `withContext` | `T` | Да | Нет | Исключение пробрасывается вызывающему, дочерние отменяются | Переключение dispatcher, последовательные операции |
| `coroutineScope` | `T` | Да | Нет | Исключение в дочерней корутине отменяет всех и пробрасывается наружу | Структурная конкуррентность, атомарные группы задач |
| `supervisorScope` | `T` | Да | Нет | Сбой дочернего не отменяет остальных; сбой тела scope завершает его с ошибкой | Независимые дочерние операции, частичный успех |

### `launch` — «запустил и забыл»

```kotlin
import kotlinx.coroutines.*

fun launchExamples() = runBlocking {
    println("=== launch ===")

    // Немедленно возвращает Job
    val job: Job = launch {
        delay(1000)
        println("launch completed")
    }

    println("launch returned immediately")

    // Родитель не ждёт автоматически: нужно явно вызывать join()
    job.join()

    // Кейc 1: fire-and-forget операции
    launch {
        updateAnalytics()
    }

    launch {
        logEvent()
    }

    // Кейc 2: параллельные независимые операции
    val job1 = launch { downloadFile1() }
    val job2 = launch { downloadFile2() }
    val job3 = launch { downloadFile3() }

    joinAll(job1, job2, job3)

    // Кейc 3: фоновая работа, привязанная к lifecycle
    val backgroundJob = launch {
        while (isActive) {
            doPeriodicWork()
            delay(1000)
        }
    }

    delay(5000)
    backgroundJob.cancel()
}

suspend fun updateAnalytics() { delay(100) }
suspend fun logEvent() { delay(100) }
suspend fun downloadFile1() { delay(500) }
suspend fun downloadFile2() { delay(500) }
suspend fun downloadFile3() { delay(500) }
suspend fun doPeriodicWork() { println("Working...") }
```

Ключевые моменты:
- Возвращает `Job`, нет значения результата.
- Исключение в дочерней корутине по умолчанию отменяет родителя (structured concurrency).
- Используйте для фоновых и побочных эффектов, когда результат не нужен.

### `async` — конкурентные вычисления с результатом

```kotlin
import kotlinx.coroutines.*

fun asyncExamples() = runBlocking {
    println("=== async ===")

    // Немедленно возвращает Deferred<T>
    val deferred: Deferred<String> = async {
        delay(1000)
        "async result"
    }

    println("async returned immediately")

    // Реальное ожидание — при await()
    val result = deferred.await()
    println("Result: $result")

    // Кейc 1: параллельные вычисления с результатами
    val time1 = measureTimeMillis {
        val result1 = async { computeValue1() }
        val result2 = async { computeValue2() }
        val result3 = async { computeValue3() }

        val sum = result1.await() + result2.await() + result3.await()
        println("Sum: $sum")
    }
    println("Parallel async: $time1 ms")

    // Кейc 2: несколько независимых API вызовов
    val users = async { fetchUsers() }
    val posts = async { fetchPosts() }
    val comments = async { fetchComments() }

    val allData = Triple(
        users.await(),
        posts.await(),
        comments.await()
    )

    // Кейc 3: «гонка» (первый завершившийся выигрывает)
    val fastest = select<String> {
        async { slowOperation() }.onAwait { "Slow: $it" }
        async { fastOperation() }.onAwait { "Fast: $it" }
    }
    println("Fastest: $fastest")
}

suspend fun computeValue1(): Int {
    delay(500)
    return 10
}

suspend fun computeValue2(): Int {
    delay(500)
    return 20
}

suspend fun computeValue3(): Int {
    delay(500)
    return 30
}

suspend fun fetchUsers(): List<String> {
    delay(300)
    return listOf("User1", "User2")
}

suspend fun fetchPosts(): List<String> {
    delay(400)
    return listOf("Post1", "Post2")
}

suspend fun fetchComments(): List<String> {
    delay(200)
    return listOf("Comment1", "Comment2")
}

suspend fun slowOperation(): String {
    delay(2000)
    return "slow"
}

suspend fun fastOperation(): String {
    delay(500)
    return "fast"
}
```

Ключевые моменты:
- Используйте `async` для конкурентных задач, от которых нужен результат.
- Исключения всплывают только при `await()`, поэтому важно не забывать вызывать `await()`.
- При множественных `Deferred` порядок вызова `await()` влияет на то, где и когда вы увидите ошибку/блокировку.

### `runBlocking` — блокирующий мост

```kotlin
import kotlinx.coroutines.*

fun runBlockingExamples() {
    println("=== runBlocking ===")

    // Блокирует текущий поток до завершения
    val result = runBlocking {
        delay(1000)
        "runBlocking result"
    }
    println("Result: $result")

    // Кейc 1: main-функция (top-level в реальном коде)
    // fun main() = runBlocking {
    //     launch {
    //         delay(1000)
    //         println("World!")
    //     }
    //     println("Hello,")
    // }

    // Кейc 2: юнит-тесты
    @Test
    fun testCoroutine() = runBlocking {
        val result = async {
            delay(100)
            42
        }
        assertEquals(42, result.await())
    }

    // Кейc 3: мост между блокирующим и suspend-кодом
    fun blockingFunction(): String = runBlocking {
        suspendingFunction()
    }

    // Плохая практика: блокирование потока в асинхронном коде
    fun badExample() {
        runBlocking {
            delay(10000) // блокирует вызывающий поток
        }
    }

    // Кейc 4: простые скрипты
    fun simpleScript() = runBlocking {
        val data = fetchData()
        processData(data)
        saveData(data)
    }
}

suspend fun suspendingFunction(): String {
    delay(100)
    return "result"
}

suspend fun fetchData(): String {
    delay(100)
    return "data"
}

suspend fun processData(data: String) {
    delay(100)
}

suspend fun saveData(data: String) {
    delay(100)
}

annotation class Test
fun assertEquals(expected: Int, actual: Int) {}
```

Ключевые моменты:
- Блокирует поток: используйте только на границах (main, тесты, интеграция со старым кодом).
- Не используйте внутри уже работающих корутин и продакшн-обработчиков.

### `withContext` — переключение контекста/dispatcher

```kotlin
import kotlinx.coroutines.*

fun withContextExamples() = runBlocking {
    println("=== withContext ===")

    // Приостанавливает и возвращает результат
    val result: String = withContext(Dispatchers.IO) {
        delay(1000)
        "withContext result"
    }
    println("Result: $result")

    // Кейc 1: I/O операции
    suspend fun loadUser(id: String): User = withContext(Dispatchers.IO) {
        delay(500)
        User(id, "John")
    }

    // Кейc 2: CPU-bound операции
    suspend fun processImage(image: ByteArray): ByteArray =
        withContext(Dispatchers.Default) {
            delay(1000)
            image
        }

    // Кейc 3: последовательные шаги с переключением dispatcher
    suspend fun loadAndProcess(id: String): ProcessedUser {
        val user = withContext(Dispatchers.IO) {
            loadUserFromDb(id)
        }

        val processed = withContext(Dispatchers.Default) {
            processUser(user)
        }

        withContext(Dispatchers.IO) {
            saveProcessedUser(processed)
        }

        return processed
    }

    // Кейc 4: изменение контекста
    withContext(CoroutineName("MyCoroutine")) {
        println("Name: ${coroutineContext[CoroutineName]}")
    }

    // Предпочтительнее, чем `async`+`await` для одиночной операции с результатом
    val data1 = withContext(Dispatchers.IO) { fetchData1() }
    val data2 = withContext(Dispatchers.IO) { fetchData2() }
}

data class User(val id: String, val name: String)
data class ProcessedUser(val id: String, val name: String, val processed: Boolean = true)

suspend fun loadUserFromDb(id: String): User {
    delay(300)
    return User(id, "User $id")
}

suspend fun processUser(user: User): ProcessedUser {
    delay(200)
    return ProcessedUser(user.id, user.name.uppercase())
}

suspend fun saveProcessedUser(user: ProcessedUser) {
    delay(100)
}

suspend fun fetchData1(): String {
    delay(300)
    return "data1"
}

suspend fun fetchData2(): String {
    delay(300)
    return "data2"
}
```

Ключевые моменты:
- Чистая семантика: «выполнить блок в другом контексте и вернуть результат».
- Вписывается в концепцию структурной конкуррентности.

### `coroutineScope` — структурная конкуррентность

```kotlin
import kotlinx.coroutines.*

fun coroutineScopeExamples() = runBlocking {
    println("=== coroutineScope ===")

    // Приостанавливает до завершения всех детей
    val result = coroutineScope {
        val deferred1 = async { computeValue1() }
        val deferred2 = async { computeValue2() }

        deferred1.await() + deferred2.await()
    }
    println("Result: $result")

    // Кейc 1: параллельная работа внутри suspend-функции
    suspend fun loadUserData(userId: String): UserData = coroutineScope {
        val user = async { loadUser(userId) }
        val posts = async { loadPosts(userId) }
        val friends = async { loadFriends(userId) }

        UserData(user.await(), posts.await(), friends.await())
    }

    // Кейc 2: все задачи либо завершаются успешно, либо вся группа падает
    suspend fun processAllItems(items: List<String>) = coroutineScope {
        items.map { item ->
            async { processItem(item) }
        }.awaitAll()
    }

    // Кейc 3: обработка исключений — сбой одного отменяет остальных
    try {
        coroutineScope {
            launch {
                delay(500)
                throw RuntimeException("Child failed")
            }

            launch {
                delay(1000)
                println("This never executes")
            }
        }
    } catch (e: RuntimeException) {
        println("Caught exception: ${e.message}")
    }

    // Кейc 4: распространение отмены
    suspend fun cancellableOperation() = coroutineScope {
        launch {
            repeat(5) {
                println("Working $it")
                delay(500)
            }
        }
        // scope ждёт всех детей или отмены
    }

    // Сравнение с launch
    launch {
        // Родитель (runBlocking) не ждёт завершения тела автоматически
        async { delay(1000) }
        println("Parent continues")
    }

    coroutineScope {
        // Родитель приостанавливается до завершения детей
        async { delay(1000) }
        println("After child completes")
    }

    delay(2000)
}

data class UserData(
    val user: User,
    val posts: List<String>,
    val friends: List<String>
)

suspend fun loadUser(userId: String): User {
    delay(300)
    return User(userId, "User $userId")
}

suspend fun loadPosts(userId: String): List<String> {
    delay(400)
    return listOf("Post1", "Post2")
}

suspend fun loadFriends(userId: String): List<String> {
    delay(200)
    return listOf("Friend1", "Friend2")
}

suspend fun processItem(item: String): String {
    delay(100)
    return "processed: $item"
}
```

Ключевые моменты:
- Гарантирует структурную конкуррентность: родитель ждёт всех детей.
- Сбой внутри scope отменяет остальные дочерние корутины и пробрасывается наружу.

### `supervisorScope` — независимые дочерние корутины

```kotlin
import kotlinx.coroutines.*

fun supervisorScopeExamples() = runBlocking {
    println("=== supervisorScope ===")

    // Дочерние задачи независимы: сбой одной не отменяет другие
    supervisorScope {
        launch {
            delay(500)
            println("Child 1 completed")
        }

        launch {
            delay(200)
            throw RuntimeException("Child 2 failed")
        }

        launch {
            delay(1000)
            println("Child 3 completed") // всё ещё выполнится
        }

        delay(1500)
    }

    // Кейc 1: независимые виджеты дашборда
    suspend fun loadDashboard(): Dashboard = supervisorScope {
        val weather = async {
            try {
                loadWeatherWidget()
            } catch (e: Exception) {
                null
            }
        }

        val news = async {
            try {
                loadNewsWidget()
            } catch (e: Exception) {
                null
            }
        }

        val stocks = async {
            try {
                loadStocksWidget()
            } catch (e: Exception) {
                null
            }
        }

        Dashboard(weather.await(), news.await(), stocks.await())
    }

    // Кейc 2: частичный сбор результатов
    suspend fun fetchPartialResults(): List<String> = supervisorScope {
        val jobs = List(5) { index ->
            async {
                if (index == 2) throw Exception("Failed")
                "Result $index"
            }
        }

        jobs.mapNotNull { job ->
            try {
                job.await()
            } catch (e: Exception) {
                null
            }
        }
    }

    // Кейc 3: независимые фоновые задачи
    suspend fun startBackgroundTasks() = supervisorScope {
        launch {
            try {
                syncUsers()
            } catch (e: Exception) {
                logError("User sync failed", e)
            }
        }

        launch {
            try {
                syncPosts()
            } catch (e: Exception) {
                logError("Post sync failed", e)
            }
        }

        delay(5000)
    }
}

data class Dashboard(
    val weather: String?,
    val news: String?,
    val stocks: String?
)

suspend fun loadWeatherWidget(): String {
    delay(300)
    return "Sunny, 72°F"
}

suspend fun loadNewsWidget(): String {
    delay(400)
    throw Exception("News service unavailable")
}

suspend fun loadStocksWidget(): String {
    delay(200)
    return "AAPL: $150"
}

suspend fun syncUsers() {
    delay(500)
    println("Users synced")
}

suspend fun syncPosts() {
    delay(400)
    throw Exception("Post sync failed")
}

fun logError(message: String, error: Exception) {
    println("ERROR: $message - ${error.message}")
}
```

Ключевые моменты:
- Используйте, когда сбой одной задачи не должен срывать остальные.
- Тело `supervisorScope` по-прежнему подчиняется обычным правилам: необработанное исключение в теле завершает scope.

### Комплексные примеры сравнения

```kotlin
import kotlinx.coroutines.*

fun comprehensiveComparison() = runBlocking {
    println("=== Return Types ===")

    val job: Job = launch { delay(100) }
    val deferred: Deferred<String> = async { "result" }

    // Вложенный runBlocking только для демонстрации, в реальном коде избегайте
    val blockingResult: String = runBlocking { "result" }

    val contextResult: String = withContext(Dispatchers.Default) { "result" }
    val scopeResult: String = coroutineScope { "result" }
    val supervisorResult: String = supervisorScope { "result" }

    println("\n=== Blocking Behavior ===")

    // runBlocking: блокирует поток
    println("Before runBlocking")
    runBlocking {
        delay(1000)
        println("Inside runBlocking")
    }
    println("After runBlocking (thread was blocked)")

    // Остальные: не блокируют поток, а приостанавливают корутину
    println("Before launch")
    val launchJob = launch {
        delay(1000)
        println("Inside launch")
    }
    println("After launch (thread not blocked by launch itself)")
    launchJob.join()

    println("\n=== Exception Handling ===")

    // `launch`: необработанное исключение идёт в родителя/handler
    val exceptionHandler = CoroutineExceptionHandler { _, e ->
        println("Caught in handler: ${e.message}")
    }

    CoroutineScope(Dispatchers.Default + exceptionHandler).launch {
        throw RuntimeException("launch exception")
    }

    // `async`: исключение выбрасывается при `await()`
    try {
        async {
            throw RuntimeException("async exception")
        }.await()
    } catch (e: RuntimeException) {
        println("Caught on await: ${e.message}")
    }

    // `withContext`: исключение сразу возвращается вызывающему
    try {
        withContext(Dispatchers.Default) {
            throw RuntimeException("withContext exception")
        }
    } catch (e: RuntimeException) {
        println("Caught from withContext: ${e.message}")
    }

    // `coroutineScope`: отменяет всех детей и пробрасывает исключение
    try {
        coroutineScope {
            launch {
                throw RuntimeException("coroutineScope exception")
            }
            delay(1000)
        }
    } catch (e: RuntimeException) {
        println("Caught from coroutineScope: ${e.message}")
    }

    // `supervisorScope`: дети независимы; ошибка в теле завершает scope
    supervisorScope {
        launch {
            throw RuntimeException("supervisorScope exception")
        }
        delay(500)
        println("supervisorScope continues")
    }

    println("\n=== Use Case: Parallel vs Sequential ===")

    // Параллельно с `async`
    val parallelTime = measureTimeMillis {
        coroutineScope {
            val a = async { delay(1000); 1 }
            val b = async { delay(1000); 2 }
            println("Sum: ${a.await() + b.await()}")
        }
    }
    println("Parallel: $parallelTime ms")

    // Последовательно с `withContext`
    val sequentialTime = measureTimeMillis {
        val a = withContext(Dispatchers.Default) { delay(1000); 1 }
        val b = withContext(Dispatchers.Default) { delay(1000); 2 }
        println("Sum: ${a + b}")
    }
    println("Sequential: $sequentialTime ms")

    delay(2000)
}
```

### Сравнение производительности (качественно)

```kotlin
import kotlinx.coroutines.*

fun performanceComparison() = runBlocking {
    println("=== Performance Comparison ===")

    val iterations = 10000

    // `launch` overhead
    val launchTime = measureTimeMillis {
        val jobs = List(iterations) {
            launch { }
        }
        jobs.forEach { it.join() }
    }
    println("launch x$iterations: $launchTime ms")

    // `async` overhead
    val asyncTime = measureTimeMillis {
        val deferreds = List(iterations) {
            async { 42 }
        }
        deferreds.forEach { it.await() }
    }
    println("async x$iterations: $asyncTime ms")

    // `withContext` overhead
    val withContextTime = measureTimeMillis {
        repeat(iterations) {
            withContext(Dispatchers.Default) { 42 }
        }
    }
    println("withContext x$iterations: $withContextTime ms")

    // `coroutineScope` overhead
    val coroutineScopeTime = measureTimeMillis {
        repeat(iterations) {
            coroutineScope { 42 }
        }
    }
    println("coroutineScope x$iterations: $coroutineScopeTime ms")

    println("\n=== Memory Allocation (qualitative) ===")

    // `launch`: выделяет `Job`
    // `async`: выделяет `Deferred` + хранение результата
    // `withContext`: использует существующий scope, не возвращает `Job`
    // `coroutineScope`: минимальные дополнительные аллокации
}
```

### Матрица принятия решений

```kotlin
// `launch`:
// - fire-and-forget
// - результат не нужен
// - старт без ожидания
launch { updateCache() }

// `async`:
// - нужен результат конкурентной операции
// - несколько параллельных задач
// - можно дождаться позже
val result = async { fetchData() }.await()

// `runBlocking`:
// - main-функция
// - юнит-тесты
// - мост между блокирующим и suspend-кодом
// - НЕ внутри активных корутин в продакшене
fun main() = runBlocking { }

// `withContext`:
// - переключение dispatcher
// - последовательная операция с результатом
// - эффективнее, чем `async` + `await` для одной задачи
val data = withContext(Dispatchers.IO) { loadFromDb() }

// `coroutineScope`:
// - структурная конкуррентность
// - все дочерние задачи должны завершиться или упасть вместе
suspend fun loadAll() = coroutineScope {
    // все дочерние корутины либо успешны, либо отменены
}

// `supervisorScope`:
// - независимые дочерние задачи
// - частичные результаты приемлемы
suspend fun loadPartial() = supervisorScope {
    // сбой одной задачи не отменяет остальные
}
```

### Лучшие практики

1. Выбирайте строитель, соответствующий задаче (`launch` для побочных эффектов, `async` для результатов, `withContext` для смены контекста).
2. Избегайте `runBlocking` в асинхронном/UI коде; используйте только на границе систем.
3. Для одиночных операций с результатом предпочитайте `withContext` вместо `async`.
4. Используйте `coroutineScope` для строгой структурной конкуррентности.
5. Используйте `supervisorScope` там, где допустим частичный успех и независимые сбои.

---

# Question (EN)

> Compare the main Kotlin coroutine builders: `launch`, `async`, `runBlocking`, `withContext`, `coroutineScope`, and `supervisorScope` in terms of return types, blocking vs suspending behavior, exception handling, structured concurrency semantics, and typical use cases.

## Answer (EN)

Below is a detailed comparison of all primary Kotlin coroutine builders with examples, focusing on return types, blocking behavior, exception handling, structured concurrency, and performance implications. See also [[c-coroutines]].

### Quick Reference Table

| Builder | Returns | Suspending (builder itself) | Blocking | Exception Handling | Use Case |
|---------|---------|-----------------------------|----------|-------------------|----------|
| `launch` | `Job` | No (must be called from coroutine/suspend/`runBlocking`) | No | Unhandled exception is reported and cancels parent | Fire-and-forget, background tasks |
| `async` | `Deferred<T>` | No (must be called from coroutine/suspend/`runBlocking`) | No | Captured and thrown on `await()` | Concurrent computations with results |
| `runBlocking` | `T` | No | Yes (blocks calling thread) | Throws out of block | Bridging blocking/suspend code (main, tests) |
| `withContext` | `T` | Yes | No | Rethrows to caller; cancels children on failure | Dispatcher switching, sequential work |
| `coroutineScope` | `T` | Yes | No | Child failure cancels siblings and is rethrown | Structured concurrency, all-or-nothing groups |
| `supervisorScope` | `T` | Yes | No | Child failure does not cancel siblings; failure in body fails scope | Independent children, partial success |

### Launch - Fire and Forget

```kotlin
import kotlinx.coroutines.*

fun launchExamples() = runBlocking {
    println("=== launch ===")

    // Returns Job immediately
    val job: Job = launch {
        delay(1000)
        println("launch completed")
    }

    println("launch returned immediately")

    // Does not suspend parent automatically
    // Must explicitly join if waiting is needed
    job.join()

    // Use case 1: Fire-and-forget operations
    launch {
        updateAnalytics()
    }

    launch {
        logEvent()
    }

    // Use case 2: Parallel independent operations
    val job1 = launch { downloadFile1() }
    val job2 = launch { downloadFile2() }
    val job3 = launch { downloadFile3() }

    joinAll(job1, job2, job3)

    // Use case 3: Background work with lifecycle
    val backgroundJob = launch {
        while (isActive) {
            doPeriodicWork()
            delay(1000)
        }
    }

    delay(5000)
    backgroundJob.cancel()
}

suspend fun updateAnalytics() { delay(100) }
suspend fun logEvent() { delay(100) }
suspend fun downloadFile1() { delay(500) }
suspend fun downloadFile2() { delay(500) }
suspend fun downloadFile3() { delay(500) }
suspend fun doPeriodicWork() { println("Working...") }
```

Key points:
- Returns `Job`, no result value.
- Exception cancels parent (by default) via structured concurrency.
- Use for side effects/background work where no result is needed.

### Async - Concurrent Computations

```kotlin
import kotlinx.coroutines.*

fun asyncExamples() = runBlocking {
    println("=== async ===")

    // Returns Deferred<T> immediately
    val deferred: Deferred<String> = async {
        delay(1000)
        "async result"
    }

    println("async returned immediately")

    // Suspends when calling await()
    val result = deferred.await()
    println("Result: $result")

    // Use case 1: Parallel computations with results
    val time1 = measureTimeMillis {
        val result1 = async { computeValue1() }
        val result2 = async { computeValue2() }
        val result3 = async { computeValue3() }

        val sum = result1.await() + result2.await() + result3.await()
        println("Sum: $sum")
    }
    println("Parallel async: $time1 ms")

    // Use case 2: Multiple independent API calls
    val users = async { fetchUsers() }
    val posts = async { fetchPosts() }
    val comments = async { fetchComments() }

    val allData = Triple(
        users.await(),
        posts.await(),
        comments.await()
    )

    // Use case 3: Race condition (first to complete)
    val fastest = select<String> {
        async { slowOperation() }.onAwait { "Slow: $it" }
        async { fastOperation() }.onAwait { "Fast: $it" }
    }
    println("Fastest: $fastest")
}

suspend fun computeValue1(): Int {
    delay(500)
    return 10
}

suspend fun computeValue2(): Int {
    delay(500)
    return 20
}

suspend fun computeValue3(): Int {
    delay(500)
    return 30
}

suspend fun fetchUsers(): List<String> {
    delay(300)
    return listOf("User1", "User2")
}

suspend fun fetchPosts(): List<String> {
    delay(400)
    return listOf("Post1", "Post2")
}

suspend fun fetchComments(): List<String> {
    delay(200)
    return listOf("Comment1", "Comment2")
}

suspend fun slowOperation(): String {
    delay(2000)
    return "slow"
}

suspend fun fastOperation(): String {
    delay(500)
    return "fast"
}
```

Key points:
- Use `async` for concurrent tasks that produce a result.
- Exceptions surface when you call `await()`.
- Ordering of `await()` affects where/when failures or suspensions occur.

### runBlocking - Blocking Bridge

```kotlin
import kotlinx.coroutines.*

fun runBlockingExamples() {
    println("=== runBlocking ===")

    // Blocks the current thread until the coroutine completes
    val result = runBlocking {
        delay(1000)
        "runBlocking result"
    }
    println("Result: $result")

    // Use case 1: main function (top-level in real code)
    // fun main() = runBlocking {
    //     launch {
    //         delay(1000)
    //         println("World!")
    //     }
    //     println("Hello,")
    // }

    // Use case 2: Unit tests
    @Test
    fun testCoroutine() = runBlocking {
        val result = async {
            delay(100)
            42
        }
        assertEquals(42, result.await())
    }

    // Use case 3: Bridging blocking and suspending code
    fun blockingFunction(): String = runBlocking {
        suspendingFunction()
    }

    // AVOID: blocking threads in production async code
    fun badExample() {
        runBlocking {
            delay(10000)
        }
    }

    // Use case 4: Simple scripts
    fun simpleScript() = runBlocking {
        val data = fetchData()
        processData(data)
        saveData(data)
    }
}

suspend fun suspendingFunction(): String {
    delay(100)
    return "result"
}

suspend fun fetchData(): String {
    delay(100)
    return "data"
}

suspend fun processData(data: String) {
    delay(100)
}

suspend fun saveData(data: String) {
    delay(100)
}

annotation class Test
fun assertEquals(expected: Int, actual: Int) {}
```

Key points:
- Blocks the thread; only for boundaries (main, tests, legacy interop).
- Never nest `runBlocking` inside coroutines in production code.

### withContext - Dispatcher Switching

```kotlin
import kotlinx.coroutines.*

fun withContextExamples() = runBlocking {
    println("=== withContext ===")

    // Suspends and returns result
    val result: String = withContext(Dispatchers.IO) {
        delay(1000)
        "withContext result"
    }
    println("Result: $result")

    // Use case 1: I/O operations
    suspend fun loadUser(id: String): User = withContext(Dispatchers.IO) {
        delay(500)
        User(id, "John")
    }

    // Use case 2: CPU-intensive operations
    suspend fun processImage(image: ByteArray): ByteArray =
        withContext(Dispatchers.Default) {
            delay(1000)
            image
        }

    // Use case 3: Sequential operations with dispatcher switching
    suspend fun loadAndProcess(id: String): ProcessedUser {
        val user = withContext(Dispatchers.IO) {
            loadUserFromDb(id)
        }

        val processed = withContext(Dispatchers.Default) {
            processUser(user)
        }

        withContext(Dispatchers.IO) {
            saveProcessedUser(processed)
        }

        return processed
    }

    // Use case 4: Context modification
    withContext(CoroutineName("MyCoroutine")) {
        println("Name: ${coroutineContext[CoroutineName]}")
    }

    // Prefer over async + await for a single operation that returns a result
    val data1 = withContext(Dispatchers.IO) { fetchData1() }
    val data2 = withContext(Dispatchers.IO) { fetchData2() }
}

data class User(val id: String, val name: String)
data class ProcessedUser(val id: String, val name: String, val processed: Boolean = true)

suspend fun loadUserFromDb(id: String): User {
    delay(300)
    return User(id, "User $id")
}

suspend fun processUser(user: User): ProcessedUser {
    delay(200)
    return ProcessedUser(user.id, user.name.uppercase())
}

suspend fun saveProcessedUser(user: ProcessedUser) {
    delay(100)
}

suspend fun fetchData1(): String {
    delay(300)
    return "data1"
}

suspend fun fetchData2(): String {
    delay(300)
    return "data2"
}
```

Key points:
- Idiomatic for executing a block in another context and returning its result.
- Integrates naturally with structured concurrency.

### coroutineScope - Structured Concurrency

```kotlin
import kotlinx.coroutines.*

fun coroutineScopeExamples() = runBlocking {
    println("=== coroutineScope ===")

    // Suspends until all children complete
    val result = coroutineScope {
        val deferred1 = async { computeValue1() }
        val deferred2 = async { computeValue2() }

        deferred1.await() + deferred2.await()
    }
    println("Result: $result")

    // Use case 1: Creating parallel operations within suspend function
    suspend fun loadUserData(userId: String): UserData = coroutineScope {
        val user = async { loadUser(userId) }
        val posts = async { loadPosts(userId) }
        val friends = async { loadFriends(userId) }

        UserData(user.await(), posts.await(), friends.await())
    }

    // Use case 2: All children must succeed or fail as a group
    suspend fun processAllItems(items: List<String>) = coroutineScope {
        items.map { item ->
            async { processItem(item) }
        }.awaitAll()
    }

    // Use case 3: Exception handling - failure cancels siblings
    try {
        coroutineScope {
            launch {
                delay(500)
                throw RuntimeException("Child failed")
            }

            launch {
                delay(1000)
                println("This never executes")
            }
        }
    } catch (e: RuntimeException) {
        println("Caught exception: ${e.message}")
    }

    // Use case 4: Cancellation propagation
    suspend fun cancellableOperation() = coroutineScope {
        launch {
            repeat(5) {
                println("Working $it")
                delay(500)
            }
        }
        // Scope waits for all children or cancellation
    }

    // Comparison with launch
    launch {
        // Parent (runBlocking) doesn't wait for this coroutine body to finish
        async { delay(1000) }
        println("Parent continues")
    }

    coroutineScope {
        // Parent suspends until children complete
        async { delay(1000) }
        println("After child completes")
    }

    delay(2000)
}

data class UserData(
    val user: User,
    val posts: List<String>,
    val friends: List<String>
)

suspend fun loadUser(userId: String): User {
    delay(300)
    return User(userId, "User $userId")
}

suspend fun loadPosts(userId: String): List<String> {
    delay(400)
    return listOf("Post1", "Post2")
}

suspend fun loadFriends(userId: String): List<String> {
    delay(200)
    return listOf("Friend1", "Friend2")
}

suspend fun processItem(item: String): String {
    delay(100)
    return "processed: $item"
}
```

Key points:
- Enforces structured concurrency: caller waits for children.
- Any child failure cancels siblings and is rethrown.

### supervisorScope - Independent Children

```kotlin
import kotlinx.coroutines.*

fun supervisorScopeExamples() = runBlocking {
    println("=== supervisorScope ===")

    // Children fail independently: failure of one child does not cancel others
    supervisorScope {
        launch {
            delay(500)
            println("Child 1 completed")
        }

        launch {
            delay(200)
            throw RuntimeException("Child 2 failed")
        }

        launch {
            delay(1000)
            println("Child 3 completed") // Still executes
        }

        delay(1500)
    }

    // Use case 1: Loading independent dashboard widgets
    suspend fun loadDashboard(): Dashboard = supervisorScope {
        val weather = async {
            try {
                loadWeatherWidget()
            } catch (e: Exception) {
                null // Widget failed, return null
            }
        }

        val news = async {
            try {
                loadNewsWidget()
            } catch (e: Exception) {
                null
            }
        }

        val stocks = async {
            try {
                loadStocksWidget()
            } catch (e: Exception) {
                null
            }
        }

        Dashboard(weather.await(), news.await(), stocks.await())
    }

    // Use case 2: Partial results collection
    suspend fun fetchPartialResults(): List<String> = supervisorScope {
        val jobs = List(5) { index ->
            async {
                if (index == 2) throw Exception("Failed")
                "Result $index"
            }
        }

        jobs.mapNotNull { job ->
            try {
                job.await()
            } catch (e: Exception) {
                null
            }
        }
    }

    // Use case 3: Independent background tasks
    suspend fun startBackgroundTasks() = supervisorScope {
        launch {
            try {
                syncUsers()
            } catch (e: Exception) {
                logError("User sync failed", e)
            }
        }

        launch {
            try {
                syncPosts()
            } catch (e: Exception) {
                logError("Post sync failed", e)
            }
        }

        delay(5000) // Let tasks run
    }
}

data class Dashboard(
    val weather: String?,
    val news: String?,
    val stocks: String?
)

suspend fun loadWeatherWidget(): String {
    delay(300)
    return "Sunny, 72°F"
}

suspend fun loadNewsWidget(): String {
    delay(400)
    throw Exception("News service unavailable")
}

suspend fun loadStocksWidget(): String {
    delay(200)
    return "AAPL: $150"
}

suspend fun syncUsers() {
    delay(500)
    println("Users synced")
}

suspend fun syncPosts() {
    delay(400)
    throw Exception("Post sync failed")
}

fun logError(message: String, error: Exception) {
    println("ERROR: $message - ${error.message}")
}
```

Key points:
- Use for independent tasks where one failure must not cancel others.
- Body failure still terminates the scope.

### Comprehensive Comparison Examples

```kotlin
import kotlinx.coroutines.*

fun comprehensiveComparison() = runBlocking {
    println("=== Return Types ===")

    val job: Job = launch { delay(100) }
    val deferred: Deferred<String> = async { "result" }

    // NOTE: Nested runBlocking here only for demonstration; avoid in real code.
    val blockingResult: String = runBlocking { "result" }

    val contextResult: String = withContext(Dispatchers.Default) { "result" }
    val scopeResult: String = coroutineScope { "result" }
    val supervisorResult: String = supervisorScope { "result" }

    println("\n=== Blocking Behavior ===")

    // runBlocking: blocks thread
    println("Before runBlocking")
    runBlocking {
        delay(1000)
        println("Inside runBlocking")
    }
    println("After runBlocking (thread was blocked)")

    // Others: don't block thread (suspend instead)
    println("Before launch")
    val launchJob = launch {
        delay(1000)
        println("Inside launch")
    }
    println("After launch (thread not blocked by launch itself)")
    launchJob.join()

    println("\n=== Exception Handling ===")

    val exceptionHandler = CoroutineExceptionHandler { _, e ->
        println("Caught in handler: ${e.message}")
    }

    // launch: unhandled exception is reported and propagates
    CoroutineScope(Dispatchers.Default + exceptionHandler).launch {
        throw RuntimeException("launch exception")
    }

    // async: exception thrown on await
    try {
        async {
            throw RuntimeException("async exception")
        }.await()
    } catch (e: RuntimeException) {
        println("Caught on await: ${e.message}")
    }

    // withContext: throws immediately to caller
    try {
        withContext(Dispatchers.Default) {
            throw RuntimeException("withContext exception")
        }
    } catch (e: RuntimeException) {
        println("Caught from withContext: ${e.message}")
    }

    // coroutineScope: cancels all children and throws
    try {
        coroutineScope {
            launch {
                throw RuntimeException("coroutineScope exception")
            }
            delay(1000)
        }
    } catch (e: RuntimeException) {
        println("Caught from coroutineScope: ${e.message}")
    }

    // supervisorScope: continues despite child failure; body failure fails scope
    supervisorScope {
        launch {
            throw RuntimeException("supervisorScope exception")
        }
        delay(500)
        println("supervisorScope continues")
    }

    println("\n=== Use Case: Parallel vs Sequential ===")

    val parallelTime = measureTimeMillis {
        coroutineScope {
            val a = async { delay(1000); 1 }
            val b = async { delay(1000); 2 }
            println("Sum: ${a.await() + b.await()}")
        }
    }
    println("Parallel: $parallelTime ms")

    val sequentialTime = measureTimeMillis {
        val a = withContext(Dispatchers.Default) { delay(1000); 1 }
        val b = withContext(Dispatchers.Default) { delay(1000); 2 }
        println("Sum: ${a + b}")
    }
    println("Sequential: $sequentialTime ms")

    delay(2000)
}
```

### Performance Comparison

```kotlin
import kotlinx.coroutines.*

fun performanceComparison() = runBlocking {
    println("=== Performance Comparison ===")

    val iterations = 10000

    // launch overhead
    val launchTime = measureTimeMillis {
        val jobs = List(iterations) {
            launch { }
        }
        jobs.forEach { it.join() }
    }
    println("launch x$iterations: $launchTime ms")

    // async overhead
    val asyncTime = measureTimeMillis {
        val deferreds = List(iterations) {
            async { 42 }
        }
        deferreds.forEach { it.await() }
    }
    println("async x$iterations: $asyncTime ms")

    // withContext overhead
    val withContextTime = measureTimeMillis {
        repeat(iterations) {
            withContext(Dispatchers.Default) { 42 }
        }
    }
    println("withContext x$iterations: $withContextTime ms")

    // coroutineScope overhead
    val coroutineScopeTime = measureTimeMillis {
        repeat(iterations) {
            coroutineScope { 42 }
        }
    }
    println("coroutineScope x$iterations: $coroutineScopeTime ms")

    println("\n=== Memory Allocation (qualitative) ===")

    // launch: allocates Job
    // async: allocates Deferred + result storage
    // withContext: uses existing scope; no separate Job returned
    // coroutineScope: uses structured concurrency; minimal extra allocations
}
```

### Decision Matrix

```kotlin
// Use launch when:
// - Fire-and-forget operation
// - Don't need result
// - Want to start coroutine without waiting
launch { updateCache() }

// Use async when:
// - Need result from concurrent operation
// - Want to parallelize multiple operations
// - Can wait for result later
val result = async { fetchData() }.await()

// Use runBlocking when:
// - In main function (top-level)
// - In unit tests
// - Bridging blocking and suspending code
// - NEVER inside existing coroutines in production code
fun main() = runBlocking { }

// Use withContext when:
// - Need to switch dispatcher
// - Sequential operation with result
// - More efficient than async + await for a single operation
val data = withContext(Dispatchers.IO) { loadFromDb() }

// Use coroutineScope when:
// - Creating structured concurrency
// - Need all children to complete (or fail as a group)
// - Want exception in a child to cancel siblings
suspend fun loadAll() = coroutineScope {
    // all children must succeed or the scope fails
}

// Use supervisorScope when:
// - Children should fail independently
// - Want partial results
// - Some operations can fail without affecting others
suspend fun loadPartial() = supervisorScope {
    // children fail independently
}
```

### Best Practices

1. Choose the right builder for each scenario.
2. Avoid `runBlocking` in coroutine-based production code.
3. Prefer `withContext` over `async` + `await` for single operations.
4. Use `coroutineScope` to enforce structured concurrency.
5. Use `supervisorScope` when partial success and independent failures are acceptable.

---

## Follow-ups (RU)

1. В каких ситуациях вы предпочтёте `async` вместо `withContext`, несмотря на дополнительный overhead?
2. Как вы бы совместили `supervisorScope` с `SupervisorJob` в реальном `CoroutineScope` приложения?
3. Какие подходы вы используете для единообразной обработки исключений из нескольких дочерних корутин?
4. Как по-разному распространяется отмена в `coroutineScope` и `supervisorScope` в вложенных иерархиях?
5. Как использование разных builders влияет на гарантии структурной конкуррентности при работе с кастомными `CoroutineScope`?

## Follow-ups

1. When would you choose `async` instead of `withContext` despite its additional overhead?
2. How would you combine `supervisorScope` with `SupervisorJob` in a real application `CoroutineScope`?
3. What patterns would you use to handle exceptions from multiple child coroutines consistently?
4. How does cancellation propagate differently for `coroutineScope` vs `supervisorScope` in nested hierarchies?
5. How do these builders interact with structured concurrency guarantees when using custom `CoroutineScope`s?

## References

- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [Coroutine Builders - API Reference](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/)
- [Roman Elizarov - Structured Concurrency](https://medium.com/@elizarov/structured-concurrency-722d765aa952)
- [Kotlin Coroutines Best Practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices)

## Related Questions

- [[q-coroutine-job-lifecycle--kotlin--medium]]
- [[q-withcontext-use-cases--kotlin--medium]]
- [[q-coroutine-supervisorjob-use-cases--kotlin--medium]]
- [[q-structured-concurrency--kotlin--hard]]
- [[q-coroutine-dispatchers--kotlin--medium]]
