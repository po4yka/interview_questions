---
id: lang-076
title: "What Is Flow / Что такое Flow"
aliases: [What Is Flow, Что такое Flow]
topic: kotlin
subtopics: [coroutines, flow, reactive-programming]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-flow, c-kotlin]
created: 2025-10-15
updated: 2025-11-09
tags: [coroutines, difficulty/medium, flow, kotlin, programming-languages]
---
# Вопрос (RU)
> Что такое `Flow` в Kotlin?

---

# Question (EN)
> What is `Flow` in Kotlin?

## Ответ (RU)

`Flow` — это холодный (cold) асинхронный поток значений, построенный на корутинах ([[c-kotlin]], [[c-flow]], [[c-coroutines]]). Концептуально он похож на ленивую последовательность (подобную `Sequence`/`List` по операциям преобразования), но:
- значения эмитируются последовательно, по одному;
- он не блокирует поток: внутри используются `suspend`-функции;
- отмена происходит через отмену корутины-сборщика (а не методом `cancel()` у самого `Flow`);
- поддерживает работу с потенциально бесконечными потоками данных;
- подходит для сетевых запросов, работы с БД, UI-событий и других реактивных сценариев.

`Flow` по умолчанию «холодный»: он начинает испускать значения только при коллекции и может быть преобразован с помощью богатого набора операторов.

### Базовая Концепция

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// Простой Flow
fun simpleFlow(): Flow<Int> = flow {
    println("Flow started")
    for (i in 1..3) {
        delay(100)
        emit(i)  // Эмит значения
    }
}

fun main() = runBlocking {
    println("Calling flow...")
    val myFlow = simpleFlow()  // Flow ещё не запущен (cold)

    println("Collecting...")
    myFlow.collect { value ->  // Flow запускается при collect
        println("Received: $value")
    }
}

// Output:
// Calling flow...
// Collecting...
// Flow started  <- Запускается только при collect
// Received: 1
// Received: 2
// Received: 3
```

### Flow Против `List`

```kotlin
// List: жадная вычисление (все значения считаются сразу)
fun getListOfNumbers(): List<Int> {
    println("Computing list...")
    return listOf(1, 2, 3, 4, 5)
}

// Flow: ленивое вычисление (значения считаются по мере коллекции)
fun getFlowOfNumbers(): Flow<Int> = flow {
    println("Computing flow...")
    for (i in 1..5) {
        delay(100)  // Можно использовать suspend-функции
        emit(i)     // По одному значению
    }
}

fun main() = runBlocking {
    // Пример с List
    println("Getting list...")
    val list = getListOfNumbers()
    println("Processing list...")
    list.forEach { println(it) }

    println("\n---\n")

    // Пример с Flow
    println("Getting flow...")
    val flow = getFlowOfNumbers()  // Пока ничего не посчитано (cold)
    println("Processing flow...")
    flow.collect { println(it) }   // Значения вычисляются/эмитятся по мере collect
}
```

### Характеристики Flow

```kotlin
// 1. Холодный поток — не эмитит значения, пока не начнётся collect
fun coldFlow(): Flow<Int> = flow {
    println("Started")  // Печатается только при collect
    emit(1)
    emit(2)
}

fun demonstrateCold() = runBlocking {
    val flow = coldFlow()  // Создан, но не запущен
    println("Flow created")
    delay(1000)
    println("Now collecting")
    flow.collect { println(it) }  // Здесь запускается
}

// 2. Последовательная эмиссия
fun sequentialFlow(): Flow<Int> = flow {
    emit(1)
    println("First emitted")
    emit(2)
    println("Second emitted")
    emit(3)
    println("Third emitted")
}

// 3. Поддержка отмены через отмену корутины
fun cancellableFlow() = runBlocking {
    withTimeoutOrNull(500) {
        flow {
            repeat(10) { i ->
                delay(200)
                emit(i)
            }
        }.collect { println(it) }
    }
    println("Cancelled")
}
```

### Создание Flow

```kotlin
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

// 1. Строитель flow { }
fun flowBuilder(): Flow<Int> = flow {
    for (i in 1..3) {
        emit(i)
    }
}

// 2. flowOf() для фиксированного набора значений
fun fixedFlow(): Flow<String> = flowOf("A", "B", "C")

// 3. asFlow() для коллекций и последовательностей
fun fromCollection(): Flow<Int> = listOf(1, 2, 3).asFlow()

fun fromSequence(): Flow<Int> = (1..10).asSequence().asFlow()

// 4. channelFlow для конкурентных эмиссий
fun concurrentFlow(): Flow<Int> = channelFlow {
    launch {
        delay(100)
        send(1)
    }
    launch {
        delay(50)
        send(2)
    }
}

// 5. Преобразование callback API в Flow (упрощённо)
fun callbackToFlow(api: ApiService): Flow<Data> = flow {
    val data = suspendCancellableCoroutine<Data> { cont ->
        val callback = object : Callback {
            override fun onSuccess(data: Data) {
                if (cont.isActive) cont.resume(data)
            }
            override fun onError(error: Exception) {
                if (cont.isActive) cont.resumeWithException(error)
            }
        }

        api.fetchData(callback)
        // В реальной реализации нужно отписаться в cont.invokeOnCancellation
    }
    emit(data)
}
```

### Операторы Flow

```kotlin
// Пример трансформаций
fun transformationExample() = runBlocking {
    flowOf(1, 2, 3, 4, 5)
        .map { it * 2 }           // Трансформация каждого значения
        .filter { it > 5 }        // Фильтрация
        .take(2)                  // Берём первые 2
        .collect { println(it) }  // Вывод: 6, 8
}

// Промежуточные операторы (не запускают коллекцию)
fun intermediateOperators(): Flow<String> =
    flowOf(1, 2, 3, 4, 5)
        .map { it * 2 }            // Промежуточный оператор
        .filter { it % 4 == 0 }    // Промежуточный оператор
        .map { "Value: $it" }     // Промежуточный оператор

// Терминальные операторы (запускают коллекцию)
suspend fun terminalOperators() {
    val flow = flowOf(1, 2, 3, 4, 5)

    // collect — собирает все значения
    flow.collect { println(it) }

    // toList — собирает в список
    val list = flow.toList()

    // first — первое значение
    val first = flow.first()

    // reduce — аккумулирует значения
    val sum = flow.reduce { acc, value -> acc + value }

    // fold — аккумулирует с начальным значением
    val total = flow.fold(0) { acc, value -> acc + value }
}
```

### Бесконечные Потоки

```kotlin
// Бесконечный поток чисел
fun infiniteNumbers(): Flow<Int> = flow {
    var i = 0
    while (true) {
        emit(i++)
        delay(100)
    }
}

// Бесконечный поток событий
fun eventStream(): Flow<Event> = flow {
    while (true) {
        val event = waitForEvent()  // Некоторая suspend-функция
        emit(event)
    }
}

// Использование с take() для ограничения
fun useInfiniteFlow() = runBlocking {
    infiniteNumbers()
        .take(5)  // Берём только 5 значений
        .collect { println(it) }
}
```

### Практические Примеры

```kotlin
// 1. Запросы к БД (многие DAO возвращают Flow)
class UserRepository(private val dao: UserDao) {
    fun observeUsers(): Flow<List<User>> = dao.getAllUsers()
}

// 2. Сетевые запросы
class ApiService {
    fun getUpdates(): Flow<Update> = flow {
        while (true) {
            val update = fetchLatestUpdate()
            emit(update)
            delay(5000)  // Пуллим каждые 5 секунд; кооперативная отмена через delay
        }
    }
}

// 3. UI-события
class SearchViewModel {
    private val _searchQuery = MutableStateFlow("")
    val searchResults: Flow<List<Result>> = _searchQuery
        .debounce(300)                    // Ждём, пока пользователь перестанет печатать
        .filter { it.length >= 3 }        // Минимум 3 символа
        .distinctUntilChanged()           // Игнорируем дубликаты
        .flatMapLatest { query ->         // Отменяем предыдущий поиск
            searchRepository.search(query)
        }

    fun updateQuery(query: String) {
        _searchQuery.value = query
    }
}

// 4. Обновления геопозиции
class LocationService {
    fun observeLocation(): Flow<Location> = callbackFlow {
        val callback = object : LocationCallback() {
            override fun onLocationChanged(location: Location) {
                trySend(location)
            }
        }

        locationProvider.requestUpdates(callback)

        awaitClose {
            locationProvider.removeUpdates(callback)
        }
    }
}

// 5. Чтение файла построчно
fun readFileAsFlow(file: File): Flow<String> = flow {
    file.useLines { lines ->
        lines.forEach { line ->
            emit(line)
        }
    }
}
```

### Отмена Flow

```kotlin
// Flow отменяется через отмену корутины
fun cancellationExample() = runBlocking {
    val job = launch {
        flow {
            repeat(10) { i ->
                println("Emitting $i")
                emit(i)
                delay(200)
            }
        }.collect { value ->
            println("Collected $value")
        }
    }

    delay(500)
    println("Cancelling...")
    job.cancel()  // Останавливаем Flow через отмену корутины
    println("Done")
}

// Пример вывода:
// Emitting 0
// Collected 0
// Emitting 1
// Collected 1
// Emitting 2
// Collected 2
// Cancelling...
// Done
```

### Обработка Исключений

```kotlin
// Пример Flow с ошибкой
fun flowWithErrors() = flow {
    emit(1)
    emit(2)
    throw RuntimeException("Error!")
    // emit(3)  // Не будет выполнено
}

fun handleFlowErrors() = runBlocking {
    flowWithErrors()
        .catch { e ->
            println("Caught: ${e.message}")
            emit(-1)  // Резервное значение
        }
        .collect { println("Value: $it") }
}

// Output:
// Value: 1
// Value: 2
// Caught: Error!
// Value: -1
```

### Сохранение Контекста

```kotlin
// По умолчанию Flow выполняется в контексте коллектора, если не изменён через flowOn
fun contextExample() = runBlocking {
    flow {
        println("Flow in: ${Thread.currentThread().name}")
        emit(1)
    }
    .map {
        println("Map in: ${Thread.currentThread().name}")
        it * 2
    }
    .collect {
        println("Collect in: ${Thread.currentThread().name}")
    }
}

// Переключение контекста с помощью flowOn
fun flowOnExample() = runBlocking {
    flow {
        println("Flow in: ${Thread.currentThread().name}")
        emit(1)
    }
    .flowOn(Dispatchers.IO)  // Upstream выполняется на IO
    .map {
        println("Map in: ${Thread.currentThread().name}")
        it * 2
    }
    .collect {
        println("Collect in: ${Thread.currentThread().name}")
    }
}
```

### Flow И Другие Реактивные Типы

```kotlin
// Flow vs RxJava Observable
// Flow: по умолчанию обычно холодный, использует suspend, структурированная конкуренция,
//       отмена через отмену корутины
// Observable: может быть горячим или холодным, колбэки, отмена через Disposable

// Flow vs LiveData
// Flow: универсальный, много операторов, обычно холодный; можно конвертировать в
//       типы, учитывающие жизненный цикл
// LiveData: Android-специфичный, учитывает жизненный цикл, горячий для активных наблюдателей

// Flow vs Channel
// Flow: холодный, pull-based API; обычный Flow чаще для одного коллектора, для
//       нескольких — SharedFlow/StateFlow
// Channel: горячий примитив для обмена между корутинами, push-модель, обычно один получатель

// Flow vs Sequence
// Flow: асинхронный, не блокирует, для корутин
// Sequence: синхронный, блокирующий, для обычных вычислений в памяти
```

### Рекомендации По Использованию

```kotlin
class FlowBestPractices {
    // ИСПОЛЬЗУЙТЕ: Flow для непрерывных/стриминговых обновлений
    fun getUserUpdates(): Flow<User> = flow {
        while (true) {
            emit(fetchUser())
            delay(1000)
        }
    }

    // ИСПОЛЬЗУЙТЕ: операторы для трансформации
    fun processedData(): Flow<Result> =
        rawData()
            .map { transform(it) }
            .filter { it.isValid }

    // ИСПОЛЬЗУЙТЕ: catch для обработки ошибок
    fun safeFlow(): Flow<Data> =
        dataSource()
            .catch { e ->
                emit(Data.Error(e))
            }

    // НЕ ДЕЛАЙТЕ: не блокируйте поток внутри flow
    fun badFlow(): Flow<Int> = flow {
        Thread.sleep(1000)  // ПЛОХО: вместо этого используйте delay
        emit(1)
    }

    // НЕ ДЕЛАЙТЕ: не используйте небезопасное разделяемое состояние
    var counter = 0
    fun problematicFlow(): Flow<Int> = flow {
        emit(counter++)  // ПЛОХО: не потокобезопасно
    }

    // ИСПОЛЬЗУЙТЕ: StateFlow/SharedFlow для горячих потоков/общего состояния
    private val _state = MutableStateFlow(State())
    val state: StateFlow<State> = _state.asStateFlow()
}
```

### Итоги

`Flow` идеально подходит для:
- асинхронных потоков данных;
- реактивного программирования;
- наблюдаемых источников данных (БД и сеть);
- управления состоянием UI;
- обработок событий и пайплайнов;
- отменяемых операций.

Ключевые преимущества:
- холодный (ленивый) по умолчанию;
- построен на корутинах и интегрируется со структурированной конкуренцией;
- поддерживает `suspend`-операции;
- управление контекстом через `flowOn`;
- богатая библиотека операторов.

## Answer (EN)

Flow is a cold asynchronous stream of values built on coroutines. Conceptually, it is similar to a lazy sequence (like `Sequence`/`List`-style operations), but:
- it emits values sequentially, one by one;
- it is non-blocking: it uses suspend functions internally;
- cancellation is handled via coroutine cancellation of the collector (not a `cancel()` method on `Flow` itself);
- it supports potentially infinite streams of values;
- it is suitable for network calls, database observations, UI events, and other reactive use cases.

Flow is cold by default: it starts emitting only when collected and can be transformed using a rich set of operators.

### Basic Concept

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// Simple Flow
fun simpleFlow(): Flow<Int> = flow {
    println("Flow started")
    for (i in 1..3) {
        delay(100)
        emit(i)  // Emit value
    }
}

fun main() = runBlocking {
    println("Calling flow...")
    val myFlow = simpleFlow()  // Flow not started yet (cold)

    println("Collecting...")
    myFlow.collect { value ->  // Flow starts when collected
        println("Received: $value")
    }
}

// Output:
// Calling flow...
// Collecting...
// Flow started  <- Only starts when collected
// Received: 1
// Received: 2
// Received: 3
```

### Flow Vs `List`

```kotlin
// List: Eager evaluation (all values computed immediately)
fun getListOfNumbers(): List<Int> {
    println("Computing list...")
    return listOf(1, 2, 3, 4, 5)  // All computed at once
}

// Flow: Lazy evaluation (values computed on demand when collected)
fun getFlowOfNumbers(): Flow<Int> = flow {
    println("Computing flow...")
    for (i in 1..5) {
        delay(100)  // Can use suspend functions
        emit(i)  // One at a time
    }
}

fun main() = runBlocking {
    // List example
    println("Getting list...")
    val list = getListOfNumbers()  // Computes all values immediately
    println("Processing list...")
    list.forEach { println(it) }

    println("\n---\n")

    // Flow example
    println("Getting flow...")
    val flow = getFlowOfNumbers()  // Nothing computed yet (cold)
    println("Processing flow...")
    flow.collect { println(it) }  // Values computed/emitted on demand
}
```

### Flow Characteristics

```kotlin
// 1. Cold stream - doesn't emit until collected
fun coldFlow(): Flow<Int> = flow {
    println("Started")  // Only printed when collected
    emit(1)
    emit(2)
}

fun demonstrateCold() = runBlocking {
    val flow = coldFlow()  // Created but not started
    println("Flow created")
    delay(1000)
    println("Now collecting")
    flow.collect { println(it) }  // Now it starts
}

// 2. Sequential emission
fun sequentialFlow(): Flow<Int> = flow {
    emit(1)
    println("First emitted")
    emit(2)
    println("Second emitted")
    emit(3)
    println("Third emitted")
}

// 3. Supports cancellation via coroutine cancellation
fun cancellableFlow() = runBlocking {
    withTimeoutOrNull(500) {
        flow {
            repeat(10) { i ->
                delay(200)
                emit(i)
            }
        }.collect { println(it) }
    }
    println("Cancelled")
}
```

### Creating Flows

```kotlin
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

// 1. flow { } builder
fun flowBuilder(): Flow<Int> = flow {
    for (i in 1..3) {
        emit(i)
    }
}

// 2. flowOf() for fixed values
fun fixedFlow(): Flow<String> = flowOf("A", "B", "C")

// 3. asFlow() extension
fun fromCollection(): Flow<Int> = listOf(1, 2, 3).asFlow()

fun fromSequence(): Flow<Int> = (1..10).asSequence().asFlow()

// 4. channelFlow for concurrent emissions
fun concurrentFlow(): Flow<Int> = channelFlow {
    launch {
        delay(100)
        send(1)
    }
    launch {
        delay(50)
        send(2)
    }
}

// 5. Custom flow from callback (simplified)
fun callbackToFlow(api: ApiService): Flow<Data> = flow {
    val data = suspendCancellableCoroutine<Data> { cont ->
        val callback = object : Callback {
            override fun onSuccess(data: Data) {
                if (cont.isActive) cont.resume(data)
            }
            override fun onError(error: Exception) {
                if (cont.isActive) cont.resumeWithException(error)
            }
        }

        api.fetchData(callback)

        // In a real implementation, you should also cancel/unsubscribe
        // the callback when cont.invokeOnCancellation is called.
    }
    emit(data)
}
```

### Flow Operators

```kotlin
// Transform operators
fun transformationExample() = runBlocking {
    flowOf(1, 2, 3, 4, 5)
        .map { it * 2 }           // Transform each value
        .filter { it > 5 }        // Filter values
        .take(2)                  // Take first 2
        .collect { println(it) }  // Output: 6, 8
}

// Intermediate operators (don't trigger collection)
fun intermediateOperators(): Flow<String> =
    flowOf(1, 2, 3, 4, 5)
        .map { it * 2 }            // Intermediate
        .filter { it % 4 == 0 }    // Intermediate
        .map { "Value: $it" }     // Intermediate

// Terminal operators (trigger collection)
suspend fun terminalOperators() {
    val flow = flowOf(1, 2, 3, 4, 5)

    // collect - collects all
    flow.collect { println(it) }

    // toList - collect to list
    val list = flow.toList()

    // first - get first value
    val first = flow.first()

    // reduce - accumulate values
    val sum = flow.reduce { acc, value -> acc + value }

    // fold - accumulate with initial value
    val total = flow.fold(0) { acc, value -> acc + value }
}
```

### Infinite Streams

```kotlin
// Infinite flow of numbers
fun infiniteNumbers(): Flow<Int> = flow {
    var i = 0
    while (true) {
        emit(i++)
        delay(100)
    }
}

// Infinite flow of events
fun eventStream(): Flow<Event> = flow {
    while (true) {
        val event = waitForEvent()  // Some suspend function
        emit(event)
    }
}

// Use with take() to limit
fun useInfiniteFlow() = runBlocking {
    infiniteNumbers()
        .take(5)  // Only take 5 values
        .collect { println(it) }
}
```

### Real-World Examples

```kotlin
// 1. Database queries (library-specific APIs may expose Flow)
class UserRepository(private val dao: UserDao) {
    fun observeUsers(): Flow<List<User>> = dao.getAllUsers()
}

// 2. Network requests
class ApiService {
    fun getUpdates(): Flow<Update> = flow {
        while (true) {
            val update = fetchLatestUpdate()
            emit(update)
            delay(5000)  // Poll every 5 seconds; cooperative cancellation via delay
        }
    }
}

// 3. UI events
class SearchViewModel {
    private val _searchQuery = MutableStateFlow("")
    val searchResults: Flow<List<Result>> = _searchQuery
        .debounce(300)                    // Wait for user to stop typing
        .filter { it.length >= 3 }        // Min 3 characters
        .distinctUntilChanged()           // Ignore duplicates
        .flatMapLatest { query ->         // Cancel previous search
            searchRepository.search(query)
        }

    fun updateQuery(query: String) {
        _searchQuery.value = query
    }
}

// 4. Location updates
class LocationService {
    fun observeLocation(): Flow<Location> = callbackFlow {
        val callback = object : LocationCallback() {
            override fun onLocationChanged(location: Location) {
                trySend(location)
            }
        }

        locationProvider.requestUpdates(callback)

        awaitClose {
            locationProvider.removeUpdates(callback)
        }
    }
}

// 5. File reading
fun readFileAsFlow(file: File): Flow<String> = flow {
    file.useLines { lines ->
        lines.forEach { line ->
            emit(line)
        }
    }
}
```

### Flow Cancellation

```kotlin
// Flow is cancellable via coroutine cancellation
fun cancellationExample() = runBlocking {
    val job = launch {
        flow {
            repeat(10) { i ->
                println("Emitting $i")
                emit(i)
                delay(200)
            }
        }.collect { value ->
            println("Collected $value")
        }
    }

    delay(500)
    println("Cancelling...")
    job.cancel()  // Stops the flow by cancelling the coroutine
    println("Done")
}

// Example output:
// Emitting 0
// Collected 0
// Emitting 1
// Collected 1
// Emitting 2
// Collected 2
// Cancelling...
// Done
```

### Exception Handling

```kotlin
// Handle exceptions in flow
fun flowWithErrors() = flow {
    emit(1)
    emit(2)
    throw RuntimeException("Error!")
    // emit(3)  // Never reached
}

fun handleFlowErrors() = runBlocking {
    flowWithErrors()
        .catch { e ->
            println("Caught: ${e.message}")
            emit(-1)  // Emit fallback value
        }
        .collect { println("Value: $it") }
}

// Output:
// Value: 1
// Value: 2
// Caught: Error!
// Value: -1
```

### Context Preservation

```kotlin
// Flow runs in the coroutine context of the collector unless changed by flowOn
fun contextExample() = runBlocking {
    flow {
        println("Flow in: ${Thread.currentThread().name}")
        emit(1)
    }
    .map {
        println("Map in: ${Thread.currentThread().name}")
        it * 2
    }
    .collect {
        println("Collect in: ${Thread.currentThread().name}")
    }
}

// Switch context with flowOn
fun flowOnExample() = runBlocking {
    flow {
        println("Flow in: ${Thread.currentThread().name}")
        emit(1)
    }
    .flowOn(Dispatchers.IO)  // Upstream runs on IO
    .map {
        println("Map in: ${Thread.currentThread().name}")
        it * 2
    }
    .collect {
        println("Collect in: ${Thread.currentThread().name}")
    }
}
```

### Flow Vs Other Reactive Streams

```kotlin
// Flow vs RxJava Observable
// Flow: Typically cold by default, suspending, structured concurrency, cancellable via coroutine cancellation
// Observable: Can be hot or cold, callback-based, uses disposables for cancellation

// Flow vs LiveData
// Flow: General-purpose, many operators, usually cold; can be converted to lifecycle-aware types
// LiveData: Android-specific, lifecycle-aware, hot for active observers

// Flow vs Channel
// Flow: Cold, pull-based API; plain Flow is usually collected by a single consumer, though SharedFlow/StateFlow support multiple collectors
// Channel: Hot, push-based primitive for communication between coroutines; typically one receiver, but can be used by multiple if designed so

// Flow vs Sequence
// Flow: Asynchronous (uses suspend), non-blocking, for coroutines
// Sequence: Synchronous (blocking), for regular in-process computations
```

### Best Practices

```kotlin
class FlowBestPractices {
    // DO: Use Flow for continuous/streaming updates
    fun getUserUpdates(): Flow<User> = flow {
        while (true) {
            emit(fetchUser())
            delay(1000)
        }
    }

    // DO: Use operators for transformation
    fun processedData(): Flow<Result> =
        rawData()
            .map { transform(it) }
            .filter { it.isValid }

    // DO: Handle errors with catch (example sealed class Data)
    fun safeFlow(): Flow<Data> =
        dataSource()
            .catch { e ->
                emit(Data.Error(e))
            }

    // DON'T: Block in flow builder
    fun badFlow(): Flow<Int> = flow {
        Thread.sleep(1000)  // BAD: Use delay instead
        emit(1)
    }

    // DON'T: Create unsafe mutable shared state inside builders
    var counter = 0
    fun problematicFlow(): Flow<Int> = flow {
        emit(counter++)  // BAD: Not thread-safe / not concurrency-safe
    }

    // DO: Use StateFlow/SharedFlow for hot streams / shared state
    private val _state = MutableStateFlow(State())
    val state: StateFlow<State> = _state.asStateFlow()
}
```

### Summary

Flow is ideal for:
- async data streams;
- reactive programming;
- database observables;
- network polling;
- UI state management;
- event streams;
- sequential processing pipelines;
- cancellable operations.

Key advantages:
- cold (lazy) by default;
- built on coroutines;
- supports suspending operations;
- context control with `flowOn`;
- structured concurrency integration;
- rich operator library.

---

## Дополнительные Вопросы (RU)

- В чём ключевые отличия `Flow` от подхода в Java?
- Когда бы вы использовали `Flow` на практике?
- Какие распространённые ошибки при работе с `Flow` стоит избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-flow-flatmap-operator--kotlin--easy]]

## Related Questions

- [[q-flow-flatmap-operator--kotlin--easy]]
