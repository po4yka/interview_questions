---
anki_cards:
- slug: q-flow-operators-deep-dive--kotlin--hard-0-en
  language: en
  anki_id: 1768326287555
  synced_at: '2026-01-23T17:03:51.197735'
- slug: q-flow-operators-deep-dive--kotlin--hard-0-ru
  language: ru
  anki_id: 1768326287580
  synced_at: '2026-01-23T17:03:51.199624'
---
# Question (EN)
> Implement custom `Flow` operators. Explain `flatMapConcat` vs `flatMapMerge` vs `flatMapLatest` with practical examples and performance characteristics.

## Ответ (RU)

Операторы `Flow` — это функции, которые трансформируют потоки различными способами. Понимание различий между вариантами `flatMap` критически важно для построения эффективных асинхронных конвейеров данных. См. также [[c-kotlin]] и [[c-flow]].

### Обзор Вариантов FlatMap

Три оператора `flatMap` различаются по обработке конкурентного выполнения и порядка:

| Оператор | Конкурентность | Порядок | Отмена | Применение |
|----------|----------------|---------|--------|------------|
| **flatMapConcat** | Последовательно (по 1) | Сохраняется | Ждет завершения текущего | Требуется строгая последовательность |
| **flatMapMerge** | Конкурентно (настраивается) | Не гарантируется | Внутренние потоки независимы | Параллельная обработка |
| **flatMapLatest** | Только последний активный | Не гарантируется | Немедленно отменяет предыдущие | Поиск, только последние данные |

(Реальные реализации этих операторов находятся в kotlinx.coroutines.flow; дальнейшие примеры показывают эквивалентные по смыслу композиции, а не заменяют стандартные операторы.)

### 1. flatMapConcat - Последовательная Обработка

**Поведение**: Обрабатывает по одному внутреннему потоку за раз, ожидая завершения каждого перед началом следующего. Порядок элементов внешнего потока сохраняется.

```kotlin
// Иллюстративный алиас, эквивалентный стандартному flatMapConcat
fun <T, R> Flow<T>.myFlatMapConcat(transform: suspend (T) -> Flow<R>): Flow<R> =
    map(transform).flattenConcat()
```

// Пример: последовательные API вызовы

```kotlin
data class User(val id: Int, val name: String)
data class UserDetails(val userId: Int, val email: String, val phone: String)

fun getUserIds(): Flow<Int> = flow {
    emit(1)
    delay(100)
    emit(2)
    delay(100)
    emit(3)
}

fun fetchUserDetails(userId: Int): Flow<UserDetails> = flow {
    delay(200) // Симуляция сетевого вызова
    emit(UserDetails(userId, "user$userId@example.com", "555-000$userId"))
    println("Получены данные пользователя $userId")
}

fun main() = runBlocking {
    val startTime = System.currentTimeMillis()

    getUserIds()
        .flatMapConcat { userId ->
            fetchUserDetails(userId)
        }
        .collect { details ->
            println("Получено: $details (прошло: ${System.currentTimeMillis() - startTime}ms)")
        }
}
```

**Когда использовать**:
- Порядок должен быть сохранен
- Каждая операция логически зависит от завершения предыдущей
- Последовательная загрузка страниц
- Обработка транзакций

### 2. flatMapMerge - Конкурентная Обработка

**Поведение**: Обрабатывает несколько внутренних потоков одновременно с настраиваемым лимитом конкурентности. Элементы приходят по мере готовности, порядок исходного потока не гарантируется.

```kotlin
// Иллюстративный алиас, эквивалентный стандартному flatMapMerge
fun <T, R> Flow<T>.myFlatMapMerge(
    concurrency: Int = DEFAULT_CONCURRENCY,
    transform: suspend (T) -> Flow<R>
): Flow<R> =
    map(transform).flattenMerge(concurrency)
```

// Пример: параллельные API вызовы

```kotlin
fun main() = runBlocking {
    val startTime = System.currentTimeMillis()

    getUserIds()
        .flatMapMerge(concurrency = 2) { userId ->
            fetchUserDetails(userId)
        }
        .collect { details ->
            println("Получено: $details (прошло: ${System.currentTimeMillis() - startTime}ms)")
        }
}
```

/*
Примерный вывод (конкурентно с concurrency=2):
Получены данные пользователя 1
Получены данные пользователя 2  // Запущен параллельно
Получено: UserDetails(1, ...) (прошло: ~300ms)
Получено: UserDetails(2, ...) (прошло: ~300ms)
Получены данные пользователя 3  // Запущен после освобождения слота
Получено: UserDetails(3, ...) (прошло: ~500ms)
Итого: быстрее чем строго последовательная обработка.
*/

**Практический пример с обработкой ошибок**:

```kotlin
// Пакетная обработка с контролем конкурентности
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
    delay(100) // Симуляция загрузки
    return "https://cdn.example.com/${UUID.randomUUID()}"
}
```

**Когда использовать**:
- Независимые операции, которые могут выполняться параллельно
- Пакетная обработка
- Множественные API вызовы
- I/O операции
- Нужна максимальная пропускная способность

### 3. flatMapLatest - Только Последнее Значение

**Поведение**: При поступлении нового значения из внешнего потока отменяет предыдущий внутренний поток и начинает новый. Гарантируется, что в каждый момент времени исполняется только один внутренний поток (для последнего значения).

```kotlin
// Иллюстративный алиас, эквивалентный стандартному flatMapLatest
fun <T, R> Flow<T>.myFlatMapLatest(transform: suspend (T) -> Flow<R>): Flow<R> =
    transformLatest { value ->
        emitAll(transform(value))
    }
```

// Пример: поисковый запрос с отменой

```kotlin
data class SearchResult(val query: String, val results: List<String>)

fun searchFlow(query: String): Flow<SearchResult> = flow {
    println("Начало поиска: $query")
    delay(300) // Симуляция API вызова
    emit(
        SearchResult(
            query,
            listOf("$query результат 1", "$query результат 2")
        )
    )
    println("Поиск завершен: $query")
}

fun main() = runBlocking {
    val searchQueries = flow {
        emit("kot")
        delay(100)
        emit("kotl")  // Отменяет поиск "kot"
        delay(100)
        emit("kotli") // Отменяет поиск "kotl"
        delay(500)    // Ждем завершения последнего
    }

    searchQueries
        .flatMapLatest { query ->
            searchFlow(query)
        }
        .collect { result ->
            println("Отображение результатов для: ${result.query}")
        }
}
```

/*
Вывод:
Начало поиска: kot
Начало поиска: kotl      // Отменяет "kot"
Начало поиска: kotli     // Отменяет "kotl"
Поиск завершен: kotli
Отображение результатов для: kotli
Завершается только последний поиск.
*/

**Реальная реализация - Поиск с debounce**:

```kotlin
class SearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<List<SearchResult>> = _searchQuery
        .debounce(300) // Ждем, пока пользователь закончит печатать
        .filter { it.length >= 3 } // Минимальная длина запроса
        .distinctUntilChanged() // Запускать поиск только при изменении строки
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

**Когда использовать**:
- Поиск/автодополнение
- Фильтрация в реальном времени
- Обновления локации
- Важно только последнее значение
- Нужна отмена устаревших запросов

### Создание Пользовательских Операторов Flow

#### Пример 1: Повтор С Экспоненциальной Задержкой

```kotlin
fun <T> Flow<T>.retryWithExponentialBackoff(
    maxRetries: Int = 3,
    initialDelayMs: Long = 1000,
    maxDelayMs: Long = 10000,
    factor: Double = 2.0
): Flow<T> =
    this.retryWhen { cause, attempt ->
        if (attempt >= maxRetries) return@retryWhen false

        val delayTime =
            (initialDelayMs * factor.pow(attempt.toDouble()))
                .toLong()
                .coerceAtMost(maxDelayMs)

        delay(delayTime)
        println("Повтор #${attempt + 1} через ${delayTime}ms из-за: ${cause.message}")
        true
    }
```

#### Пример 2: Оператор Окна (фиксированный Размер И шаг)

Ниже исправленный вариант для фиксированного окна с шагом `windowSlide`, поддерживающий как перекрывающиеся, так и неперекрывающиеся окна.

```kotlin
fun <T> Flow<T>.window(
    windowSize: Int,
    windowSlide: Int = windowSize
): Flow<List<T>> = flow {
    require(windowSize > 0) { "Window size must be positive" }
    require(windowSlide > 0) { "Window slide must be positive" }

    val buffer = ArrayDeque<T>(windowSize)
    var sinceLastEmit = 0

    collect { value ->
        buffer.addLast(value)
        if (buffer.size < windowSize) return@collect

        if (sinceLastEmit == 0) {
            // первое или очередное окно
            emit(buffer.toList())
            sinceLastEmit = 1
        } else if (sinceLastEmit == windowSlide) {
            // дошли до шага: сдвигаем окно и эмитим снова
            repeat(windowSlide) {
                if (buffer.isNotEmpty()) buffer.removeFirst()
            }
            // после сдвига может стать меньше windowSize — проверяем
            if (buffer.size == windowSize) {
                emit(buffer.toList())
                sinceLastEmit = 1
            } else {
                sinceLastEmit = 0
            }
            return@collect
        } else {
            sinceLastEmit++
        }

        // поддерживаем размер буфера не больше windowSize при скользящих окнах
        if (buffer.size > windowSize) {
            buffer.removeFirst()
        }
    }
}
```

// Использование: скользящее среднее с шагом 1

```kotlin
flowOf(1, 2, 3, 4, 5, 6, 7, 8)
    .window(windowSize = 3, windowSlide = 1)
    .map { window -> window.average() }
    .collect { avg -> println("Скользящее среднее: $avg") }
```

(Этот оператор показан как учебный пример. В продакшене имеет смысл дополнительно аккуратно определить поведение на границах и для всех комбинаций windowSize/windowSlide.)

#### Пример 3: Ограничение Частоты

```kotlin
fun <T> Flow<T>.rateLimit(
    count: Int,
    duration: Duration
): Flow<T> = flow {
    require(count > 0) { "count must be positive" }
    require(!duration.isNegative()) { "duration must be non-negative" }

    val timestamps = ArrayDeque<Long>(count)
    val windowNanos = duration.inWholeNanoseconds

    collect { value ->
        var now = System.nanoTime()

        // Удаляем устаревшие метки в окне
        while (timestamps.isNotEmpty() &&
            now - timestamps.first() >= windowNanos
        ) {
            timestamps.removeFirst()
        }

        // Если достигли лимита — ждем освобождение слота
        if (timestamps.size >= count) {
            val oldest = timestamps.first()
            val waitNanos = windowNanos - (now - oldest)
            if (waitNanos > 0) {
                delay(waitNanos.nanos)
            }
            timestamps.removeFirst()
            now = System.nanoTime()
        }

        timestamps.addLast(now)
        emit(value)
    }
}
```

### Сравнение Производительности

```kotlin
// Условный бенчмарк различных вариантов flatMap
suspend fun benchmarkFlatMapVariants() {
    val itemCount = 100
    val processingTime = 10L // мс на элемент

    // flatMapConcat: все элементы обрабатываются последовательно
    var startTime = System.currentTimeMillis()
    (1..itemCount).asFlow()
        .flatMapConcat { flowOf(it).onEach { delay(processingTime) } }
        .collect()
    println("flatMapConcat: ${System.currentTimeMillis() - startTime}ms") // ~1000ms

    // flatMapMerge с concurrency=10: до 10 внутренних потоков одновременно
    startTime = System.currentTimeMillis()
    (1..itemCount).asFlow()
        .flatMapMerge(10) { flowOf(it).onEach { delay(processingTime) } }
        .collect()
    println("flatMapMerge(10): ${System.currentTimeMillis() - startTime}ms") // может быть ~100ms

    // flatMapLatest: предыдущие внутренние потоки отменяются,
    // фактическое время зависит от частоты эмиссий внешнего потока.
    startTime = System.currentTimeMillis()
    (1..itemCount).asFlow()
        .onEach { delay(processingTime) }
        .flatMapLatest { value ->
            flowOf(value).onEach { delay(processingTime) }
        }
        .collect()
    println("flatMapLatest: ${System.currentTimeMillis() - startTime}ms")
}
```

Комментарий: значения времени для `flatMapMerge` и `flatMapLatest` зависят от конкретного сценария (частота эмиссий, задержки, concurrency) и приведены только для иллюстрации относительного поведения.

### Лучшие Практики

1. Выбирайте правильный оператор:
   - Нужен порядок → `flatMapConcat`
   - Нужна высокая пропускная способность → `flatMapMerge`
   - Важно только последнее значение → `flatMapLatest`

2. Контролируйте конкурентность:
   ```kotlin
   // Избегайте неограниченной конкурентности
   .flatMapMerge(concurrency = Int.MAX_VALUE) // Опасно
   .flatMapMerge(concurrency = 10) // Контролируемо
   ```

3. Учитывайте ограничения ресурсов:
   ```kotlin
   // Ограничение числа конкурентных сетевых запросов
   val maxConcurrentRequests = 5
   requests.flatMapMerge(maxConcurrentRequests) { makeRequest(it) }
   ```

4. Обрабатывайте ошибки правильно:
   ```kotlin
   .flatMapMerge { item ->
       flow { emit(process(item)) }
           .catch { e -> emit(defaultValue) }
   }
   ```

5. Учитывайте память:
   - `flatMapMerge` держит несколько внутренних потоков и буферов
   - `flatMapLatest` обычно использует меньше памяти (один активный поток)
   - `flatMapConcat` предсказуем по использованию памяти, так как обрабатывает по одному

### Распространенные Ошибки

1. Использование flatMapConcat вместо flatMapMerge:
   ```kotlin
   // Медленно: обработка 1000 элементов строго последовательно
   (1..1000).asFlow().flatMapConcat { fetchData(it) }

   // Быстрее: обработка до 10 одновременно
   (1..1000).asFlow().flatMapMerge(10) { fetchData(it) }
   ```

2. Игнорирование отмены с flatMapLatest:
   ```kotlin
   // Потенциальная утечка ресурсов, если не учитывать отмену
   searchQuery.flatMapLatest { query ->
       flow {
           val connection = openConnection() // Должен корректно отменяться
           // ...
       }
   }

   // Правильная отмена (cleanup в finally)
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

3. Не настроена конкурентность:
   ```kotlin
   // Значение по умолчанию может быть не оптимальным
   .flatMapMerge { ... }

   // Явная настройка под сценарий
   .flatMapMerge(concurrency = 3) { ... }
   ```

**Краткое содержание**: Операторы `Flow` трансформируют потоки разными способами. `flatMapConcat` обрабатывает последовательно, сохраняя порядок, `flatMapMerge` объединяет конкурентно с настраиваемой степенью параллелизма, а `flatMapLatest` отменяет предыдущие внутренние потоки, оставляя только последний активный. Пользовательские операторы создаются комбинированием существующих операторов и аккуратной работой с отменой, ресурсами и конкурентностью. Выбор оператора зависит от требований к порядку, производительности и ограничениям ресурсов.

---

## Answer (EN)

`Flow` operators are functions that transform flows in various ways. Understanding the differences between `flatMap` variants is crucial for building efficient asynchronous data pipelines. See also [[c-kotlin]] and [[c-flow]].

### FlatMap Variants Overview

The three `flatMap` operators differ in how they handle concurrent execution and ordering:

| Operator | Concurrency | Ordering | Cancellation | Use Case |
|----------|-------------|----------|--------------|----------|
| **flatMapConcat** | Sequential (1 at a time) | Preserved | Waits for current inner flow | Strict sequencing |
| **flatMapMerge** | Concurrent (configurable) | Not guaranteed | Inner flows independent | Parallel processing |
| **flatMapLatest** | Only latest active | Not guaranteed | Cancels previous | Search, latest data only |

(Actual implementations are provided by kotlinx.coroutines.flow; examples below use equivalent compositions for illustration and should not replace the library operators.)

### 1. flatMapConcat - Sequential Processing

**Behavior**: Processes one inner flow at a time, waiting for each to complete before starting the next. The order of the outer flow is preserved.

```kotlin
// Illustrative alias equivalent to standard flatMapConcat
fun <T, R> Flow<T>.myFlatMapConcat(transform: suspend (T) -> Flow<R>): Flow<R> =
    map(transform).flattenConcat()
```

// Example: Sequential API calls

```kotlin
data class User(val id: Int, val name: String)
data class UserDetails(val userId: Int, val email: String, val phone: String)

fun getUserIds(): Flow<Int> = flow {
    emit(1)
    delay(100)
    emit(2)
    delay(100)
    emit(3)
}

fun fetchUserDetails(userId: Int): Flow<UserDetails> = flow {
    delay(200) // Simulate network call
    emit(UserDetails(userId, "user$userId@example.com", "555-000$userId"))
    println("Fetched details for user $userId")
}

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
```

**When to use**:
- Order must be preserved
- Each operation logically depends on previous completion
- Loading pages sequentially
- Transaction-like processing

### 2. flatMapMerge - Concurrent Processing

**Behavior**: Processes multiple inner flows concurrently with a configurable concurrency limit. Elements are emitted as they are produced; original ordering is not guaranteed.

```kotlin
// Illustrative alias equivalent to standard flatMapMerge
fun <T, R> Flow<T>.myFlatMapMerge(
    concurrency: Int = DEFAULT_CONCURRENCY,
    transform: suspend (T) -> Flow<R>
): Flow<R> =
    map(transform).flattenMerge(concurrency)
```

// Example: Parallel API calls

```kotlin
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
```

/*
Sample output (concurrent with concurrency=2):
Fetched details for user 1
Fetched details for user 2  // Started in parallel
Received: UserDetails(1, ...) (elapsed: ~300ms)
Received: UserDetails(2, ...) (elapsed: ~300ms)
Fetched details for user 3  // Started after slot freed
Received: UserDetails(3, ...) (elapsed: ~500ms)
Total: faster than strictly sequential.
*/

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
- I/O-bound workloads
- Maximum throughput needed

### 3. flatMapLatest - Latest Value Only

**Behavior**: When a new value is emitted by the upstream (outer flow), the previous inner flow is cancelled and a new one starts. At most one inner flow (for the latest value) is active at any time.

```kotlin
// Illustrative alias equivalent to standard flatMapLatest
fun <T, R> Flow<T>.myFlatMapLatest(transform: suspend (T) -> Flow<R>): Flow<R> =
    transformLatest { value ->
        emitAll(transform(value))
    }
```

// Example: Search query with cancellation

```kotlin
data class SearchResult(val query: String, val results: List<String>)

fun searchFlow(query: String): Flow<SearchResult> = flow {
    println("Starting search for: $query")
    delay(300) // Simulate API call
    emit(
        SearchResult(
            query,
            listOf("$query result 1", "$query result 2")
        )
    )
    println("Completed search for: $query")
}

fun main() = runBlocking {
    val searchQueries = flow {
        emit("kot")
        delay(100)
        emit("kotl")  // Cancels "kot" search
        delay(100)
        emit("kotli") // Cancels "kotl" search
        delay(500)    // Wait for last to complete
    }

    searchQueries
        .flatMapLatest { query ->
            searchFlow(query)
        }
        .collect { result ->
            println("Displaying results for: ${result.query}")
        }
}
```

/*
Output:
Starting search for: kot
Starting search for: kotl      // Cancels "kot"
Starting search for: kotli     // Cancels "kotl"
Completed search for: kotli
Displaying results for: kotli
Only the last search completes.
*/

**Real-world implementation - Search with debounce**:

```kotlin
class SearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<List<SearchResult>> = _searchQuery
        .debounce(300) // Wait for user to finish typing
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

#### Example 1: Custom Retry with Exponential Backoff

```kotlin
fun <T> Flow<T>.retryWithExponentialBackoff(
    maxRetries: Int = 3,
    initialDelayMs: Long = 1000,
    maxDelayMs: Long = 10000,
    factor: Double = 2.0
): Flow<T> =
    this.retryWhen { cause, attempt ->
        if (attempt >= maxRetries) return@retryWhen false

        val delayTime =
            (initialDelayMs * factor.pow(attempt.toDouble()))
                .toLong()
                .coerceAtMost(maxDelayMs)

        delay(delayTime)
        println("Retry attempt #${attempt + 1} after ${delayTime}ms due to: ${cause.message}")
        true
    }
```

```kotlin
// Usage example
fun unstableFlow(): Flow<String> = flow {
    val random = Random.nextInt(0, 3)
    if (random != 2) {
        throw IOException("Network error")
    }
    emit("Success!")
}

val resultFlow = unstableFlow()
    .retryWithExponentialBackoff(
        maxRetries = 3,
        initialDelayMs = 1000
    )
```

#### Example 2: Custom Window Operator (fixed Size and slide)

This variant supports fixed-size windows with a configurable slide. It is illustrative and can be refined for production.

```kotlin
fun <T> Flow<T>.window(
    windowSize: Int,
    windowSlide: Int = windowSize
): Flow<List<T>> = flow {
    require(windowSize > 0) { "Window size must be positive" }
    require(windowSlide > 0) { "Window slide must be positive" }

    val buffer = ArrayDeque<T>(windowSize)
    var sinceLastEmit = 0

    collect { value ->
        buffer.addLast(value)
        if (buffer.size < windowSize) return@collect

        if (sinceLastEmit == 0) {
            emit(buffer.toList())
            sinceLastEmit = 1
        } else if (sinceLastEmit == windowSlide) {
            repeat(windowSlide) {
                if (buffer.isNotEmpty()) buffer.removeFirst()
            }
            if (buffer.size == windowSize) {
                emit(buffer.toList())
                sinceLastEmit = 1
            } else {
                sinceLastEmit = 0
            }
            return@collect
        } else {
            sinceLastEmit++
        }

        if (buffer.size > windowSize) {
            buffer.removeFirst()
        }
    }
}
```

```kotlin
// Usage: Moving average with slide = 1
fun main() = runBlocking {
    flowOf(1, 2, 3, 4, 5, 6, 7, 8)
        .window(windowSize = 3, windowSlide = 1)
        .map { window -> window.average() }
        .collect { avg -> println("Moving average: $avg") }
}
```

#### Example 3: Custom Rate Limiting Operator

```kotlin
fun <T> Flow<T>.rateLimit(
    count: Int,
    duration: Duration
): Flow<T> = flow {
    require(count > 0) { "count must be positive" }
    require(!duration.isNegative()) { "duration must be non-negative" }

    val timestamps = ArrayDeque<Long>(count)
    val windowNanos = duration.inWholeNanoseconds

    collect { value ->
        var now = System.nanoTime()

        // Remove timestamps older than duration window
        while (timestamps.isNotEmpty() &&
            now - timestamps.first() >= windowNanos
        ) {
            timestamps.removeFirst()
        }

        // If at rate limit, wait until a slot is free
        if (timestamps.size >= count) {
            val oldest = timestamps.first()
            val waitNanos = windowNanos - (now - oldest)
            if (waitNanos > 0) {
                delay(waitNanos.nanos)
            }
            timestamps.removeFirst()
            now = System.nanoTime()
        }

        timestamps.addLast(now)
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
// Benchmark different flatMap variants (illustrative)
suspend fun benchmarkFlatMapVariants() {
    val itemCount = 100
    val processingTime = 10L // ms per item

    // flatMapConcat: all items processed sequentially
    var startTime = System.currentTimeMillis()
    (1..itemCount).asFlow()
        .flatMapConcat { flowOf(it).onEach { delay(processingTime) } }
        .collect()
    println("flatMapConcat: ${System.currentTimeMillis() - startTime}ms") // ~1000ms

    // flatMapMerge with concurrency=10: up to 10 inner flows in parallel
    startTime = System.currentTimeMillis()
    (1..itemCount).asFlow()
        .flatMapMerge(10) { flowOf(it).onEach { delay(processingTime) } }
        .collect()
    println("flatMapMerge(10): ${System.currentTimeMillis() - startTime}ms") // Can be ~100ms

    // flatMapLatest: behavior depends heavily on upstream emission rate.
    startTime = System.currentTimeMillis()
    (1..itemCount).asFlow()
        .onEach { delay(processingTime) }
        .flatMapLatest { value ->
            flowOf(value).onEach { delay(processingTime) }
        }
        .collect()
    println("flatMapLatest: ${System.currentTimeMillis() - startTime}ms")
}
```

Note: The above timings are illustrative to show relative behavior, not exact guarantees.

### Best Practices

1. Choose the right operator:
   - Need ordering → `flatMapConcat`
   - Need higher throughput → `flatMapMerge`
   - Only latest matters → `flatMapLatest`

2. Control concurrency:
   ```kotlin
   // Avoid unbounded concurrency
   .flatMapMerge(concurrency = Int.MAX_VALUE) // Dangerous
   .flatMapMerge(concurrency = 10) // Controlled
   ```

3. Consider resource limits:
   ```kotlin
   // Limit concurrent network calls
   val maxConcurrentRequests = 5
   requests.flatMapMerge(maxConcurrentRequests) { makeRequest(it) }
   ```

4. Handle errors appropriately:
   ```kotlin
   .flatMapMerge { item ->
       flow { emit(process(item)) }
           .catch { e -> emit(defaultValue) }
   }
   ```

5. Memory considerations:
   - `flatMapMerge` keeps multiple inner flows/buffers active
   - `flatMapLatest` often uses less memory (single active inner flow)
   - `flatMapConcat` has predictable memory use (one inner flow at a time)

### Common Pitfalls

1. Using flatMapConcat when flatMapMerge is needed:
   ```kotlin
   // Slow: processes 1000 items strictly sequentially
   (1..1000).asFlow()
       .flatMapConcat { fetchData(it) }

   // Faster: processes up to 10 at a time
   (1..1000).asFlow()
       .flatMapMerge(10) { fetchData(it) }
   ```

2. Forgetting about cancellation with flatMapLatest:
   ```kotlin
   // Potential resource leak if not cancellation-aware
   searchQuery.flatMapLatest { query ->
       flow {
           val connection = openConnection() // Must be cleaned up on cancel
           // ...
       }
   }

   // Properly cancellable
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

3. Not configuring concurrency:
   ```kotlin
   // Default concurrency may be suboptimal
   .flatMapMerge { ... }

   // Explicit configuration based on use case
   .flatMapMerge(concurrency = 3) { ... }
   ```

**English Summary**: `Flow` operators transform flows in different ways. `flatMapConcat` processes sequentially preserving order, `flatMapMerge` processes concurrently with configurable concurrency to increase throughput, and `flatMapLatest` cancels previous inner flows keeping only the latest active. Custom operators are built by composing existing operators while handling cancellation, resources, and concurrency correctly. Choose based on ordering requirements, performance needs, and resource constraints.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Flow documentation - Kotlin](https://kotlinlang.org/docs/flow.html)
- [Flow operators - Kotlin Coroutines Guide](https://kotlinlang.org/docs/flow.html#flow-operators)
- [flatMapConcat, flatMapMerge, flatMapLatest - API Reference](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/)

## Related Questions

### Related (Hard)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-backpressure-strategies--kotlin--hard]] - `Flow`
- [[q-flow-testing-advanced--kotlin--hard]] - `Flow`

### Prerequisites (Easier)
- [[q-instant-search-flow-operators--kotlin--medium]] - `Flow`
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-flow-operators--kotlin--medium]] - `Flow`

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive `Flow` introduction
