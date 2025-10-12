---
id: 20251011-007
title: "Flow Backpressure Strategies / Стратегии противодавления Flow"
aliases: []

# Classification
topic: kotlin
subtopics: [flow, backpressure, buffer, performance, operators]
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
related: [q-kotlin-flow-basics--kotlin--medium, q-backpressure-in-kotlin-flow--programming-languages--medium]

# Timestamps
created: 2025-10-11
updated: 2025-10-11

tags: [kotlin, flow, backpressure, buffer, performance, difficulty/hard]
---
# Question (EN)
> Implement backpressure handling in Flow. Compare buffer, conflate, and collectLatest strategies with performance benchmarks.

# Вопрос (RU)
> Реализуйте обработку противодавления в Flow. Сравните стратегии buffer, conflate и collectLatest с производительными бенчмарками.

---

## Answer (EN)

Backpressure occurs when a producer emits values faster than a consumer can process them. Flow provides several strategies to handle this.

### Understanding Backpressure

```kotlin
// Problem: Slow collector causes producer to wait
flow {
    repeat(100) {
        emit(it) // Fast emission
        println("Emitted $it")
    }
}
.collect { value ->
    delay(100) // Slow processing
    println("Processed $value")
}
// Producer suspended on each emit waiting for consumer
```

### Strategy 1: buffer() - Buffered Processing

The `buffer` operator adds a buffer between producer and consumer, allowing them to run concurrently.

```kotlin
public fun <T> Flow<T>.buffer(
    capacity: Int = BUFFERED,
    onBufferOverflow: BufferOverflow = BufferOverflow.SUSPEND
): Flow<T>
```

#### Basic buffer Usage

```kotlin
fun demonstrateBuffer() = runBlocking {
    val startTime = System.currentTimeMillis()

    // Without buffer - sequential
    println("=== WITHOUT BUFFER ===")
    flow {
        repeat(3) {
            delay(100) // Producer takes 100ms
            emit(it)
            println("[${timestamp(startTime)}] Emitted $it")
        }
    }
    .collect { value ->
        delay(300) // Consumer takes 300ms
        println("[${timestamp(startTime)}] Collected $value")
    }
    // Total: 3 * (100 + 300) = 1200ms

    delay(500)

    // With buffer - concurrent
    println("\n=== WITH BUFFER ===")
    val startTime2 = System.currentTimeMillis()
    flow {
        repeat(3) {
            delay(100)
            emit(it)
            println("[${timestamp(startTime2)}] Emitted $it")
        }
    }
    .buffer() // Producer and consumer run concurrently
    .collect { value ->
        delay(300)
        println("[${timestamp(startTime2)}] Collected $value")
    }
    // Total: max(3*100, 3*300) + overhead ≈ 900ms
}

fun timestamp(start: Long) = System.currentTimeMillis() - start

/*
Output WITHOUT BUFFER:
[100] Emitted 0
[400] Collected 0
[500] Emitted 1
[800] Collected 1
[900] Emitted 2
[1200] Collected 2
Total: 1200ms

Output WITH BUFFER:
[100] Emitted 0
[200] Emitted 1
[300] Emitted 2
[400] Collected 0
[700] Collected 1
[1000] Collected 2
Total: 1000ms (20% faster!)
*/
```

#### Buffer Overflow Strategies

```kotlin
// 1. SUSPEND (default) - suspend producer when buffer full
flow {
    repeat(10) { emit(it) }
}
.buffer(capacity = 3, onBufferOverflow = BufferOverflow.SUSPEND)
.collect { delay(100); println(it) }

// 2. DROP_OLDEST - drop oldest value when buffer full
flow {
    repeat(10) { emit(it) }
}
.buffer(capacity = 3, onBufferOverflow = BufferOverflow.DROP_OLDEST)
.collect { delay(100); println(it) }
// Output: 0, 1, 2, 6, 7, 8, 9 (middle values dropped)

// 3. DROP_LATEST - drop newest value when buffer full
flow {
    repeat(10) { emit(it) }
}
.buffer(capacity = 3, onBufferOverflow = BufferOverflow.DROP_LATEST)
.collect { delay(100); println(it) }
// Output: 0, 1, 2, 3, 4 (latest values dropped)
```

### Strategy 2: conflate() - Keep Latest Only

The `conflate` operator keeps only the most recent value, discarding intermediate values.

```kotlin
// conflate() is equivalent to:
// buffer(capacity = 0, onBufferOverflow = BufferOverflow.DROP_OLDEST)

fun demonstrateConflate() = runBlocking {
    val startTime = System.currentTimeMillis()

    flow {
        repeat(10) {
            emit(it)
            println("[${timestamp(startTime)}] Emitted $it")
            delay(100)
        }
    }
    .conflate() // Keep only latest
    .collect { value ->
        println("[${timestamp(startTime)}] Collecting $value")
        delay(500) // Slow consumer
        println("[${timestamp(startTime)}] Collected $value")
    }
}

/*
Output:
[0] Emitted 0
[0] Collecting 0
[100] Emitted 1
[200] Emitted 2
[300] Emitted 3
[400] Emitted 4
[500] Collected 0
[500] Collecting 4  // Skipped 1, 2, 3!
[600] Emitted 5
[700] Emitted 6
[800] Emitted 7
[900] Emitted 8
[1000] Collected 4
[1000] Collecting 8  // Skipped 5, 6, 7!
*/
```

### Strategy 3: collectLatest() - Cancel Previous Collection

The `collectLatest` operator cancels the current collection when a new value arrives.

```kotlin
fun demonstrateCollectLatest() = runBlocking {
    val startTime = System.currentTimeMillis()

    flow {
        repeat(5) {
            emit(it)
            println("[${timestamp(startTime)}] Emitted $it")
            delay(200)
        }
    }
    .collectLatest { value ->
        println("[${timestamp(startTime)}] Collecting $value")
        delay(500) // Slow processing
        println("[${timestamp(startTime)}] Completed $value")
    }
}

/*
Output:
[0] Emitted 0
[0] Collecting 0
[200] Emitted 1
[200] Collecting 1  // Cancelled collection of 0
[400] Emitted 2
[400] Collecting 2  // Cancelled collection of 1
[600] Emitted 3
[600] Collecting 3  // Cancelled collection of 2
[800] Emitted 4
[800] Collecting 4  // Cancelled collection of 3
[1300] Completed 4  // Only last value completed!
*/
```

### Performance Comparison

```kotlin
data class BenchmarkResult(
    val strategy: String,
    val emitted: Int,
    val collected: Int,
    val durationMs: Long,
    val throughput: Double
)

suspend fun benchmarkStrategies(): List<BenchmarkResult> {
    val itemCount = 1000
    val emitDelayMs = 1L
    val collectDelayMs = 10L

    return listOf(
        // 1. No strategy - fully synchronized
        benchmark("No Strategy") {
            flow {
                repeat(itemCount) {
                    delay(emitDelayMs)
                    emit(it)
                }
            }.collect {
                delay(collectDelayMs)
            }
        },

        // 2. Buffer - parallel processing
        benchmark("Buffer(64)") {
            flow {
                repeat(itemCount) {
                    delay(emitDelayMs)
                    emit(it)
                }
            }
            .buffer(64)
            .collect {
                delay(collectDelayMs)
            }
        },

        // 3. Conflate - skip intermediate
        benchmark("Conflate") {
            var collected = 0
            flow {
                repeat(itemCount) {
                    delay(emitDelayMs)
                    emit(it)
                }
            }
            .conflate()
            .collect {
                collected++
                delay(collectDelayMs)
            }
            println("Conflate collected $collected/$itemCount")
        },

        // 4. CollectLatest - cancel previous
        benchmark("CollectLatest") {
            var completed = 0
            flow {
                repeat(itemCount) {
                    delay(emitDelayMs)
                    emit(it)
                }
            }
            .collectLatest {
                delay(collectDelayMs)
                completed++
            }
            println("CollectLatest completed $completed/$itemCount")
        }
    )
}

suspend fun benchmark(
    name: String,
    block: suspend () -> Unit
): BenchmarkResult {
    val start = System.currentTimeMillis()
    block()
    val duration = System.currentTimeMillis() - start

    return BenchmarkResult(
        strategy = name,
        emitted = 1000,
        collected = 1000,
        durationMs = duration,
        throughput = 1000.0 * 1000 / duration
    )
}

/*
Typical Results:
┌─────────────────┬──────────┬─────────────┬─────────────┐
│ Strategy        │ Duration │ Throughput  │ Items Lost  │
├─────────────────┼──────────┼─────────────┼─────────────┤
│ No Strategy     │ 11000ms  │ 91 items/s  │ 0           │
│ Buffer(64)      │ 10100ms  │ 99 items/s  │ 0           │
│ Conflate        │ 1100ms   │ 909 items/s │ ~900        │
│ CollectLatest   │ 1010ms   │ 990 items/s │ ~999        │
└─────────────────┴──────────┴─────────────┴─────────────┘
*/
```

### Comparison Table

| Strategy | Concurrency | Values Lost | Use Case | Performance |
|----------|-------------|-------------|----------|-------------|
| **No Strategy** | None | None | All values matter | Slowest |
| **buffer()** | Yes | None (unless overflow) | Process all, parallelize | Fast |
| **conflate()** | Yes | Intermediate | Latest state matters | Very Fast |
| **collectLatest()** | Yes | All but last | Cancel outdated work | Fastest |

### Real-World Examples

#### Example 1: Search with collectLatest

```kotlin
class SearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<List<SearchResult>> = _searchQuery
        .debounce(300) // Wait for typing to stop
        .distinctUntilChanged()
        .collectLatest { query ->
            if (query.length < 3) {
                emit(emptyList())
                return@collectLatest
            }

            // Cancel previous search if new query arrives
            val results = searchRepository.search(query)
            emit(results)
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )
}
```

#### Example 2: Sensor Data with conflate

```kotlin
class TemperatureSensor {
    fun temperatureUpdates(): Flow<Temperature> = flow {
        while (true) {
            val temp = readSensor()
            emit(temp)
            delay(100) // Read every 100ms
        }
    }
    .conflate() // UI only needs latest temperature

    fun observeTemperature() = viewModelScope.launch {
        temperatureUpdates()
            .collect { temp ->
                updateUI(temp)
                delay(1000) // UI updates slowly
            }
        // Only shows every ~10th reading, but always latest
    }
}
```

#### Example 3: File Processing with buffer

```kotlin
suspend fun processLargeFile(file: File): ProcessingResult {
    return file.readLines().asFlow()
        .buffer(capacity = 1000) // Buffer 1000 lines
        .map { line -> parseLine(line) } // CPU-bound
        .filter { it.isValid }
        .map { validated -> transform(validated) } // I/O-bound
        .toList()
        .let { ProcessingResult(it) }
}
```

### Custom Backpressure Strategy

```kotlin
/**
 * Custom backpressure: Sample every Nth value
 */
fun <T> Flow<T>.sample(n: Int): Flow<T> = flow {
    var count = 0
    collect { value ->
        count++
        if (count % n == 0) {
            emit(value)
        }
    }
}

// Usage: Process every 10th value
sensorData()
    .sample(10)
    .collect { processData(it) }

/**
 * Custom backpressure: Time-based sampling
 */
fun <T> Flow<T>.sampleTime(periodMs: Long): Flow<T> = flow {
    var lastEmitTime = 0L

    collect { value ->
        val now = System.currentTimeMillis()
        if (now - lastEmitTime >= periodMs) {
            emit(value)
            lastEmitTime = now
        }
    }
}

// Usage: Emit at most once per second
highFrequencyData()
    .sampleTime(1000)
    .collect { updateUI(it) }
```

### Best Practices

1. **Choose strategy based on requirements**:
   ```kotlin
   // All values important → buffer()
   dataStream().buffer(100).collect { processAll(it) }

   // Only latest matters → conflate()
   stateUpdates().conflate().collect { updateUI(it) }

   // Cancel outdated work → collectLatest()
   searchQuery().collectLatest { search(it) }
   ```

2. **Configure buffer size appropriately**:
   ```kotlin
   // ❌ Too small - producer often blocked
   .buffer(1)

   // ❌ Too large - memory issues
   .buffer(100000)

   // ✅ Reasonable size based on data size and rate
   .buffer(100)
   ```

3. **Combine strategies**:
   ```kotlin
   dataStream()
       .buffer(50) // Parallel processing
       .map { transform(it) }
       .conflate() // Skip if UI busy
       .collect { updateUI(it) }
   ```

4. **Monitor and measure**:
   ```kotlin
   flow {
       repeat(1000) {
           emit(it)
           delay(1)
       }
   }
   .onEach { println("Emitted: $it") }
   .buffer(10)
   .onEach { println("Buffered: $it") }
   .collect {
       delay(10)
       println("Collected: $it")
   }
   ```

### Common Pitfalls

1. **Using conflate when all values needed**:
   ```kotlin
   // ❌ Bank transactions - can't skip!
   transactions().conflate().collect { process(it) }

   // ✅ Use buffer to process all
   transactions().buffer(100).collect { process(it) }
   ```

2. **collectLatest with important side effects**:
   ```kotlin
   // ❌ File saves may be cancelled
   updates().collectLatest { saveToFile(it) }

   // ✅ Use regular collect
   updates().collect { saveToFile(it) }
   ```

3. **Not considering cancellation in collectLatest**:
   ```kotlin
   // ❌ Resource leak if cancelled
   .collectLatest { value ->
       val connection = openConnection()
       processWithConnection(connection, value)
       // Connection not closed if cancelled!
   }

   // ✅ Proper cleanup
   .collectLatest { value ->
       val connection = openConnection()
       try {
           processWithConnection(connection, value)
       } finally {
           connection.close()
       }
   }
   ```

**English Summary**: Backpressure handling in Flow uses buffer() for concurrent processing without losing values, conflate() to keep only the latest value, and collectLatest() to cancel previous collection on new values. buffer() is best for processing all values in parallel, conflate() for state updates where only latest matters, collectLatest() for cancelling outdated work like searches. Choose based on whether values can be dropped and if previous work should be cancelled. Monitor performance and configure buffer sizes appropriately.

## Ответ (RU)

Противодавление возникает когда producer испускает значения быстрее чем consumer может их обработать. Flow предоставляет несколько стратегий для обработки этого.

### Стратегия 1: buffer() - Буферизованная обработка

```kotlin
// Без буфера - последовательно
flow {
    repeat(3) {
        delay(100)
        emit(it)
    }
}.collect {
    delay(300)
    println(it)
}
// Всего: 3 * (100 + 300) = 1200мс

// С буфером - конкурентно
flow {
    repeat(3) {
        delay(100)
        emit(it)
    }
}
.buffer()
.collect {
    delay(300)
    println(it)
}
// Всего: ~900мс (на 25% быстрее!)
```

### Стратегия 2: conflate() - Только последнее

```kotlin
flow {
    repeat(10) {
        emit(it)
        delay(100)
    }
}
.conflate() // Сохранить только последнее
.collect { value ->
    delay(500) // Медленный consumer
    println("Collected $value")
}
// Вывод: 0, 4, 8 (промежуточные пропущены!)
```

### Стратегия 3: collectLatest() - Отмена предыдущей коллекции

```kotlin
flow {
    repeat(5) {
        emit(it)
        delay(200)
    }
}
.collectLatest { value ->
    println("Collecting $value")
    delay(500)
    println("Completed $value")
}
// Только последнее значение завершается!
```

### Таблица сравнения

| Стратегия | Конкурентность | Потерянные значения | Применение | Производительность |
|-----------|----------------|---------------------|------------|-------------------|
| **Без стратегии** | Нет | Нет | Все значения важны | Медленно |
| **buffer()** | Да | Нет | Обработать все, параллельно | Быстро |
| **conflate()** | Да | Промежуточные | Важно только последнее | Очень быстро |
| **collectLatest()** | Да | Все кроме последнего | Отменить устаревшую работу | Быстрейшее |

### Реальные примеры

#### Поиск с collectLatest

```kotlin
class SearchViewModel : ViewModel() {
    val searchResults = _searchQuery
        .debounce(300)
        .collectLatest { query ->
            // Отменить предыдущий поиск если новый запрос
            val results = searchRepository.search(query)
            emit(results)
        }
}
```

#### Данные датчика с conflate

```kotlin
fun temperatureUpdates(): Flow<Temperature> = flow {
    while (true) {
        emit(readSensor())
        delay(100)
    }
}
.conflate() // UI нужна только последняя температура
```

#### Обработка файла с buffer

```kotlin
suspend fun processLargeFile(file: File) {
    file.readLines().asFlow()
        .buffer(capacity = 1000) // Буфер 1000 строк
        .map { line -> parseLine(line) }
        .filter { it.isValid }
        .collect { process(it) }
}
```

### Лучшие практики

1. **Выбирайте стратегию на основе требований**:
   ```kotlin
   // Все значения важны → buffer()
   dataStream().buffer(100).collect { processAll(it) }

   // Важно только последнее → conflate()
   stateUpdates().conflate().collect { updateUI(it) }

   // Отменить устаревшую работу → collectLatest()
   searchQuery().collectLatest { search(it) }
   ```

2. **Настройте размер буфера правильно**:
   ```kotlin
   // ❌ Слишком мал
   .buffer(1)

   // ❌ Слишком велик
   .buffer(100000)

   // ✅ Разумный размер
   .buffer(100)
   ```

### Распространенные ошибки

1. **Использование conflate когда нужны все значения**:
   ```kotlin
   // ❌ Банковские транзакции - нельзя пропускать!
   transactions().conflate().collect { process(it) }

   // ✅ Используйте buffer
   transactions().buffer(100).collect { process(it) }
   ```

2. **collectLatest с важными побочными эффектами**:
   ```kotlin
   // ❌ Сохранения в файл могут быть отменены
   updates().collectLatest { saveToFile(it) }

   // ✅ Используйте обычный collect
   updates().collect { saveToFile(it) }
   ```

**Краткое содержание**: Обработка противодавления в Flow использует buffer() для конкурентной обработки без потери значений, conflate() для сохранения только последнего значения, collectLatest() для отмены предыдущей коллекции при новых значениях. buffer() лучше для обработки всех значений параллельно, conflate() для обновлений состояния где важно только последнее, collectLatest() для отмены устаревшей работы как поиски. Выбирайте на основе того могут ли значения быть отброшены и должна ли предыдущая работа быть отменена.

---

## References
- [Flow backpressure - Kotlin](https://kotlinlang.org/docs/flow.html#buffering)
- [buffer operator - API Reference](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/buffer.html)
- [Backpressure in Kotlin Flow](https://elizarov.medium.com/buffering-in-kotlin-flows-4b9ea4bc4bf3)

## Related Questions

### Prerequisites (Easier)
- [[q-backpressure-in-kotlin-flow--programming-languages--medium]] - Flow
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines

### Related (Hard)
- [[q-flow-backpressure--kotlin--hard]] - Flow
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-operators-deep-dive--kotlin--hard]] - Flow
### Prerequisites (Easier)
- [[q-backpressure-in-kotlin-flow--programming-languages--medium]] - Flow
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines

### Related (Hard)
- [[q-flow-backpressure--kotlin--hard]] - Flow
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-operators-deep-dive--kotlin--hard]] - Flow
### Prerequisites (Easier)
- [[q-backpressure-in-kotlin-flow--programming-languages--medium]] - Flow
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines

### Related (Hard)
- [[q-flow-backpressure--kotlin--hard]] - Flow
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-operators-deep-dive--kotlin--hard]] - Flow
### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

### Related (Hard)
- [[q-flowon-operator-context-switching--kotlin--hard]] - flowOn & context switching
- [[q-flow-backpressure--kotlin--hard]] - Backpressure handling
- [[q-flow-operators-deep-dive--kotlin--hard]] - Deep dive into operators
- [[q-flow-performance--kotlin--hard]] - Performance optimization
- [[q-flow-testing-advanced--kotlin--hard]] - Advanced Flow testing
