---
id: kotlin-061
title: "channelFlow vs callbackFlow vs flow: when to use each / channelFlow vs callbackFlow vs flow: когда использовать"
topic: kotlin
difficulty: medium
status: draft
created: 2025-10-12
tags:
  - kotlin
  - coroutines
  - flow
  - channelflow
  - callbackflow
  - builders
moc: moc-kotlin
related: [q-channel-pipelines--kotlin--hard, q-kotlin-flow-basics--kotlin--medium, q-compose-side-effects-coroutines--kotlin--medium]
  - q-suspend-cancellable-coroutine--kotlin--hard
  - q-mutex-synchronized-coroutines--kotlin--medium
  - q-common-coroutine-mistakes--kotlin--medium
subtopics:
  - coroutines
  - flow
  - channelflow
  - callbackflow
  - builders
---

# Question (EN)
> What's the difference between `flow{}`, `channelFlow{}`, and `callbackFlow{}`? When should you use each builder?

# Вопрос (RU)
> В чем разница между `flow{}`, `channelFlow{}`, и `callbackFlow{}`? Когда следует использовать каждый билдер?

---

## Answer (EN)

Kotlin Flow provides multiple builders (`flow{}`, `channelFlow{}`, `callbackFlow{}`) each with different characteristics. Choosing the wrong builder can lead to performance issues, crashes, or incorrect behavior. Understanding when to use each is essential for production-ready Flow code.



### Overview of Flow Builders

| Builder | Type | Concurrency | Buffering | Use Case |
|---------|------|-------------|-----------|----------|
| **flow{}** | Cold | Sequential only | No buffer | Simple sequential emissions |
| **channelFlow{}** | Hot | Concurrent sends | Buffered channel | Concurrent data sources |
| **callbackFlow{}** | Hot | Concurrent sends | Buffered + awaitClose | Callback-based APIs |

### flow{} - Cold, Sequential Flow

**Characteristics:**
- **Cold**: Starts on collection
- **Sequential**: `emit()` is suspend, blocks until collected
- **No concurrency**: Cannot emit from multiple coroutines
- **No buffer**: Back-pressure by default

**Basic usage:**

```kotlin
fun simpleFlow(): Flow<Int> = flow {
    for (i in 1..5) {
        delay(100)
        emit(i) // Suspends until collector processes
    }
}

// Usage
launch {
    simpleFlow().collect { value ->
        println(value)
    }
}
```

**When to use:**
- Simple sequential data generation
- Transforming other flows
- Wrapping suspend functions
- Default choice for most cases

**Example: API pagination**

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

**Cannot emit concurrently:**

```kotlin
//  ERROR: Flow invariant is violated
fun concurrentFlow(): Flow<Int> = flow {
    launch {
        emit(1) // ERROR: emit() called from different coroutine
    }
}

// Exception: Flow invariant is violated:
// Flow was collected in [coroutine#1],
// but emission happened in [coroutine#2].
```

### channelFlow{} - Concurrent Flow

**Characteristics:**
- **Hot**: Producer runs independently
- **Concurrent**: Can `send()` from multiple coroutines
- **Buffered**: Uses Channel internally
- **No back-pressure control**: By default

**Basic usage:**

```kotlin
fun concurrentFlow(): Flow<Int> = channelFlow {
    launch {
        repeat(5) { i ->
            delay(100)
            send(i) // Can send from any coroutine
        }
    }

    launch {
        repeat(5) { i ->
            delay(150)
            send(i + 10)
        }
    }
}

// Output: 0, 10, 1, 2, 11, 3, 4, 12, 13, 14
// Interleaved from both coroutines
```

**When to use:**
- Multiple concurrent data sources
- Parallel data processing
- Need buffering between producer and consumer
- Converting channels to flows

**Example: Parallel API calls**

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

**Buffer configuration:**

```kotlin
fun bufferedFlow(): Flow<Int> = channelFlow {
    // Set buffer capacity
    // Default: Channel.BUFFERED (64)
    launch {
        repeat(100) { i ->
            send(i)
        }
    }
}.buffer(capacity = Channel.UNLIMITED) // Or CONFLATED, RENDEZVOUS, etc.
```

### callbackFlow{} - Callback-Based APIs

**Characteristics:**
- **Hot**: Producer runs independently
- **Concurrent**: Can `send()` from callbacks
- **Buffered**: Uses Channel
- **awaitClose {}**: Required cleanup block
- **trySend()**: Non-suspending send for callbacks

**Basic usage:**

```kotlin
fun locationUpdates(locationManager: LocationManager): Flow<Location> = callbackFlow {
    val listener = object : LocationListener {
        override fun onLocationChanged(location: Location) {
            trySend(location) // Non-suspending for callback
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

    // REQUIRED: Cleanup when flow is closed/cancelled
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

**When to use:**
- Converting callback-based APIs
- Event listeners (clicks, sensors, network)
- WebSockets, SSE (Server-Sent Events)
- Any API that pushes data via callbacks

**awaitClose is mandatory:**

```kotlin
//  WRONG: No awaitClose
fun badCallbackFlow() = callbackFlow {
    val listener = { data: String ->
        trySend(data)
    }
    api.registerListener(listener)
    // Missing awaitClose - listener never removed!
}

//  CORRECT: With awaitClose
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
            trySend(snapshot).isSuccess // Check if sent successfully
        }

        override fun onCancelled(error: DatabaseError) {
            close(error.toException()) // Close flow with error
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

    // Under the hood, Room uses something like:
    fun getUserFlowManual(userId: String): Flow<User> = callbackFlow {
        val observer = object : InvalidationTracker.Observer("users") {
            override fun onInvalidated(tables: Set<String>) {
                // Query and send new data
                val user = queryUser(userId)
                trySend(user)
            }
        }

        database.invalidationTracker.addObserver(observer)

        // Send initial value
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
            trySend(text)
        }

        override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
            close(t)
        }

        override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
            channel.close()
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

### send() vs trySend() vs emit()

**emit():** Suspending, waits for collector
- Use in: `flow{}`, `channelFlow{}`
- Cannot use in: callbacks (not suspend)

**send():** Suspending, waits for buffer space
- Use in: `channelFlow{}`, `callbackFlow{}`
- Cannot use in: `flow{}`

**trySend():** Non-suspending, returns immediately
- Use in: callbacks within `callbackFlow{}`
- Returns: `ChannelResult<Unit>` (success/failure)

```kotlin
// flow{} - use emit()
flow {
    emit(1) // Suspending
}

// channelFlow{} - use send() or emit()
channelFlow {
    send(1) // Suspending
    emit(1) // Also available, same as send()
}

// callbackFlow{} - use send() in coroutines, trySend() in callbacks
callbackFlow {
    launch {
        send(1) // Suspending - OK in coroutine
    }

    val callback = { value: Int ->
        trySend(value) // Non-suspending - OK in callback
    }

    awaitClose { }
}
```

### Error Handling

**flow{}:**

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

**channelFlow{}:**

```kotlin
fun channelFlowWithError(): Flow<Int> = channelFlow {
    launch {
        send(1)
        throw RuntimeException("Error in launch")
    }

    launch {
        send(2) // This still executes
    }
}

// Errors in launch don't automatically close flow
// Use CoroutineExceptionHandler or try-catch
```

**callbackFlow{}:**

```kotlin
fun callbackFlowWithError(): Flow<String> = callbackFlow {
    val listener = object : Listener {
        override fun onData(data: String) {
            trySend(data)
        }

        override fun onError(error: Exception) {
            close(error) // Close flow with error
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

**flow{}:** Automatically cancelled when collector cancels

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

**channelFlow{}/callbackFlow{}:** Use awaitClose for cleanup

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

### Performance Implications

**flow{}:**
- **Lowest overhead**: Direct emit, no channel
- **Best for**: Simple sequential operations
- **Latency**: Lowest (no buffering)

**channelFlow{}:**
- **Medium overhead**: Channel buffering
- **Best for**: Concurrent producers
- **Latency**: Higher (buffering delay)

**callbackFlow{}:**
- **Medium overhead**: Channel buffering + callback management
- **Best for**: Callback-based APIs
- **Latency**: Depends on callback frequency

**Benchmark:**

```kotlin
// flow{}: ~100ns per emission
flow {
    repeat(10000) { emit(it) }
}.collect { }

// channelFlow{}: ~500ns per emission (channel overhead)
channelFlow {
    repeat(10000) { send(it) }
}.collect { }

// callbackFlow{}: ~500ns + callback overhead
```

### Testing Strategies

**Testing flow{}:**

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

**Testing channelFlow{}:**

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

**Testing callbackFlow{}:**

```kotlin
@Test
fun `test callback flow`() = runTest {
    val listener = FakeListener()

    val flow = callbackFlow {
        listener.callback = { trySend(it) }
        awaitClose { listener.callback = null }
    }

    launch {
        flow.take(3).collect { value ->
            println(value)
        }
    }

    listener.emit("A")
    listener.emit("B")
    listener.emit("C")
}

class FakeListener {
    var callback: ((String) -> Unit)? = null

    fun emit(value: String) {
        callback?.invoke(value)
    }
}
```

### Common Pitfalls

**Pitfall 1: Using flow{} for concurrent emissions**

```kotlin
//  WRONG: Crashes
fun concurrentEmit() = flow {
    launch {
        emit(1) // ERROR: Flow invariant violated
    }
}

//  CORRECT: Use channelFlow
fun concurrentEmit() = channelFlow {
    launch {
        send(1) // OK
    }
}
```

**Pitfall 2: Forgetting awaitClose in callbackFlow**

```kotlin
//  WRONG: Listener leak
fun leakyFlow() = callbackFlow {
    val listener = { trySend(it) }
    api.register(listener)
    // Listener never unregistered!
}

//  CORRECT: awaitClose
fun cleanFlow() = callbackFlow {
    val listener = { trySend(it) }
    api.register(listener)
    awaitClose { api.unregister(listener) }
}
```

**Pitfall 3: Using emit() in callbacks**

```kotlin
//  WRONG: emit is suspend, can't use in callback
fun badFlow() = callbackFlow {
    val listener = { data: String ->
        emit(data) // ERROR: suspend function in non-suspend callback
    }
}

//  CORRECT: Use trySend()
fun goodFlow() = callbackFlow {
    val listener = { data: String ->
        trySend(data) // Non-suspending
    }
}
```

**Pitfall 4: Not checking trySend() result**

```kotlin
//  WARNING: Silently drops if buffer full
callbackFlow {
    val listener = { data: String ->
        trySend(data) // Drops if buffer full!
    }
}

//  BETTER: Handle failure
callbackFlow {
    val listener = { data: String ->
        trySend(data).onFailure {
            Log.w("Flow", "Failed to send $data")
        }
    }
}

//  BEST: Use channel buffer strategy
callbackFlow {
    val listener = { data: String ->
        trySend(data)
    }
}.buffer(Channel.CONFLATED) // Drop oldest on buffer full
```

### Choosing the Right Builder: Decision Tree

```
Need to emit values?
 Sequential emissions?
   Use flow{}

 Concurrent emissions from multiple coroutines?
   Use channelFlow{}

 Emissions from callbacks/listeners?
    Use callbackFlow{}
```

**Examples:**

```kotlin
// Sequential data generation → flow{}
fun countDown() = flow {
    for (i in 10 downTo 1) {
        delay(1000)
        emit(i)
    }
}

// Parallel API calls → channelFlow{}
fun fetchAllUsers() = channelFlow {
    userIds.forEach { id ->
        launch {
            val user = api.getUser(id)
            send(user)
        }
    }
}

// Callback-based sensor → callbackFlow{}
fun sensorData(sensor: Sensor) = callbackFlow {
    val listener = object : SensorEventListener {
        override fun onSensorChanged(event: SensorEvent) {
            trySend(event)
        }
    }
    sensorManager.registerListener(listener, sensor, SENSOR_DELAY_NORMAL)
    awaitClose { sensorManager.unregisterListener(listener) }
}
```

### Key Takeaways

1. **flow{}** - Default choice, sequential, cold
2. **channelFlow{}** - Concurrent producers, hot
3. **callbackFlow{}** - Callback APIs, hot, requires awaitClose
4. **emit() vs send() vs trySend()** - Know when to use each
5. **awaitClose is mandatory** - In callbackFlow for cleanup
6. **Cold vs Hot** - flow{} is cold, others are hot
7. **Buffering** - channelFlow/callbackFlow have buffers
8. **Choose based on data source** - Sequential, concurrent, or callback
9. **Test cancellation** - Ensure cleanup happens
10. **Consider performance** - flow{} has lowest overhead

---

## Ответ (RU)

Kotlin Flow предоставляет несколько билдеров (`flow{}`, `channelFlow{}`, `callbackFlow{}`), каждый с разными характеристиками. Выбор неправильного билдера может привести к проблемам производительности, крашам или некорректному поведению. Понимание когда использовать каждый критично для production-ready Flow кода.



[Полный русский перевод следует той же структуре]

### Ключевые выводы

1. **flow{}** - Выбор по умолчанию, последовательный, холодный
2. **channelFlow{}** - Конкурентные производители, горячий
3. **callbackFlow{}** - Callback API, горячий, требует awaitClose
4. **emit() vs send() vs trySend()** - Знайте когда использовать каждый
5. **awaitClose обязателен** - В callbackFlow для очистки
6. **Холодный vs Горячий** - flow{} холодный, остальные горячие
7. **Буферизация** - channelFlow/callbackFlow имеют буферы
8. **Выбирайте на основе источника данных** - Последовательный, конкурентный или callback
9. **Тестируйте отмену** - Убедитесь что очистка происходит
10. **Учитывайте производительность** - flow{} имеет наименьшие накладные расходы

---

## Follow-ups

1. How do you convert a Flow to a Channel and vice versa?
2. What's the difference between buffer strategies in channelFlow?
3. How do you handle backpressure in callbackFlow when producer is faster than consumer?
4. Can you explain the internal implementation of channelFlow vs flow?
5. How do you test flows that emit values over long periods?
6. What happens if awaitClose throws an exception?
7. How do you implement a hybrid flow that's both hot and cold?

## References

- [Kotlin Flow Documentation](https://kotlinlang.org/docs/flow.html)
- [channelFlow vs callbackFlow](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/channel-flow.html)
- [Flow Builders](https://elizarov.medium.com/callbacks-and-kotlin-flows-2b53aa2525cf)

## Related Questions

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

### Related (Medium)
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold flows
- [[q-cold-vs-hot-flows--kotlin--medium]] - Cold vs Hot flows explained
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - Flow vs LiveData
- [[q-channels-vs-flow--kotlin--medium]] - Channels vs Flow
- [[q-sharedflow-stateflow--kotlin--medium]] - SharedFlow vs StateFlow

### Advanced (Harder)
- [[q-flowon-operator-context-switching--kotlin--hard]] - flowOn & context switching
- [[q-flow-backpressure--kotlin--hard]] - Backpressure handling
- [[q-flow-backpressure-strategies--kotlin--hard]] - Backpressure strategies
