---
id: 20251012-140002
title: "Testing StateFlow and SharedFlow in ViewModels / Тестирование StateFlow и SharedFlow в ViewModels"
aliases: []

# Classification
topic: kotlin
subtopics: [coroutines, testing, stateflow, sharedflow, viewmodel]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Flow Testing Guide

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-testing-coroutines-runtest--kotlin--medium, q-testing-flow-operators--kotlin--hard, q-stateflow-sharedflow-differences--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [kotlin, coroutines, testing, stateflow, sharedflow, viewmodel, difficulty/medium]
---
# Question (EN)
> How to test StateFlow and SharedFlow in ViewModels? Cover collection strategies, turbine library, TestScope, assertions, and edge cases like replay cache and conflation.

# Вопрос (RU)
> Как тестировать StateFlow и SharedFlow в ViewModels? Покрыть стратегии коллекции, библиотеку turbine, TestScope, утверждения и граничные случаи вроде replay cache и conflation.

---

## Answer (EN)

Testing StateFlow and SharedFlow requires understanding their unique characteristics: StateFlow maintains current state and conflates values, while SharedFlow can replay emissions and doesn't have conflation by default.

### StateFlow Basics

StateFlow is a hot Flow that always has a value and emits the most recent value to new collectors.

```kotlin
class CounterViewModel : ViewModel() {
    private val _counter = MutableStateFlow(0)
    val counter: StateFlow<Int> = _counter.asStateFlow()

    fun increment() {
        _counter.value++
    }

    fun decrement() {
        _counter.value--
    }

    fun reset() {
        _counter.value = 0
    }
}

// Basic StateFlow testing
@OptIn(ExperimentalCoroutinesApi::class)
class CounterViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var viewModel: CounterViewModel

    @Before
    fun setup() {
        viewModel = CounterViewModel()
    }

    @Test
    fun `initial state is 0`() {
        assertEquals(0, viewModel.counter.value)
    }

    @Test
    fun `increment increases counter`() {
        viewModel.increment()
        assertEquals(1, viewModel.counter.value)

        viewModel.increment()
        assertEquals(2, viewModel.counter.value)
    }

    @Test
    fun `decrement decreases counter`() {
        viewModel.increment()
        viewModel.increment()
        viewModel.decrement()

        assertEquals(1, viewModel.counter.value)
    }

    @Test
    fun `reset sets counter to 0`() {
        viewModel.increment()
        viewModel.increment()
        viewModel.reset()

        assertEquals(0, viewModel.counter.value)
    }
}
```

### Testing StateFlow with Async Operations

```kotlin
sealed class UiState<out T> {
    object Idle : UiState<Nothing>()
    object Loading : UiState<Nothing>()
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val message: String) : UiState<Nothing>()
}

class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState<User>>(UiState.Idle)
    val uiState: StateFlow<UiState<User>> = _uiState.asStateFlow()

    fun loadUser(id: Int) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            try {
                val user = repository.fetchUser(id)
                _uiState.value = UiState.Success(user)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var repository: FakeUserRepository
    private lateinit var viewModel: UserViewModel

    @Before
    fun setup() {
        repository = FakeUserRepository()
        viewModel = UserViewModel(repository)
    }

    @Test
    fun `loadUser success emits Loading then Success`() = runTest {
        val user = User(1, "John Doe", "john@example.com")
        repository.setResult(Result.success(user))

        val states = mutableListOf<UiState<User>>()
        val job = launch(UnconfinedTestDispatcher(testScheduler)) {
            viewModel.uiState.collect { states.add(it) }
        }

        viewModel.loadUser(1)
        advanceUntilIdle()

        assertEquals(3, states.size)
        assertTrue(states[0] is UiState.Idle)
        assertTrue(states[1] is UiState.Loading)
        assertTrue(states[2] is UiState.Success)
        assertEquals(user, (states[2] as UiState.Success).data)

        job.cancel()
    }

    @Test
    fun `loadUser failure emits Loading then Error`() = runTest {
        repository.setResult(Result.failure(IOException("Network error")))

        val states = mutableListOf<UiState<User>>()
        val job = launch(UnconfinedTestDispatcher(testScheduler)) {
            viewModel.uiState.collect { states.add(it) }
        }

        viewModel.loadUser(1)
        advanceUntilIdle()

        assertEquals(3, states.size)
        assertTrue(states[0] is UiState.Idle)
        assertTrue(states[1] is UiState.Loading)
        assertTrue(states[2] is UiState.Error)
        assertEquals("Network error", (states[2] as UiState.Error).message)

        job.cancel()
    }

    @Test
    fun `loadUser can be called multiple times`() = runTest {
        repository.setResult(Result.success(User(1, "User 1", "user1@example.com")))

        viewModel.loadUser(1)
        advanceUntilIdle()

        assertTrue(viewModel.uiState.value is UiState.Success)

        repository.setResult(Result.success(User(2, "User 2", "user2@example.com")))
        viewModel.loadUser(2)
        advanceUntilIdle()

        val state = viewModel.uiState.value as UiState.Success
        assertEquals(User(2, "User 2", "user2@example.com"), state.data)
    }
}
```

### Testing StateFlow Conflation

StateFlow conflates rapid emissions - only the latest value is kept.

```kotlin
class RapidUpdatesViewModel : ViewModel() {
    private val _value = MutableStateFlow(0)
    val value: StateFlow<Int> = _value.asStateFlow()

    fun updateRapidly() {
        viewModelScope.launch {
            repeat(100) {
                _value.value = it
            }
        }
    }
}

@Test
fun `StateFlow conflates rapid updates`() = runTest {
    val viewModel = RapidUpdatesViewModel()

    val emissions = mutableListOf<Int>()
    val job = launch(UnconfinedTestDispatcher(testScheduler)) {
        viewModel.value.collect { emissions.add(it) }
    }

    viewModel.updateRapidly()
    advanceUntilIdle()

    // StateFlow conflates, so we don't see all 100 values
    // We see: initial (0), and final (99)
    assertTrue(emissions.size < 100)
    assertEquals(0, emissions.first())
    assertEquals(99, emissions.last())

    job.cancel()
}

@Test
fun `StateFlow current value is always available`() {
    val viewModel = RapidUpdatesViewModel()

    // Current value accessible without collection
    assertEquals(0, viewModel.value.value)

    viewModel.updateRapidly()

    // After updates complete, final value is available
    assertEquals(99, viewModel.value.value)
}
```

### Testing SharedFlow Basics

SharedFlow is a hot Flow that can have replay cache and doesn't conflate by default.

```kotlin
class EventsViewModel : ViewModel() {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    fun sendEvent(event: Event) {
        viewModelScope.launch {
            _events.emit(event)
        }
    }
}

sealed class Event {
    object UserLoggedIn : Event()
    data class UserLoggedOut(val reason: String) : Event()
    data class DataLoaded(val itemCount: Int) : Event()
    data class Error(val message: String) : Event()
}

@OptIn(ExperimentalCoroutinesApi::class)
class EventsViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var viewModel: EventsViewModel

    @Before
    fun setup() {
        viewModel = EventsViewModel()
    }

    @Test
    fun `events are emitted to collectors`() = runTest {
        val collectedEvents = mutableListOf<Event>()
        val job = launch(UnconfinedTestDispatcher(testScheduler)) {
            viewModel.events.collect { collectedEvents.add(it) }
        }

        viewModel.sendEvent(Event.UserLoggedIn)
        viewModel.sendEvent(Event.DataLoaded(10))
        viewModel.sendEvent(Event.Error("Test error"))

        advanceUntilIdle()

        assertEquals(3, collectedEvents.size)
        assertTrue(collectedEvents[0] is Event.UserLoggedIn)
        assertTrue(collectedEvents[1] is Event.DataLoaded)
        assertTrue(collectedEvents[2] is Event.Error)

        job.cancel()
    }

    @Test
    fun `SharedFlow has no initial value`() = runTest {
        val collectedEvents = mutableListOf<Event>()
        val job = launch(UnconfinedTestDispatcher(testScheduler)) {
            viewModel.events.take(2).collect { collectedEvents.add(it) }
        }

        // Nothing collected yet
        assertTrue(collectedEvents.isEmpty())

        viewModel.sendEvent(Event.UserLoggedIn)
        advanceUntilIdle()

        assertEquals(1, collectedEvents.size)

        viewModel.sendEvent(Event.DataLoaded(5))
        advanceUntilIdle()

        assertEquals(2, collectedEvents.size)

        job.cancel()
    }
}
```

### Testing SharedFlow with Replay Cache

```kotlin
class NotificationsViewModel : ViewModel() {
    // replay = 3: Last 3 emissions are replayed to new collectors
    private val _notifications = MutableSharedFlow<Notification>(
        replay = 3,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val notifications: SharedFlow<Notification> = _notifications.asSharedFlow()

    fun notify(notification: Notification) {
        viewModelScope.launch {
            _notifications.emit(notification)
        }
    }
}

data class Notification(val id: Int, val message: String)

@Test
fun `SharedFlow replays last N emissions to new collectors`() = runTest {
    val viewModel = NotificationsViewModel()

    // Emit 5 notifications before collecting
    viewModel.notify(Notification(1, "Message 1"))
    viewModel.notify(Notification(2, "Message 2"))
    viewModel.notify(Notification(3, "Message 3"))
    viewModel.notify(Notification(4, "Message 4"))
    viewModel.notify(Notification(5, "Message 5"))

    advanceUntilIdle()

    // Now collect - should receive last 3 (replay cache)
    val collected = mutableListOf<Notification>()
    val job = launch(UnconfinedTestDispatcher(testScheduler)) {
        viewModel.notifications.take(3).collect { collected.add(it) }
    }

    advanceUntilIdle()

    assertEquals(3, collected.size)
    assertEquals(3, collected[0].id)
    assertEquals(4, collected[1].id)
    assertEquals(5, collected[2].id)

    job.cancel()
}

@Test
fun `multiple collectors receive same emissions`() = runTest {
    val viewModel = NotificationsViewModel()

    val collector1 = mutableListOf<Notification>()
    val collector2 = mutableListOf<Notification>()

    val job1 = launch(UnconfinedTestDispatcher(testScheduler)) {
        viewModel.notifications.collect { collector1.add(it) }
    }

    val job2 = launch(UnconfinedTestDispatcher(testScheduler)) {
        viewModel.notifications.collect { collector2.add(it) }
    }

    viewModel.notify(Notification(1, "Message 1"))
    viewModel.notify(Notification(2, "Message 2"))

    advanceUntilIdle()

    assertEquals(collector1, collector2)
    assertEquals(2, collector1.size)

    job1.cancel()
    job2.cancel()
}
```

### Using Turbine Library

Turbine makes Flow testing much cleaner and more readable.

```gradle
testImplementation("app.cash.turbine:turbine:1.0.0")
```

```kotlin
import app.cash.turbine.test

class SearchViewModel(
    private val repository: SearchRepository
) : ViewModel() {

    private val _searchResults = MutableStateFlow<List<SearchResult>>(emptyList())
    val searchResults: StateFlow<List<SearchResult>> = _searchResults.asStateFlow()

    private val _searchEvents = MutableSharedFlow<SearchEvent>()
    val searchEvents: SharedFlow<SearchEvent> = _searchEvents.asSharedFlow()

    fun search(query: String) {
        viewModelScope.launch {
            _searchEvents.emit(SearchEvent.SearchStarted)

            try {
                val results = repository.search(query)
                _searchResults.value = results
                _searchEvents.emit(SearchEvent.SearchCompleted(results.size))
            } catch (e: Exception) {
                _searchEvents.emit(SearchEvent.SearchFailed(e.message ?: "Unknown error"))
            }
        }
    }
}

sealed class SearchEvent {
    object SearchStarted : SearchEvent()
    data class SearchCompleted(val resultCount: Int) : SearchEvent()
    data class SearchFailed(val error: String) : SearchEvent()
}

// Tests with Turbine
@OptIn(ExperimentalCoroutinesApi::class)
class SearchViewModelTurbineTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `search updates results - with turbine`() = runTest {
        val repository = FakeSearchRepository()
        val viewModel = SearchViewModel(repository)

        viewModel.searchResults.test {
            // Initial value
            assertEquals(emptyList(), awaitItem())

            repository.setResults(listOf(
                SearchResult("Result 1"),
                SearchResult("Result 2")
            ))
            viewModel.search("query")

            // Wait for update
            val results = awaitItem()
            assertEquals(2, results.size)
            assertEquals("Result 1", results[0].title)

            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `search emits events - with turbine`() = runTest {
        val repository = FakeSearchRepository()
        val viewModel = SearchViewModel(repository)

        viewModel.searchEvents.test {
            repository.setResults(listOf(SearchResult("Result")))
            viewModel.search("query")

            // Expect SearchStarted
            val startedEvent = awaitItem()
            assertTrue(startedEvent is SearchEvent.SearchStarted)

            // Expect SearchCompleted
            val completedEvent = awaitItem()
            assertTrue(completedEvent is SearchEvent.SearchCompleted)
            assertEquals(1, (completedEvent as SearchEvent.SearchCompleted).resultCount)

            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `search failure emits error event - with turbine`() = runTest {
        val repository = FakeSearchRepository()
        repository.shouldFail = true
        val viewModel = SearchViewModel(repository)

        viewModel.searchEvents.test {
            viewModel.search("query")

            awaitItem() // SearchStarted

            val errorEvent = awaitItem()
            assertTrue(errorEvent is SearchEvent.SearchFailed)
            assertEquals("Search error", (errorEvent as SearchEvent.SearchFailed).error)

            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `turbine expectNoEvents validates no emissions`() = runTest {
        val viewModel = SearchViewModel(FakeSearchRepository())

        viewModel.searchEvents.test {
            // Expect no events initially
            expectNoEvents()

            viewModel.search("query")
            awaitItem() // SearchStarted
            awaitItem() // SearchCompleted

            // No more events
            expectNoEvents()
        }
    }
}
```

### Turbine Advanced Features

```kotlin
@Test
fun `turbine awaitItem with timeout`() = runTest {
    val viewModel = SlowViewModel()

    viewModel.results.test(timeout = 5.seconds) {
        viewModel.loadData()

        val result = awaitItem()
        assertNotNull(result)
    }
}

@Test
fun `turbine skip items`() = runTest {
    val viewModel = RapidEmissionsViewModel()

    viewModel.values.test {
        val initial = awaitItem()
        assertEquals(0, initial)

        viewModel.startEmitting()

        skipItems(5) // Skip first 5 emissions

        val item = awaitItem()
        assertTrue(item >= 5)

        cancelAndIgnoreRemainingEvents()
    }
}

@Test
fun `turbine expect error`() = runTest {
    val viewModel = ErrorViewModel()

    viewModel.data.test {
        viewModel.loadDataThatFails()

        val error = awaitError()
        assertTrue(error is IOException)
        assertEquals("Load failed", error.message)
    }
}

@Test
fun `turbine expect completion`() = runTest {
    val flow = flow {
        emit(1)
        emit(2)
        emit(3)
    }

    flow.test {
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())
        assertEquals(3, awaitItem())
        awaitComplete() // Flow completes normally
    }
}

@Test
fun `turbine multiple assertions`() = runTest {
    val viewModel = CounterViewModel()

    viewModel.counter.test {
        assertEquals(0, awaitItem())

        viewModel.increment()
        assertEquals(1, awaitItem())

        viewModel.increment()
        assertEquals(2, awaitItem())

        viewModel.decrement()
        assertEquals(1, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Testing StateFlow distinctUntilChanged

StateFlow only emits when value changes (built-in distinctUntilChanged).

```kotlin
class ToggleViewModel : ViewModel() {
    private val _isEnabled = MutableStateFlow(false)
    val isEnabled: StateFlow<Boolean> = _isEnabled.asStateFlow()

    fun toggle() {
        _isEnabled.value = !_isEnabled.value
    }

    fun setEnabled(enabled: Boolean) {
        _isEnabled.value = enabled
    }
}

@Test
fun `StateFlow skips duplicate values`() = runTest {
    val viewModel = ToggleViewModel()

    viewModel.isEnabled.test {
        assertEquals(false, awaitItem())

        // Set to same value - no emission
        viewModel.setEnabled(false)
        expectNoEvents()

        // Change value - emission
        viewModel.setEnabled(true)
        assertEquals(true, awaitItem())

        // Set to same value again - no emission
        viewModel.setEnabled(true)
        expectNoEvents()

        // Change back - emission
        viewModel.setEnabled(false)
        assertEquals(false, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}

@Test
fun `toggle always emits`() = runTest {
    val viewModel = ToggleViewModel()

    viewModel.isEnabled.test {
        assertEquals(false, awaitItem())

        viewModel.toggle()
        assertEquals(true, awaitItem())

        viewModel.toggle()
        assertEquals(false, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Testing SharedFlow Buffer Overflow

```kotlin
class BufferedEventsViewModel : ViewModel() {
    private val _events = MutableSharedFlow<Int>(
        replay = 0,
        extraBufferCapacity = 3,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val events: SharedFlow<Int> = _events.asSharedFlow()

    suspend fun emitMany(count: Int) {
        repeat(count) {
            _events.emit(it)
        }
    }
}

@Test
fun `SharedFlow drops oldest when buffer full`() = runTest {
    val viewModel = BufferedEventsViewModel()

    // Emit many values without collector
    viewModel.emitMany(10)

    // Collect - should only get last 3 (buffer capacity)
    val collected = mutableListOf<Int>()
    viewModel.events.take(3).test {
        // But replay is 0, so won't get old emissions
        expectNoEvents()
    }

    // Emit while collecting
    viewModel.events.test {
        viewModel.emitMany(10)

        // With DROP_OLDEST and buffer=3, get last 3
        val items = List(3) { awaitItem() }

        // Exact values depend on timing, but should be last ones
        assertTrue(items.all { it >= 7 })

        cancelAndIgnoreRemainingEvents()
    }
}

@Test
fun `SharedFlow with SUSPEND strategy blocks emitter`() = runTest {
    val viewModel = object : ViewModel() {
        val events = MutableSharedFlow<Int>(
            replay = 0,
            extraBufferCapacity = 2,
            onBufferOverflow = BufferOverflow.SUSPEND
        )

        suspend fun emit(value: Int) {
            events.emit(value) // Will suspend if buffer full
        }
    }

    val emissions = mutableListOf<Int>()
    var emitterCompleted = false

    // Start collecting slowly
    val collectorJob = launch {
        viewModel.events.collect {
            emissions.add(it)
            delay(100) // Slow collector
        }
    }

    // Emit rapidly - should block after buffer is full
    val emitterJob = launch {
        repeat(5) {
            viewModel.emit(it)
        }
        emitterCompleted = true
    }

    advanceTimeBy(50)
    // Emitter blocked because collector is slow and buffer full
    assertFalse(emitterCompleted)

    advanceUntilIdle()
    // Now all emitted
    assertTrue(emitterCompleted)
    assertEquals(5, emissions.size)

    collectorJob.cancel()
    emitterJob.cancel()
}
```

### Testing StateFlow with Derived State

```kotlin
class ShoppingCartViewModel : ViewModel() {
    private val _items = MutableStateFlow<List<CartItem>>(emptyList())
    val items: StateFlow<List<CartItem>> = _items.asStateFlow()

    val totalPrice: StateFlow<Double> = _items
        .map { items -> items.sumOf { it.price * it.quantity } }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = 0.0
        )

    val itemCount: StateFlow<Int> = _items
        .map { it.size }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = 0
        )

    fun addItem(item: CartItem) {
        _items.value = _items.value + item
    }

    fun removeItem(itemId: String) {
        _items.value = _items.value.filterNot { it.id == itemId }
    }

    fun clear() {
        _items.value = emptyList()
    }
}

data class CartItem(val id: String, val name: String, val price: Double, val quantity: Int)

@Test
fun `derived StateFlows update when source changes`() = runTest {
    val viewModel = ShoppingCartViewModel()

    val totalPrices = mutableListOf<Double>()
    val itemCounts = mutableListOf<Int>()

    val totalJob = launch(UnconfinedTestDispatcher(testScheduler)) {
        viewModel.totalPrice.collect { totalPrices.add(it) }
    }

    val countJob = launch(UnconfinedTestDispatcher(testScheduler)) {
        viewModel.itemCount.collect { itemCounts.add(it) }
    }

    // Initial values
    runCurrent()
    assertEquals(0.0, totalPrices.last())
    assertEquals(0, itemCounts.last())

    // Add item
    viewModel.addItem(CartItem("1", "Item 1", 10.0, 2))
    runCurrent()
    assertEquals(20.0, totalPrices.last())
    assertEquals(1, itemCounts.last())

    // Add another item
    viewModel.addItem(CartItem("2", "Item 2", 5.0, 3))
    runCurrent()
    assertEquals(35.0, totalPrices.last())
    assertEquals(2, itemCounts.last())

    // Remove item
    viewModel.removeItem("1")
    runCurrent()
    assertEquals(15.0, totalPrices.last())
    assertEquals(1, itemCounts.last())

    totalJob.cancel()
    countJob.cancel()
}

@Test
fun `derived StateFlow with turbine`() = runTest {
    val viewModel = ShoppingCartViewModel()

    viewModel.totalPrice.test {
        assertEquals(0.0, awaitItem())

        viewModel.addItem(CartItem("1", "Item", 10.0, 3))
        assertEquals(30.0, awaitItem())

        viewModel.addItem(CartItem("2", "Item 2", 20.0, 1))
        assertEquals(50.0, awaitItem())

        viewModel.clear()
        assertEquals(0.0, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Edge Cases and Gotchas

```kotlin
// Edge case 1: Late collector misses emissions
@Test
fun `SharedFlow without replay - late collector misses emissions`() = runTest {
    val viewModel = EventsViewModel()

    // Emit before collecting
    viewModel.sendEvent(Event.UserLoggedIn)
    viewModel.sendEvent(Event.DataLoaded(10))

    advanceUntilIdle()

    // Now collect - won't receive previous emissions
    val collected = mutableListOf<Event>()
    val job = launch(UnconfinedTestDispatcher(testScheduler)) {
        viewModel.events.collect { collected.add(it) }
    }

    runCurrent()
    assertTrue(collected.isEmpty())

    // Only new emissions received
    viewModel.sendEvent(Event.Error("Test"))
    runCurrent()

    assertEquals(1, collected.size)

    job.cancel()
}

// Edge case 2: StateFlow always has current value
@Test
fun `StateFlow current value accessible without collection`() {
    val viewModel = CounterViewModel()

    viewModel.increment()
    viewModel.increment()

    // Can access current value directly
    assertEquals(2, viewModel.counter.value)

    // No need for runTest or collection
}

// Edge case 3: SharedFlow cannot access current value
@Test
fun `SharedFlow has no current value property`() {
    val viewModel = EventsViewModel()

    // Cannot do: viewModel.events.value
    // SharedFlow doesn't have a value property
}

// Edge case 4: StateFlow subscription timing
@Test
fun `StateFlow emissions during collection setup`() = runTest {
    val viewModel = RapidUpdatesViewModel()

    val emissions = mutableListOf<Int>()

    viewModel.updateRapidly() // Start emitting

    val job = launch(UnconfinedTestDispatcher(testScheduler)) {
        viewModel.value.collect { emissions.add(it) }
    }

    advanceUntilIdle()

    // Got final value, possibly some intermediate values
    assertEquals(99, emissions.last())

    job.cancel()
}

// Edge case 5: Multiple collectors performance
@Test
fun `multiple collectors don't duplicate work`() = runTest {
    var executionCount = 0

    val sharedFlow = flow {
        executionCount++
        emit(1)
        emit(2)
        emit(3)
    }.shareIn(
        scope = this,
        started = SharingStarted.Eagerly,
        replay = 1
    )

    val collector1 = mutableListOf<Int>()
    val collector2 = mutableListOf<Int>()

    val job1 = launch { sharedFlow.take(3).toList(collector1) }
    val job2 = launch { sharedFlow.take(3).toList(collector2) }

    advanceUntilIdle()

    // Both collectors got same data
    assertEquals(collector1, collector2)

    // But upstream only executed once
    assertEquals(1, executionCount)

    job1.cancel()
    job2.cancel()
}
```

### Best Practices

```kotlin
// ✅ DO: Use turbine for cleaner tests
@Test
fun goodTest() = runTest {
    viewModel.state.test {
        assertEquals(expected, awaitItem())
    }
}

// ❌ DON'T: Manually manage collection jobs
@Test
fun badTest() = runTest {
    val items = mutableListOf<State>()
    val job = launch { viewModel.state.collect { items.add(it) } }
    // ... assertions ...
    job.cancel() // Easy to forget!
}

// ✅ DO: Test StateFlow current value directly
@Test
fun goodTest() {
    viewModel.action()
    assertEquals(expected, viewModel.state.value)
}

// ❌ DON'T: Collect StateFlow just to read current value
@Test
fun badTest() = runTest {
    viewModel.state.test {
        viewModel.action()
        assertEquals(expected, awaitItem())
    }
}

// ✅ DO: Use UnconfinedTestDispatcher for simple tests
@get:Rule
val mainDispatcherRule = MainDispatcherRule(UnconfinedTestDispatcher())

// ❌ DON'T: Use StandardTestDispatcher for simple state tests
// (It's fine, just unnecessary complexity)

// ✅ DO: Cancel collection jobs
@Test
fun goodTest() = runTest {
    flow.test {
        // ...
        cancelAndIgnoreRemainingEvents()
    }
}

// ✅ DO: Use fake repositories
class FakeRepository : Repository {
    var result: Result<Data>? = null
    override suspend fun getData() = result!!.getOrThrow()
}

// ❌ DON'T: Use Mockito for suspend functions
// (Can work, but fakes are cleaner)
```

### Summary

**StateFlow**:
- Always has current value (`.value` property)
- Conflates rapid emissions
- Replays current value to new collectors
- Built-in `distinctUntilChanged`
- Best for representing state
- Test current value directly or collect emissions

**SharedFlow**:
- No current value property
- Doesn't conflate by default
- Configurable replay cache
- Configurable buffer overflow strategy
- Best for events
- Must collect to receive emissions

**Turbine**:
- `test {}` - cleaner Flow testing
- `awaitItem()` - wait for and assert emission
- `awaitError()` - expect error
- `awaitComplete()` - expect completion
- `expectNoEvents()` - assert no emissions
- `cancelAndIgnoreRemainingEvents()` - clean cancellation

**Testing strategies**:
- Use `runTest` for coroutine control
- Use `MainDispatcherRule` for ViewModels
- Use turbine for cleaner assertions
- Use fake repositories
- Test state sequences for complex flows
- Test current value for simple state checks

---

## Ответ (RU)

Тестирование StateFlow и SharedFlow требует понимания их уникальных характеристик: StateFlow поддерживает текущее состояние и объединяет значения, в то время как SharedFlow может воспроизводить эмиссии и не имеет объединения по умолчанию.

### Основы StateFlow

StateFlow - это горячий Flow, который всегда имеет значение и эмитит самое последнее значение новым коллекторам.

```kotlin
class CounterViewModel : ViewModel() {
    private val _counter = MutableStateFlow(0)
    val counter: StateFlow<Int> = _counter.asStateFlow()

    fun increment() {
        _counter.value++
    }
}

@Test
fun `начальное состояние равно 0`() {
    assertEquals(0, viewModel.counter.value)
}
```

### Использование библиотеки Turbine

Turbine делает тестирование Flow намного чище и читабельнее.

```kotlin
@Test
fun `поиск обновляет результаты - с turbine`() = runTest {
    viewModel.searchResults.test {
        assertEquals(emptyList(), awaitItem())

        viewModel.search("query")

        val results = awaitItem()
        assertEquals(2, results.size)

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Лучшие практики

1. **Используйте turbine** для более чистых тестов
2. **Тестируйте текущее значение StateFlow** напрямую
3. **Используйте fake репозитории**, не моки
4. **Отменяйте collection jobs** с помощью `cancelAndIgnoreRemainingEvents()`
5. **Используйте UnconfinedTestDispatcher** для простых тестов
6. **Тестируйте последовательности состояний** для сложных потоков

---

## Follow-ups

1. How does SharingStarted.WhileSubscribed affect testing?
2. What are the performance implications of SharedFlow replay cache?
3. How to test Flow operators with StateFlow/SharedFlow?
4. When to use StateFlow vs LiveData in ViewModels?
5. How to test StateFlow/SharedFlow with multiple collectors?

---

## References

- [StateFlow and SharedFlow - Kotlin Docs](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/)
- [Turbine - Testing Library](https://github.com/cashapp/turbine)
- [Testing Flows - Android Developers](https://developer.android.com/kotlin/flow/test)

---

## Related Questions

- [[q-testing-coroutines-runtest--kotlin--medium]] - runTest basics
- [[q-testing-flow-operators--kotlin--hard]] - Testing Flow operators
- [[q-stateflow-sharedflow-differences--kotlin--medium]] - StateFlow vs SharedFlow
- [[q-statein-sharein-flow--kotlin--medium]] - stateIn and shareIn operators
