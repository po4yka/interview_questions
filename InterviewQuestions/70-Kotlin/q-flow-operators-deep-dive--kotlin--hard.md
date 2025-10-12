---
id: 20251011-001
title: "Flow Operators Deep Dive / Глубокое погружение в операторы Flow"
aliases: []

# Classification
topic: kotlin
subtopics: [flow, operators, async, transformation, flatmap]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Phase 1 Coroutines & Flow Advanced Questions

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-kotlin-flow-basics--kotlin--medium, q-stateflow-sharedflow-differences--kotlin--medium]

# Timestamps
created: 2025-10-11
updated: 2025-10-11

tags: [kotlin, flow, operators, async, transformation, difficulty/hard]
---
# Question (EN)
> Implement custom Flow operators. Explain flatMapConcat vs flatMapMerge vs flatMapLatest with practical examples and performance characteristics.

# Вопрос (RU)
> Реализуйте пользовательские операторы Flow. Объясните flatMapConcat vs flatMapMerge vs flatMapLatest с практическими примерами и характеристиками производительности.

---

## Answer (EN)

Flow operators are functions that transform flows in various ways. Understanding the differences between flatMap variants is crucial for building efficient asynchronous data pipelines.

### FlatMap Variants Overview

The three flatMap operators differ in how they handle concurrent execution and ordering:

| Operator | Concurrency | Ordering | Cancellation | Use Case |
|----------|-------------|----------|--------------|----------|
| **flatMapConcat** | Sequential (1 at a time) | Preserved | Waits for completion | Sequential processing required |
| **flatMapMerge** | Concurrent (configurable) | Not preserved | Independent flows | Parallel processing |
| **flatMapLatest** | Only latest | Not preserved | Cancels previous | Search queries, latest data only |

### 1. flatMapConcat - Sequential Processing

**Behavior**: Processes one inner flow at a time, waiting for each to complete before starting the next.

```kotlin
fun <T, R> Flow<T>.flatMapConcat(transform: suspend (T) -> Flow<R>): Flow<R> =
    map(transform).flattenConcat()

// Example: Sequential API calls
data class User(val id: Int, val name: String)
data class UserDetails(val userId: Int, val email: String, val phone: String)

suspend fun getUserIds(): Flow<Int> = flow {
    emit(1)
    delay(100)
    emit(2)
    delay(100)
    emit(3)
}

suspend fun fetchUserDetails(userId: Int): Flow<UserDetails> = flow {
    delay(200) // Simulate network call
    emit(UserDetails(userId, "user$userId@example.com", "555-000$userId"))
    println("Fetched details for user $userId at ${System.currentTimeMillis()}")
}

// Usage
fun main() = runBlocking {
    val startTime = System.currentTimeMillis()

    getUserIds()
        .flatMapConcat { userId ->
            fetchUserDetails(userId)
        }
        .collect { details ->
            println("Received: $details (elapsed: ${System.currentTimeMillis() - startTime}ms)")
        }
}

/*
Output (sequential):
Fetched details for user 1 at 300ms
Received: UserDetails(1, ...) (elapsed: 300ms)
Fetched details for user 2 at 600ms
Received: UserDetails(2, ...) (elapsed: 600ms)
Fetched details for user 3 at 900ms
Received: UserDetails(3, ...) (elapsed: 900ms)
Total: ~900ms
*/
```

**When to use**:
- Order must be preserved
- Each operation depends on previous completion
- Loading pages sequentially
- Transaction processing

### 2. flatMapMerge - Concurrent Processing

**Behavior**: Processes multiple inner flows concurrently with configurable concurrency limit.

```kotlin
fun <T, R> Flow<T>.flatMapMerge(
    concurrency: Int = DEFAULT_CONCURRENCY,
    transform: suspend (T) -> Flow<R>
): Flow<R>

// Example: Parallel API calls
fun main() = runBlocking {
    val startTime = System.currentTimeMillis()

    getUserIds()
        .flatMapMerge(concurrency = 2) { userId ->
            fetchUserDetails(userId)
        }
        .collect { details ->
            println("Received: $details (elapsed: ${System.currentTimeMillis() - startTime}ms)")
        }
}

/*
Output (concurrent with concurrency=2):
Fetched details for user 1 at 300ms
Fetched details for user 2 at 300ms  // Started in parallel
Received: UserDetails(1, ...) (elapsed: 300ms)
Received: UserDetails(2, ...) (elapsed: 300ms)
Fetched details for user 3 at 500ms  // Started after slot freed
Received: UserDetails(3, ...) (elapsed: 500ms)
Total: ~500ms (40% faster!)
*/
```

**Practical example with error handling**:

```kotlin
// Batch processing with concurrency control
data class ImageUploadTask(val id: String, val imageData: ByteArray)
data class UploadResult(val id: String, val url: String, val success: Boolean)

fun uploadImages(tasks: List<ImageUploadTask>): Flow<UploadResult> =
    tasks.asFlow()
        .flatMapMerge(concurrency = 5) { task ->
            flow {
                try {
                    val url = uploadImage(task.imageData)
                    emit(UploadResult(task.id, url, true))
                } catch (e: Exception) {
                    emit(UploadResult(task.id, "", false))
                }
            }
        }

suspend fun uploadImage(data: ByteArray): String {
    delay(100) // Simulate upload
    return "https://cdn.example.com/${UUID.randomUUID()}"
}
```

**When to use**:
- Independent operations that can run in parallel
- Batch processing
- Multiple API calls
- I/O-bound operations
- Maximum throughput needed

### 3. flatMapLatest - Latest Value Only

**Behavior**: Cancels previous inner flow when new value arrives, only processes the latest.

```kotlin
fun <T, R> Flow<T>.flatMapLatest(transform: suspend (T) -> Flow<R>): Flow<R> =
    transformLatest { value ->
        emitAll(transform(value))
    }

// Example: Search query with debounce
data class SearchResult(val query: String, val results: List<String>)

fun searchFlow(query: String): Flow<SearchResult> = flow {
    println("Starting search for: $query")
    delay(300) // Simulate API call
    emit(SearchResult(
        query,
        listOf("$query result 1", "$query result 2")
    ))
    println("Completed search for: $query")
}

fun main() = runBlocking {
    val searchQueries = flow {
        emit("kot")
        delay(100)
        emit("kotl")  // Cancels "kot" search
        delay(100)
        emit("kotli") // Cancels "kotl" search
        delay(500)    // Wait for completion
    }

    searchQueries
        .flatMapLatest { query ->
            searchFlow(query)
        }
        .collect { result ->
            println("Displaying results for: ${result.query}")
        }
}

/*
Output:
Starting search for: kot
Starting search for: kotl      // Cancels "kot"
Starting search for: kotli     // Cancels "kotl"
Completed search for: kotli
Displaying results for: kotli
Only the last search completes!
*/
```

**Real-world implementation - Search with debounce**:

```kotlin
class SearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<List<SearchResult>> = _searchQuery
        .debounce(300) // Wait for user to stop typing
        .filter { it.length >= 3 } // Minimum query length
        .distinctUntilChanged() // Only search if query changed
        .flatMapLatest { query ->
            searchRepository.search(query)
                .catch { emit(emptyList()) }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
    }
}
```

**When to use**:
- Search/autocomplete
- Real-time filtering
- Location updates
- Only the latest value matters
- Cancelling outdated requests

### Creating Custom Flow Operators

#### Example 1: Custom retry with exponential backoff

```kotlin
fun <T> Flow<T>.retryWithExponentialBackoff(
    maxRetries: Int = 3,
    initialDelayMs: Long = 1000,
    maxDelayMs: Long = 10000,
    factor: Double = 2.0
): Flow<T> = flow {
    var currentDelay = initialDelayMs
    var retryCount = 0

    retry(maxRetries.toLong()) { cause ->
        if (retryCount >= maxRetries) {
            return@retry false
        }

        retryCount++
        println("Retry attempt $retryCount after ${currentDelay}ms due to: ${cause.message}")
        delay(currentDelay)

        currentDelay = (currentDelay * factor).toLong().coerceAtMost(maxDelayMs)
        true
    }
}

// Usage
suspend fun fetchDataWithRetry(): Flow<String> = flow {
    val random = Random.nextInt(0, 3)
    if (random != 2) {
        throw IOException("Network error")
    }
    emit("Success!")
}
    .retryWithExponentialBackoff(
        maxRetries = 3,
        initialDelayMs = 1000
    )
```

#### Example 2: Custom window operator

```kotlin
fun <T> Flow<T>.window(
    windowSize: Int,
    windowSlide: Int = windowSize
): Flow<List<T>> = flow {
    require(windowSize > 0) { "Window size must be positive" }
    require(windowSlide > 0) { "Window slide must be positive" }

    val buffer = ArrayDeque<T>(windowSize)
    var emittedCount = 0

    collect { value ->
        buffer.add(value)

        if (buffer.size > windowSize) {
            repeat(windowSlide) {
                if (buffer.isNotEmpty()) buffer.removeFirst()
            }
        }

        if (buffer.size == windowSize) {
            emit(buffer.toList())
            emittedCount++

            if (windowSlide >= windowSize) {
                buffer.clear()
            }
        }
    }
}

// Usage: Moving average
fun main() = runBlocking {
    flowOf(1, 2, 3, 4, 5, 6, 7, 8)
        .window(windowSize = 3, windowSlide = 1)
        .map { window -> window.average() }
        .collect { avg -> println("Moving average: $avg") }
}
/*
Output:
Moving average: 2.0
Moving average: 3.0
Moving average: 4.0
Moving average: 5.0
Moving average: 6.0
Moving average: 7.0
*/
```

#### Example 3: Custom rate limiting operator

```kotlin
fun <T> Flow<T>.rateLimit(
    count: Int,
    duration: Duration
): Flow<T> = flow {
    val timestamps = ArrayDeque<Long>(count)

    collect { value ->
        val now = System.currentTimeMillis()

        // Remove timestamps older than duration
        while (timestamps.isNotEmpty() &&
               now - timestamps.first() > duration.inWholeMilliseconds) {
            timestamps.removeFirst()
        }

        // Check if we're at the rate limit
        if (timestamps.size >= count) {
            val oldestTimestamp = timestamps.first()
            val delayTime = duration.inWholeMilliseconds - (now - oldestTimestamp)
            if (delayTime > 0) {
                delay(delayTime)
            }
            timestamps.removeFirst()
        }

        timestamps.add(System.currentTimeMillis())
        emit(value)
    }
}

// Usage: API rate limiting (max 5 requests per second)
suspend fun makeApiCalls() {
    (1..20).asFlow()
        .rateLimit(count = 5, duration = 1.seconds)
        .collect { request ->
            println("API call $request at ${System.currentTimeMillis()}")
        }
}
```

### Performance Comparison

```kotlin
// Benchmark different flatMap variants
suspend fun benchmarkFlatMapVariants() {
    val itemCount = 100
    val processingTime = 10L // ms per item

    // flatMapConcat
    var startTime = System.currentTimeMillis()
    (1..itemCount).asFlow()
        .flatMapConcat { flowOf(it).onEach { delay(processingTime) } }
        .collect()
    println("flatMapConcat: ${System.currentTimeMillis() - startTime}ms") // ~1000ms

    // flatMapMerge with concurrency=10
    startTime = System.currentTimeMillis()
    (1..itemCount).asFlow()
        .flatMapMerge(10) { flowOf(it).onEach { delay(processingTime) } }
        .collect()
    println("flatMapMerge(10): ${System.currentTimeMillis() - startTime}ms") // ~100ms

    // flatMapLatest (only last completes)
    startTime = System.currentTimeMillis()
    (1..itemCount).asFlow()
        .flatMapLatest { flowOf(it).onEach { delay(processingTime) } }
        .collect()
    println("flatMapLatest: ${System.currentTimeMillis() - startTime}ms") // ~10ms
}
```

### Best Practices

1. **Choose the right operator**:
   - Need ordering? → `flatMapConcat`
   - Need speed? → `flatMapMerge`
   - Only latest matters? → `flatMapLatest`

2. **Control concurrency**:
   ```kotlin
   // Avoid unbounded concurrency
   .flatMapMerge(concurrency = Int.MAX_VALUE) // ❌ Dangerous
   .flatMapMerge(concurrency = 10) // ✅ Controlled
   ```

3. **Consider resource limits**:
   ```kotlin
   // Limit concurrent network calls
   val maxConcurrentRequests = 5
   requests.flatMapMerge(maxConcurrentRequests) { makeRequest(it) }
   ```

4. **Handle errors appropriately**:
   ```kotlin
   .flatMapMerge { item ->
       flow { emit(process(item)) }
           .catch { e -> emit(defaultValue) }
   }
   ```

5. **Memory considerations**:
   - `flatMapMerge` keeps multiple flows in memory
   - `flatMapLatest` most memory efficient (only one active)
   - `flatMapConcat` moderate memory usage

### Common Pitfalls

1. **Using flatMapConcat when flatMapMerge is needed**:
   ```kotlin
   // ❌ Slow: processes 1000 items sequentially
   (1..1000).asFlow()
       .flatMapConcat { fetchData(it) }

   // ✅ Fast: processes 10 at a time
   (1..1000).asFlow()
       .flatMapMerge(10) { fetchData(it) }
   ```

2. **Forgetting cancellation with flatMapLatest**:
   ```kotlin
   // ❌ Resources leak if not cancellation-aware
   searchQuery.flatMapLatest { query ->
       flow {
           val connection = openConnection() // Not cancelled!
           // ...
       }
   }

   // ✅ Properly cancellable
   searchQuery.flatMapLatest { query ->
       flow {
           val connection = openConnection()
           try {
               // ...
           } finally {
               connection.close()
           }
       }
   }
   ```

3. **Not configuring concurrency**:
   ```kotlin
   // ❌ Default concurrency might be too high or low
   .flatMapMerge { ... }

   // ✅ Explicitly set based on use case
   .flatMapMerge(concurrency = 3) { ... }
   ```

**English Summary**: Flow operators transform flows in different ways. flatMapConcat processes sequentially preserving order, flatMapMerge processes concurrently with configurable concurrency for maximum throughput, and flatMapLatest cancels previous flows keeping only the latest. Custom operators can be created by combining existing operators. Choose based on ordering requirements, performance needs, and resource constraints.

## Ответ (RU)

Операторы Flow — это функции, которые трансформируют потоки различными способами. Понимание различий между вариантами flatMap критически важно для построения эффективных асинхронных конвейеров данных.

### Обзор вариантов FlatMap

Три оператора flatMap различаются по обработке конкурентного выполнения и порядка:

| Оператор | Конкурентность | Порядок | Отмена | Применение |
|----------|----------------|---------|--------|------------|
| **flatMapConcat** | Последовательно (по 1) | Сохраняется | Ждет завершения | Требуется последовательность |
| **flatMapMerge** | Конкурентно (настраивается) | Не сохраняется | Независимые потоки | Параллельная обработка |
| **flatMapLatest** | Только последний | Не сохраняется | Отменяет предыдущие | Поиск, только последние данные |

### 1. flatMapConcat - Последовательная обработка

**Поведение**: Обрабатывает по одному внутреннему потоку за раз, ожидая завершения каждого перед началом следующего.

```kotlin
fun <T, R> Flow<T>.flatMapConcat(transform: suspend (T) -> Flow<R>): Flow<R> =
    map(transform).flattenConcat()

// Пример: Последовательные API вызовы
suspend fun fetchUserDetails(userId: Int): Flow<UserDetails> = flow {
    delay(200) // Симуляция сетевого вызова
    emit(UserDetails(userId, "user$userId@example.com", "555-000$userId"))
    println("Получены данные пользователя $userId")
}

// Использование - обработка последовательно
getUserIds()
    .flatMapConcat { userId ->
        fetchUserDetails(userId)
    }
    .collect { details ->
        println("Получено: $details")
    }
```

**Когда использовать**:
- Порядок должен быть сохранен
- Каждая операция зависит от завершения предыдущей
- Последовательная загрузка страниц
- Обработка транзакций

### 2. flatMapMerge - Конкурентная обработка

**Поведение**: Обрабатывает несколько внутренних потоков одновременно с настраиваемым лимитом конкурентности.

```kotlin
// Пример: Параллельные API вызовы
getUserIds()
    .flatMapMerge(concurrency = 2) { userId ->
        fetchUserDetails(userId)
    }
    .collect { details ->
        println("Получено: $details")
    }
// Результат: на 40% быстрее благодаря параллелизму!
```

**Практический пример с обработкой ошибок**:

```kotlin
// Пакетная обработка с контролем конкурентности
fun uploadImages(tasks: List<ImageUploadTask>): Flow<UploadResult> =
    tasks.asFlow()
        .flatMapMerge(concurrency = 5) { task ->
            flow {
                try {
                    val url = uploadImage(task.imageData)
                    emit(UploadResult(task.id, url, true))
                } catch (e: Exception) {
                    emit(UploadResult(task.id, "", false))
                }
            }
        }
```

**Когда использовать**:
- Независимые операции, которые могут выполняться параллельно
- Пакетная обработка
- Множественные API вызовы
- I/O операции
- Нужна максимальная пропускная способность

### 3. flatMapLatest - Только последнее значение

**Поведение**: Отменяет предыдущий внутренний поток при поступлении нового значения, обрабатывает только последнее.

```kotlin
// Пример: Поисковый запрос
fun searchFlow(query: String): Flow<SearchResult> = flow {
    println("Начало поиска: $query")
    delay(300) // Симуляция API вызова
    emit(SearchResult(query, listOf("$query результат 1", "$query результат 2")))
    println("Поиск завершен: $query")
}

searchQueries
    .flatMapLatest { query ->
        searchFlow(query)
    }
    .collect { result ->
        println("Отображение результатов для: ${result.query}")
    }
// Завершается только последний поиск!
```

**Реальная реализация - Поиск с debounce**:

```kotlin
class SearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<List<SearchResult>> = _searchQuery
        .debounce(300) // Ждем, пока пользователь закончит печатать
        .filter { it.length >= 3 } // Минимальная длина запроса
        .distinctUntilChanged() // Поиск только если запрос изменился
        .flatMapLatest { query ->
            searchRepository.search(query)
                .catch { emit(emptyList()) }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )
}
```

**Когда использовать**:
- Поиск/автодополнение
- Фильтрация в реальном времени
- Обновления локации
- Важно только последнее значение
- Отмена устаревших запросов

### Создание пользовательских операторов Flow

#### Пример 1: Повтор с экспоненциальной задержкой

```kotlin
fun <T> Flow<T>.retryWithExponentialBackoff(
    maxRetries: Int = 3,
    initialDelayMs: Long = 1000,
    maxDelayMs: Long = 10000,
    factor: Double = 2.0
): Flow<T> = flow {
    var currentDelay = initialDelayMs
    var retryCount = 0

    retry(maxRetries.toLong()) { cause ->
        if (retryCount >= maxRetries) {
            return@retry false
        }

        retryCount++
        delay(currentDelay)
        currentDelay = (currentDelay * factor).toLong().coerceAtMost(maxDelayMs)
        true
    }
}
```

#### Пример 2: Оператор окна

```kotlin
fun <T> Flow<T>.window(
    windowSize: Int,
    windowSlide: Int = windowSize
): Flow<List<T>> = flow {
    val buffer = ArrayDeque<T>(windowSize)

    collect { value ->
        buffer.add(value)

        if (buffer.size > windowSize) {
            repeat(windowSlide) {
                if (buffer.isNotEmpty()) buffer.removeFirst()
            }
        }

        if (buffer.size == windowSize) {
            emit(buffer.toList())
        }
    }
}

// Использование: Скользящее среднее
flowOf(1, 2, 3, 4, 5, 6, 7, 8)
    .window(windowSize = 3, windowSlide = 1)
    .map { window -> window.average() }
    .collect { avg -> println("Скользящее среднее: $avg") }
```

#### Пример 3: Ограничение частоты

```kotlin
fun <T> Flow<T>.rateLimit(
    count: Int,
    duration: Duration
): Flow<T> = flow {
    val timestamps = ArrayDeque<Long>(count)

    collect { value ->
        val now = System.currentTimeMillis()

        // Удаляем устаревшие метки времени
        while (timestamps.isNotEmpty() &&
               now - timestamps.first() > duration.inWholeMilliseconds) {
            timestamps.removeFirst()
        }

        // Проверяем лимит
        if (timestamps.size >= count) {
            val oldestTimestamp = timestamps.first()
            val delayTime = duration.inWholeMilliseconds - (now - oldestTimestamp)
            if (delayTime > 0) {
                delay(delayTime)
            }
            timestamps.removeFirst()
        }

        timestamps.add(System.currentTimeMillis())
        emit(value)
    }
}
```

### Лучшие практики

1. **Выбирайте правильный оператор**:
   - Нужен порядок? → `flatMapConcat`
   - Нужна скорость? → `flatMapMerge`
   - Важно только последнее? → `flatMapLatest`

2. **Контролируйте конкурентность**:
   ```kotlin
   // Избегайте неограниченной конкурентности
   .flatMapMerge(concurrency = Int.MAX_VALUE) // ❌ Опасно
   .flatMapMerge(concurrency = 10) // ✅ Контролируемо
   ```

3. **Обрабатывайте ошибки правильно**:
   ```kotlin
   .flatMapMerge { item ->
       flow { emit(process(item)) }
           .catch { e -> emit(defaultValue) }
   }
   ```

### Распространенные ошибки

1. **Использование flatMapConcat вместо flatMapMerge**:
   ```kotlin
   // ❌ Медленно: обработка 1000 элементов последовательно
   (1..1000).asFlow().flatMapConcat { fetchData(it) }

   // ✅ Быстро: обработка 10 одновременно
   (1..1000).asFlow().flatMapMerge(10) { fetchData(it) }
   ```

2. **Не настройка конкурентности**:
   ```kotlin
   // ❌ Конкурентность по умолчанию может быть слишком большой
   .flatMapMerge { ... }

   // ✅ Явно установлено в зависимости от случая
   .flatMapMerge(concurrency = 3) { ... }
   ```

**Краткое содержание**: Операторы Flow трансформируют потоки разными способами. flatMapConcat обрабатывает последовательно сохраняя порядок, flatMapMerge обрабатывает конкурентно с настраиваемой конкурентностью для максимальной пропускной способности, а flatMapLatest отменяет предыдущие потоки оставляя только последний. Пользовательские операторы создаются комбинированием существующих. Выбор зависит от требований к порядку, производительности и ограничений ресурсов.

---

## References
- [Flow documentation - Kotlin](https://kotlinlang.org/docs/flow.html)
- [Flow operators - Kotlin Coroutines Guide](https://kotlinlang.org/docs/flow.html#flow-operators)
- [flatMapConcat, flatMapMerge, flatMapLatest - API Reference](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/)

## Related Questions

### Prerequisites (Easier)
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-flow-operators--kotlin--medium]] - Flow

### Related (Hard)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-backpressure-strategies--kotlin--hard]] - Flow
- [[q-flow-testing-advanced--kotlin--hard]] - Flow
### Prerequisites (Easier)
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-flow-operators--kotlin--medium]] - Flow

### Related (Hard)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-backpressure-strategies--kotlin--hard]] - Flow
- [[q-flow-testing-advanced--kotlin--hard]] - Flow
### Prerequisites (Easier)
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-flow-operators--kotlin--medium]] - Flow

### Related (Hard)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-backpressure-strategies--kotlin--hard]] - Flow
- [[q-flow-testing-advanced--kotlin--hard]] - Flow
### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

### Related (Hard)
- [[q-flowon-operator-context-switching--kotlin--hard]] - flowOn & context switching
- [[q-flow-backpressure--kotlin--hard]] - Backpressure handling
- [[q-flow-backpressure-strategies--kotlin--hard]] - Backpressure strategies
- [[q-flow-performance--kotlin--hard]] - Performance optimization
- [[q-flow-testing-advanced--kotlin--hard]] - Advanced Flow testing
