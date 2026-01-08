---id: kotlin-126
title: "Testing Coroutine Cancellation Scenarios / Тестирование сценариев отмены корутин"
aliases: ["Testing Coroutine Cancellation Scenarios", "Тестирование сценариев отмены корутин"]

# Classification
topic: kotlin
subtopics: [coroutines, testing]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Coroutine Cancellation Testing Guide

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-coroutines, c-stateflow, q-coroutine-cancellation-cooperation--kotlin--medium, q-coroutine-cancellation-mechanisms--kotlin--medium, q-testing-coroutines-runtest--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-11-11

tags: [cancellation, coroutines, difficulty/medium, kotlin, testing]
---
# Вопрос (RU)
> Как тестировать сценарии отмены корутин? Покрыть тестирование кооперативной отмены, timeout, ensureActive, CancellationException и очистки ресурсов с NonCancellable.

***

# Question (EN)
> How to test coroutine cancellation scenarios? Cover testing cooperative cancellation, timeout, ensureActive, CancellationException, and resource cleanup with NonCancellable.

## Ответ (RU)

Тестирование отмены критически важно для обеспечения правильной очистки ресурсов и корректной реакции на запросы отмены. В корутинах Kotlin отмена кооперативна, поэтому важно тестировать как своевременную остановку работы, так и корректную очистку.

Все примеры ниже предполагают использование `kotlinx-coroutines-test` и виртуального времени через `runTest`.

### Базовое Тестирование Отмены

```kotlin
@Test
fun `корутина может быть отменена`() = runTest {
    val job = launch {
        repeat(1000) {
            delay(100)
            println("Working $it")
        }
    }

    advanceTimeBy(250) // даем ей немного поработать (виртуальное время)
    assertTrue(job.isActive)

    job.cancel()
    advanceUntilIdle()

    assertTrue(job.isCancelled)
    assertTrue(job.isCompleted)
}

@Test
fun `cancel останавливает выполнение`() = runTest {
    var counter = 0

    val job = launch {
        repeat(10) {
            delay(100)
            counter++
        }
    }

    advanceTimeBy(250)
    assertEquals(2, counter)

    job.cancel()
    advanceUntilIdle()

    // Счетчик не доходит до 10
    assertTrue(counter < 10)
}
```

### Тестирование Кооперативной Отмены

Корутины должны "сотрудничать" с отменой: вызывать приостановленные функции или явно проверять состояние с помощью `isActive` / `ensureActive()`.

```kotlin
// Некооперативная корутина (ПЛОХО)
class NonCooperativeTask {
    suspend fun process(): Int {
        var result = 0
        repeat(1_000_000) {
            result += it // CPU-интенсивно, нет проверок отмены
        }
        return result
    }
}

@Test
fun `некооперативная корутина игнорирует запрос отмены`() = runTest {
    val task = NonCooperativeTask()
    var completed = false

    val job = launch {
        task.process()
        completed = true
    }

    // Запрашиваем отмену
    job.cancel()
    advanceUntilIdle()

    // Job переходит в состояние отмены, но работа могла выполниться до этого,
    // так как внутри нет точек кооперации
    assertTrue(job.isCancelled)
    // completed может быть как true, так и false в зависимости от того,
    // успела ли корутина завершиться до обработки отмены, поэтому на него не полагаемся
}

// Кооперативная корутина (ХОРОШО)
class CooperativeTask {
    suspend fun process(): Int = coroutineScope {
        var result = 0
        repeat(1_000_000) {
            ensureActive() // Проверка отмены
            result += it
        }
        result
    }
}

@Test
fun `кооперативная корутина корректно отменяется`() = runTest {
    val task = CooperativeTask()
    var completed = false

    val job = launch {
        try {
            task.process()
            completed = true
        } catch (e: CancellationException) {
            // Ожидается при отмене
        }
    }

    job.cancel()
    advanceUntilIdle()

    assertTrue(job.isCancelled)
    assertFalse(completed)
}
```

### Тестирование ensureActive

```kotlin
class DataProcessor {
    suspend fun processLargeDataset(data: List<Int>): List<Int> = coroutineScope {
        val results = mutableListOf<Int>()

        for (item in data) {
            ensureActive() // бросит, если корутина отменена
            results.add(processItem(item))
        }

        results
    }

    private fun processItem(item: Int): Int = item * 2
}

@Test
fun `ensureActive бросает при отмене`() = runTest {
    val processor = DataProcessor()
    val largeDataset = (1..10_000).toList()

    val job = launch {
        try {
            processor.processLargeDataset(largeDataset)
            fail("Должна была произойти отмена")
        } catch (e: CancellationException) {
            // ожидается
        }
    }

    advanceTimeBy(50)
    job.cancel()
    advanceUntilIdle()

    assertTrue(job.isCancelled)
}

@Test
fun `ensureActive позволяет завершиться без отмены`() = runTest {
    val processor = DataProcessor()
    val dataset = (1..100).toList()

    val result = processor.processLargeDataset(dataset)

    assertEquals(100, result.size)
    assertEquals(dataset.map { it * 2 }, result)
}
```

### Тестирование isActive

```kotlin
class FileProcessor {
    suspend fun processFiles(files: List<File>): Int = coroutineScope {
        var processed = 0

        for (file in files) {
            if (!isActive) break // проверка отмены

            processFile(file)
            processed++
        }

        processed
    }

    private suspend fun processFile(file: File) {
        delay(100)
    }
}

@Test
fun `isActive останавливает обработку при отмене`() = runTest {
    val processor = FileProcessor()
    val files = List(10) { File("file$it") }

    var result = 0

    val job = launch {
        result = processor.processFiles(files)
    }

    advanceTimeBy(350) // обработано 3 файла (виртуальное время)
    job.cancel()
    advanceUntilIdle()

    assertEquals(3, result)
}
```

### Тестирование CancellationException

```kotlin
@Test
fun `CancellationException выбрасывается при cancel`() = runTest {
    var exception: Throwable? = null

    val job = launch {
        try {
            delay(1000)
        } catch (e: CancellationException) {
            exception = e
            throw e // важно пробросить дальше
        }
    }

    advanceTimeBy(500)
    job.cancel("Test cancellation", TestException())
    advanceUntilIdle()

    assertNotNull(exception)
    assertTrue(exception is CancellationException)
    assertEquals("Test cancellation", exception?.message)
}

class TestException : Exception("Test")

@Test
fun `CancellationException не подавляется`() = runTest {
    var finalized = false

    val job = launch {
        try {
            delay(1000)
        } catch (e: CancellationException) {
            finalized = true
            throw e // MUST rethrow
        }
    }

    job.cancel()
    advanceUntilIdle()

    assertTrue(finalized)
    assertTrue(job.isCancelled)
}
```

### Тестирование Timeout

```kotlin
class SlowApi {
    suspend fun fetchData(): String {
        delay(5000)
        return "data"
    }
}

@Test
fun `timeout отменяет долгую операцию`() = runTest {
    val api = SlowApi()

    val result = try {
        withTimeout(1000) {
            api.fetchData()
        }
    } catch (e: TimeoutCancellationException) {
        null
    }

    assertNull(result)
}

@Test
fun `timeout успешен если операция успевает`() = runTest {
    val api = object {
        suspend fun fetchData(): String {
            delay(500)
            return "data"
        }
    }

    val result = withTimeout(1000) {
        api.fetchData()
    }

    assertEquals("data", result)
}

@Test
fun `withTimeoutOrNull возвращает null при таймауте`() = runTest {
    val result = withTimeoutOrNull(1000) {
        delay(2000)
        "completed"
    }

    assertNull(result)
}

@Test
fun `withTimeoutOrNull возвращает значение при успехе`() = runTest {
    val result = withTimeoutOrNull(1000) {
        delay(500)
        "completed"
    }

    assertEquals("completed", result)
}
```

### Тестирование Очистки Ресурсов

```kotlin
class DatabaseConnection : Closeable {
    var closed = false
    var transactionActive = false

    fun beginTransaction() {
        transactionActive = true
    }

    fun commit() {
        transactionActive = false
    }

    override fun close() {
        closed = true
    }
}

class DatabaseService {
    suspend fun performTransaction(connection: DatabaseConnection) {
        try {
            connection.beginTransaction()
            delay(1000) // имитация работы
            connection.commit()
        } finally {
            connection.close()
        }
    }
}

@Test
fun `ресурсы закрываются при отмене`() = runTest {
    val connection = DatabaseConnection()
    val service = DatabaseService()

    val job = launch {
        service.performTransaction(connection)
    }

    advanceTimeBy(500)
    job.cancel()
    advanceUntilIdle()

    // Соединение закрыто даже при отмене до commit
    assertTrue(connection.closed)
}

@Test
fun `use гарантирует очистку ресурсов`() = runTest {
    val connection = DatabaseConnection()

    val job = launch {
        connection.use {
            it.beginTransaction()
            delay(1000)
            it.commit()
        }
    }

    advanceTimeBy(500)
    job.cancel()
    advanceUntilIdle()

    assertTrue(connection.closed)
}
```

### Тестирование NonCancellable

```kotlin
class FileWriter {
    var fileOpen = false
    var bufferFlushed = false
    var fileClosed = false

    fun open() {
        fileOpen = true
    }

    suspend fun flush() {
        delay(100)
        bufferFlushed = true
    }

    suspend fun close() {
        delay(50)
        fileClosed = true
        fileOpen = false
    }
}

class FileService {
    suspend fun writeData(writer: FileWriter, data: String) {
        try {
            writer.open()
            delay(500) // запись данных
        } finally {
            withContext(NonCancellable) {
                writer.flush()
                writer.close()
            }
        }
    }
}

@Test
fun `NonCancellable позволяет завершить очистку`() = runTest {
    val writer = FileWriter()
    val service = FileService()

    val job = launch {
        service.writeData(writer, "test data")
    }

    advanceTimeBy(250)
    job.cancel()
    advanceUntilIdle()

    assertTrue(writer.bufferFlushed)
    assertTrue(writer.fileClosed)
    assertFalse(writer.fileOpen)
}

@Test
fun `очистка с NonCancellable занимает время`() = runTest {
    val writer = FileWriter()
    val service = FileService()

    val job = launch {
        service.writeData(writer, "test data")
    }

    advanceTimeBy(250)
    val cancelTime = currentTime
    job.cancel()
    advanceUntilIdle()
    val completeTime = currentTime

    val cleanupTime = completeTime - cancelTime
    assertEquals(150, cleanupTime)
}
```

### Тестирование Отмены Дочерних Корутин

```kotlin
@Test
fun `отмена родителя отменяет детей`() = runTest {
    val child1Cancelled = CompletableDeferred<Unit>()
    val child2Cancelled = CompletableDeferred<Unit>()

    val parent = launch {
        launch {
            try {
                delay(Long.MAX_VALUE)
            } catch (e: CancellationException) {
                child1Cancelled.complete(Unit)
                throw e
            }
        }

        launch {
            try {
                delay(Long.MAX_VALUE)
            } catch (e: CancellationException) {
                child2Cancelled.complete(Unit)
                throw e
            }
        }

        delay(Long.MAX_VALUE)
    }

    advanceTimeBy(100)
    parent.cancel()
    advanceUntilIdle()

    assertTrue(child1Cancelled.isCompleted)
    assertTrue(child2Cancelled.isCompleted)
    assertTrue(parent.isCancelled)
}

@Test
fun `с SupervisorJob сбой ребенка не отменяет сиблингов`() = runTest {
    val child1Completed = CompletableDeferred<Unit>()
    val child2Completed = CompletableDeferred<Unit>()

    supervisorScope {
        launch {
            try {
                delay(500)
                child1Completed.complete(Unit)
            } catch (e: CancellationException) {
                // не должно случиться
            }
        }

        launch {
            delay(100)
            throw IllegalStateException("Child 2 failed")
        }

        launch {
            delay(500)
            child2Completed.complete(Unit)
        }
    }

    assertTrue(child1Completed.isCompleted)
    assertTrue(child2Completed.isCompleted)
}
```

### Тестирование invokeOnCancellation

```kotlin
class ResourceManager {
    val releasedResources = mutableListOf<String>()

    suspend fun acquireResource(name: String) = suspendCancellableCoroutine<Unit> { continuation ->
        continuation.invokeOnCancellation {
            releasedResources.add(name)
        }
        continuation.resume(Unit)
    }
}

@Test
fun `invokeOnCancellation вызывается при отмене`() = runTest {
    val manager = ResourceManager()

    val job = launch {
        manager.acquireResource("Resource1")
        delay(1000)
    }

    advanceTimeBy(500)
    job.cancel()
    advanceUntilIdle()

    assertEquals(listOf("Resource1"), manager.releasedResources)
}

@Test
fun `invokeOnCancellation не вызывается при завершении`() = runTest {
    val manager = ResourceManager()

    val job = launch {
        manager.acquireResource("Resource1")
        delay(100)
    }

    advanceUntilIdle()

    assertTrue(manager.releasedResources.isEmpty())
}
```

### Тестирование Job.join И cancelAndJoin

```kotlin
@Test
fun `join ждет завершения`() = runTest {
    var completed = false

    val job = launch {
        delay(500)
        completed = true
    }

    assertFalse(completed)

    job.join()

    assertTrue(completed)
}

@Test
fun `cancelAndJoin отменяет и ждет очистку`() = runTest {
    var cleanedUp = false

    val job = launch {
        try {
            delay(1000)
        } finally {
            withContext(NonCancellable) {
                delay(200)
                cleanedUp = true
            }
        }
    }

    advanceTimeBy(500)

    val cancelTime = currentTime
    job.cancelAndJoin()
    val joinTime = currentTime

    assertTrue(job.isCancelled)
    assertTrue(cleanedUp)
    assertEquals(200, joinTime - cancelTime)
}
```

### Тестирование Structured Concurrency Cancellation

```kotlin
@Test
fun `coroutineScope отменяет всех детей при сбое одного`() = runTest {
    val task1Started = CompletableDeferred<Unit>()
    val task1Cancelled = CompletableDeferred<Unit>()
    val task2Started = CompletableDeferred<Unit>()
    val task2Cancelled = CompletableDeferred<Unit>()

    val result = try {
        coroutineScope {
            launch {
                task1Started.complete(Unit)
                try {
                    delay(Long.MAX_VALUE)
                } catch (e: CancellationException) {
                    task1Cancelled.complete(Unit)
                    throw e
                }
            }

            launch {
                task2Started.complete(Unit)
                delay(100)
                task2Cancelled.complete(Unit)
                throw IllegalStateException("Task 2 failed")
            }

            delay(Long.MAX_VALUE)
        }
        "completed"
    } catch (e: IllegalStateException) {
        "failed"
    }

    assertEquals("failed", result)
    assertTrue(task1Started.isCompleted)
    assertTrue(task1Cancelled.isCompleted)
    assertTrue(task2Started.isCompleted)
    assertTrue(task2Cancelled.isCompleted)
}

@Test
fun `supervisorScope не отменяет сиблингов при сбое одного`() = runTest {
    val task1Completed = CompletableDeferred<Unit>()
    val task2Failed = CompletableDeferred<Unit>()

    supervisorScope {
        launch {
            delay(500)
            task1Completed.complete(Unit)
        }

        launch {
            delay(100)
            task2Failed.complete(Unit)
            throw IllegalStateException("Task 2 failed")
        }
    }

    assertTrue(task1Completed.isCompleted)
    assertTrue(task2Failed.isCompleted)
}
```

### Тестирование Cancellation В `Flow`

```kotlin
@Test
fun `коллекция Flow может быть отменена`() = runTest {
    var emissionCount = 0

    val flow = flow {
        repeat(10) {
            delay(100)
            emissionCount++
            emit(it)
        }
    }

    val job = launch {
        flow.collect { }
    }

    advanceTimeBy(350)
    job.cancel()
    advanceUntilIdle()

    assertEquals(3, emissionCount)
}

@Test
fun `отмена коллектора отменяет upstream`() = runTest {
    var upstreamCancelled = false

    val flow = flow {
        try {
            repeat(10) {
                delay(100)
                emit(it)
            }
        } catch (e: CancellationException) {
            upstreamCancelled = true
            throw e
        }
    }

    val job = launch {
        flow.collect { }
    }

    advanceTimeBy(250)
    job.cancel()
    advanceUntilIdle()

    assertTrue(upstreamCancelled)
}

@Test
fun `onCompletion видит причину отмены`() = runTest {
    var cancellationDetected = false
    var cause: Throwable? = null

    val flow = flow {
        repeat(10) {
            delay(100)
            emit(it)
        }
    }.onCompletion { throwable ->
        cause = throwable
        cancellationDetected = throwable is CancellationException
    }

    val job = launch {
        flow.collect { }
    }

    advanceTimeBy(250)
    job.cancel()
    advanceUntilIdle()

    assertTrue(cancellationDetected)
    assertNotNull(cause)
}
```

### Лучшие Практики

```kotlin
//  DO: используйте ensureActive для CPU-интенсивной работы
suspend fun processData(data: List<Int>) = coroutineScope {
    data.map { item ->
        ensureActive()
        processItem(item)
    }
}

//  DON'T: игнорировать отмену
suspend fun badProcess(data: List<Int>) {
    data.forEach { item ->
        // нет проверки отмены
        processItem(item)
    }
}

//  DO: используйте NonCancellable для критичной очистки
try {
    // основная работа
} finally {
    withContext(NonCancellable) {
        cleanup()
    }
}

//  DON'T: подавлять CancellationException
try {
    delay(1000)
} catch (e: CancellationException) {
    // нельзя просто игнорировать
    throw e
}

//  DO: пробрасывать CancellationException после очистки
try {
    delay(1000)
} catch (e: CancellationException) {
    cleanup()
    throw e
}

//  DO: использовать use() для ресурсов
resource.use {
    // автоматическая очистка при отмене/ошибке
}

//  DO: тестировать тайминг отмены
@Test
fun testCancellationTiming() = runTest {
    val job = launch { /* ... */ }
    advanceTimeBy(500)
    job.cancel()
    advanceUntilIdle()
    assertTrue(job.isCancelled)
}
```

### Итог (RU)

Ключевые моменты:
- Кооперативная отмена: корутины должны проверять `isActive` или вызывать приостановленные функции.
- `ensureActive()`: выбрасывает `CancellationException`, если корутина отменена.
- `CancellationException`: после очистки должен быть проброшен дальше, не подавлять без необходимости.
- `NonCancellable`: используется для очистки, которая обязана завершиться даже после отмены.
- `invokeOnCancellation`: регистрирует колбэк очистки для пользовательских приостанавливаний.
- Отмена в `Flow`: важно проверять корректное завершение и отмену upstream-потока.

Стратегии тестирования:
- Проверяйте, что отмена своевременно останавливает работу кооперативного кода.
- Проверяйте, что ресурсы корректно очищаются при отмене (try/finally, `use`, `NonCancellable`).
- Проверяйте, что `CancellationException` корректно пробрасывается и не подавляется.
- Покрывайте сценарии таймаутов (`withTimeout`, `withTimeoutOrNull`).
- Тестируйте отмену дочерних корутин и поведение структурированной конкуренции.
- Используйте виртуальное время в `runTest` для детерминированного контроля таймингов.

Типичные ошибки:
- Отсутствие проверок отмены в CPU-интенсивных циклах.
- Подавление или игнорирование `CancellationException`.
- Неиспользование `NonCancellable` для критичной очистки.
- Непротестированная очистка ресурсов и сценарии отмены.

---

## Answer (EN)

Testing cancellation is critical to ensure proper resource cleanup and correct reaction to cancellation requests. In Kotlin coroutines, cancellation is cooperative, so you must test both timely stopping and proper cleanup.

All examples below assume `kotlinx-coroutines-test` with virtual time via `runTest`.

### Basic Cancellation Testing

```kotlin
@Test
fun `coroutine can be cancelled`() = runTest {
    val job = launch {
        repeat(1000) {
            delay(100)
            println("Working $it")
        }
    }

    advanceTimeBy(250) // let it run a bit (virtual time)
    assertTrue(job.isActive)

    job.cancel()
    advanceUntilIdle()

    assertTrue(job.isCancelled)
    assertTrue(job.isCompleted)
}

@Test
fun `cancel stops execution`() = runTest {
    var counter = 0

    val job = launch {
        repeat(10) {
            delay(100)
            counter++
        }
    }

    advanceTimeBy(250)
    assertEquals(2, counter)

    job.cancel()
    advanceUntilIdle()

    // Counter never reaches 10
    assertTrue(counter < 10)
}
```

### Testing Cooperative Cancellation

Coroutines should cooperate with cancellation by invoking suspending functions or explicitly checking `isActive` / `ensureActive()`.

```kotlin
// Non-cooperative coroutine (BAD)
class NonCooperativeTask {
    suspend fun process(): Int {
        var result = 0
        repeat(1_000_000) {
            result += it // CPU-intensive, no cancellation checks
        }
        return result
    }
}

@Test
fun `non-cooperative coroutine ignores cancellation`() = runTest {
    val task = NonCooperativeTask()
    var completed = false

    val job = launch {
        task.process()
        completed = true
    }

    job.cancel()
    advanceUntilIdle()

    assertTrue(job.isCancelled)
    // `completed` may or may not be true; we don't assert on it
}

// Cooperative coroutine (GOOD)
class CooperativeTask {
    suspend fun process(): Int = coroutineScope {
        var result = 0
        repeat(1_000_000) {
            ensureActive() // cancellation check
            result += it
        }
        result
    }
}

@Test
fun `cooperative coroutine cancels correctly`() = runTest {
    val task = CooperativeTask()
    var completed = false

    val job = launch {
        try {
            task.process()
            completed = true
        } catch (e: CancellationException) {
            // expected on cancellation
        }
    }

    job.cancel()
    advanceUntilIdle()

    assertTrue(job.isCancelled)
    assertFalse(completed)
}
```

### Testing ensureActive

```kotlin
class DataProcessor {
    suspend fun processLargeDataset(data: List<Int>): List<Int> = coroutineScope {
        val results = mutableListOf<Int>()

        for (item in data) {
            ensureActive() // throws if cancelled
            results.add(processItem(item))
        }

        results
    }

    private fun processItem(item: Int): Int = item * 2
}

@Test
fun `ensureActive throws on cancellation`() = runTest {
    val processor = DataProcessor()
    val largeDataset = (1..10_000).toList()

    val job = launch {
        try {
            processor.processLargeDataset(largeDataset)
            fail("Cancellation expected")
        } catch (e: CancellationException) {
            // expected
        }
    }

    advanceTimeBy(50)
    job.cancel()
    advanceUntilIdle()

    assertTrue(job.isCancelled)
}

@Test
fun `ensureActive allows completion when not cancelled`() = runTest {
    val processor = DataProcessor()
    val dataset = (1..100).toList()

    val result = processor.processLargeDataset(dataset)

    assertEquals(100, result.size)
    assertEquals(dataset.map { it * 2 }, result)
}
```

### Testing isActive

```kotlin
class FileProcessor {
    suspend fun processFiles(files: List<File>): Int = coroutineScope {
        var processed = 0

        for (file in files) {
            if (!isActive) break // cancellation check

            processFile(file)
            processed++
        }

        processed
    }

    private suspend fun processFile(file: File) {
        delay(100)
    }
}

@Test
fun `isActive stops processing on cancellation`() = runTest {
    val processor = FileProcessor()
    val files = List(10) { File("file$it") }

    var result = 0

    val job = launch {
        result = processor.processFiles(files)
    }

    advanceTimeBy(350)
    job.cancel()
    advanceUntilIdle()

    assertEquals(3, result)
}
```

### Testing CancellationException

```kotlin
@Test
fun `CancellationException is thrown on cancel`() = runTest {
    var exception: Throwable? = null

    val job = launch {
        try {
            delay(1000)
        } catch (e: CancellationException) {
            exception = e
            throw e // rethrow is important
        }
    }

    advanceTimeBy(500)
    job.cancel("Test cancellation", TestException())
    advanceUntilIdle()

    assertNotNull(exception)
    assertTrue(exception is CancellationException)
    assertEquals("Test cancellation", exception?.message)
}

class TestException : Exception("Test")

@Test
fun `CancellationException is not swallowed`() = runTest {
    var finalized = false

    val job = launch {
        try {
            delay(1000)
        } catch (e: CancellationException) {
            finalized = true
            throw e // MUST rethrow
        }
    }

    job.cancel()
    advanceUntilIdle()

    assertTrue(finalized)
    assertTrue(job.isCancelled)
}
```

### Testing Timeout

```kotlin
class SlowApi {
    suspend fun fetchData(): String {
        delay(5000)
        return "data"
    }
}

@Test
fun `timeout cancels long-running operation`() = runTest {
    val api = SlowApi()

    val result = try {
        withTimeout(1000) {
            api.fetchData()
        }
    } catch (e: TimeoutCancellationException) {
        null
    }

    assertNull(result)
}

@Test
fun `timeout succeeds when operation fits limit`() = runTest {
    val api = object {
        suspend fun fetchData(): String {
            delay(500)
            return "data"
        }
    }

    val result = withTimeout(1000) {
        api.fetchData()
    }

    assertEquals("data", result)
}

@Test
fun `withTimeoutOrNull returns null on timeout`() = runTest {
    val result = withTimeoutOrNull(1000) {
        delay(2000)
        "completed"
    }

    assertNull(result)
}

@Test
fun `withTimeoutOrNull returns value on success`() = runTest {
    val result = withTimeoutOrNull(1000) {
        delay(500)
        "completed"
    }

    assertEquals("completed", result)
}
```

### Testing Resource Cleanup

```kotlin
class DatabaseConnection : Closeable {
    var closed = false
    var transactionActive = false

    fun beginTransaction() {
        transactionActive = true
    }

    fun commit() {
        transactionActive = false
    }

    override fun close() {
        closed = true
    }
}

class DatabaseService {
    suspend fun performTransaction(connection: DatabaseConnection) {
        try {
            connection.beginTransaction()
            delay(1000)
            connection.commit()
        } finally {
            connection.close()
        }
    }
}

@Test
fun `resources are closed on cancellation`() = runTest {
    val connection = DatabaseConnection()
    val service = DatabaseService()

    val job = launch {
        service.performTransaction(connection)
    }

    advanceTimeBy(500)
    job.cancel()
    advanceUntilIdle()

    assertTrue(connection.closed)
}

@Test
fun `use ensures resource cleanup`() = runTest {
    val connection = DatabaseConnection()

    val job = launch {
        connection.use {
            it.beginTransaction()
            delay(1000)
            it.commit()
        }
    }

    advanceTimeBy(500)
    job.cancel()
    advanceUntilIdle()

    assertTrue(connection.closed)
}
```

### Testing NonCancellable

```kotlin
class FileWriter {
    var fileOpen = false
    var bufferFlushed = false
    var fileClosed = false

    fun open() {
        fileOpen = true
    }

    suspend fun flush() {
        delay(100)
        bufferFlushed = true
    }

    suspend fun close() {
        delay(50)
        fileClosed = true
        fileOpen = false
    }
}

class FileService {
    suspend fun writeData(writer: FileWriter, data: String) {
        try {
            writer.open()
            delay(500)
        } finally {
            withContext(NonCancellable) {
                writer.flush()
                writer.close()
            }
        }
    }
}

@Test
fun `NonCancellable completes cleanup after cancellation`() = runTest {
    val writer = FileWriter()
    val service = FileService()

    val job = launch {
        service.writeData(writer, "test data")
    }

    advanceTimeBy(250)
    job.cancel()
    advanceUntilIdle()

    assertTrue(writer.bufferFlushed)
    assertTrue(writer.fileClosed)
    assertFalse(writer.fileOpen)
}

@Test
fun `NonCancellable cleanup takes expected time`() = runTest {
    val writer = FileWriter()
    val service = FileService()

    val job = launch {
        service.writeData(writer, "test data")
    }

    advanceTimeBy(250)
    val cancelTime = currentTime
    job.cancel()
    advanceUntilIdle()
    val completeTime = currentTime

    val cleanupTime = completeTime - cancelTime
    assertEquals(150, cleanupTime)
}
```

### Testing Child Coroutine Cancellation

```kotlin
@Test
fun `cancelling parent cancels children`() = runTest {
    val child1Cancelled = CompletableDeferred<Unit>()
    val child2Cancelled = CompletableDeferred<Unit>()

    val parent = launch {
        launch {
            try {
                delay(Long.MAX_VALUE)
            } catch (e: CancellationException) {
                child1Cancelled.complete(Unit)
                throw e
            }
        }

        launch {
            try {
                delay(Long.MAX_VALUE)
            } catch (e: CancellationException) {
                child2Cancelled.complete(Unit)
                throw e
            }
        }

        delay(Long.MAX_VALUE)
    }

    advanceTimeBy(100)
    parent.cancel()
    advanceUntilIdle()

    assertTrue(child1Cancelled.isCompleted)
    assertTrue(child2Cancelled.isCompleted)
    assertTrue(parent.isCancelled)
}

@Test
fun `SupervisorJob child failure does not cancel siblings`() = runTest {
    val child1Completed = CompletableDeferred<Unit>()
    val child2Completed = CompletableDeferred<Unit>()

    supervisorScope {
        launch {
            try {
                delay(500)
                child1Completed.complete(Unit)
            } catch (e: CancellationException) {
                // should not happen
            }
        }

        launch {
            delay(100)
            throw IllegalStateException("Child 2 failed")
        }

        launch {
            delay(500)
            child2Completed.complete(Unit)
        }
    }

    assertTrue(child1Completed.isCompleted)
    assertTrue(child2Completed.isCompleted)
}
```

### Testing invokeOnCancellation

```kotlin
class ResourceManager {
    val releasedResources = mutableListOf<String>()

    suspend fun acquireResource(name: String) = suspendCancellableCoroutine<Unit> { continuation ->
        continuation.invokeOnCancellation {
            releasedResources.add(name)
        }
        continuation.resume(Unit)
    }
}

@Test
fun `invokeOnCancellation called on cancellation`() = runTest {
    val manager = ResourceManager()

    val job = launch {
        manager.acquireResource("Resource1")
        delay(1000)
    }

    advanceTimeBy(500)
    job.cancel()
    advanceUntilIdle()

    assertEquals(listOf("Resource1"), manager.releasedResources)
}

@Test
fun `invokeOnCancellation not called on normal completion`() = runTest {
    val manager = ResourceManager()

    val job = launch {
        manager.acquireResource("Resource1")
        delay(100)
    }

    advanceUntilIdle()

    assertTrue(manager.releasedResources.isEmpty())
}
```

### Testing Job.join and cancelAndJoin

```kotlin
@Test
fun `join waits for completion`() = runTest {
    var completed = false

    val job = launch {
        delay(500)
        completed = true
    }

    assertFalse(completed)

    job.join()

    assertTrue(completed)
}

@Test
fun `cancelAndJoin cancels and waits for cleanup`() = runTest {
    var cleanedUp = false

    val job = launch {
        try {
            delay(1000)
        } finally {
            withContext(NonCancellable) {
                delay(200)
                cleanedUp = true
            }
        }
    }

    advanceTimeBy(500)

    val cancelTime = currentTime
    job.cancelAndJoin()
    val joinTime = currentTime

    assertTrue(job.isCancelled)
    assertTrue(cleanedUp)
    assertEquals(200, joinTime - cancelTime)
}
```

### Testing Structured Concurrency Cancellation

```kotlin
@Test
fun `coroutineScope cancels all children on failure`() = runTest {
    val task1Started = CompletableDeferred<Unit>()
    val task1Cancelled = CompletableDeferred<Unit>()
    val task2Started = CompletableDeferred<Unit>()
    val task2Cancelled = CompletableDeferred<Unit>()

    val result = try {
        coroutineScope {
            launch {
                task1Started.complete(Unit)
                try {
                    delay(Long.MAX_VALUE)
                } catch (e: CancellationException) {
                    task1Cancelled.complete(Unit)
                    throw e
                }
            }

            launch {
                task2Started.complete(Unit)
                delay(100)
                task2Cancelled.complete(Unit)
                throw IllegalStateException("Task 2 failed")
            }

            delay(Long.MAX_VALUE)
        }
        "completed"
    } catch (e: IllegalStateException) {
        "failed"
    }

    assertEquals("failed", result)
    assertTrue(task1Started.isCompleted)
    assertTrue(task1Cancelled.isCompleted)
    assertTrue(task2Started.isCompleted)
    assertTrue(task2Cancelled.isCompleted)
}

@Test
fun `supervisorScope does not cancel siblings on failure`() = runTest {
    val task1Completed = CompletableDeferred<Unit>()
    val task2Failed = CompletableDeferred<Unit>()

    supervisorScope {
        launch {
            delay(500)
            task1Completed.complete(Unit)
        }

        launch {
            delay(100)
            task2Failed.complete(Unit)
            throw IllegalStateException("Task 2 failed")
        }
    }

    assertTrue(task1Completed.isCompleted)
    assertTrue(task2Failed.isCompleted)
}
```

### Testing Cancellation in `Flow`

```kotlin
@Test
fun `Flow collection can be cancelled`() = runTest {
    var emissionCount = 0

    val flow = flow {
        repeat(10) {
            delay(100)
            emissionCount++
            emit(it)
        }
    }

    val job = launch {
        flow.collect { }
    }

    advanceTimeBy(350)
    job.cancel()
    advanceUntilIdle()

    assertEquals(3, emissionCount)
}

@Test
fun `cancelling collector cancels upstream`() = runTest {
    var upstreamCancelled = false

    val flow = flow {
        try {
            repeat(10) {
                delay(100)
                emit(it)
            }
        } catch (e: CancellationException) {
            upstreamCancelled = true
            throw e
        }
    }

    val job = launch {
        flow.collect { }
    }

    advanceTimeBy(250)
    job.cancel()
    advanceUntilIdle()

    assertTrue(upstreamCancelled)
}

@Test
fun `onCompletion observes cancellation cause`() = runTest {
    var cancellationDetected = false
    var cause: Throwable? = null

    val flow = flow {
        repeat(10) {
            delay(100)
            emit(it)
        }
    }.onCompletion { throwable ->
        cause = throwable
        cancellationDetected = throwable is CancellationException
    }

    val job = launch {
        flow.collect { }
    }

    advanceTimeBy(250)
    job.cancel()
    advanceUntilIdle()

    assertTrue(cancellationDetected)
    assertNotNull(cause)
}
```

### Best Practices (EN)

```kotlin
// DO: use ensureActive for CPU-intensive work
suspend fun processData(data: List<Int>) = coroutineScope {
    data.map { item ->
        ensureActive()
        processItem(item)
    }
}

// DON'T: ignore cancellation
suspend fun badProcess(data: List<Int>) {
    data.forEach { item ->
        // no cancellation check
        processItem(item)
    }
}

// DO: use NonCancellable for critical cleanup
try {
    // main work
} finally {
    withContext(NonCancellable) {
        cleanup()
    }
}

// DON'T: swallow CancellationException
try {
    delay(1000)
} catch (e: CancellationException) {
    // must not ignore
    throw e
}

// DO: rethrow CancellationException after cleanup
try {
    delay(1000)
} catch (e: CancellationException) {
    cleanup()
    throw e
}

// DO: use use() for resources
resource.use {
    // automatic cleanup on cancel/error
}

// DO: test cancellation timing
@Test
fun testCancellationTiming() = runTest {
    val job = launch { /* ... */ }
    advanceTimeBy(500)
    job.cancel()
    advanceUntilIdle()
    assertTrue(job.isCancelled)
}
```

### Summary (EN)

Key points:
- Cooperative cancellation: coroutines should check `isActive` or call suspending functions.
- `ensureActive()`: throws `CancellationException` when the coroutine is cancelled.
- `CancellationException`: should be rethrown after cleanup; avoid suppressing it.
- `NonCancellable`: use it for cleanup that must complete even after cancellation.
- `invokeOnCancellation`: registers cleanup callbacks for custom suspensions.
- Cancellation in `Flow`: verify correct termination and upstream cancellation.

Testing strategies:
- Assert that cancellation stops cooperative work promptly.
- Assert that resources are cleaned up on cancellation (`try/finally`, `use`, `NonCancellable`).
- Assert that `CancellationException` is propagated, not swallowed.
- Cover timeout scenarios (`withTimeout`, `withTimeoutOrNull`).
- Test child coroutine cancellation and structured concurrency behavior.
- Use virtual time in `runTest` for deterministic control of timing.

Typical mistakes:
- Missing cancellation checks in CPU-intensive loops.
- Swallowing or ignoring `CancellationException`.
- Not using `NonCancellable` for critical cleanup.
- Not testing resource cleanup and cancellation scenarios thoroughly.

## Дополнительные Вопросы (RU)

- Как протестировать взаимодействие `withTimeout` с несколькими вложенными корутинами?
- Как убедиться, что пользовательские операции на основе `suspendCancellableCoroutine` корректно обрабатывают отмену?
- Как тестировать поведение `Flow`, когда отмена происходит одновременно с выбросом исключения?

## Follow-ups

- How to test interaction of `withTimeout` with multiple nested coroutines?
- How to ensure custom `suspendCancellableCoroutine`-based operations handle cancellation correctly?
- How to test `Flow` behavior when cancellation happens concurrently with an exception being thrown?

## Ссылки (RU)

- [[c-coroutines]]

## References

- [[c-coroutines]]

## Связанные Вопросы (RU)

- [[q-coroutine-cancellation-cooperation--kotlin--medium]]
- [[q-coroutine-cancellation-mechanisms--kotlin--medium]]
- [[q-testing-coroutines-runtest--kotlin--medium]]

## Related Questions

- [[q-coroutine-cancellation-cooperation--kotlin--medium]]
- [[q-coroutine-cancellation-mechanisms--kotlin--medium]]
- [[q-testing-coroutines-runtest--kotlin--medium]]
