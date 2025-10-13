---
id: 20251012-140003
title: "Testing Flow Operators and Transformations / Тестирование операторов и трансформаций Flow"
aliases: []

# Classification
topic: kotlin
subtopics: [coroutines, testing, flow, operators]
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
related: [q-testing-coroutines-runtest--kotlin--medium, q-testing-stateflow-sharedflow--kotlin--medium, q-flow-operators-deep-dive--kotlin--hard]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [kotlin, coroutines, testing, flow, operators, difficulty/hard]
---
# Question (EN)
> How to test Flow operators and transformations like flatMap, debounce, retry, and combine? Cover virtual time testing, turbine usage, and complex flow chain testing strategies.

# Вопрос (RU)
> Как тестировать операторы и трансформации Flow такие как flatMap, debounce, retry и combine? Покрыть тестирование виртуального времени, использование turbine и стратегии тестирования сложных цепочек flow.

---

## Answer (EN)

Testing Flow operators requires understanding timing, cancellation, error handling, and how operators transform the data stream. This is particularly challenging because flows are cold, asynchronous, and reactive.

### Testing Basic Transformations

#### map and filter

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

// With turbine
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

#### transform

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

### Testing Timing Operators

#### debounce

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
        delay(400) // Longer than debounce timeout
        emit("abcde")
        delay(400)
    }

    processor.debounceQueries(queries, 300).test {
        // First 4 emissions are within 300ms of each other
        // Only "abcd" is emitted after quiet period
        assertEquals("abcd", awaitItem())

        // Last emission after another quiet period
        assertEquals("abcde", awaitItem())

        awaitComplete()
    }
}

@Test
fun `debounce cancels rapid emissions`() = runTest {
    val emissions = mutableListOf<String>()

    val rapidFlow = flow {
        repeat(10) {
            emit("query$it")
            delay(50) // Faster than debounce
        }
        delay(400) // Let debounce complete
    }

    rapidFlow.debounce(300).test {
        // Only last emission after all rapid ones
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
        delay(500) // Debounce completes here
    }

    val result = mutableListOf<String>()
    val job = launch {
        queries.debounce(300).collect { result.add(it) }
    }

    advanceTimeBy(200) // a and b emitted, neither debounced yet
    assertTrue(result.isEmpty())

    advanceTimeBy(200) // c emitted, still in debounce
    assertTrue(result.isEmpty())

    advanceTimeBy(300) // Debounce timeout passed
    assertEquals(listOf("c"), result)

    job.cancel()
}
```

#### sample and throttle

```kotlin
@Test
fun `sample emits latest value at intervals`() = runTest {
    val flow = flow {
        repeat(10) {
            emit(it)
            delay(50)
        }
    }

    flow.sample(150).test {
        // At 150ms: latest is ~2-3
        val first = awaitItem()
        assertTrue(first in 2..3)

        // At 300ms: latest is ~5-6
        val second = awaitItem()
        assertTrue(second in 5..6)

        // At 450ms: latest is ~8-9
        val third = awaitItem()
        assertTrue(third in 8..9)

        awaitComplete()
    }
}

// Custom throttleFirst
fun <T> Flow<T>.throttleFirst(windowDuration: Long): Flow<T> = flow {
    var lastEmissionTime = 0L

    collect { value ->
        val currentTime = System.currentTimeMillis()
        if (currentTime - lastEmissionTime >= windowDuration) {
            lastEmissionTime = currentTime
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
        delay(300) // New window
        emit(4)
        delay(100)
        emit(5)
    }

    emissions.throttleFirst(250).test {
        assertEquals(1, awaitItem()) // First in first window
        assertEquals(4, awaitItem()) // First in second window
        awaitComplete()
    }
}
```

### Testing flatMap Variants

#### flatMapConcat

```kotlin
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

    val startTime = currentTime

    repo.getUserIds()
        .flatMapConcat { id -> repo.getUserDetails(id) }
        .test {
            val user1 = awaitItem()
            assertEquals(1, user1.id)
            val time1 = currentTime - startTime
            assertTrue(time1 >= 200) // After first getUserDetails

            val user2 = awaitItem()
            assertEquals(2, user2.id)
            val time2 = currentTime - startTime
            assertTrue(time2 >= 500) // 200 + 100 + 200

            val user3 = awaitItem()
            assertEquals(3, user3.id)
            val time3 = currentTime - startTime
            assertTrue(time3 >= 800) // 200 + 100 + 200 + 100 + 200

            awaitComplete()
        }
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

#### flatMapMerge

```kotlin
@Test
fun `flatMapMerge processes concurrently`() = runTest {
    val repo = UserRepository()

    val startTime = currentTime

    repo.getUserIds()
        .flatMapMerge(concurrency = 3) { id -> repo.getUserDetails(id) }
        .test {
            // All processed in parallel, order not guaranteed
            val users = List(3) { awaitItem() }

            // All completed in ~300ms (parallel), not 800ms (sequential)
            val totalTime = currentTime - startTime
            assertTrue(totalTime < 400)

            // All user IDs present
            val ids = users.map { it.id }.sorted()
            assertEquals(listOf(1, 2, 3), ids)

            awaitComplete()
        }
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

    // Never more than 2 concurrent tasks
    assertEquals(2, maxConcurrentTasks)
}
```

#### flatMapLatest

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
        delay(500) // Let last one complete
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
        // Only last query completes
        assertEquals("Result for 3", awaitItem())
        awaitComplete()
    }

    // First two were cancelled
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
        delay(300) // Let last search complete
    }

    searches.flatMapLatest { query -> searchApi(query) }
        .test {
            // Only "abc" search completes
            val results = awaitItem()
            assertEquals(2, results.size)
            assertTrue(results[0].startsWith("abc"))

            awaitComplete()
        }
}
```

### Testing combine and zip

#### combine

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
            // Initial combination
            assertEquals("1A", awaitItem())

            // flow1 emits 2
            assertEquals("2A", awaitItem())

            // flow2 emits B (around 150ms)
            assertEquals("2B", awaitItem())

            // flow1 emits 3
            assertEquals("3B", awaitItem())

            awaitComplete()
        }
}

@Test
fun `combine with 3 flows`() = runTest {
    val ints = flowOf(1, 2, 3)
    val strings = flowOf("A", "B")
    val booleans = flowOf(true, false)

    combine(ints, strings, booleans) { i, s, b -> "$i-$s-$b" }
        .test {
            // Combinations as values emit
            awaitItem() // Initial combination
            awaitItem()
            // ...
            awaitComplete()
        }
}
```

#### zip

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
            awaitComplete() // Stops when shorter flow completes
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

### Testing Error Handling Operators

#### catch

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
        .catch { e -> emit(-1) } // Emit fallback value
        .test {
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            assertEquals(-1, awaitItem()) // Fallback
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
        .catch { e ->
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
            awaitError() // Downstream exception not caught
        }
}
```

#### retry and retryWhen

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
        .retry(2) // Retry up to 2 times
        .test {
            assertEquals(1, awaitItem())
            assertEquals(1, awaitItem()) // After 1st retry
            assertEquals(1, awaitItem()) // After 2nd retry
            assertEquals(2, awaitItem()) // Success on 3rd attempt
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

    assertEquals(3, attempts) // Initial + 2 retries
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
            // Retry only IOException, max 3 attempts
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
fun `retryWhen with exponential backoff`() = runTest {
    val delays = mutableListOf<Long>()
    var attempts = 0

    flow {
        attempts++
        emit(attempts)
        throw IOException("Error")
    }
        .retryWhen { cause, attempt ->
            if (cause is IOException && attempt < 3) {
                val delayMs = (1000 * (1 shl attempt.toInt())).toLong() // 1s, 2s, 4s
                delays.add(delayMs)
                delay(delayMs)
                true
            } else {
                false
            }
        }
        .test {
            assertEquals(1, awaitItem())

            advanceTimeBy(1000)
            assertEquals(2, awaitItem())

            advanceTimeBy(2000)
            assertEquals(3, awaitItem())

            advanceTimeBy(4000)
            assertEquals(4, awaitItem())

            awaitError()
        }

    assertEquals(listOf(1000L, 2000L, 4000L), delays)
}
```

### Testing onEach and onStart/onCompletion

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
            assertEquals(0, awaitItem()) // From onStart
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

### Testing Buffer and Conflate

```kotlin
@Test
fun `buffer allows parallel processing`() = runTest {
    val processingTimes = mutableListOf<Long>()

    flow {
        repeat(3) {
            emit(it)
        }
    }
        .onEach { delay(100) } // Slow emission
        .buffer(2)
        .map {
            val start = currentTime
            delay(200) // Slow processing
            processingTimes.add(currentTime - start)
            it
        }
        .test {
            awaitItem()
            awaitItem()
            awaitItem()
            awaitComplete()

            // With buffer, processing can overlap
            // Without buffer, would take 900ms total
        }
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
        .onEach { delay(200) } // Slow collector
        .test {
            val first = awaitItem()
            assertEquals(0, first)

            // Next item will be one of the later emissions
            // because conflate skips intermediate ones
            val second = awaitItem()
            assertTrue(second > 1) // Skipped some emissions

            cancelAndIgnoreRemainingEvents()
        }
}
```

### Testing distinctUntilChanged

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
        User(1, "John", 200), // Same id, different timestamp
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

### Testing takeWhile and takeUntil

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

            // Flow was cancelled after 3 emissions
            assertTrue(currentTime < 200)
        }
}
```

### Testing Complex Flow Chains

```kotlin
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
        emit("abc") // First valid query
        delay(400) // Let debounce complete
    }

    service.search(queries).test {
        // Loading state
        assertTrue(awaitItem() is SearchResult.Loading)

        // Success
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
        // Only processes final query after debounce
        assertTrue(awaitItem() is SearchResult.Loading)

        val result = awaitItem()
        assertTrue(result is SearchResult.Success)
        val items = (result as SearchResult.Success).items
        assertTrue(items[0].startsWith("abcde"))

        awaitComplete()
    }

    // Only one API call made
    assertEquals(1, api.callCount)
}

@Test
fun `search service retries on failure`() = runTest {
    val api = FakeSearchApi()
    api.failureCount = 2 // Fail first 2 attempts
    val service = SearchService(api)

    val queries = flowOf("test")

    service.search(queries).test {
        assertTrue(awaitItem() is SearchResult.Loading)

        // Eventually succeeds after retries
        val result = awaitItem()
        assertTrue(result is SearchResult.Success)

        awaitComplete()
    }

    assertEquals(3, api.callCount) // Initial + 2 retries
}
```

### Testing Custom Operators

```kotlin
// Custom operator: emitBatches
fun <T> Flow<T>.emitBatches(size: Int): Flow<List<T>> = flow {
    val batch = mutableListOf<T>()

    collect { value ->
        batch.add(value)
        if (batch.size == size) {
            emit(batch.toList())
            batch.clear()
        }
    }

    if (batch.isNotEmpty()) {
        emit(batch)
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
            assertEquals(listOf(4, 5), awaitItem()) // Partial batch
            awaitComplete()
        }
}

// Custom operator: timeoutEach
fun <T> Flow<T>.timeoutEach(timeoutMs: Long): Flow<T> = transform { value ->
    withTimeout(timeoutMs) {
        emit(value)
    }
}

@Test
fun `timeoutEach fails on slow emissions`() = runTest {
    flow {
        emit(1)
        delay(100)
        emit(2)
        delay(600) // Exceeds timeout
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
//  DO: Use turbine for flow testing
@Test
fun goodTest() = runTest {
    flow.test {
        assertEquals(expected, awaitItem())
    }
}

//  DON'T: Manually collect and assert
@Test
fun badTest() = runTest {
    val results = mutableListOf<Int>()
    flow.collect { results.add(it) }
    assertEquals(expected, results)
}

//  DO: Test timing with virtual time
@Test
fun goodTest() = runTest {
    val start = currentTime
    // ... flow operations with delays
    val duration = currentTime - start
    assertEquals(expectedDuration, duration)
}

//  DO: Test operator combinations
@Test
fun goodTest() = runTest {
    flow
        .debounce(300)
        .distinctUntilChanged()
        .flatMapLatest { /* ... */ }
        .test {
            // Assert behavior of entire chain
        }
}

//  DO: Test error handling
@Test
fun goodTest() = runTest {
    flow
        .retry(3)
        .catch { emit(fallback) }
        .test {
            // Assert error recovery
        }
}

//  DO: Test cancellation
@Test
fun goodTest() = runTest {
    val job = launch {
        flow.collect { /* ... */ }
    }

    job.cancel()
    assertTrue(job.isCancelled)
}
```

### Summary

**Testing strategies**:
- Use **turbine** for clean, declarative flow testing
- Use **runTest** for virtual time control
- Test **timing** with `advanceTimeBy()` and `currentTime`
- Test **operator behavior** in isolation and combination
- Test **error handling** with catch, retry, retryWhen
- Test **cancellation** scenarios
- Use **fake implementations**, not mocks

**Key operators to test**:
- Transformations: map, filter, transform
- Timing: debounce, sample, throttle
- Flattening: flatMapConcat, flatMapMerge, flatMapLatest
- Combining: combine, zip
- Errors: catch, retry, retryWhen
- Side effects: onEach, onStart, onCompletion
- Buffering: buffer, conflate
- Filtering: distinctUntilChanged, take, takeWhile

**Common patterns**:
- Debounced search with error handling
- Parallel data fetching with merge
- Latest value processing with flatMapLatest
- Retry with exponential backoff
- Combined state from multiple flows

---

## Ответ (RU)

Тестирование операторов Flow требует понимания времени выполнения, отмены, обработки ошибок и того, как операторы трансформируют поток данных.

### Тестирование базовых трансформаций

```kotlin
@Test
fun `map и filter трансформируют данные правильно`() = runTest {
    val input = flowOf(-1, 0, 1, 2, 3)

    input
        .filter { it > 0 }
        .map { "Number: $it" }
        .test {
            assertEquals("Number: 1", awaitItem())
            assertEquals("Number: 2", awaitItem())
            assertEquals("Number: 3", awaitItem())
            awaitComplete()
        }
}
```

### Тестирование операторов времени

```kotlin
@Test
fun `debounce эмитит только после тихого периода`() = runTest {
    val queries = flow {
        emit("a")
        delay(100)
        emit("ab")
        delay(100)
        emit("abc")
        delay(400) // Дольше, чем debounce timeout
    }

    queries.debounce(300).test {
        assertEquals("abc", awaitItem())
        awaitComplete()
    }
}
```

### Лучшие практики

1. **Используйте turbine** для тестирования Flow
2. **Используйте виртуальное время** для контроля таймингов
3. **Тестируйте цепочки операторов** вместе
4. **Тестируйте обработку ошибок** с catch и retry
5. **Используйте fake реализации**, не моки

---

## Follow-ups

1. How to test SharedFlow and StateFlow operators?
2. What is the difference between conflate and collectLatest?
3. How to test custom Flow operators?
4. How to benchmark Flow performance?
5. How to test Flow with multiple collectors?

---

## References

- [Flow Operators - Kotlin Docs](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/)
- [Turbine Testing Library](https://github.com/cashapp/turbine)
- [Testing Flows - Android Developers](https://developer.android.com/kotlin/flow/test)

---

## Related Questions

### Prerequisites (Easier)
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-flow-operators--kotlin--medium]] - Flow

### Related (Hard)
- [[q-flow-operators-deep-dive--kotlin--hard]] - Flow
- [[q-flow-testing-advanced--kotlin--hard]] - Flow
### Prerequisites (Easier)
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-flow-operators--kotlin--medium]] - Flow

### Related (Hard)
- [[q-flow-operators-deep-dive--kotlin--hard]] - Flow
- [[q-flow-testing-advanced--kotlin--hard]] - Flow
### Prerequisites (Easier)
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-flow-operators--kotlin--medium]] - Flow

### Related (Hard)
- [[q-flow-operators-deep-dive--kotlin--hard]] - Flow
- [[q-flow-testing-advanced--kotlin--hard]] - Flow
### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

### Related (Hard)
- [[q-flowon-operator-context-switching--kotlin--hard]] - flowOn & context switching
- [[q-flow-backpressure--kotlin--hard]] - Backpressure handling
- [[q-flow-backpressure-strategies--kotlin--hard]] - Backpressure strategies
- [[q-flow-operators-deep-dive--kotlin--hard]] - Deep dive into operators
- [[q-flow-performance--kotlin--hard]] - Performance optimization
