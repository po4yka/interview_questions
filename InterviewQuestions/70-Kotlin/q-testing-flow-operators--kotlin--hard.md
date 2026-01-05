---
id: kotlin-082
title: "Testing Flow Operators and Transformations / Тестирование операторов и трансформаций Flow"
aliases: ["Testing Flow Operators and Transformations", "Тестирование операторов и трансформаций Flow"]

# Classification
topic: kotlin
subtopics: [coroutines, flow, operators]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Advanced Flow Testing Techniques

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-flow, c-testing, q-flow-operators-deep-dive--kotlin--hard, q-testing-coroutines-runtest--kotlin--medium, q-testing-stateflow-sharedflow--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-11-09

tags: [coroutines, difficulty/hard, flow, kotlin, operators, testing]
---
# Вопрос (RU)
> Как тестировать операторы и трансформации `Flow` такие как `flatMap`, `debounce`, `retry` и `combine`? Покрыть тестирование виртуального времени, использование Turbine и стратегии тестирования сложных цепочек `Flow`.

---

# Question (EN)
> How to test `Flow` operators and transformations like `flatMap`, `debounce`, `retry`, and `combine`? Cover virtual time testing, Turbine usage, and complex `Flow` chain testing strategies.

## Ответ (RU)

Тестирование операторов `Flow` требует глубокого понимания их семантики: холодность и ленивость потоков, асинхронность, реактивность, отмена, обработка ошибок и то, как отдельные операторы трансформируют поток данных и взаимодействуют друг с другом. Для операторов, зависящих от времени (`debounce`, `sample`, пользовательские throttle-операторы, `retry` с задержками), критично использовать виртуальное время (`runTest`, `advanceTimeBy`, `currentTime` тестового скоупа или шедулера) и не полагаться на реальные часы (`System.currentTimeMillis()`), иначе тесты будут медленными и нестабильными.

Ниже приведены ключевые шаблоны тестирования операторов `Flow` с использованием библиотеки Turbine и виртуального времени. Примеры кода идентичны английской версии; комментарии и пояснения локализованы.

### Тестирование Базовых Трансформаций

#### `map` И `filter`

```kotlin
class DataProcessor {
    fun processNumbers(input: Flow<Int>): Flow<String> = input
        .filter { it > 0 }
        .map { "Number: $it" }
}

@Test
fun `map and filter transform data correctly`() = runTest {
    val processor = DataProcessor()
    val input = flowOf(-1, 0, 1, 2, 3, -5, 10)

    val result = processor.processNumbers(input).toList()

    assertEquals(
        listOf("Number: 1", "Number: 2", "Number: 3", "Number: 10"),
        result
    )
}

// Тот же тест с Turbine
@Test
fun `map and filter with turbine`() = runTest {
    val processor = DataProcessor()
    val input = flowOf(0, 5, -3, 10)

    processor.processNumbers(input).test {
        assertEquals("Number: 5", awaitItem())
        assertEquals("Number: 10", awaitItem())
        awaitComplete()
    }
}
```

#### `transform`

```kotlin
fun Flow<Int>.duplicateEach(): Flow<Int> = transform { value ->
    emit(value)
    emit(value)
}

@Test
fun `transform emits multiple values per input`() = runTest {
    val input = flowOf(1, 2, 3)

    input.duplicateEach().test {
        assertEquals(1, awaitItem())
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())
        assertEquals(2, awaitItem())
        assertEquals(3, awaitItem())
        assertEquals(3, awaitItem())
        awaitComplete()
    }
}

fun Flow<String>.splitWords(): Flow<String> = transform { sentence ->
    sentence.split(" ").forEach { word ->
        emit(word)
    }
}

@Test
fun `splitWords emits each word separately`() = runTest {
    val input = flowOf("Hello world", "Kotlin Flow")

    input.splitWords().test {
        assertEquals("Hello", awaitItem())
        assertEquals("world", awaitItem())
        assertEquals("Kotlin", awaitItem())
        assertEquals("Flow", awaitItem())
        awaitComplete()
    }
}
```

### Тестирование Операторов Времени

#### `debounce`

```kotlin
class SearchQueryProcessor {
    fun debounceQueries(queries: Flow<String>, timeoutMs: Long = 300): Flow<String> =
        queries.debounce(timeoutMs)
}

@Test
fun `debounce emits only after quiet period`() = runTest {
    val processor = SearchQueryProcessor()

    val queries = flow {
        emit("a")
        delay(100)
        emit("ab")
        delay(100)
        emit("abc")
        delay(100)
        emit("abcd")
        delay(400) // Дольше, чем debounce timeout
        emit("abcde")
        delay(400)
    }

    processor.debounceQueries(queries, 300).test {
        // Первые 4 эмиссии находятся в одном окне, в итоге придёт только "abcd"
        assertEquals("abcd", awaitItem())

        // Последняя эмиссия после тихого периода
        assertEquals("abcde", awaitItem())

        awaitComplete()
    }
}

@Test
fun `debounce cancels rapid emissions`() = runTest {
    val rapidFlow = flow {
        repeat(10) {
            emit("query$it")
            delay(50)
        }
        delay(400)
    }

    rapidFlow.debounce(300).test {
        // Ожидаем только последнюю эмиссию
        assertEquals("query9", awaitItem())
        awaitComplete()
    }
}

@Test
fun `debounce with virtual time`() = runTest {
    val queries = flow {
        emit("a")
        delay(100)
        emit("b")
        delay(100)
        emit("c")
        delay(500)
    }

    val result = mutableListOf<String>()
    val job = launch {
        queries.debounce(300).collect { result.add(it) }
    }

    advanceTimeBy(200)
    assertTrue(result.isEmpty())

    advanceTimeBy(200)
    assertTrue(result.isEmpty())

    advanceTimeBy(300)
    assertEquals(listOf("c"), result)

    job.cancel()
}
```

#### `sample`

```kotlin
@Test
fun `sample emits latest value at intervals with virtual time`() = runTest {
    val source = flow {
        repeat(10) {
            emit(it)
            delay(50)
        }
    }

    val collected = mutableListOf<Int>()
    val job = launch {
        source.sample(150).collect { collected.add(it) }
    }

    advanceTimeBy(1000)
    job.cancel()

    assertTrue(collected.isNotEmpty())
}
```

#### Пользовательский Throttle (`throttleFirst`)

Для собственных операторов, зависящих от времени, используйте виртуальное время тест-диспетчера, а не реальные часы. При этом логика оператора не должна напрямую ссылаться на тестовые API — вместо этого прокидывайте абстракцию времени при необходимости.

```kotlin
// Пример throttleFirst, опирающийся на виртуальное время TestScope
fun <T> Flow<T>.throttleFirst(windowDuration: Long): Flow<T> = flow {
    require(windowDuration > 0)
    var lastEmissionTime = Long.MIN_VALUE
    collect { value ->
        // В тестах этот flow должен запускаться внутри runTest,
        // текущие значения времени контролируются тестовым шедулером.
        val time = coroutineContext[TestCoroutineScheduler]?.currentTime ?: 0L
        if (time - lastEmissionTime >= windowDuration) {
            lastEmissionTime = time
            emit(value)
        }
    }
}

@Test
fun `throttleFirst emits first value in window`() = runTest {
    val emissions = flow {
        emit(1)
        delay(100)
        emit(2)
        delay(100)
        emit(3)
        delay(300)
        emit(4)
        delay(100)
        emit(5)
    }

    emissions.throttleFirst(250).test {
        assertEquals(1, awaitItem())
        assertEquals(4, awaitItem())
        awaitComplete()
    }
}
```

### Тестирование flatMap-вариантов

#### `flatMapConcat`

```kotlin
class User(val id: Int, val name: String)

class UserRepository {
    fun getUserIds(): Flow<Int> = flow {
        emit(1)
        delay(100)
        emit(2)
        delay(100)
        emit(3)
    }

    fun getUserDetails(id: Int): Flow<User> = flow {
        delay(200)
        emit(User(id, "User $id"))
    }
}

@Test
fun `flatMapConcat processes sequentially`() = runTest {
    val repo = UserRepository()

    val result = repo.getUserIds()
        .flatMapConcat { id -> repo.getUserDetails(id) }
        .toList()

    assertEquals(listOf(1, 2, 3), result.map { it.id })
}

@Test
fun `flatMapConcat preserves order`() = runTest {
    val input = flowOf(3, 1, 2)

    input.flatMapConcat { value ->
        flow {
            delay(100)
            emit(value)
        }
    }.test {
        assertEquals(3, awaitItem())
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())
        awaitComplete()
    }
}
```

#### `flatMapMerge`

```kotlin
@Test
fun `flatMapMerge processes concurrently`() = runTest {
    val repo = UserRepository()

    val users = repo.getUserIds()
        .flatMapMerge(concurrency = 3) { id -> repo.getUserDetails(id) }
        .toList()

    val ids = users.map { it.id }.sorted()
    assertEquals(listOf(1, 2, 3), ids)
}

@Test
fun `flatMapMerge respects concurrency limit`() = runTest {
    var concurrentTasks = 0
    var maxConcurrentTasks = 0

    val input = flowOf(1, 2, 3, 4, 5)

    input.flatMapMerge(concurrency = 2) { value ->
        flow {
            concurrentTasks++
            maxConcurrentTasks = maxOf(maxConcurrentTasks, concurrentTasks)

            delay(100)
            emit(value)

            concurrentTasks--
        }
    }.test {
        repeat(5) { awaitItem() }
        awaitComplete()
    }

    assertEquals(2, maxConcurrentTasks)
}
```

#### `flatMapLatest`

```kotlin
@Test
fun `flatMapLatest cancels previous flow`() = runTest {
    val cancelledIds = mutableListOf<Int>()

    val queries = flow {
        emit(1)
        delay(100)
        emit(2)
        delay(100)
        emit(3)
        delay(500)
    }

    queries.flatMapLatest { id ->
        flow {
            try {
                delay(300)
                emit("Result for $id")
            } catch (e: CancellationException) {
                cancelledIds.add(id)
                throw e
            }
        }
    }.test {
        assertEquals("Result for 3", awaitItem())
        awaitComplete()
    }

    assertEquals(listOf(1, 2), cancelledIds)
}

@Test
fun `flatMapLatest for search`() = runTest {
    fun searchApi(query: String): Flow<List<String>> = flow {
        delay(200)
        emit(listOf("$query result 1", "$query result 2"))
    }

    val searches = flow {
        emit("a")
        delay(50)
        emit("ab")
        delay(50)
        emit("abc")
        delay(300)
    }

    searches.flatMapLatest { query -> searchApi(query) }
        .test {
            val results = awaitItem()
            assertEquals(2, results.size)
            assertTrue(results[0].startsWith("abc"))

            awaitComplete()
        }
}
```

### Тестирование `combine` И `zip`

#### `combine`

```kotlin
@Test
fun `combine emits when any flow emits`() = runTest {
    val flow1 = flow {
        emit(1)
        delay(100)
        emit(2)
        delay(100)
        emit(3)
    }

    val flow2 = flow {
        emit("A")
        delay(150)
        emit("B")
    }

    combine(flow1, flow2) { num, letter -> "$num$letter" }
        .test {
            assertEquals("1A", awaitItem())
            assertEquals("2A", awaitItem())
            assertEquals("2B", awaitItem())
            assertEquals("3B", awaitItem())
            awaitComplete()
        }
}

@Test
fun `combine with 3 flows produces combined values`() = runTest {
    val ints = flowOf(1, 2, 3)
    val strings = flowOf("A", "B")
    val booleans = flowOf(true, false)

    combine(ints, strings, booleans) { i, s, b -> "$i-$s-$b" }
        .test {
            assertEquals("1-A-true", awaitItem())
            assertEquals("2-B-false", awaitItem())
            awaitComplete()
        }
}
```

#### `zip`

```kotlin
@Test
fun `zip pairs corresponding elements`() = runTest {
    val numbers = flowOf(1, 2, 3, 4)
    val letters = flowOf("A", "B", "C")

    numbers.zip(letters) { num, letter -> "$num$letter" }
        .test {
            assertEquals("1A", awaitItem())
            assertEquals("2B", awaitItem())
            assertEquals("3C", awaitItem())
            awaitComplete()
        }
}

@Test
fun `zip waits for both flows`() = runTest {
    val slow = flow {
        delay(200)
        emit(1)
        delay(200)
        emit(2)
    }

    val fast = flow {
        emit("A")
        delay(50)
        emit("B")
    }

    val startTime = currentTime

    slow.zip(fast) { num, letter -> "$num$letter" }
        .test {
            val first = awaitItem()
            assertEquals("1A", first)
            assertTrue(currentTime - startTime >= 200)

            val second = awaitItem()
            assertEquals("2B", second)
            assertTrue(currentTime - startTime >= 400)

            awaitComplete()
        }
}
```

### Тестирование Операторов Обработки Ошибок

#### `catch`

```kotlin
class DataSource {
    fun fetchData(): Flow<Int> = flow {
        emit(1)
        emit(2)
        throw IOException("Network error")
    }
}

@Test
fun `catch handles exceptions`() = runTest {
    val dataSource = DataSource()

    dataSource.fetchData()
        .catch { e -> emit(-1) }
        .test {
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            assertEquals(-1, awaitItem())
            awaitComplete()
        }
}

@Test
fun `catch can emit multiple fallback values`() = runTest {
    flowOf(1, 2, 3)
        .map {
            if (it == 2) throw IllegalStateException("Error at 2")
            it
        }
        .catch {
            emit(-1)
            emit(-2)
        }
        .test {
            assertEquals(1, awaitItem())
            assertEquals(-1, awaitItem())
            assertEquals(-2, awaitItem())
            awaitComplete()
        }
}

@Test
fun `catch does not handle downstream exceptions`() = runTest {
    flowOf(1, 2, 3)
        .catch { emit(-1) }
        .map {
            if (it == 2) throw IllegalStateException("Downstream error")
            it
        }
        .test {
            assertEquals(1, awaitItem())
            awaitError()
        }
}
```

#### `retry` И `retryWhen`

```kotlin
@Test
fun `retry attempts operation multiple times`() = runTest {
    var attempts = 0

    flow {
        attempts++
        emit(1)
        if (attempts < 3) {
            throw IOException("Attempt $attempts failed")
        }
        emit(2)
    }
        .retry(2)
        .test {
            assertEquals(1, awaitItem())
            assertEquals(1, awaitItem())
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            awaitComplete()
        }

    assertEquals(3, attempts)
}

@Test
fun `retry fails after max attempts`() = runTest {
    var attempts = 0

    flow {
        attempts++
        throw IOException("Attempt $attempts")
    }
        .retry(2)
        .test {
            val error = awaitError()
            assertTrue(error is IOException)
            assertEquals("Attempt 3", error.message)
        }

    assertEquals(3, attempts)
}

@Test
fun `retryWhen with custom logic`() = runTest {
    var attempts = 0

    flow {
        attempts++
        emit(attempts)
        throw IOException("Network error")
    }
        .retryWhen { cause, attempt ->
            cause is IOException && attempt < 3
        }
        .test {
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            assertEquals(3, awaitItem())
            awaitError()
        }

    assertEquals(4, attempts)
}

@Test
fun `retryWhen with exponential backoff tracked via delays list`() = runTest {
    val delays = mutableListOf<Long>()
    var attempts = 0

    flow {
        attempts++
        emit(attempts)
        throw IOException("Error")
    }
        .retryWhen { cause, attempt ->
            if (cause is IOException && attempt < 3) {
                val delayMs = (1000 * (1 shl attempt.toInt())).toLong()
                delays.add(delayMs)
                delay(delayMs)
                true
            } else {
                false
            }
        }
        .catch { }
        .toList()

    assertEquals(listOf(1000L, 2000L, 4000L), delays)
    assertEquals(4, attempts)
}
```

### Тестирование `onEach` И `onStart`/`onCompletion`

```kotlin
@Test
fun `onEach executes side effects`() = runTest {
    val sideEffects = mutableListOf<Int>()

    flowOf(1, 2, 3)
        .onEach { sideEffects.add(it) }
        .test {
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            assertEquals(3, awaitItem())
            awaitComplete()
        }

    assertEquals(listOf(1, 2, 3), sideEffects)
}

@Test
fun `onStart emits before upstream`() = runTest {
    flowOf(1, 2, 3)
        .onStart { emit(0) }
        .test {
            assertEquals(0, awaitItem())
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            assertEquals(3, awaitItem())
            awaitComplete()
        }
}

@Test
fun `onCompletion executes after completion`() = runTest {
    var completed = false

    flowOf(1, 2, 3)
        .onCompletion { completed = true }
        .test {
            assertFalse(completed)
            awaitItem()
            awaitItem()
            awaitItem()
            awaitComplete()
            assertTrue(completed)
        }
}

@Test
fun `onCompletion with exception`() = runTest {
    var completionCause: Throwable? = null

    flow {
        emit(1)
        throw IOException("Error")
    }
        .onCompletion { cause -> completionCause = cause }
        .test {
            assertEquals(1, awaitItem())
            val error = awaitError()
            assertTrue(error is IOException)
            assertNotNull(completionCause)
            assertTrue(completionCause is IOException)
        }
}
```

### Тестирование `buffer` И `conflate`

```kotlin
@Test
fun `buffer allows parallel processing`() = runTest {
    val processingTimes = mutableListOf<Long>()

    flow {
        repeat(3) { emit(it) }
    }
        .onEach { delay(100) }
        .buffer(2)
        .map {
            val start = currentTime
            delay(200)
            processingTimes.add(currentTime - start)
            it
        }
        .test {
            awaitItem()
            awaitItem()
            awaitItem()
            awaitComplete()
        }

    assertEquals(3, processingTimes.size)
}

@Test
fun `conflate skips intermediate values`() = runTest {
    flow {
        repeat(10) {
            emit(it)
            delay(50)
        }
    }
        .conflate()
        .onEach { delay(200) }
        .test {
            val first = awaitItem()
            assertEquals(0, first)

            val second = awaitItem()
            assertTrue(second > 1)

            cancelAndIgnoreRemainingEvents()
        }
}
```

### Тестирование `distinctUntilChanged`

```kotlin
@Test
fun `distinctUntilChanged filters consecutive duplicates`() = runTest {
    flowOf(1, 1, 2, 2, 2, 3, 2, 2, 1)
        .distinctUntilChanged()
        .test {
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            assertEquals(3, awaitItem())
            assertEquals(2, awaitItem())
            assertEquals(1, awaitItem())
            awaitComplete()
        }
}

@Test
fun `distinctUntilChanged with selector`() = runTest {
    data class User(val id: Int, val name: String, val timestamp: Long)

    flowOf(
        User(1, "John", 100),
        User(1, "John", 200),
        User(2, "Jane", 300),
        User(2, "Jane", 400)
    )
        .distinctUntilChangedBy { it.id }
        .test {
            val user1 = awaitItem()
            assertEquals(1, user1.id)

            val user2 = awaitItem()
            assertEquals(2, user2.id)

            awaitComplete()
        }
}
```

### Тестирование `takeWhile` И `take`

```kotlin
@Test
fun `takeWhile stops when predicate fails`() = runTest {
    flowOf(1, 2, 3, 4, 5, 6)
        .takeWhile { it < 4 }
        .test {
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            assertEquals(3, awaitItem())
            awaitComplete()
        }
}

@Test
fun `take limits number of emissions`() = runTest {
    flow {
        repeat(100) {
            emit(it)
            delay(50)
        }
    }
        .take(3)
        .test {
            assertEquals(0, awaitItem())
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            awaitComplete()
        }
}
```

### Тестирование Сложных Цепочек `Flow`

```kotlin
interface SearchApi {
    suspend fun search(query: String): List<String>
}

class FakeSearchApi : SearchApi {
    var callCount = 0
    var failureCount = 0

    override suspend fun search(query: String): List<String> {
        callCount++
        if (failureCount > 0) {
            failureCount--
            throw IOException("Failure $callCount")
        }
        return listOf("$query result 1", "$query result 2")
    }
}

class SearchService(private val api: SearchApi) {
    fun search(queries: Flow<String>): Flow<SearchResult> = queries
        .debounce(300)
        .distinctUntilChanged()
        .filter { it.length >= 3 }
        .flatMapLatest { query ->
            flow {
                emit(SearchResult.Loading)
                try {
                    val results = api.search(query)
                    emit(SearchResult.Success(results))
                } catch (e: Exception) {
                    emit(SearchResult.Error(e.message ?: "Unknown error"))
                }
            }
        }
        .retry(2)
        .catch { e ->
            emit(SearchResult.Error("Failed after retries: ${e.message}"))
        }
}

sealed class SearchResult {
    object Loading : SearchResult()
    data class Success(val items: List<String>) : SearchResult()
    data class Error(val message: String) : SearchResult()
}

@Test
fun `search service handles complete flow`() = runTest {
    val api = FakeSearchApi()
    val service = SearchService(api)

    val queries = flow {
        emit("a")
        delay(100)
        emit("ab")
        delay(100)
        emit("abc")
        delay(400)
    }

    service.search(queries).test {
        assertTrue(awaitItem() is SearchResult.Loading)

        val result = awaitItem()
        assertTrue(result is SearchResult.Success)
        assertEquals(listOf("abc result 1", "abc result 2"), (result as SearchResult.Success).items)

        awaitComplete()
    }
}

@Test
fun `search service debounces rapid queries`() = runTest {
    val api = FakeSearchApi()
    val service = SearchService(api)

    val queries = flow {
        emit("abc")
        delay(100)
        emit("abcd")
        delay(100)
        emit("abcde")
        delay(400)
    }

    service.search(queries).test {
        assertTrue(awaitItem() is SearchResult.Loading)

        val result = awaitItem()
        assertTrue(result is SearchResult.Success)
        val items = (result as SearchResult.Success).items
        assertTrue(items[0].startsWith("abcde"))

        awaitComplete()
    }

    assertEquals(1, api.callCount)
}

@Test
fun `search service retries on failure`() = runTest {
    val api = FakeSearchApi().apply { failureCount = 2 }
    val service = SearchService(api)

    val queries = flowOf("test")

    service.search(queries).test {
        assertTrue(awaitItem() is SearchResult.Loading)

        val result = awaitItem()
        assertTrue(result is SearchResult.Success)

        awaitComplete()
    }

    assertEquals(3, api.callCount)
}
```

### Тестирование Пользовательских Операторов

```kotlin
// Пользовательский оператор: emitBatches
fun <T> Flow<T>.emitBatches(size: Int): Flow<List<T>> = flow {
    require(size > 0)
    val batch = mutableListOf<T>()

    collect { value ->
        batch.add(value)
        if (batch.size == size) {
            emit(batch.toList())
            batch.clear()
        }
    }

    if (batch.isNotEmpty()) {
        emit(batch.toList())
    }
}

@Test
fun `emitBatches groups elements`() = runTest {
    flowOf(1, 2, 3, 4, 5, 6, 7, 8, 9)
        .emitBatches(3)
        .test {
            assertEquals(listOf(1, 2, 3), awaitItem())
            assertEquals(listOf(4, 5, 6), awaitItem())
            assertEquals(listOf(7, 8, 9), awaitItem())
            awaitComplete()
        }
}

@Test
fun `emitBatches handles partial batch`() = runTest {
    flowOf(1, 2, 3, 4, 5)
        .emitBatches(3)
        .test {
            assertEquals(listOf(1, 2, 3), awaitItem())
            assertEquals(listOf(4, 5), awaitItem())
            awaitComplete()
        }
}

// Пользовательский оператор: timeoutEach
// Оборачивает обработку каждого элемента во временное ограничение;
// если обработка следующего элемента (или send в канал) выходит за таймаут, выбрасывается TimeoutCancellationException.
fun <T> Flow<T>.timeoutEach(timeoutMs: Long): Flow<T> = channelFlow {
    require(timeoutMs > 0)
    collect { value ->
        withTimeout(timeoutMs) {
            send(value)
        }
    }
}

@Test
fun `timeoutEach fails on slow emissions`() = runTest {
    flow {
        emit(1)
        delay(100)
        emit(2)
        delay(600)
        emit(3)
    }
        .timeoutEach(500)
        .test {
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            val error = awaitError()
            assertTrue(error is TimeoutCancellationException)
        }
}
```

### Лучшие Практики

```kotlin
// DO: используйте Turbine для декларативных и детерминированных проверок Flow
@Test
fun goodTest_turbine() = runTest {
    val flow = flowOf(1)
    flow.test {
        assertEquals(1, awaitItem())
        awaitComplete()
    }
}

// ВОЗМОЖНО, НО НЕ РЕКОМЕНДУЕТСЯ: вручную собирать и затем проверять, когда доступен Turbine
@Test
fun badTest_manualCollect() = runTest {
    val flow = flowOf(1)
    val results = mutableListOf<Int>()
    flow.collect { results.add(it) }
    assertEquals(listOf(1), results)
}

// DO: использовать виртуальное время вместо реальных часов
@Test
fun goodTest_virtualTime() = runTest {
    val flow = flow {
        emit(1)
        delay(1000)
        emit(2)
    }

    val results = mutableListOf<Int>()
    val job = launch { flow.collect { results.add(it) } }

    advanceTimeBy(1000)

    assertEquals(listOf(1, 2), results)
    job.cancel()
}

// DO: тестировать цепочки операторов целиком
@Test
fun goodTest_operatorChain() = runTest {
    val flow = flow {
        emit("a")
        delay(100)
        emit("ab")
        delay(400)
    }

    flow
        .debounce(300)
        .distinctUntilChanged()
        .flatMapLatest { value -> flowOf(value.length) }
        .test {
            assertEquals(2, awaitItem())
            awaitComplete()
        }
}

// DO: тестировать обработку ошибок
@Test
fun goodTest_errorHandling() = runTest {
    var attempts = 0
    val flow = flow {
        attempts++
        if (attempts < 2) throw IOException("fail") else emit(42)
    }

    flow
        .retry(3)
        .catch { emit(-1) }
        .test {
            assertEquals(42, awaitItem())
            awaitComplete()
        }
}

// DO: тестировать отмену
@Test
fun goodTest_cancellation() = runTest {
    val flow = flow {
        while (true) {
            emit(1)
            delay(100)
        }
    }

    val job = launch {
        flow.collect { }
    }

    job.cancel()
    assertTrue(job.isCancelled)
}
```

Кратко, лучшие практики:
- Использовать Turbine для декларативных проверок операторов.
- Использовать `runTest`, управление виртуальным временем и `currentTime` тестового шедулера вместо реальных часов.
- Тестировать операторы как по отдельности, так и в комбинациях.
- Явно покрывать обработку ошибок (`catch`, `retry`, `retryWhen`).
- Тестировать сценарии отмены и взаимодействие с холодной природой `Flow`.
- Использовать fake-реализации вместо тяжёлых моков для асинхронных источников.

### Резюме

Основные стратегии тестирования операторов и трансформаций `Flow`:
- Применять Turbine для удобного и детерминированного тестирования.
- Контролировать время через `runTest` и виртуальное время, избегая реальных таймеров.
- Проверять поведение ключевых операторов: трансформации (`map`, `filter`, `transform`),
  временные (`debounce`, `sample`, пользовательские throttle),
  плоские отображения (`flatMapConcat`, `flatMapMerge`, `flatMapLatest`),
  комбинирование (`combine`, `zip`),
  обработку ошибок (`catch`, `retry`, `retryWhen`),
  побочные эффекты (`onEach`, `onStart`, `onCompletion`),
  буферизацию (`buffer`, `conflate`), фильтрацию (`distinctUntilChanged`, `take`, `takeWhile`).
- Тестировать сложные цепочки как единое целое (поиск, ретраи, комбинирование нескольких источников).

---

## Answer (EN)

Testing `Flow` operators requires a deep understanding of their semantics: flow coldness and laziness, asynchrony, reactivity, cancellation, error handling, and how individual operators transform and compose data streams. For time-based operators such as `debounce`, `sample`, custom throttles, or `retry` with delays, it is critical to use virtual time via `runTest`, `advanceTimeBy`, and the test scope or scheduler `currentTime` instead of real-time APIs like `System.currentTimeMillis()` to keep tests fast and deterministic.

Below are key patterns for testing `Flow` operators using the Turbine library and virtual time. Code examples mirror the RU section; comments and explanations are in English.

### Testing Basic Transformations

#### `map` And `filter`

```kotlin
class DataProcessor {
    fun processNumbers(input: Flow<Int>): Flow<String> = input
        .filter { it > 0 }
        .map { "Number: $it" }
}

@Test
fun `map and filter transform data correctly`() = runTest {
    val processor = DataProcessor()
    val input = flowOf(-1, 0, 1, 2, 3, -5, 10)

    val result = processor.processNumbers(input).toList()

    assertEquals(
        listOf("Number: 1", "Number: 2", "Number: 3", "Number: 10"),
        result
    )
}

// Same test with Turbine
@Test
fun `map and filter with turbine`() = runTest {
    val processor = DataProcessor()
    val input = flowOf(0, 5, -3, 10)

    processor.processNumbers(input).test {
        assertEquals("Number: 5", awaitItem())
        assertEquals("Number: 10", awaitItem())
        awaitComplete()
    }
}
```

#### `transform`

```kotlin
fun Flow<Int>.duplicateEach(): Flow<Int> = transform { value ->
    emit(value)
    emit(value)
}

@Test
fun `transform emits multiple values per input`() = runTest {
    val input = flowOf(1, 2, 3)

    input.duplicateEach().test {
        assertEquals(1, awaitItem())
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())
        assertEquals(2, awaitItem())
        assertEquals(3, awaitItem())
        assertEquals(3, awaitItem())
        awaitComplete()
    }
}

fun Flow<String>.splitWords(): Flow<String> = transform { sentence ->
    sentence.split(" ").forEach { word ->
        emit(word)
    }
}

@Test
fun `splitWords emits each word separately`() = runTest {
    val input = flowOf("Hello world", "Kotlin Flow")

    input.splitWords().test {
        assertEquals("Hello", awaitItem())
        assertEquals("world", awaitItem())
        assertEquals("Kotlin", awaitItem())
        assertEquals("Flow", awaitItem())
        awaitComplete()
    }
}
```

### Testing Time-based Operators

#### `debounce`

```kotlin
class SearchQueryProcessor {
    fun debounceQueries(queries: Flow<String>, timeoutMs: Long = 300): Flow<String> =
        queries.debounce(timeoutMs)
}

@Test
fun `debounce emits only after quiet period`() = runTest {
    val processor = SearchQueryProcessor()

    val queries = flow {
        emit("a")
        delay(100)
        emit("ab")
        delay(100)
        emit("abc")
        delay(100)
        emit("abcd")
        delay(400)
        emit("abcde")
        delay(400)
    }

    processor.debounceQueries(queries, 300).test {
        // First 4 emissions fall into one window -> only "abcd" survives
        assertEquals("abcd", awaitItem())

        // Last emission after a quiet period
        assertEquals("abcde", awaitItem())

        awaitComplete()
    }
}

@Test
fun `debounce cancels rapid emissions`() = runTest {
    val rapidFlow = flow {
        repeat(10) {
            emit("query$it")
            delay(50)
        }
        delay(400)
    }

    rapidFlow.debounce(300).test {
        // Only the last emission is expected
        assertEquals("query9", awaitItem())
        awaitComplete()
    }
}

@Test
fun `debounce with virtual time`() = runTest {
    val queries = flow {
        emit("a")
        delay(100)
        emit("b")
        delay(100)
        emit("c")
        delay(500)
    }

    val result = mutableListOf<String>()
    val job = launch {
        queries.debounce(300).collect { result.add(it) }
    }

    advanceTimeBy(200)
    assertTrue(result.isEmpty())

    advanceTimeBy(200)
    assertTrue(result.isEmpty())

    advanceTimeBy(300)
    assertEquals(listOf("c"), result)

    job.cancel()
}
```

#### `sample`

```kotlin
@Test
fun `sample emits latest value at intervals with virtual time`() = runTest {
    val source = flow {
        repeat(10) {
            emit(it)
            delay(50)
        }
    }

    val collected = mutableListOf<Int>()
    val job = launch {
        source.sample(150).collect { collected.add(it) }
    }

    advanceTimeBy(1000)
    job.cancel()

    assertTrue(collected.isNotEmpty())
}
```

#### Custom Throttle (`throttleFirst`)

For custom time-based operators, prefer using the test dispatcher and virtual time in tests, but avoid coupling the operator implementation directly to test-only APIs. If timing needs to be injectable, pass an abstraction.

```kotlin
// Example throttleFirst that relies on the coroutine context's test scheduler when present.
fun <T> Flow<T>.throttleFirst(windowDuration: Long): Flow<T> = flow {
    require(windowDuration > 0)
    var lastEmissionTime = Long.MIN_VALUE
    collect { value ->
        val time = coroutineContext[TestCoroutineScheduler]?.currentTime ?: 0L
        if (time - lastEmissionTime >= windowDuration) {
            lastEmissionTime = time
            emit(value)
        }
    }
}

@Test
fun `throttleFirst emits first value in window`() = runTest {
    val emissions = flow {
        emit(1)
        delay(100)
        emit(2)
        delay(100)
        emit(3)
        delay(300)
        emit(4)
        delay(100)
        emit(5)
    }

    emissions.throttleFirst(250).test {
        assertEquals(1, awaitItem())
        assertEquals(4, awaitItem())
        awaitComplete()
    }
}
```

### Testing flatMap Variants

#### `flatMapConcat`

```kotlin
class User(val id: Int, val name: String)

class UserRepository {
    fun getUserIds(): Flow<Int> = flow {
        emit(1)
        delay(100)
        emit(2)
        delay(100)
        emit(3)
    }

    fun getUserDetails(id: Int): Flow<User> = flow {
        delay(200)
        emit(User(id, "User $id"))
    }
}

@Test
fun `flatMapConcat processes sequentially`() = runTest {
    val repo = UserRepository()

    val result = repo.getUserIds()
        .flatMapConcat { id -> repo.getUserDetails(id) }
        .toList()

    assertEquals(listOf(1, 2, 3), result.map { it.id })
}

@Test
fun `flatMapConcat preserves order`() = runTest {
    val input = flowOf(3, 1, 2)

    input.flatMapConcat { value ->
        flow {
            delay(100)
            emit(value)
        }
    }.test {
        assertEquals(3, awaitItem())
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())
        awaitComplete()
    }
}
```

#### `flatMapMerge`

```kotlin
@Test
fun `flatMapMerge processes concurrently`() = runTest {
    val repo = UserRepository()

    val users = repo.getUserIds()
        .flatMapMerge(concurrency = 3) { id -> repo.getUserDetails(id) }
        .toList()

    val ids = users.map { it.id }.sorted()
    assertEquals(listOf(1, 2, 3), ids)
}

@Test
fun `flatMapMerge respects concurrency limit`() = runTest {
    var concurrentTasks = 0
    var maxConcurrentTasks = 0

    val input = flowOf(1, 2, 3, 4, 5)

    input.flatMapMerge(concurrency = 2) { value ->
        flow {
            concurrentTasks++
            maxConcurrentTasks = maxOf(maxConcurrentTasks, concurrentTasks)

            delay(100)
            emit(value)

            concurrentTasks--
        }
    }.test {
        repeat(5) { awaitItem() }
        awaitComplete()
    }

    assertEquals(2, maxConcurrentTasks)
}
```

#### `flatMapLatest`

```kotlin
@Test
fun `flatMapLatest cancels previous flow`() = runTest {
    val cancelledIds = mutableListOf<Int>()

    val queries = flow {
        emit(1)
        delay(100)
        emit(2)
        delay(100)
        emit(3)
        delay(500)
    }

    queries.flatMapLatest { id ->
        flow {
            try {
                delay(300)
                emit("Result for $id")
            } catch (e: CancellationException) {
                cancelledIds.add(id)
                throw e
            }
        }
    }.test {
        assertEquals("Result for 3", awaitItem())
        awaitComplete()
    }

    assertEquals(listOf(1, 2), cancelledIds)
}

@Test
fun `flatMapLatest for search`() = runTest {
    fun searchApi(query: String): Flow<List<String>> = flow {
        delay(200)
        emit(listOf("$query result 1", "$query result 2"))
    }

    val searches = flow {
        emit("a")
        delay(50)
        emit("ab")
        delay(50)
        emit("abc")
        delay(300)
    }

    searches.flatMapLatest { query -> searchApi(query) }
        .test {
            val results = awaitItem()
            assertEquals(2, results.size)
            assertTrue(results[0].startsWith("abc"))

            awaitComplete()
        }
}
```

### Testing `combine` and `zip`

#### `combine`

```kotlin
@Test
fun `combine emits when any flow emits`() = runTest {
    val flow1 = flow {
        emit(1)
        delay(100)
        emit(2)
        delay(100)
        emit(3)
    }

    val flow2 = flow {
        emit("A")
        delay(150)
        emit("B")
    }

    combine(flow1, flow2) { num, letter -> "$num$letter" }
        .test {
            assertEquals("1A", awaitItem())
            assertEquals("2A", awaitItem())
            assertEquals("2B", awaitItem())
            assertEquals("3B", awaitItem())
            awaitComplete()
        }
}

@Test
fun `combine with 3 flows produces combined values`() = runTest {
    val ints = flowOf(1, 2, 3)
    val strings = flowOf("A", "B")
    val booleans = flowOf(true, false)

    combine(ints, strings, booleans) { i, s, b -> "$i-$s-$b" }
        .test {
            assertEquals("1-A-true", awaitItem())
            assertEquals("2-B-false", awaitItem())
            awaitComplete()
        }
}
```

#### `zip`

```kotlin
@Test
fun `zip pairs corresponding elements`() = runTest {
    val numbers = flowOf(1, 2, 3, 4)
    val letters = flowOf("A", "B", "C")

    numbers.zip(letters) { num, letter -> "$num$letter" }
        .test {
            assertEquals("1A", awaitItem())
            assertEquals("2B", awaitItem())
            assertEquals("3C", awaitItem())
            awaitComplete()
        }
}

@Test
fun `zip waits for both flows`() = runTest {
    val slow = flow {
        delay(200)
        emit(1)
        delay(200)
        emit(2)
    }

    val fast = flow {
        emit("A")
        delay(50)
        emit("B")
    }

    val startTime = currentTime

    slow.zip(fast) { num, letter -> "$num$letter" }
        .test {
            val first = awaitItem()
            assertEquals("1A", first)
            assertTrue(currentTime - startTime >= 200)

            val second = awaitItem()
            assertEquals("2B", second)
            assertTrue(currentTime - startTime >= 400)

            awaitComplete()
        }
}
```

### Testing Error-handling Operators

#### `catch`

```kotlin
class DataSource {
    fun fetchData(): Flow<Int> = flow {
        emit(1)
        emit(2)
        throw IOException("Network error")
    }
}

@Test
fun `catch handles exceptions`() = runTest {
    val dataSource = DataSource()

    dataSource.fetchData()
        .catch { e -> emit(-1) }
        .test {
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            assertEquals(-1, awaitItem())
            awaitComplete()
        }
}

@Test
fun `catch can emit multiple fallback values`() = runTest {
    flowOf(1, 2, 3)
        .map {
            if (it == 2) throw IllegalStateException("Error at 2")
            it
        }
        .catch {
            emit(-1)
            emit(-2)
        }
        .test {
            assertEquals(1, awaitItem())
            assertEquals(-1, awaitItem())
            assertEquals(-2, awaitItem())
            awaitComplete()
        }
}

@Test
fun `catch does not handle downstream exceptions`() = runTest {
    flowOf(1, 2, 3)
        .catch { emit(-1) }
        .map {
            if (it == 2) throw IllegalStateException("Downstream error")
            it
        }
        .test {
            assertEquals(1, awaitItem())
            awaitError()
        }
}
```

#### `retry` And `retryWhen`

```kotlin
@Test
fun `retry attempts operation multiple times`() = runTest {
    var attempts = 0

    flow {
        attempts++
        emit(1)
        if (attempts < 3) {
            throw IOException("Attempt $attempts failed")
        }
        emit(2)
    }
        .retry(2)
        .test {
            assertEquals(1, awaitItem())
            assertEquals(1, awaitItem())
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            awaitComplete()
        }

    assertEquals(3, attempts)
}

@Test
fun `retry fails after max attempts`() = runTest {
    var attempts = 0

    flow {
        attempts++
        throw IOException("Attempt $attempts")
    }
        .retry(2)
        .test {
            val error = awaitError()
            assertTrue(error is IOException)
            assertEquals("Attempt 3", error.message)
        }

    assertEquals(3, attempts)
}

@Test
fun `retryWhen with custom logic`() = runTest {
    var attempts = 0

    flow {
        attempts++
        emit(attempts)
        throw IOException("Network error")
    }
        .retryWhen { cause, attempt ->
            cause is IOException && attempt < 3
        }
        .test {
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            assertEquals(3, awaitItem())
            awaitError()
        }

    assertEquals(4, attempts)
}

@Test
fun `retryWhen with exponential backoff tracked via delays list`() = runTest {
    val delays = mutableListOf<Long>()
    var attempts = 0

    flow {
        attempts++
        emit(attempts)
        throw IOException("Error")
    }
        .retryWhen { cause, attempt ->
            if (cause is IOException && attempt < 3) {
                val delayMs = (1000 * (1 shl attempt.toInt())).toLong()
                delays.add(delayMs)
                delay(delayMs)
                true
            } else {
                false
            }
        }
        .catch { }
        .toList()

    assertEquals(listOf(1000L, 2000L, 4000L), delays)
    assertEquals(4, attempts)
}
```

### Testing `onEach` and `onStart`/`onCompletion`

```kotlin
@Test
fun `onEach executes side effects`() = runTest {
    val sideEffects = mutableListOf<Int>()

    flowOf(1, 2, 3)
        .onEach { sideEffects.add(it) }
        .test {
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            assertEquals(3, awaitItem())
            awaitComplete()
        }

    assertEquals(listOf(1, 2, 3), sideEffects)
}

@Test
fun `onStart emits before upstream`() = runTest {
    flowOf(1, 2, 3)
        .onStart { emit(0) }
        .test {
            assertEquals(0, awaitItem())
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            assertEquals(3, awaitItem())
            awaitComplete()
        }
}

@Test
fun `onCompletion executes after completion`() = runTest {
    var completed = false

    flowOf(1, 2, 3)
        .onCompletion { completed = true }
        .test {
            assertFalse(completed)
            awaitItem()
            awaitItem()
            awaitItem()
            awaitComplete()
            assertTrue(completed)
        }
}

@Test
fun `onCompletion with exception`() = runTest {
    var completionCause: Throwable? = null

    flow {
        emit(1)
        throw IOException("Error")
    }
        .onCompletion { cause -> completionCause = cause }
        .test {
            assertEquals(1, awaitItem())
            val error = awaitError()
            assertTrue(error is IOException)
            assertNotNull(completionCause)
            assertTrue(completionCause is IOException)
        }
}
```

### Testing `buffer` and `conflate`

```kotlin
@Test
fun `buffer allows parallel processing`() = runTest {
    val processingTimes = mutableListOf<Long>()

    flow {
        repeat(3) { emit(it) }
    }
        .onEach { delay(100) }
        .buffer(2)
        .map {
            val start = currentTime
            delay(200)
            processingTimes.add(currentTime - start)
            it
        }
        .test {
            awaitItem()
            awaitItem()
            awaitItem()
            awaitComplete()
        }

    assertEquals(3, processingTimes.size)
}

@Test
fun `conflate skips intermediate values`() = runTest {
    flow {
        repeat(10) {
            emit(it)
            delay(50)
        }
    }
        .conflate()
        .onEach { delay(200) }
        .test {
            val first = awaitItem()
            assertEquals(0, first)

            val second = awaitItem()
            assertTrue(second > 1)

            cancelAndIgnoreRemainingEvents()
        }
}
```

### Testing `distinctUntilChanged`

```kotlin
@Test
fun `distinctUntilChanged filters consecutive duplicates`() = runTest {
    flowOf(1, 1, 2, 2, 2, 3, 2, 2, 1)
        .distinctUntilChanged()
        .test {
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            assertEquals(3, awaitItem())
            assertEquals(2, awaitItem())
            assertEquals(1, awaitItem())
            awaitComplete()
        }
}

@Test
fun `distinctUntilChanged with selector`() = runTest {
    data class User(val id: Int, val name: String, val timestamp: Long)

    flowOf(
        User(1, "John", 100),
        User(1, "John", 200),
        User(2, "Jane", 300),
        User(2, "Jane", 400)
    )
        .distinctUntilChangedBy { it.id }
        .test {
            val user1 = awaitItem()
            assertEquals(1, user1.id)

            val user2 = awaitItem()
            assertEquals(2, user2.id)

            awaitComplete()
        }
}
```

### Testing `takeWhile` and `take`

```kotlin
@Test
fun `takeWhile stops when predicate fails`() = runTest {
    flowOf(1, 2, 3, 4, 5, 6)
        .takeWhile { it < 4 }
        .test {
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            assertEquals(3, awaitItem())
            awaitComplete()
        }
}

@Test
fun `take limits number of emissions`() = runTest {
    flow {
        repeat(100) {
            emit(it)
            delay(50)
        }
    }
        .take(3)
        .test {
            assertEquals(0, awaitItem())
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            awaitComplete()
        }
}
```

### Testing Complex `Flow` Chains

```kotlin
interface SearchApi {
    suspend fun search(query: String): List<String>
}

class FakeSearchApi : SearchApi {
    var callCount = 0
    var failureCount = 0

    override suspend fun search(query: String): List<String> {
        callCount++
        if (failureCount > 0) {
            failureCount--
            throw IOException("Failure $callCount")
        }
        return listOf("$query result 1", "$query result 2")
    }
}

class SearchService(private val api: SearchApi) {
    fun search(queries: Flow<String>): Flow<SearchResult> = queries
        .debounce(300)
        .distinctUntilChanged()
        .filter { it.length >= 3 }
        .flatMapLatest { query ->
            flow {
                emit(SearchResult.Loading)
                try {
                    val results = api.search(query)
                    emit(SearchResult.Success(results))
                } catch (e: Exception) {
                    emit(SearchResult.Error(e.message ?: "Unknown error"))
                }
            }
        }
        .retry(2)
        .catch { e ->
            emit(SearchResult.Error("Failed after retries: ${e.message}"))
        }
}

sealed class SearchResult {
    object Loading : SearchResult()
    data class Success(val items: List<String>) : SearchResult()
    data class Error(val message: String) : SearchResult()
}

@Test
fun `search service handles complete flow`() = runTest {
    val api = FakeSearchApi()
    val service = SearchService(api)

    val queries = flow {
        emit("a")
        delay(100)
        emit("ab")
        delay(100)
        emit("abc")
        delay(400)
    }

    service.search(queries).test {
        assertTrue(awaitItem() is SearchResult.Loading)

        val result = awaitItem()
        assertTrue(result is SearchResult.Success)
        assertEquals(listOf("abc result 1", "abc result 2"), (result as SearchResult.Success).items)

        awaitComplete()
    }
}

@Test
fun `search service debounces rapid queries`() = runTest {
    val api = FakeSearchApi()
    val service = SearchService(api)

    val queries = flow {
        emit("abc")
        delay(100)
        emit("abcd")
        delay(100)
        emit("abcde")
        delay(400)
    }

    service.search(queries).test {
        assertTrue(awaitItem() is SearchResult.Loading)

        val result = awaitItem()
        assertTrue(result is SearchResult.Success)
        val items = (result as SearchResult.Success).items
        assertTrue(items[0].startsWith("abcde"))

        awaitComplete()
    }

    assertEquals(1, api.callCount)
}

@Test
fun `search service retries on failure`() = runTest {
    val api = FakeSearchApi().apply { failureCount = 2 }
    val service = SearchService(api)

    val queries = flowOf("test")

    service.search(queries).test {
        assertTrue(awaitItem() is SearchResult.Loading)

        val result = awaitItem()
        assertTrue(result is SearchResult.Success)

        awaitComplete()
    }

    assertEquals(3, api.callCount)
}
```

### Testing Custom Operators

```kotlin
// Custom operator: emitBatches
fun <T> Flow<T>.emitBatches(size: Int): Flow<List<T>> = flow {
    require(size > 0)
    val batch = mutableListOf<T>()

    collect { value ->
        batch.add(value)
        if (batch.size == size) {
            emit(batch.toList())
            batch.clear()
        }
    }

    if (batch.isNotEmpty()) {
        emit(batch.toList())
    }
}

@Test
fun `emitBatches groups elements`() = runTest {
    flowOf(1, 2, 3, 4, 5, 6, 7, 8, 9)
        .emitBatches(3)
        .test {
            assertEquals(listOf(1, 2, 3), awaitItem())
            assertEquals(listOf(4, 5, 6), awaitItem())
            assertEquals(listOf(7, 8, 9), awaitItem())
            awaitComplete()
        }
}

@Test
fun `emitBatches handles partial batch`() = runTest {
    flowOf(1, 2, 3, 4, 5)
        .emitBatches(3)
        .test {
            assertEquals(listOf(1, 2, 3), awaitItem())
            assertEquals(listOf(4, 5), awaitItem())
            awaitComplete()
        }
}

// Custom operator: timeoutEach
// Wraps handling of each element with a timeout; if processing/sending exceeds the timeout,
// a TimeoutCancellationException is thrown.
fun <T> Flow<T>.timeoutEach(timeoutMs: Long): Flow<T> = channelFlow {
    require(timeoutMs > 0)
    collect { value ->
        withTimeout(timeoutMs) {
            send(value)
        }
    }
}

@Test
fun `timeoutEach fails on slow emissions`() = runTest {
    flow {
        emit(1)
        delay(100)
        emit(2)
        delay(600)
        emit(3)
    }
        .timeoutEach(500)
        .test {
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            val error = awaitError()
            assertTrue(error is TimeoutCancellationException)
        }
}
```

### Best Practices

```kotlin
// DO: use Turbine for concise and deterministic Flow assertions
@Test
fun goodTest_turbine() = runTest {
    val flow = flowOf(1)
    flow.test {
        assertEquals(1, awaitItem())
        awaitComplete()
    }
}

// VALID BUT LESS IDEAL: manual collect-and-assert when Turbine is available
@Test
fun badTest_manualCollect() = runTest {
    val flow = flowOf(1)
    val results = mutableListOf<Int>()
    flow.collect { results.add(it) }
    assertEquals(listOf(1), results)
}

// DO: use virtual time instead of real clocks
@Test
fun goodTest_virtualTime() = runTest {
    val flow = flow {
        emit(1)
        delay(1000)
        emit(2)
    }

    val results = mutableListOf<Int>()
    val job = launch { flow.collect { results.add(it) } }

    advanceTimeBy(1000)

    assertEquals(listOf(1, 2), results)
    job.cancel()
}

// DO: test entire operator chains
@Test
fun goodTest_operatorChain() = runTest {
    val flow = flow {
        emit("a")
        delay(100)
        emit("ab")
        delay(400)
    }

    flow
        .debounce(300)
        .distinctUntilChanged()
        .flatMapLatest { value -> flowOf(value.length) }
        .test {
            assertEquals(2, awaitItem())
            awaitComplete()
        }
}

// DO: test error handling
@Test
fun goodTest_errorHandling() = runTest {
    var attempts = 0
    val flow = flow {
        attempts++
        if (attempts < 2) throw IOException("fail") else emit(42)
    }

    flow
        .retry(3)
        .catch { emit(-1) }
        .test {
            assertEquals(42, awaitItem())
            awaitComplete()
        }
}

// DO: test cancellation
@Test
fun goodTest_cancellation() = runTest {
    val flow = flow {
        while (true) {
            emit(1)
            delay(100)
        }
    }

    val job = launch {
        flow.collect { }
    }

    job.cancel()
    assertTrue(job.isCancelled)
}
```

In summary, core strategies when testing `Flow` operators and transformations:
- Prefer Turbine for concise, deterministic assertions.
- Use `runTest`, virtual time control, and the test scheduler's `currentTime`; avoid real timers.
- Verify behavior of key operator groups: transformations (`map`, `filter`, `transform`),
  time-based (`debounce`, `sample`, custom throttling),
  flattening (`flatMapConcat`, `flatMapMerge`, `flatMapLatest`),
  combination (`combine`, `zip`),
  error handling (`catch`, `retry`, `retryWhen`),
  side-effects (`onEach`, `onStart`, `onCompletion`),
  buffering (`buffer`, `conflate`), filtering (`distinctUntilChanged`, `take`, `takeWhile`).
- Test complex chains end-to-end (search flows, retries, combining multiple sources).

---

## Дополнительные Вопросы (RU)

1. Как тестировать операторы `StateFlow` и `SharedFlow` и их особенности (replay, буфер, горячая природа)?
2. В чём разница между `conflate` и `collectLatest` при тестировании и как проверять их корректность?
3. Как структурировать тесты для пользовательских операторов `Flow`, чтобы они были изолированными и поддерживаемыми?
4. Как измерять и сравнивать производительность сложных цепочек `Flow` в тестах?
5. Как тестировать `Flow` с несколькими коллекторами и конкурентным доступом к данным?

---

## Follow-ups

1. How to test `StateFlow` and `SharedFlow` operators and their hot-stream semantics (replay, buffering, etc.)?
2. What is the difference between `conflate` and `collectLatest` in terms of behavior, and how would you verify each in tests?
3. How to structure tests for custom `Flow` operators so they remain isolated, readable, and maintainable?
4. How to measure or compare performance characteristics of complex `Flow` chains under test conditions?
5. How to test `Flow` behavior with multiple concurrent collectors and shared state?

---

## Ссылки (RU)

- [[c-flow]]
- [[c-testing]]
- Операторы Flow в документации Kotlin: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/
- Библиотека Turbine: https://github.com/cashapp/turbine
- Тестирование Flow на Android: https://developer.android.com/kotlin/flow/test

---

## References

- [[c-flow]]
- [[c-testing]]
- Flow Operators - Kotlin Docs: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/
- Turbine Testing Library: https://github.com/cashapp/turbine
- Testing Flows - Android Developers: https://developer.android.com/kotlin/flow/test

---

## Связанные Вопросы (RU)

### Сложные (Hard)
- [[q-flow-operators-deep-dive--kotlin--hard]]
- [[q-flow-testing-advanced--kotlin--hard]]

### Предпосылки (полегче)
- [[q-instant-search-flow-operators--kotlin--medium]]
- [[q-flow-operators-map-filter--kotlin--medium]]
- [[q-flow-operators--kotlin--medium]]
- [[q-testing-coroutines-runtest--kotlin--medium]]
- [[q-testing-stateflow-sharedflow--kotlin--medium]]

### Хаб
- [[q-kotlin-flow-basics--kotlin--medium]]

---

## Related Questions

### Related (Hard)
- [[q-flow-operators-deep-dive--kotlin--hard]]
- [[q-flow-testing-advanced--kotlin--hard]]

### Prerequisites (Easier)
- [[q-instant-search-flow-operators--kotlin--medium]]
- [[q-flow-operators-map-filter--kotlin--medium]]
- [[q-flow-operators--kotlin--medium]]
- [[q-testing-coroutines-runtest--kotlin--medium]]
- [[q-testing-stateflow-sharedflow--kotlin--medium]]

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]]
