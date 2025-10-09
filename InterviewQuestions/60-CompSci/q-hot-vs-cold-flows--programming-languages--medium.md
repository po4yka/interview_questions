---
tags:
  - programming-languages
difficulty: medium
status: reviewed
---

# Hot vs Cold Flows

## Answer

**Cold flows** start generating data only after subscription (lazy).
Examples: Flow, Observable

**Hot flows** generate data independently of subscribers (eager).
Examples: SharedFlow, StateFlow, LiveData, Broadcast

### Cold Flow Characteristics

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// Cold Flow: Starts only when collected
fun coldFlowExample(): Flow<Int> = flow {
    println("Flow started")  // Printed when collect() is called
    repeat(3) { i ->
        delay(100)
        emit(i)
    }
}

fun main() = runBlocking {
    val coldFlow = coldFlowExample()
    println("Flow created")

    delay(1000)
    println("Starting collection")

    coldFlow.collect { value ->
        println("Received: $value")
    }
}

// Output:
// Flow created
// (1 second delay)
// Starting collection
// Flow started  <- Only starts when collect() is called
// Received: 0
// Received: 1
// Received: 2
```

### Hot Flow Characteristics

```kotlin
// Hot Flow: Starts immediately, emits regardless of subscribers
fun hotFlowExample() = runBlocking {
    val hotFlow = MutableSharedFlow<Int>()

    // Start emitting (no subscribers yet)
    launch {
        repeat(5) { i ->
            println("Emitting $i")
            hotFlow.emit(i)
            delay(100)
        }
    }

    delay(250)  // Wait before subscribing

    // Subscribe late - will miss first values
    launch {
        hotFlow.collect { value ->
            println("Subscriber 1: $value")
        }
    }

    delay(500)
}

// Output:
// Emitting 0  <- Emitted before any subscriber
// Emitting 1  <- Emitted before any subscriber
// Emitting 2  <- Emitted before any subscriber
// Subscriber 1: 2  <- Late subscriber, missed 0 and 1
// Emitting 3
// Subscriber 1: 3
// Emitting 4
// Subscriber 1: 4
```

### Cold Flow - Each Collector Gets Own Execution

```kotlin
fun multipleColdCollectors() = runBlocking {
    val coldFlow = flow {
        println("Flow started for ${Thread.currentThread().name}")
        repeat(3) { emit(it) }
    }

    // Collector 1
    launch {
        coldFlow.collect { println("Collector 1: $it") }
    }

    // Collector 2
    launch {
        coldFlow.collect { println("Collector 2: $it") }
    }
}

// Output:
// Flow started for ...  <- Started for collector 1
// Collector 1: 0
// Flow started for ...  <- Started again for collector 2
// Collector 1: 1
// Collector 2: 0
// ...
// (Each collector gets independent execution)
```

### Hot Flow - Shared Execution

```kotlin
fun multipleHotCollectors() = runBlocking {
    val hotFlow = MutableSharedFlow<Int>()

    // Start emitting
    launch {
        repeat(5) { i ->
            hotFlow.emit(i)
            delay(100)
        }
    }

    // Collector 1
    launch {
        hotFlow.collect { println("Collector 1: $it") }
    }

    delay(50)

    // Collector 2 joins later
    launch {
        hotFlow.collect { println("Collector 2: $it") }
    }

    delay(500)
}

// Output:
// Collector 1: 0
// Collector 1: 1
// Collector 2: 1  <- Collector 2 starts here, receives same value
// Collector 1: 2
// Collector 2: 2
// ...
// (Both collectors receive same values from shared source)
```

### Converting Cold to Hot

```kotlin
// shareIn: Convert cold to hot
fun coldToHot() = runBlocking {
    val coldFlow = flow {
        println("Flow started")
        repeat(5) { i ->
            delay(100)
            emit(i)
        }
    }

    // Convert to hot flow
    val hotFlow = coldFlow.shareIn(
        scope = this,
        started = SharingStarted.Eagerly,
        replay = 0
    )

    delay(250)

    // Subscribe to hot flow (flow already started)
    hotFlow.collect { println("Received: $it") }
}
```

### Converting Hot to Cold

```kotlin
// Every collector gets the hot flow, but it's still hot
fun hotFlowUsage() = runBlocking {
    val sharedFlow = MutableSharedFlow<Int>()

    // Each collect call subscribes to the same shared source
    launch {
        sharedFlow.collect { println("A: $it") }
    }

    launch {
        sharedFlow.collect { println("B: $it") }
    }

    // Both receive same values
    sharedFlow.emit(1)
    sharedFlow.emit(2)
}
```

### StateFlow - Hot Flow with State

```kotlin
fun stateFlowExample() = runBlocking {
    val stateFlow = MutableStateFlow(0)

    // StateFlow is hot - always has a value
    println("Initial value: ${stateFlow.value}")  // 0

    // Start updating
    launch {
        repeat(5) { i ->
            delay(100)
            stateFlow.value = i + 1
        }
    }

    delay(250)

    // Late subscriber gets current value immediately
    launch {
        stateFlow.collect { println("Subscriber: $it") }
    }

    delay(500)
}

// Output:
// Initial value: 0
// Subscriber: 2  <- Late subscriber immediately gets current value
// Subscriber: 3
// Subscriber: 4
// Subscriber: 5
```

### Real-World Examples

```kotlin
// Cold Flow: API calls (each collector makes own request)
class Repository {
    fun getUsers(): Flow<List<User>> = flow {
        val users = api.fetchUsers()  // New request for each collector
        emit(users)
    }
}

// Hot Flow: Location updates (single source, multiple observers)
class LocationService {
    private val _location = MutableSharedFlow<Location>()
    val location: SharedFlow<Location> = _location.asSharedFlow()

    init {
        // Start receiving location updates immediately
        locationProvider.startUpdates { newLocation ->
            _location.tryEmit(newLocation)
        }
    }
}

// StateFlow: UI state (always has current value)
class ViewModel {
    private val _uiState = MutableStateFlow(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    // Late subscribers immediately get current state
}
```

### Summary Table

| Feature | Cold Flow | Hot Flow |
|---------|-----------|----------|
| **Start behavior** | On collection | Immediately or on first subscriber |
| **Execution** | Independent per collector | Shared among collectors |
| **Late subscribers** | Get all values from start | Miss previous values (unless replay) |
| **Examples** | Flow, Observable | SharedFlow, StateFlow, LiveData |
| **Use case** | API calls, transformations | Events, state, sensors |
| **Resource usage** | New execution per collector | Single execution shared |

---
## Вопрос (RU)

В чем отличие горячих и холодных потоков

## Ответ

Холодные (cold) — начинают генерировать данные только после подписки Например Flow Observable Горячие (hot) — генерируют данные независимо от подписчиков Например SharedFlow LiveData Broadcast
