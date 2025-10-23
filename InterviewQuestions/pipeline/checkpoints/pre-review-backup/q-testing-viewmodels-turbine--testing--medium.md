---
id: 20251012-122711119
title: "Testing Viewmodels Turbine / Тестирование Viewmodels Turbine"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-graphql-vs-rest--networking--easy, q-bundle-data-types--android--medium, q-how-does-jetpackcompose-work--android--medium]
created: 2025-10-15
tags: [viewmodel, flow, turbine, state-management, coroutines, difficulty/medium]
---

# Testing ViewModels with Turbine

# Question (EN)

> How do you test StateFlow and SharedFlow emissions in ViewModels using Turbine? Handle multiple emissions and timeouts.

# Вопрос (RU)

> Как тестировать эмиссии StateFlow и SharedFlow в ViewModels используя Turbine? Обработка множественных эмиссий и таймаутов.

---

## Answer (EN)

**Turbine** is a testing library that simplifies Flow testing with a clean API for asserting emissions, handling timeouts, and managing multiple flows.

---

### Basic ViewModel Testing

**ViewModel example:**

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Initial)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    fun loadUser(id: Int) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            try {
                val user = repository.getUser(id)
                _uiState.value = UiState.Success(user)
                _events.emit(Event.UserLoaded)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
                _events.emit(Event.LoadFailed)
            }
        }
    }
}

sealed class UiState {
    object Initial : UiState()
    object Loading : UiState()
    data class Success(val user: User) : UiState()
    data class Error(val message: String) : UiState()
}

sealed class Event {
    object UserLoaded : Event()
    object LoadFailed : Event()
}
```

---

### Testing with Turbine

```gradle
dependencies {
    testImplementation("app.cash.turbine:turbine:1.0.0")
}
```

**Test setup:**

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var repository: UserRepository
    private lateinit var viewModel: UserViewModel

    @Before
    fun setUp() {
        repository = mockk()
        viewModel = UserViewModel(repository)
    }

    @Test
    fun `loadUser success emits loading then success`() = runTest {
        val user = User(1, "John")
        coEvery { repository.getUser(1) } returns user

        viewModel.uiState.test {
            // Initial state
            assertEquals(UiState.Initial, awaitItem())

            viewModel.loadUser(1)

            // Loading state
            assertEquals(UiState.Loading, awaitItem())

            // Success state
            val successState = awaitItem() as UiState.Success
            assertEquals("John", successState.user.name)

            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `loadUser error emits loading then error`() = runTest {
        coEvery { repository.getUser(1) } throws IOException("Network error")

        viewModel.uiState.test {
            assertEquals(UiState.Initial, awaitItem())

            viewModel.loadUser(1)

            assertEquals(UiState.Loading, awaitItem())

            val errorState = awaitItem() as UiState.Error
            assertEquals("Network error", errorState.message)

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

---

### Testing Events (SharedFlow)

```kotlin
@Test
fun `loadUser success emits UserLoaded event`() = runTest {
    val user = User(1, "John")
    coEvery { repository.getUser(1) } returns user

    viewModel.events.test {
        viewModel.loadUser(1)

        // Wait for event
        assertEquals(Event.UserLoaded, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}

@Test
fun `loadUser error emits LoadFailed event`() = runTest {
    coEvery { repository.getUser(1) } throws IOException("Network error")

    viewModel.events.test {
        viewModel.loadUser(1)

        assertEquals(Event.LoadFailed, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

---

### Testing Multiple Emissions

```kotlin
class SearchViewModel : ViewModel() {
    private val _searchResults = MutableStateFlow<List<Item>>(emptyList())
    val searchResults: StateFlow<List<Item>> = _searchResults

    fun search(query: String) {
        viewModelScope.launch {
            delay(300) // Debounce
            _searchResults.value = performSearch(query)
        }
    }
}

@Test
fun `search emits multiple results`() = runTest {
    val viewModel = SearchViewModel()

    viewModel.searchResults.test {
        // Initial empty list
        assertEquals(emptyList(), awaitItem())

        // First search
        viewModel.search("a")
        assertEquals(listOf(Item("Apple")), awaitItem())

        // Second search
        viewModel.search("ab")
        assertEquals(listOf(Item("Abacus")), awaitItem())

        // Third search
        viewModel.search("abc")
        assertEquals(emptyList(), awaitItem()) // No results

        cancelAndIgnoreRemainingEvents()
    }
}
```

---

### Handling Timeouts

```kotlin
@Test
fun `test with timeout`() = runTest {
    viewModel.events.test(timeout = 5.seconds) {
        viewModel.loadUser(1)

        // Wait up to 5 seconds for event
        val event = awaitItem()
        assertEquals(Event.UserLoaded, event)

        cancelAndIgnoreRemainingEvents()
    }
}

@Test
fun `expectNoEvents verifies silence`() = runTest {
    viewModel.events.test {
        // Should not emit anything yet
        expectNoEvents()

        viewModel.loadUser(1)

        awaitItem() // Now we expect an event

        cancelAndIgnoreRemainingEvents()
    }
}
```

---

### Skip and Ignore Items

```kotlin
@Test
fun `skipItems skips emissions`() = runTest {
    viewModel.uiState.test {
        awaitItem() // Initial

        viewModel.loadUser(1)

        skipItems(1) // Skip Loading state

        // Jump to Success
        val state = awaitItem() as UiState.Success
        assertEquals("John", state.user.name)

        cancelAndIgnoreRemainingEvents()
    }
}

@Test
fun `expectMostRecentItem gets latest`() = runTest {
    viewModel.uiState.test {
        awaitItem() // Initial

        // Trigger multiple quick updates
        repeat(5) { viewModel.refresh() }

        // Get most recent, ignore intermediate
        val latestState = expectMostRecentItem()

        cancelAndIgnoreRemainingEvents()
    }
}
```

---

### Testing Multiple Flows Simultaneously

```kotlin
@Test
fun `test state and events together`() = runTest {
    val user = User(1, "John")
    coEvery { repository.getUser(1) } returns user

    // Launch both collectors
    launch {
        viewModel.uiState.test {
            assertEquals(UiState.Initial, awaitItem())
            assertEquals(UiState.Loading, awaitItem())

            val successState = awaitItem() as UiState.Success
            assertEquals("John", successState.user.name)

            cancelAndIgnoreRemainingEvents()
        }
    }

    launch {
        viewModel.events.test {
            val event = awaitItem()
            assertEquals(Event.UserLoaded, event)

            cancelAndIgnoreRemainingEvents()
        }
    }

    // Trigger action
    viewModel.loadUser(1)
}
```

---

### Complex ViewModel Example

```kotlin
class CartViewModel : ViewModel() {
    private val _items = MutableStateFlow<List<CartItem>>(emptyList())
    val items: StateFlow<List<CartItem>> = _items

    private val _total = MutableStateFlow(0.0)
    val total: StateFlow<Double> = _total

    private val _checkoutState = MutableStateFlow<CheckoutState>(CheckoutState.Idle)
    val checkoutState: StateFlow<CheckoutState> = _checkoutState

    private val _messages = MutableSharedFlow<Message>()
    val messages: SharedFlow<Message> = _messages

    fun addItem(item: CartItem) {
        viewModelScope.launch {
            val currentItems = _items.value.toMutableList()
            currentItems.add(item)
            _items.value = currentItems

            updateTotal()
            _messages.emit(Message.ItemAdded(item.name))
        }
    }

    fun removeItem(itemId: String) {
        viewModelScope.launch {
            _items.value = _items.value.filter { it.id != itemId }

            updateTotal()
            _messages.emit(Message.ItemRemoved)
        }
    }

    fun checkout() {
        viewModelScope.launch {
            _checkoutState.value = CheckoutState.Processing

            delay(1000) // Simulate payment

            if (_total.value > 0) {
                _checkoutState.value = CheckoutState.Success
                _messages.emit(Message.CheckoutSuccess)
                _items.value = emptyList()
                _total.value = 0.0
            } else {
                _checkoutState.value = CheckoutState.Error("Cart is empty")
            }
        }
    }

    private fun updateTotal() {
        _total.value = _items.value.sumOf { it.price * it.quantity }
    }
}

data class CartItem(
    val id: String,
    val name: String,
    val price: Double,
    val quantity: Int
)

sealed class CheckoutState {
    object Idle : CheckoutState()
    object Processing : CheckoutState()
    object Success : CheckoutState()
    data class Error(val message: String) : CheckoutState()
}

sealed class Message {
    data class ItemAdded(val name: String) : Message()
    object ItemRemoved : Message()
    object CheckoutSuccess : Message()
}
```

**Complete test:**

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class CartViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var viewModel: CartViewModel

    @Before
    fun setUp() {
        viewModel = CartViewModel()
    }

    @Test
    fun `addItem updates items, total, and emits message`() = runTest {
        val item = CartItem("1", "Apple", 1.99, 2)

        // Test all flows together
        launch {
            viewModel.items.test {
                assertEquals(emptyList(), awaitItem())

                val items = awaitItem()
                assertEquals(1, items.size)
                assertEquals("Apple", items[0].name)

                cancelAndIgnoreRemainingEvents()
            }
        }

        launch {
            viewModel.total.test {
                assertEquals(0.0, awaitItem())
                assertEquals(3.98, awaitItem(), 0.01)

                cancelAndIgnoreRemainingEvents()
            }
        }

        launch {
            viewModel.messages.test {
                val message = awaitItem() as Message.ItemAdded
                assertEquals("Apple", message.name)

                cancelAndIgnoreRemainingEvents()
            }
        }

        // Trigger action
        viewModel.addItem(item)
    }

    @Test
    fun `checkout success flow`() = runTest {
        // Add item first
        viewModel.addItem(CartItem("1", "Apple", 1.99, 1))
        advanceUntilIdle()

        // Test checkout state
        viewModel.checkoutState.test {
            assertEquals(CheckoutState.Idle, awaitItem())

            viewModel.messages.test {
                viewModel.checkout()

                // Wait for processing
                assertEquals(CheckoutState.Processing, awaitItem())

                // Wait for success
                assertEquals(CheckoutState.Success, awaitItem())

                // Verify message
                assertEquals(Message.CheckoutSuccess, awaitItem())

                cancelAndIgnoreRemainingEvents()
            }

            cancelAndIgnoreRemainingEvents()
        }

        // Verify items cleared
        assertEquals(emptyList(), viewModel.items.value)
        assertEquals(0.0, viewModel.total.value)
    }

    @Test
    fun `checkout with empty cart fails`() = runTest {
        viewModel.checkoutState.test {
            assertEquals(CheckoutState.Idle, awaitItem())

            viewModel.checkout()

            assertEquals(CheckoutState.Processing, awaitItem())

            val errorState = awaitItem() as CheckoutState.Error
            assertEquals("Cart is empty", errorState.message)

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

---

### Best Practices

**1. Always await initial emission for StateFlow:**

```kotlin
//  DO
viewModel.uiState.test {
    assertEquals(UiState.Initial, awaitItem()) // Initial value
    // ... test logic
}

//  DON'T (will fail)
viewModel.uiState.test {
    viewModel.load()
    assertEquals(UiState.Loading, awaitItem()) // Misses initial!
}
```

**2. Use cancelAndIgnoreRemainingEvents:**

```kotlin
//  DO
test {
    assertEquals(expected, awaitItem())
    cancelAndIgnoreRemainingEvents()
}

//  DON'T (test may hang)
test {
    assertEquals(expected, awaitItem())
    // Missing cancel - test waits forever
}
```

**3. Test state and events separately or together:**

```kotlin
//  GOOD: Separate tests
@Test fun testState()
@Test fun testEvents()

//  ALSO GOOD: Together when related
@Test fun testStateAndEvents()
```

---

## Ответ (RU)

**Turbine** — это библиотека тестирования, которая упрощает тестирование Flow с чистым API для утверждений эмиссий, обработки таймаутов и управления множественными потоками.

### Базовое тестирование ViewModel

Используйте `test {}` блок для тестирования StateFlow и SharedFlow эмиссий.

### Тестирование событий (SharedFlow)

SharedFlow не имеет начального значения, поэтому начинайте слушать до эмиссии события.

### Тестирование множественных эмиссий

Используйте `awaitItem()` для каждой эмиссии последовательно.

### Обработка таймаутов

Используйте `test(timeout = duration)` и `expectNoEvents()` для контроля таймингов.

### Пропуск элементов

`skipItems(n)` пропускает n эмиссий, `expectMostRecentItem()` получает последнюю.

### Тестирование множества потоков одновременно

Запускайте несколько `launch { flow.test { } }` блоков для параллельного тестирования.

### Лучшие практики

1. Всегда ожидайте начальную эмиссию для StateFlow
2. Используйте `cancelAndIgnoreRemainingEvents()`
3. Тестируйте состояние и события отдельно или вместе

Turbine делает тестирование Flow простым и выразительным.

---

## Follow-ups

-   How do you test ViewModels that emit both StateFlow and SharedFlow simultaneously?
-   What are the best practices for handling timeout scenarios in Flow testing?
-   How can you mock dependencies in ViewModel tests while using Turbine?

## References

-   `https://github.com/cashapp/turbine` — Turbine library
-   `https://developer.android.com/topic/libraries/architecture/viewmodel` — ViewModel testing
-   `https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-test/` — Coroutines testing

## Related Questions

### Hub

-   [[q-clean-architecture-android--android--hard]] - Clean Architecture principles

### Related (Medium)

-   [[q-mvvm-pattern--android--medium]] - MVVM pattern explained
-   [[q-mvvm-vs-mvp-differences--android--medium]] - MVVM vs MVP comparison
-   [[q-what-is-viewmodel--android--medium]] - What is ViewModel
-   [[q-why-is-viewmodel-needed-and-what-happens-in-it--android--medium]] - ViewModel purpose & internals
-   [[q-until-what-point-does-viewmodel-guarantee-state-preservation--android--medium]] - ViewModel state preservation

### Advanced (Harder)

-   [[q-mvi-architecture--android--hard]] - MVI architecture pattern
-   [[q-mvi-handle-one-time-events--android--hard]] - MVI one-time event handling
-   [[q-offline-first-architecture--android--hard]] - Offline-first architecture
