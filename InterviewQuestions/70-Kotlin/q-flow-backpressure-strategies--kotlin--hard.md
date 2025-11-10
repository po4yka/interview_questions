---
id: kotlin-055
title: "Flow Backpressure Strategies / Стратегии противодавления Flow"
aliases: ["Flow Backpressure Strategies", "Стратегии противодавления Flow"]

# Classification
topic: kotlin
subtopics: [flow, buffer, performance]
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
related: [c-flow, q-kotlin-flow-basics--kotlin--medium]

# Timestamps
created: 2023-10-11
updated: 2025-11-09

tags: [backpressure, buffer, difficulty/hard, flow, kotlin, performance]
---
# Вопрос (RU)
> Реализуйте обработку противодавления в `Flow`. Сравните стратегии `buffer`, `conflate` и `collectLatest` с производительными бенчмарками.

---

# Question (EN)
> Implement backpressure handling in `Flow`. Compare `buffer`, `conflate`, and `collectLatest` strategies with performance benchmarks.

## Ответ (RU)

Противодавление возникает, когда producer испускает значения быстрее, чем consumer может их обработать. По умолчанию в холодном `Flow` producer и consumer связаны: `emit` приостанавливается, пока `collect` не обработает значение. `Flow` предоставляет несколько стратегий для изменения этого поведения.

### Понимание противодавления

```kotlin
// Проблема: медленный collector заставляет producer ждать каждый emit
flow {
    repeat(100) {
        emit(it) // Быстрые эмиссии в коде, но будут приостанавливаться из-за медленного collector-а
        println("Emitted $it")
    }
}
.collect { value ->
    delay(100) // Медленная обработка
    println("Processed $value")
}
// Producer приостанавливается на каждом emit, ожидая collector
```

### Стратегия 1: buffer() - Буферизованная обработка

Оператор `buffer` добавляет буфер между producer и consumer, позволяя им работать конкурентно.

```kotlin
public fun <T> Flow<T>.buffer(
    capacity: Int = BUFFERED,
    onBufferOverflow: BufferOverflow = BufferOverflow.SUSPEND
): Flow<T>
```

#### Базовое использование buffer

```kotlin
fun demonstrateBuffer() = runBlocking {
    val startTime = System.currentTimeMillis()

    // Без буфера - последовательная работа
    println("=== WITHOUT BUFFER ===")
    flow {
        repeat(3) {
            delay(100) // Producer: 100мс
            emit(it)
            println("[${timestamp(startTime)}] Emitted $it")
        }
    }
    .collect { value ->
        delay(300) // Consumer: 300мс
        println("[${timestamp(startTime)}] Collected $value")
    }
    // Итого: 3 * (100 + 300) ≈ 1200мс

    delay(500)

    // С буфером - producer и consumer могут выполняться параллельно
    println("\n=== WITH BUFFER ===")
    val startTime2 = System.currentTimeMillis()
    flow {
        repeat(3) {
            delay(100)
            emit(it)
            println("[${timestamp(startTime2)}] Emitted $it")
        }
    }
    .buffer() // Ослабляет связь между producer и consumer
    .collect { value ->
        delay(300)
        println("[${timestamp(startTime2)}] Collected $value")
    }
    // Итого: примерно max(3*100, 3*300) плюс накладные расходы ≈ 900–1000мс (иллюстративно)
}

fun timestamp(start: Long) = System.currentTimeMillis() - start
```

#### Стратегии переполнения буфера (пример)

```kotlin
// 1. SUSPEND (по умолчанию) - при переполнении буфера приостанавливаем producer
flow {
    repeat(10) { emit(it) }
}
.buffer(capacity = 3, onBufferOverflow = BufferOverflow.SUSPEND)
.collect { delay(100); println(it) }

// 2. DROP_OLDEST - отбрасываем самое старое значение при переполнении
flow {
    repeat(10) { emit(it) }
}
.buffer(capacity = 3, onBufferOverflow = BufferOverflow.DROP_OLDEST)
.collect { delay(100); println(it) }
// Некоторые ранние значения будут отброшены, если consumer слишком медленный.

// 3. DROP_LATEST - отбрасываем новое значение при переполнении
flow {
    repeat(10) { emit(it) }
}
.buffer(capacity = 3, onBufferOverflow = BufferOverflow.DROP_LATEST)
.collect { delay(100); println(it) }
// Некоторые из последних эмиссий будут отброшены при полном буфере.
```

### Стратегия 2: conflate() - Только последнее значение

Оператор `conflate` при медленном collector сохраняет только последнее значение, пропуская промежуточные. Концептуально это похоже на сбор в отдельной корутине, где до медленного collector-а доходит только актуальное значение.

```kotlin
fun demonstrateConflate() = runBlocking {
    val startTime = System.currentTimeMillis()

    flow {
        repeat(10) {
            emit(it)
            println("[${timestamp(startTime)}] Emitted $it")
            delay(100)
        }
    }
    .conflate() // Хранит только последнее, когда collector занят
    .collect { value ->
        println("[${timestamp(startTime)}] Collecting $value")
        delay(500) // Медленный consumer
        println("[${timestamp(startTime)}] Collected $value")
    }
}

/*
Типичное поведение:
- При медленном consumer часть промежуточных значений пропускается.
*/
```

### Стратегия 3: collectLatest() - Отмена предыдущей обработки

Оператор `collectLatest` отменяет блок обработки предыдущего значения при поступлении нового. Значения по-прежнему эмитятся, но их обработка может быть отменена.

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
        delay(500) // Медленная обработка
        println("[${timestamp(startTime)}] Completed $value")
    }
}

/*
Типичное поведение:
- При каждом новом значении блок collectLatest для предыдущего значения отменяется.
- Обычно до завершения доходит только последнее значение.
*/
```

### Сравнение стратегий (концептуально)

| Стратегия | Конкурентность | Потерянные значения / отмена | Применение | Производительность |
|-----------|----------------|------------------------------|------------|--------------------|
| **Без стратегии** | Нет | Нет | Нужны все значения, строгий порядок | Самое медленное при медленном consumer |
| **buffer()** | Да | Нет (если не задан `onBufferOverflow`) | Обработать все значения, ослабить связь | Быстрее при правильном буфере |
| **conflate()** | Да | Пропускает промежуточные | Важно только последнее состояние | Высокая пропускная способность |
| **collectLatest()** | Да | Отменяет обработку старых | Отмена устаревшей работы | Меньше бесполезной работы |

### Сравнение производительности (иллюстративный бенчмарк)

Ниже приведён иллюстративный пример бенчмарка. Конкретные числа зависят от окружения и таймингов; важно относительное поведение стратегий.

```kotlin
data class BenchmarkResult(
    val strategy: String,
    val durationMs: Long
)

suspend fun benchmark(
    name: String,
    block: suspend () -> Unit
): BenchmarkResult {
    val start = System.currentTimeMillis()
    block()
    val duration = System.currentTimeMillis() - start
    return BenchmarkResult(name, duration)
}

suspend fun benchmarkStrategies(): List<BenchmarkResult> {
    val itemCount = 1000
    val emitDelayMs = 1L
    val collectDelayMs = 10L

    return listOf(
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
        benchmark("Conflate") {
            flow {
                repeat(itemCount) {
                    delay(emitDelayMs)
                    emit(it)
                }
            }
            .conflate()
            .collect {
                delay(collectDelayMs)
            }
        },
        benchmark("CollectLatest") {
            flow {
                repeat(itemCount) {
                    delay(emitDelayMs)
                    emit(it)
                }
            }
            .collectLatest {
                delay(collectDelayMs)
            }
        }
    )
}
```

### Реальные примеры

#### Пример 1: Поиск с collectLatest

```kotlin
class SearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<List<SearchResult>> = _searchQuery
        .debounce(300)
        .distinctUntilChanged()
        .flatMapLatest { query ->
            if (query.length < 3) {
                flowOf(emptyList())
            } else {
                // При новом запросе предыдущая работа поиска отменяется
                flow {
                    emit(searchRepository.search(query))
                }
            }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )
}
```

#### Пример 2: Данные датчика с conflate

```kotlin
class TemperatureSensor {
    fun temperatureUpdates(): Flow<Temperature> = flow {
        while (true) {
            val temp = readSensor()
            emit(temp)
            delay(100) // Чтение каждые 100 мс
        }
    }
    .conflate() // UI нужна только последняя температура

    fun observeTemperature() = viewModelScope.launch {
        temperatureUpdates()
            .collect { temp ->
                updateUI(temp)
                delay(1000) // Медленные обновления UI, промежуточные значения могут пропускаться
            }
    }
}
```

#### Пример 3: Обработка файла с buffer

```kotlin
suspend fun processLargeFile(file: File) {
    file.readLines().asFlow()
        .buffer(capacity = 1000) // Буфер до 1000 строк, развязываем чтение и обработку
        .map { line -> parseLine(line) }
        .filter { it.isValid }
        .collect { process(it) }
}
```

### Пользовательские стратегии противодавления

```kotlin
/**
 * Пользовательская стратегия: брать каждое N-е значение.
 * Осознанно отбрасывает часть значений для снижения нагрузки.
 */
fun <T> Flow<T>.sampleEvery(n: Int): Flow<T> = flow {
    require(n > 0)
    var count = 0
    collect { value ->
        count++
        if (count % n == 0) {
            emit(value)
        }
    }
}

// Использование: обрабатывать каждое 10-е значение
sensorData()
    .sampleEvery(10)
    .collect { processData(it) }

/**
 * Пользовательская стратегия: выборка по времени.
 */
fun <T> Flow<T>.sampleTime(periodMs: Long): Flow<T> = flow {
    require(periodMs > 0)
    var lastEmitTime = 0L

    collect { value ->
        val now = System.currentTimeMillis()
        if (now - lastEmitTime >= periodMs) {
            emit(value)
            lastEmitTime = now
        }
    }
}

// Использование: не чаще раза в секунду
highFrequencyData()
    .sampleTime(1000)
    .collect { updateUI(it) }
```

### Лучшие практики

1. **Выбирайте стратегию по семантике**:
   ```kotlin
   // Все значения важны → buffer()
   dataStream().buffer(100).collect { processAll(it) }

   // Важно только последнее → conflate()
   stateUpdates().conflate().collect { updateUI(it) }

   // Нужно отменять устаревшую работу → collectLatest()/flatMapLatest
   searchQuery().collectLatest { search(it) }
   ```

2. **Настраивайте размер буфера осознанно**:
   ```kotlin
   .buffer(1)      // слишком мал — частые приостановки producer-а
   .buffer(100000) // слишком велик — риск по памяти
   .buffer(100)    // пример разумного компромисса
   ```

3. **Комбинируйте стратегии, когда это оправдано**:
   ```kotlin
   dataStream()
       .buffer(50)   // параллелим producer/consumer
       .map { transform(it) }
       .conflate()   // пропускаем, если downstream (например, UI) не успевает
       .collect { updateUI(it) }
   ```

4. **Измеряйте и наблюдайте поведение**:
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

### Распространенные ошибки

1. **Использование conflate, когда нужны все значения**:
   ```kotlin
   // Банковские транзакции — нельзя пропускать!
   transactions().conflate().collect { process(it) }

   // Используйте buffer, чтобы не терять значения
   transactions().buffer(100).collect { process(it) }
   ```

2. **Использование collectLatest для критичных побочных эффектов**:
   ```kotlin
   // Сохранения в файл могут быть отменены
   updates().collectLatest { saveToFile(it) }

   // Используйте обычный collect для гарантированного завершения
   updates().collect { saveToFile(it) }
   ```

3. **Игнорирование отмены в collectLatest (утечки ресурсов)**:
   ```kotlin
   // Потенциальная утечка ресурса при отмене
   .collectLatest { value ->
       val connection = openConnection()
       processWithConnection(connection, value)
       // При отмене соединение может не закрыться!
   }

   // Правильная очистка
   .collectLatest { value ->
       val connection = openConnection()
       try {
           processWithConnection(connection, value)
       } finally {
           connection.close()
       }
   }
   ```

**Краткое содержание**: Противодавление в `Flow` контролируется выбором операторов: `buffer()` развязывает producer и consumer без потерь значений (если не задана политика сброса), `conflate()` пропускает промежуточные значения и оставляет только последнее, `collectLatest()` отменяет обработку старых значений при появлении новых. Также возможны пользовательские стратегии (например, семплирование). Выбор зависит от допустимости потерь значений и необходимости отмены уже начатой работы; поведение следует проверять измерениями, а не предположениями.

---

## Answer (EN)

Backpressure occurs when a producer emits values faster than a consumer can process them. In cold `Flow`s, by default, the producer and consumer are coupled: `emit` suspends until the downstream processing of that value completes. `Flow` provides several operators to change this backpressure behavior.

### Understanding Backpressure

```kotlin
// Problem: Slow collector causes producer to wait on each emit
flow {
    repeat(100) {
        emit(it) // Fast emission in code, but will suspend on slow collector
        println("Emitted $it")
    }
}
.collect { value ->
    delay(100) // Slow processing
    println("Processed $value")
}
// Producer is suspended on each emit waiting for collector
```

### Strategy 1: buffer() - Buffered Processing

The `buffer` operator adds a buffer between producer and consumer, allowing them to run concurrently.

```kotlin
public fun <T> Flow<T>.buffer(
    capacity: Int = BUFFERED,
    onBufferOverflow: BufferOverflow = BufferOverflow.SUSPEND
): Flow<T>
```

#### Basic Buffer Usage

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
    // Total: 3 * (100 + 300) ≈ 1200ms

    delay(500)

    // With buffer - producer and consumer can run concurrently
    println("\n=== WITH BUFFER ===")
    val startTime2 = System.currentTimeMillis()
    flow {
        repeat(3) {
            delay(100)
            emit(it)
            println("[${timestamp(startTime2)}] Emitted $it")
        }
    }
    .buffer() // Decouples producer/consumer
    .collect { value ->
        delay(300)
        println("[${timestamp(startTime2)}] Collected $value")
    }
    // Total: approximately max(3*100, 3*300) plus overhead ≈ 900–1000ms (illustrative)
}

fun timestamp(start: Long) = System.currentTimeMillis() - start
```

#### Buffer Overflow Strategies (Illustrative)

```kotlin
// 1. SUSPEND (default) - suspend producer when buffer is full
flow {
    repeat(10) { emit(it) }
}
.buffer(capacity = 3, onBufferOverflow = BufferOverflow.SUSPEND)
.collect { delay(100); println(it) }

// 2. DROP_OLDEST - drop oldest buffered value when full
flow {
    repeat(10) { emit(it) }
}
.buffer(capacity = 3, onBufferOverflow = BufferOverflow.DROP_OLDEST)
.collect { delay(100); println(it) }
// Some earliest buffered values will be dropped when consumer is too slow.

// 3. DROP_LATEST - drop newly emitted value when full
flow {
    repeat(10) { emit(it) }
}
.buffer(capacity = 3, onBufferOverflow = BufferOverflow.DROP_LATEST)
.collect { delay(100); println(it) }
// Some of the latest emissions will be dropped when buffer is full.
```

### Strategy 2: conflate() - Keep Latest Only

The `conflate` operator keeps only the most recent value when the collector is slow, skipping intermediate values. Conceptually, it behaves like collecting in a separate coroutine and always delivering only the latest available value to the slow collector.

```kotlin
fun demonstrateConflate() = runBlocking {
    val startTime = System.currentTimeMillis()

    flow {
        repeat(10) {
            emit(it)
            println("[${timestamp(startTime)}] Emitted $it")
            delay(100)
        }
    }
    .conflate() // Keep only latest when collector is busy
    .collect { value ->
        println("[${timestamp(startTime)}] Collecting $value")
        delay(500) // Slow consumer
        println("[${timestamp(startTime)}] Collected $value")
    }
}

/*
Typical behavior:
- Several intermediate values are skipped when consumer is slower than producer.
*/
```

### Strategy 3: collectLatest() - Cancel Previous Collection

The `collectLatest` operator cancels the block for the previous value when a new value arrives. Values themselves are still emitted by upstream, but their processing can be cancelled.

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
Typical behavior:
- For each new value, the previous collectLatest block is cancelled.
- Usually only the last value's work completes.
*/
```

### Performance Comparison (Illustrative Benchmark)

Below is an illustrative benchmark-style snippet. Exact numbers depend on environment and timing; key is relative behavior.

```kotlin
data class BenchmarkResult(
    val strategy: String,
    val durationMs: Long
)

suspend fun benchmark(
    name: String,
    block: suspend () -> Unit
): BenchmarkResult {
    val start = System.currentTimeMillis()
    block()
    val duration = System.currentTimeMillis() - start
    return BenchmarkResult(name, duration)
}

suspend fun benchmarkStrategies(): List<BenchmarkResult> {
    val itemCount = 1000
    val emitDelayMs = 1L
    val collectDelayMs = 10L

    return listOf(
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
        benchmark("Conflate") {
            flow {
                repeat(itemCount) {
                    delay(emitDelayMs)
                    emit(it)
                }
            }
            .conflate()
            .collect {
                delay(collectDelayMs)
            }
        },
        benchmark("CollectLatest") {
            flow {
                repeat(itemCount) {
                    delay(emitDelayMs)
                    emit(it)
                }
            }
            .collectLatest {
                delay(collectDelayMs)
            }
        }
    )
}
```

### Comparison Table

| Strategy | Concurrency | Values Dropped / Cancelled | Use Case | Performance (conceptual) |
|----------|-------------|----------------------------|----------|--------------------------|
| **No Strategy** | None | None | All values must be processed, strict ordering | Slowest when consumer is slow |
| **buffer()** | Yes | None (unless overflow policy drops) | Process all values, decouple producer | Faster when buffering is effective |
| **conflate()** | Yes | Skips intermediate values | Latest state-only updates (e.g., UI state) | Very high throughput, fewer processed items |
| **collectLatest()** | Yes | Cancels work for previous values | Cancel outdated work (e.g., search) | Avoids wasted work on old values |

### Real-World Examples

#### Example 1: Search with collectLatest

```kotlin
class SearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<List<SearchResult>> = _searchQuery
        .debounce(300) // Wait for typing to pause
        .distinctUntilChanged()
        .flatMapLatest { query ->
            if (query.length < 3) {
                flowOf(emptyList())
            } else {
                flow {
                    // New query cancels previous flow work
                    emit(searchRepository.search(query))
                }
            }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )
}
```

#### Example 2: Sensor Data with Conflate

```kotlin
class TemperatureSensor {
    fun temperatureUpdates(): Flow<Temperature> = flow {
        while (true) {
            val temp = readSensor()
            emit(temp)
            delay(100) // Read every 100ms
        }
    }
    .conflate() // UI only needs the latest temperature

    fun observeTemperature() = viewModelScope.launch {
        temperatureUpdates()
            .collect { temp ->
                updateUI(temp)
                delay(1000) // UI updates slowly, intermediate values may be skipped
            }
    }
}
```

#### Example 3: File Processing with Buffer

```kotlin
suspend fun processLargeFile(file: File): ProcessingResult {
    return file.readLines().asFlow()
        .buffer(capacity = 1000) // Buffer 1000 lines to decouple reading and processing
        .map { line -> parseLine(line) } // CPU-bound
        .filter { it.isValid }
        .map { validated -> transform(validated) } // Potentially I/O-bound
        .toList()
        .let { ProcessingResult(it) }
}
```

### Custom Backpressure Strategy

```kotlin
/**
 * Custom backpressure: Sample every Nth value.
 * This intentionally drops values to reduce load.
 */
fun <T> Flow<T>.sampleEvery(n: Int): Flow<T> = flow {
    require(n > 0)
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
    .sampleEvery(10)
    .collect { processData(it) }

/**
 * Custom backpressure: Time-based sampling.
 */
fun <T> Flow<T>.sampleTime(periodMs: Long): Flow<T> = flow {
    require(periodMs > 0)
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

1. **Choose strategy based on semantics**:
   ```kotlin
   // All values important → buffer()
   dataStream().buffer(100).collect { processAll(it) }

   // Only latest matters → conflate()
   stateUpdates().conflate().collect { updateUI(it) }

   // Cancel outdated work → collectLatest()/flatMapLatest
   searchQuery().collectLatest { search(it) }
   ```

2. **Configure buffer size appropriately**:
   ```kotlin
   .buffer(1)      // Very small - producer often blocked
   .buffer(100000) // Very large - memory risk
   .buffer(100)    // Example of a reasonable compromise
   ```

3. **Combine strategies when appropriate**:
   ```kotlin
   dataStream()
       .buffer(50)   // Parallelize producer/consumer
       .map { transform(it) }
       .conflate()   // Skip if downstream (e.g., UI) is busy
       .collect { updateUI(it) }
   ```

4. **Measure and observe behavior**:
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

1. **Using conflate when every value is required**:
   ```kotlin
   // Bank transactions - can't skip!
   transactions().conflate().collect { process(it) }

   // Use buffer to avoid dropping
   transactions().buffer(100).collect { process(it) }
   ```

2. **Using collectLatest for important side effects**:
   ```kotlin
   // File saves may be cancelled
   updates().collectLatest { saveToFile(it) }

   // Use regular collect when completion must be guaranteed
   updates().collect { saveToFile(it) }
   ```

3. **Ignoring cancellation in collectLatest**:
   ```kotlin
   // Potential resource leak if cancelled
   .collectLatest { value ->
       val connection = openConnection()
       processWithConnection(connection, value)
       // Connection not closed if cancelled!
   }

   // Proper cleanup
   .collectLatest { value ->
       val connection = openConnection()
       try {
           processWithConnection(connection, value)
       } finally {
           connection.close()
       }
   }
   ```

**English Summary**: Backpressure handling in `Flow` relies on choosing the right operator: `buffer()` decouples producer and consumer without dropping values unless you opt into overflow policies, `conflate()` keeps only the latest value when the collector is slow and skips intermediates, `collectLatest()` cancels ongoing work for previous values when new ones arrive, and you can implement custom sampling strategies. Select based on whether values may be dropped and whether previous work should be cancelled; validate behavior with measurement.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Flow backpressure - Kotlin](https://kotlinlang.org/docs/flow.html#buffering)
- [buffer operator - API Reference](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/buffer.html)
- [Backpressure in Kotlin Flow](https://elizarov.medium.com/buffering-in-kotlin-flows-4b9ea4bc4bf3)
- [[c-flow]]

## Related Questions

### Related (Hard)
- [[q-flow-backpressure--kotlin--hard]] - Flow
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-operators-deep-dive--kotlin--hard]] - Flow

### Prerequisites (Easier)
-  - Flow
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction
