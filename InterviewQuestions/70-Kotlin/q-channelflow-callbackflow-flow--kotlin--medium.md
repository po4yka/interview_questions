---
id: kotlin-061
title: "channelFlow vs callbackFlow vs flow: when to use each / channelFlow vs callbackFlow vs flow: когда использовать"
topic: kotlin
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-12
updated: 2025-11-09
tags: [builders, callbackflow, channelflow, coroutines, difficulty/medium, flow, kotlin]
moc: moc-kotlin
aliases: ["channelFlow vs callbackFlow vs flow: когда использовать", "channelFlow vs callbackFlow vs flow"]
question_kind: coding
related: [c-coroutines, c-flow, c-kotlin, q-channels-vs-flow--kotlin--medium, q-kotlin-flow-basics--kotlin--medium]
subtopics:
  - builders
  - coroutines
  - flow
date created: Friday, November 7th 2025, 6:45:04 pm
date modified: Tuesday, November 25th 2025, 8:53:53 pm
---
# Вопрос (RU)
> В чем разница между `flow{}`, `channelFlow{}`, и `callbackFlow{}`? Когда следует использовать каждый билдер?

---

# Question (EN)
> What's the difference between `flow{}`, `channelFlow{}`, and `callbackFlow{}`? When should you use each builder?

## Ответ (RU)

Kotlin `Flow` предоставляет несколько билдеров (`flow{}`, `channelFlow{}`, `callbackFlow{}`), каждый с разными характеристиками. Неверный выбор билдера может привести к лишним накладным расходам, сложностям с отменой, утечкам ресурсов или некорректному поведению. Важно понимать точные семантики каждого, чтобы писать production-ready `Flow` код.

### Обзор Билдера Flow

| Билдер | Тип потока | Конкурентность | Буферизация | Основной кейс |
|--------|------------|----------------|-------------|---------------|
| `flow{}` | Холодный | Только последовательные эмиссии (одна корутина) | Без дополнительного буфера (back-pressure через приостановку `emit`) | Простая последовательная генерация/трансформации данных |
| `channelFlow{}` | Холодный `Flow` с внутренним `Channel` | Поддерживает конкурентных продюсеров внутри блока | Буферизованный канал (можно настраивать) | Объединение/координация нескольких конкурентных источников |
| `callbackFlow{}` | Холодный `Flow` с внутренним `Channel` | Безопасная обертка над callback + корутинами | Буфер + требуются корректные `awaitClose`-очистки | Обертка над callback/listener API |

Важно: все три билдера создают холодные `Flow`. Для `channelFlow{}` и `callbackFlow{}` продюсер запускается для каждой новой коллекции, и внутри используется `Channel`. Это может делать поведение похожим на «горячий» источник (несколько конкурентных продюсеров, буфер), но жизненный цикл по-прежнему строго ограничен коллекцией (они не становятся глобально горячими потоками сами по себе).

### `flow{}` — Холодный, Последовательный Flow

Характеристики:
- Холодный: выполнение начинается только при запуске терминального оператора; каждый новый коллектор заново запускает блок.
- Последовательный: `emit()` — приостанавливающая функция, вызывать её можно только из той же корутины, конкурентные эмиссии запрещены (иначе нарушение инварианта Flow).
- Back-pressure: реализуется через приостановку `emit()` до готовности downstream.
- Без дополнительной буферизации: значения идут напрямую коллекторам (если явно не добавить `buffer`).

Базовый пример:

```kotlin
fun simpleFlow(): Flow<Int> = flow {
    for (i in 1..5) {
        delay(100)
        emit(i) // Приостанавливается, пока коллектор не готов
    }
}

// Использование
launch {
    simpleFlow().collect { value ->
        println(value)
    }
}
```

Когда использовать `flow{}`:
- Простая последовательная генерация значений.
- Трансформация других `Flow`.
- Обертка над suspend-функциями.
- Вариант по умолчанию, когда не нужны каналы, callback-и или несколько продюсеров.

Пример: пагинация API

```kotlin
fun fetchPages(): Flow<List<Item>> = flow {
    var page = 1
    var hasMore = true

    while (hasMore) {
        val response = api.fetchPage(page)
        emit(response.items)

        hasMore = response.hasNext
        page++
    }
}

// Использование
fetchPages().collect { items ->
    displayItems(items)
}
```

Нельзя эмитить конкурентно (инвариант Flow):

```kotlin
// ОШИБКА: нарушение инварианта Flow
fun concurrentFlow(): Flow<Int> = flow {
    launch {
        emit(1) // Нельзя: emit() из другой корутины
    }
}

// Пример исключения:
// Flow invariant is violated: Flow was collected in [coroutine#1],
// but emission happened in [coroutine#2].
```

### `channelFlow{}` — Конкурентные Продюсеры И Channel

Характеристики:
- Холодный `Flow`, блок выполняется в `ProducerScope`, основанном на `Channel`.
- Можно запускать несколько корутин внутри блока и вызывать `send`/`emit` из любой из них.
- По умолчанию используется буферизованный `Channel` (обычно `Channel.BUFFERED`), емкость можно конфигурировать.
- Back-pressure: через приостановку `send`/`emit`, когда буфер заполнен.

Базовый пример:

```kotlin
fun concurrentFlow(): Flow<Int> = channelFlow {
    launch {
        repeat(5) { i ->
            delay(100)
            send(i) // Можно из дочерней корутины
        }
    }

    launch {
        repeat(5) { i ->
            delay(150)
            send(i + 10)
        }
    }
}

// Порядок значений не гарантирован, т.к. источники конкурентные
```

Когда использовать `channelFlow{}`:
- Нужно слить несколько конкурентных источников в один `Flow`.
- Параллельная работа продюсеров с независимыми эмиссиями.
- Нужна явная буферизация между продюсером(ами) и потребителем.
- Обертка над существующими `Channel`-ами или fan-in паттернами.

Пример: параллельные API-запросы

```kotlin
fun fetchMultipleSources(): Flow<Data> = channelFlow {
    val sources = listOf("source1", "source2", "source3")

    sources.forEach { source ->
        launch {
            val data = api.fetchFromSource(source)
            send(data) // Конкурентные send
        }
    }
}

// Использование
fetchMultipleSources().collect { data ->
    println("Received: $data")
}
```

Пример с настройкой буфера:

```kotlin
fun bufferedFlow(): Flow<Int> = channelFlow {
    launch {
        repeat(100) { i ->
            send(i)
        }
    }
}.buffer(capacity = Channel.UNLIMITED) // либо CONFLATED, RENDEZVOUS и т.п.
```

### `callbackFlow{}` — Обертка Над Callback API

Характеристики:
- Холодный `Flow` с `ProducerScope` и `Channel`.
- Специально предназначен для обертки callback/listener-API.
- Разрешено использовать `send()` из корутин и `trySend()` из обычных (несуспендящихся) callback-ов.
- Требует `awaitClose {}` для корректного снятия слушателей и освобождения ресурсов.

Базовый пример:

```kotlin
fun locationUpdates(locationManager: LocationManager): Flow<Location> = callbackFlow {
    val listener = object : LocationListener {
        override fun onLocationChanged(location: Location) {
            trySend(location).isSuccess // Несуспендирующая отправка
        }

        override fun onStatusChanged(provider: String?, status: Int, extras: Bundle?) {}
        override fun onProviderEnabled(provider: String) {}
        override fun onProviderDisabled(provider: String) {
            close(Exception("Provider disabled"))
        }
    }

    locationManager.requestLocationUpdates(
        LocationManager.GPS_PROVIDER,
        1000L,
        10f,
        listener
    )

    // ОБЯЗАТЕЛЬНО: очистка при отмене/завершении Flow
    awaitClose {
        locationManager.removeUpdates(listener)
    }
}

// Использование
locationUpdates(locationManager)
    .collect { location ->
        println("Location: $location")
    }
```

Когда использовать `callbackFlow{}`:
- Обертка над callback-/listener-базированными API.
- Событийные источники (клики, сенсоры, сеть, подключения и т.п.).
- WebSocket, SSE и любые push-стили.

Про `awaitClose`:
- Компилятор не заставляет, но практически всегда нужно вызвать `awaitClose {}` или закрыть канал/отписаться иным образом, иначе ресурсы будут течь.

Неправильное и правильное использование:

```kotlin
// НЕПРАВИЛЬНО: нет awaitClose -> listener не снимается
fun badCallbackFlow() = callbackFlow {
    val listener = { data: String ->
        trySend(data)
    }
    api.registerListener(listener)
    // Нет awaitClose
}

// ПРАВИЛЬНО
fun goodCallbackFlow() = callbackFlow {
    val listener = { data: String ->
        trySend(data)
    }
    api.registerListener(listener)

    awaitClose {
        api.unregisterListener(listener)
    }
}
```

### Реальный Пример: Firebase Realtime Database

```kotlin
fun DatabaseReference.asFlow(): Flow<DataSnapshot> = callbackFlow {
    val listener = object : ValueEventListener {
        override fun onDataChange(snapshot: DataSnapshot) {
            trySend(snapshot).isSuccess
        }

        override fun onCancelled(error: DatabaseError) {
            close(error.toException())
        }
    }

    addValueEventListener(listener)

    awaitClose {
        removeEventListener(listener)
    }
}

// Использование
database.child("users").asFlow()
    .map { snapshot -> snapshot.getValue(User::class.java) }
    .collect { user ->
        updateUI(user)
    }
```

### Реальный Пример: Room Database

```kotlin
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :userId")
    fun getUserFlow(userId: String): Flow<User>

    // Упрощенная ручная реализация через callbackFlow (концептуальный пример)
    fun getUserFlowManual(userId: String): Flow<User> = callbackFlow {
        val observer = object : InvalidationTracker.Observer("users") {
            override fun onInvalidated(tables: Set<String>) {
                val user = queryUser(userId)
                trySend(user)
            }
        }

        database.invalidationTracker.addObserver(observer)

        val initialUser = queryUser(userId)
        send(initialUser)

        awaitClose {
            database.invalidationTracker.removeObserver(observer)
        }
    }
}
```

### Реальный Пример: WebSocket

```kotlin
fun webSocketFlow(url: String): Flow<String> = callbackFlow {
    val client = OkHttpClient()
    val request = Request.Builder().url(url).build()

    val listener = object : WebSocketListener() {
        override fun onMessage(webSocket: WebSocket, text: String) {
            trySend(text).isSuccess
        }

        override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
            close(t)
        }

        override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
            close()
        }
    }

    val webSocket = client.newWebSocket(request, listener)

    awaitClose {
        webSocket.close(1000, "Flow cancelled")
    }
}

// Использование
webSocketFlow("wss://example.com/ws")
    .catch { e -> println("Error: $e") }
    .collect { message ->
        println("Received: $message")
    }
```

### `send()` Vs `trySend()` Vs `emit()`

`emit()`:
- Приостанавливающая функция, уважает back-pressure.
- Используется в `flow{}` и доступна в `channelFlow{}`/`callbackFlow{}` через `FlowCollector`/`ProducerScope`.

`send()`:
- Приостанавливающая отправка в `Channel` (`ProducerScope`).
- Доступна в `channelFlow{}`/`callbackFlow{}`.

`trySend()`:
- Не приостанавливающая, сразу возвращает `ChannelResult<Unit>`.
- Предпочтительно внутри обычных callback-ов в `callbackFlow{}`.

Примеры:

```kotlin
// flow{} — используем emit()
flow {
    emit(1)
}

// channelFlow{} — можно send() или emit() (emit в этом scope делегирует в send)
channelFlow {
    send(1)
    emit(2)
}

// callbackFlow{} — send() в корутинах, trySend() в callback-ах
callbackFlow {
    launch {
        send(1)
    }

    val callback = { value: Int ->
        trySend(value)
    }

    awaitClose { }
}
```

### Обработка Ошибок

`flow{}`:

```kotlin
fun flowWithError(): Flow<Int> = flow {
    emit(1)
    throw RuntimeException("Error")
}

flowWithError()
    .catch { e -> println("Caught: $e") }
    .collect { value -> println(value) }
```

`channelFlow{}`:

```kotlin
fun channelFlowWithError(): Flow<Int> = channelFlow {
    launch {
        send(1)
        throw RuntimeException("Error in launch")
    }

    launch {
        send(2)
    }
}

// Исключения в дочерних корутинах по умолчанию отменяют ProducerScope и тем самым всю Flow-коллекцию.
// Если нужно особое поведение, оборачивайте send/emit в try/catch и/или используйте отдельные обработчики.
```

`callbackFlow{}`:

```kotlin
fun callbackFlowWithError(): Flow<String> = callbackFlow {
    val listener = object : Listener {
        override fun onData(data: String) {
            trySend(data)
        }

        override fun onError(error: Exception) {
            close(error)
        }
    }

    api.register(listener)

    awaitClose {
        api.unregister(listener)
    }
}

callbackFlowWithError()
    .catch { e -> println("Error: $e") }
    .collect { data -> println(data) }
```

### Обработка Отмены

`flow{}`:
- Автоматически отменяется при отмене корутины коллектора.
- Для очистки можно использовать `finally`.

```kotlin
flow {
    try {
        repeat(10) { i ->
            emit(i)
            delay(100)
        }
    } finally {
        println("Flow cancelled")
    }
}
```

`channelFlow{}` / `callbackFlow{}`:
- Для очистки используйте `awaitClose {}` и/или `try/finally`.

```kotlin
callbackFlow {
    println("Started")

    val listener = { data: String -> trySend(data) }
    api.register(listener)

    awaitClose {
        println("Cleaning up")
        api.unregister(listener)
    }
}
```

### Соображения По Производительности

- `flow{}`:
  - Минимальные накладные расходы, нет внутреннего `Channel`.
  - Предпочтителен для простых последовательных операций и трансформаций.
- `channelFlow{}`:
  - Выше накладные расходы из-за `Channel` и конкуренции.
  - Используйте только при реальной необходимости нескольких продюсеров или канал-семантики.
- `callbackFlow{}`:
  - Похож на `channelFlow{}`, плюс цена интеграции с callback-ами.
  - Используйте для обертки внешних API, а не для обычной логики.

Точные цифры зависят от окружения — при необходимости измеряйте отдельно.

### Стратегии Тестирования

Тестирование `flow{}`:

```kotlin
@Test
fun `test simple flow`() = runTest {
    val flow = flow {
        emit(1)
        emit(2)
        emit(3)
    }

    val result = flow.toList()
    assertEquals(listOf(1, 2, 3), result)
}
```

Тестирование `channelFlow{}`:

```kotlin
@Test
fun `test concurrent channel flow`() = runTest {
    val flow = channelFlow {
        launch { send(1) }
        launch { send(2) }
        launch { send(3) }
    }

    val result = flow.toList().sorted()
    assertEquals(listOf(1, 2, 3), result)
}
```

Тестирование `callbackFlow{}`:

```kotlin
@Test
fun `test callback flow`() = runTest {
    val listener = FakeListener()

    val flow = callbackFlow {
        listener.callback = { value -> trySend(value) }
        awaitClose { listener.callback = null }
    }

    val collected = mutableListOf<String>()

    val job = launch {
        flow.take(3).toList(collected)
    }

    listener.emit("A")
    listener.emit("B")
    listener.emit("C")

    job.join()

    assertEquals(listOf("A", "B", "C"), collected)
}

class FakeListener {
    var callback: ((String) -> Unit)? = null

    fun emit(value: String) {
        callback?.invoke(value)
    }
}
```

### Типичные Ошибки

1. Использование `flow{}` для конкурентных эмиссий:

```kotlin
// НЕПРАВИЛЬНО
fun concurrentEmit() = flow {
    launch {
        emit(1)
    }
}

// ПРАВИЛЬНО: channelFlow
fun concurrentEmitFixed() = channelFlow {
    launch {
        send(1)
    }
}
```

1. Забытый `awaitClose` в `callbackFlow{}`:

```kotlin
// НЕПРАВИЛЬНО: listener-утечка
fun leakyFlow() = callbackFlow {
    val listener = { data: String -> trySend(data) }
    api.register(listener)
}

// ПРАВИЛЬНО
fun cleanFlow() = callbackFlow {
    val listener = { data: String -> trySend(data) }
    api.register(listener)
    awaitClose { api.unregister(listener) }
}
```

1. Использование `emit()` напрямую в callback-е:

```kotlin
// НЕПРАВИЛЬНО: emit() — suspend, нельзя в обычном callback-е
fun badFlow() = callbackFlow {
    val listener = { data: String ->
        emit(data) // Ошибка
    }
}

// ПРАВИЛЬНО: trySend()
fun goodFlow() = callbackFlow {
    val listener = { data: String ->
        trySend(data)
    }
}
```

1. Игнорирование результата `trySend()`:

```kotlin
// Может терять данные, если буфер полон или канал закрыт
callbackFlow {
    val listener = { data: String ->
        trySend(data)
    }
}

// Лучше явно обрабатывать неудачу
callbackFlow {
    val listener = { data: String ->
        trySend(data).onFailure {
            Log.w("Flow", "Failed to send $data")
        }
    }
}

// Или настроить стратегию буферизации
callbackFlow {
    val listener = { data: String ->
        trySend(data)
    }
}.buffer(Channel.CONFLATED)
```

### Выбор Правильного Билдера: Шпаргалка

- Нужно последовательно эмитить значения из suspend-кода в одной корутине?
  - Используйте `flow{}`.
- Нужно объединить эмиссии из нескольких конкурентных корутин в один поток?
  - Используйте `channelFlow{}`.
- Нужно превратить callback-/listener- или внешние push-API в `Flow`?
  - Используйте `callbackFlow{}`.

Примеры:

```kotlin
// Последовательная генерация → flow{}
fun countDown() = flow {
    for (i in 10 downTo 1) {
        delay(1000)
        emit(i)
    }
}

// Параллельные API вызовы → channelFlow{}
fun fetchAllUsers(userIds: List<String>) = channelFlow {
    userIds.forEach { id ->
        launch {
            val user = api.getUser(id)
            send(user)
        }
    }
}

// Callback-основанный сенсор → callbackFlow{}
fun sensorData(sensor: Sensor): Flow<SensorEvent> = callbackFlow {
    val listener = object : SensorEventListener {
        override fun onSensorChanged(event: SensorEvent) {
            trySend(event)
        }

        override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}
    }

    sensorManager.registerListener(listener, sensor, SENSOR_DELAY_NORMAL)

    awaitClose {
        sensorManager.unregisterListener(listener)
    }
}
```

### Ключевые Выводы

1. `flow{}` — выбор по умолчанию: холодный, последовательный, минимальные накладные расходы.
2. `channelFlow{}` — холодный `Flow` на базе `Channel`; позволяет конкурентных продюсеров и настраиваемую буферизацию.
3. `callbackFlow{}` — холодный `Flow` на базе `Channel`; идеален для callback/listener API; почти всегда требует `awaitClose {}`.
4. Используйте `emit()` в обычном `flow{}` и в `ProducerScope` где уместно; `send()` — для приостанавливающих отправок в `Channel`; `trySend()` — для не-блокирующих callback-ов.
5. Back-pressure обеспечивается приостановкой; стратегия буферизации влияет на поведение быстрых продюсеров.
6. Все три билдера создают холодные потоки; для реально разделяемых горячих потоков используйте `shareIn`, `stateIn` или отдельные hot-источники (`StateFlow`, `SharedFlow`).
7. Всегда тестируйте отмену и очистку ресурсов, особенно при интеграции с внешними API.
8. Предпочитайте `flow{}` для простоты и производительности, а `channelFlow{}`/`callbackFlow{}` включайте осознанно.

---

## Answer (EN)

Kotlin `Flow` provides multiple builders (`flow{}`, `channelFlow{}`, `callbackFlow{}`), each with distinct semantics. Choosing the wrong builder can add unnecessary overhead, complicate cancellation, or cause resource leaks and incorrect behavior. Understanding when to use each is essential for production-ready `Flow` code.

### Overview of Flow Builders

| Builder | Flow nature | Concurrency | Buffering | Primary use case |
|---------|------------|-------------|-----------|------------------|
| `flow{}` | Cold | Sequential emissions only (single coroutine) | No extra buffer (direct backpressure via suspension) | Simple sequential suspending emissions, transformations |
| `channelFlow{}` | Cold Flow using a Channel internally | Concurrent producers inside the builder | Buffered channel (configurable) | Merge/coordinate multiple concurrent sources |
| `callbackFlow{}` | Cold Flow using a Channel internally | Safe from callbacks + coroutines | Buffered + requires proper `awaitClose` cleanup | Wrapping callback/listener-style APIs |

Note: All three builders create cold Flows. For `channelFlow{}` and `callbackFlow{}`, the producer logic is started per collection and uses an internal Channel. This can make them resemble hot sources (concurrent producers, buffering), but their lifecycle is still scoped to the collector; they do not become globally hot on their own.

### flow{} - Cold, Sequential Flow

Characteristics:
- Cold: Execution starts when a terminal operator (collector) is called; each new collector re-runs the block.
- Sequential: `emit()` is suspending and must be called from the same coroutine (no concurrent emissions).
- Backpressure: Implemented by suspension — `emit()` suspends until the downstream is ready.
- No extra buffering: Values are delivered directly to the collector (unless you explicitly add operators like `buffer`).

Basic usage:

```kotlin
fun simpleFlow(): Flow<Int> = flow {
    for (i in 1..5) {
        delay(100)
        emit(i) // Suspends until collector is ready
    }
}

// Usage
launch {
    simpleFlow().collect { value ->
        println(value)
    }
}
```

When to use:
- Simple sequential data generation.
- Transforming other Flows.
- Wrapping suspend functions.
- Default choice when you don't explicitly need channels, callbacks, or concurrent producers.

Example: API pagination

```kotlin
fun fetchPages(): Flow<List<Item>> = flow {
    var page = 1
    var hasMore = true

    while (hasMore) {
        val response = api.fetchPage(page)
        emit(response.items)

        hasMore = response.hasNext
        page++
    }
}

// Usage
fetchPages().collect { items ->
    displayItems(items)
}
```

Cannot emit concurrently (Flow invariant):

```kotlin
// ERROR: Flow invariant is violated
fun concurrentFlow(): Flow<Int> = flow {
    launch {
        emit(1) // ERROR: emit() called from a different coroutine
    }
}

// Exception example:
// Flow invariant is violated: Flow was collected in [coroutine#1],
// but emission happened in [coroutine#2].
```

### channelFlow{} - Concurrent Producers with Channel

Characteristics:
- Cold Flow whose block runs in a `ProducerScope` backed by a Channel.
- Concurrent: You can launch multiple coroutines inside the block and `send`/`emit` from any of them.
- Buffered: Uses a Channel; default capacity is `Channel.BUFFERED` (typically 64) unless changed.
- Backpressure: Achieved via suspending `send`/`emit` when the buffer is full.

Basic usage:

```kotlin
fun concurrentFlow(): Flow<Int> = channelFlow {
    launch {
        repeat(5) { i ->
            delay(100)
            send(i) // Can send from any child coroutine of this scope
        }
    }

    launch {
        repeat(5) { i ->
            delay(150)
            send(i + 10)
        }
    }
}

// Output order is not guaranteed due to concurrency
```

When to use:
- Multiple concurrent data sources that should be merged into a single Flow.
- Parallel data processing where producers may emit independently.
- Need explicit buffering between producer(s) and consumer.
- Bridging existing channels or fan-in patterns into a Flow.

Example: Parallel API calls

```kotlin
fun fetchMultipleSources(): Flow<Data> = channelFlow {
    val sources = listOf("source1", "source2", "source3")

    sources.forEach { source ->
        launch {
            val data = api.fetchFromSource(source)
            send(data) // Concurrent sends
        }
    }
}

// Usage
fetchMultipleSources().collect { data ->
    println("Received: $data")
}
```

Buffer configuration example:

```kotlin
fun bufferedFlow(): Flow<Int> = channelFlow {
    launch {
        repeat(100) { i ->
            send(i)
        }
    }
}.buffer(capacity = Channel.UNLIMITED) // Or CONFLATED, RENDEZVOUS, etc.
```

### callbackFlow{} - Wrapping Callback-Based APIs

Characteristics:
- Cold Flow whose block runs in a `ProducerScope` with a Channel.
- Designed for callback/listener-style APIs.
- Can safely use `send()` from coroutines in the scope and `trySend()` from non-suspending callbacks.
- Requires `awaitClose {}` to unregister listeners / close resources correctly.

Basic usage:

```kotlin
fun locationUpdates(locationManager: LocationManager): Flow<Location> = callbackFlow {
    val listener = object : LocationListener {
        override fun onLocationChanged(location: Location) {
            trySend(location).isSuccess // Non-suspending, handle result if needed
        }

        override fun onStatusChanged(provider: String?, status: Int, extras: Bundle?) {}
        override fun onProviderEnabled(provider: String) {}
        override fun onProviderDisabled(provider: String) {
            close(Exception("Provider disabled"))
        }
    }

    // Register callback
    locationManager.requestLocationUpdates(
        LocationManager.GPS_PROVIDER,
        1000L,
        10f,
        listener
    )

    // REQUIRED FOR CLEANUP: called when the flow is cancelled or completed
    awaitClose {
        locationManager.removeUpdates(listener)
    }
}

// Usage
locationUpdates(locationManager)
    .collect { location ->
        println("Location: $location")
    }
```

When to use:
- Converting callback-based or listener-based APIs into Flows.
- Event listeners (clicks, sensors, connectivity, etc.).
- WebSockets, SSE, or other push-style APIs.

On `awaitClose`:
- The compiler does not enforce it, but in practice you almost always must provide `awaitClose {}` (or otherwise close/unregister) to avoid leaks.

Incorrect vs correct usage:

```kotlin
// WRONG: No awaitClose -> listener never removed, potential leak
fun badCallbackFlow() = callbackFlow {
    val listener = { data: String ->
        trySend(data)
    }
    api.registerListener(listener)
    // Missing awaitClose
}

// CORRECT: With awaitClose
fun goodCallbackFlow() = callbackFlow {
    val listener = { data: String ->
        trySend(data)
    }
    api.registerListener(listener)

    awaitClose {
        api.unregisterListener(listener)
    }
}
```

### Real Example: Firebase Realtime Database

```kotlin
fun DatabaseReference.asFlow(): Flow<DataSnapshot> = callbackFlow {
    val listener = object : ValueEventListener {
        override fun onDataChange(snapshot: DataSnapshot) {
            trySend(snapshot).isSuccess
        }

        override fun onCancelled(error: DatabaseError) {
            close(error.toException())
        }
    }

    addValueEventListener(listener)

    awaitClose {
        removeEventListener(listener)
    }
}

// Usage
database.child("users").asFlow()
    .map { snapshot -> snapshot.getValue(User::class.java) }
    .collect { user ->
        updateUI(user)
    }
```

### Real Example: Room Database Query

```kotlin
// Room can return Flow directly
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :userId")
    fun getUserFlow(userId: String): Flow<User>

    // Conceptual manual implementation (simplified)
    fun getUserFlowManual(userId: String): Flow<User> = callbackFlow {
        val observer = object : InvalidationTracker.Observer("users") {
            override fun onInvalidated(tables: Set<String>) {
                val user = queryUser(userId)
                trySend(user)
            }
        }

        database.invalidationTracker.addObserver(observer)

        val initialUser = queryUser(userId)
        send(initialUser)

        awaitClose {
            database.invalidationTracker.removeObserver(observer)
        }
    }
}
```

### Real Example: WebSocket Connection

```kotlin
fun webSocketFlow(url: String): Flow<String> = callbackFlow {
    val client = OkHttpClient()
    val request = Request.Builder().url(url).build()

    val listener = object : WebSocketListener() {
        override fun onMessage(webSocket: WebSocket, text: String) {
            trySend(text).isSuccess
        }

        override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
            close(t)
        }

        override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
            close() // Signal normal completion of the flow
        }
    }

    val webSocket = client.newWebSocket(request, listener)

    awaitClose {
        webSocket.close(1000, "Flow cancelled")
    }
}

// Usage
webSocketFlow("wss://example.com/ws")
    .catch { e -> println("Error: $e") }
    .collect { message ->
        println("Received: $message")
    }
```

### send() Vs trySend() Vs emit()

`emit()`:
- Suspending, respects backpressure.
- Used in `flow{}` and also available in `channelFlow{}`/`callbackFlow{}` via `FlowCollector`/`ProducerScope` extensions.

`send()`:
- Suspending send to the underlying Channel (`ProducerScope`).
- Available in `channelFlow{}`/`callbackFlow{}`.

`trySend()`:
- Non-suspending, immediately returns a `ChannelResult<Unit>`.
- Preferred inside non-suspending callbacks in `callbackFlow{}`.

Usage examples:

```kotlin
// flow{} - use emit()
flow {
    emit(1)
}

// channelFlow{} - can use send() or emit() (in this scope emit delegates to send)
channelFlow {
    send(1)
    emit(2) // In ProducerScope, effectively send(2)
}

// callbackFlow{} - send() in coroutines, trySend() in callbacks
callbackFlow {
    launch {
        send(1)
    }

    val callback = { value: Int ->
        trySend(value)
    }

    awaitClose { }
}
```

### Error Handling

`flow{}`:

```kotlin
fun flowWithError(): Flow<Int> = flow {
    emit(1)
    throw RuntimeException("Error")
    emit(2) // Never reached
}

// Catch in collector
flowWithError()
    .catch { e -> println("Caught: $e") }
    .collect { value -> println(value) }
```

`channelFlow{}`:

```kotlin
fun channelFlowWithError(): Flow<Int> = channelFlow {
    launch {
        send(1)
        throw RuntimeException("Error in launch")
    }

    launch {
        send(2)
    }
}

// Exceptions in child coroutines by default cancel the ProducerScope and thus the whole Flow collection.
// If you need custom behavior, wrap send/emit in try/catch and/or use dedicated exception handling strategies.
```

`callbackFlow{}`:

```kotlin
fun callbackFlowWithError(): Flow<String> = callbackFlow {
    val listener = object : Listener {
        override fun onData(data: String) {
            trySend(data)
        }

        override fun onError(error: Exception) {
            close(error)
        }
    }

    api.register(listener)

    awaitClose {
        api.unregister(listener)
    }
}

// Usage
callbackFlowWithError()
    .catch { e -> println("Error: $e") }
    .collect { data -> println(data) }
```

### Cancellation Handling

`flow{}`:
- Automatically cancelled when the collector's coroutine is cancelled.
- Use `finally` for cleanup if needed.

```kotlin
flow {
    try {
        repeat(10) { i ->
            emit(i)
            delay(100)
        }
    } finally {
        println("Flow cancelled")
    }
}
```

`channelFlow{}` / `callbackFlow{}`:
- Use `awaitClose {}` (and/or `try/finally`) to clean up resources when the Flow is cancelled.

```kotlin
callbackFlow {
    println("Started")

    val listener = { data: String -> trySend(data) }
    api.register(listener)

    awaitClose {
        println("Cleaning up")
        api.unregister(listener)
    }
}
```

### Performance Considerations

Relative guidelines (not exact benchmarks):
- `flow{}`:
  - Lowest overhead: direct emissions, no internal Channel.
  - Best for simple sequential operations and transformations.
- `channelFlow{}`:
  - Higher overhead due to Channel operations and concurrency.
  - Use when you truly need multiple concurrent producers or channel semantics.
- `callbackFlow{}`:
  - Similar overhead to `channelFlow{}` plus cost of callback integration.
  - Use when wrapping external callback-based APIs.

Avoid relying on fixed nanosecond-per-emission numbers; measure in your own environment if needed.

### Testing Strategies

Testing `flow{}`:

```kotlin
@Test
fun `test simple flow`() = runTest {
    val flow = flow {
        emit(1)
        emit(2)
        emit(3)
    }

    val result = flow.toList()
    assertEquals(listOf(1, 2, 3), result)
}
```

Testing `channelFlow{}`:

```kotlin
@Test
fun `test concurrent channel flow`() = runTest {
    val flow = channelFlow {
        launch { send(1) }
        launch { send(2) }
        launch { send(3) }
    }

    val result = flow.toList().sorted()
    assertEquals(listOf(1, 2, 3), result)
}
```

Testing `callbackFlow{}`:

```kotlin
@Test
fun `test callback flow`() = runTest {
    val listener = FakeListener()

    val flow = callbackFlow {
        listener.callback = { value -> trySend(value) }
        awaitClose { listener.callback = null }
    }

    val collected = mutableListOf<String>()

    val job = launch {
        flow.take(3).toList(collected)
    }

    listener.emit("A")
    listener.emit("B")
    listener.emit("C")

    job.join()

    assertEquals(listOf("A", "B", "C"), collected)
}

class FakeListener {
    var callback: ((String) -> Unit)? = null

    fun emit(value: String) {
        callback?.invoke(value)
    }
}
```

### Common Pitfalls

Pitfall 1: Using `flow{}` for concurrent emissions

```kotlin
// WRONG: Violates Flow invariant
fun concurrentEmit() = flow {
    launch {
        emit(1)
    }
}

// CORRECT: Use channelFlow
fun concurrentEmitFixed() = channelFlow {
    launch {
        send(1)
    }
}
```

Pitfall 2: Forgetting `awaitClose` in `callbackFlow{}`

```kotlin
// WRONG: Listener leak
fun leakyFlow() = callbackFlow {
    val listener = { data: String -> trySend(data) }
    api.register(listener)
    // No awaitClose -> no unregister
}

// CORRECT
fun cleanFlow() = callbackFlow {
    val listener = { data: String -> trySend(data) }
    api.register(listener)
    awaitClose { api.unregister(listener) }
}
```

Pitfall 3: Using `emit()` directly in callbacks

```kotlin
// WRONG: emit is suspend, cannot be called from a regular callback
fun badFlow() = callbackFlow {
    val listener = { data: String ->
        emit(data) // ERROR
    }
}

// CORRECT: Use trySend()
fun goodFlow() = callbackFlow {
    val listener = { data: String ->
        trySend(data)
    }
}
```

Pitfall 4: Ignoring `trySend()` result

```kotlin
// May drop silently if buffer is full or channel closed
callbackFlow {
    val listener = { data: String ->
        trySend(data)
    }
}

// Better: Handle failure
callbackFlow {
    val listener = { data: String ->
        trySend(data).onFailure {
            Log.w("Flow", "Failed to send $data")
        }
    }
}

// Or configure buffer strategy
callbackFlow {
    val listener = { data: String ->
        trySend(data)
    }
}.buffer(Channel.CONFLATED)
```

### Choosing the Right Builder: Decision Guide

- Need to emit values sequentially from suspend code in a single coroutine?
  - Use `flow{}`.
- Need to combine emissions from multiple concurrent coroutines in one Flow?
  - Use `channelFlow{}`.
- Need to turn callbacks/listeners or external push APIs into a Flow?
  - Use `callbackFlow{}`.

Examples:

```kotlin
// Sequential data generation → flow{}
fun countDown() = flow {
    for (i in 10 downTo 1) {
        delay(1000)
        emit(i)
    }
}

// Parallel API calls → channelFlow{}
fun fetchAllUsers(userIds: List<String>) = channelFlow {
    userIds.forEach { id ->
        launch {
            val user = api.getUser(id)
            send(user)
        }
    }
}

// Callback-based sensor → callbackFlow{}
fun sensorData(sensor: Sensor): Flow<SensorEvent> = callbackFlow {
    val listener = object : SensorEventListener {
        override fun onSensorChanged(event: SensorEvent) {
            trySend(event)
        }

        override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}
    }

    sensorManager.registerListener(listener, sensor, SENSOR_DELAY_NORMAL)

    awaitClose {
        sensorManager.unregisterListener(listener)
    }
}
```

### Key Takeaways

1. `flow{}` — default choice, cold, sequential, minimal overhead.
2. `channelFlow{}` — cold Flow backed by Channel; supports concurrent producers and configurable buffering.
3. `callbackFlow{}` — cold Flow backed by Channel; ideal for callback/listener APIs; requires `awaitClose {}` for proper cleanup.
4. Use `emit()` in regular `flow{}` and in producer scopes when appropriate; use `send()` for suspending channel sends; use `trySend()` for non-suspending callbacks.
5. Remember that backpressure is handled by suspension; buffering strategies affect behavior for fast producers.
6. All three builders are cold; to get truly shared hot behavior, use `shareIn`, `stateIn`, or explicit shared sources (`StateFlow`, `SharedFlow`).
7. Always test cancellation and cleanup, especially when integrating with external resources.
8. Prefer `flow{}` for simplicity and performance unless you specifically need channel- or callback-based behavior.

---

## Дополнительные Вопросы (RU)

1. Как преобразовать `Flow` в `Channel` и обратно?
2. В чем различия стратегий буферизации в `channelFlow` и как они влияют на back-pressure?
3. Как обрабатывать ситуацию, когда продюсер в `callbackFlow` быстрее потребителя?
4. Какие внутренние отличия реализации между `channelFlow` и `flow` наиболее важны для понимания поведения?
5. Как тестировать долгоживущие потоки, которые эмитят значения в течение длительного времени?
6. Что произойдет, если блок `awaitClose` выбросит исключение?
7. Как построить горячий, разделяемый поток на основе этих билдеров (например, с помощью `shareIn`, `stateIn`)?

## Follow-ups

1. How do you convert a `Flow` to a `Channel` and vice versa?
2. What's the difference between buffer strategies in `channelFlow` and how do they affect backpressure?
3. How do you handle producers in `callbackFlow` that are faster than consumers?
4. What internal implementation differences between `channelFlow` and `flow` matter for behavior?
5. How do you test long-lived flows that emit over extended periods?
6. What happens if an `awaitClose` block throws an exception?
7. How do you build a hot, shared stream on top of these builders (e.g., with `shareIn`, `stateIn`)?

## Ссылки (RU)

- Документация по Kotlin Flow: https://kotlinlang.org/docs/flow.html
- `channelFlow` и `callbackFlow` в kotlinx.coroutines: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/channel-flow.html
- Статья Романа Елизарова о callback-ах и Flows: https://elizarov.medium.com/callbacks-and-kotlin-flows-2b53aa2525cf

## References

- Kotlin Flow Documentation: https://kotlinlang.org/docs/flow.html
- channelFlow vs callbackFlow: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/channel-flow.html
- Callbacks and Kotlin Flows (Elizarov): https://elizarov.medium.com/callbacks-and-kotlin-flows-2b53aa2525cf

## Связанные Вопросы (RU)

### Хаб
- [[q-kotlin-flow-basics--kotlin--medium]] — ввод в `Flow`

### Похожие (medium)
- [[q-hot-cold-flows--kotlin--medium]] — горячие vs холодные потоки
- [[q-cold-vs-hot-flows--kotlin--medium]] — объяснение разницы холодных и горячих потоков
- [[q-flow-vs-livedata-comparison--kotlin--medium]] — `Flow` vs `LiveData`
- [[q-channels-vs-flow--kotlin--medium]] — каналы против `Flow`
- [[q-sharedflow-stateflow--kotlin--medium]] — `SharedFlow` vs `StateFlow`

### Продвинутое (hard)
- [[q-flowon-operator-context-switching--kotlin--hard]] — `flowOn` и переключение контекста
- [[q-flow-backpressure--kotlin--hard]] — обработка back-pressure
- [[q-flow-backpressure-strategies--kotlin--hard]] — стратегии back-pressure

## Related Questions

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

### Related (Medium)
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold flows
- [[q-cold-vs-hot-flows--kotlin--medium]] - Cold vs Hot flows explained
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - `Flow` vs `LiveData`
- [[q-channels-vs-flow--kotlin--medium]] - Channels vs Flow
- [[q-sharedflow-stateflow--kotlin--medium]] - `SharedFlow` vs `StateFlow`

### Advanced (Harder)
- [[q-flowon-operator-context-switching--kotlin--hard]] - flowOn & context switching
- [[q-flow-backpressure--kotlin--hard]] - Backpressure handling
- [[q-flow-backpressure-strategies--kotlin--hard]] - Backpressure strategies
