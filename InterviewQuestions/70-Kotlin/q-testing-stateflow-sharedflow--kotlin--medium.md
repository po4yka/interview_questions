---
---
---id: kotlin-062
title: "Testing StateFlow and SharedFlow in ViewModels / Тестирование StateFlow и SharedFlow в ViewModels"
aliases: ["Testing StateFlow and SharedFlow in ViewModels", "Тестирование StateFlow и SharedFlow в ViewModels"]
topic: kotlin
subtopics: [coroutines, sharedflow, stateflow]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Flow Testing Guide
status: draft
moc: moc-kotlin
related: [c-flow, c-kotlin, c-stateflow, q-stateflow-sharedflow-differences--kotlin--medium, q-testing-coroutines-runtest--kotlin--medium]
created: 2025-10-12
updated: 2025-11-09
tags: [coroutines, difficulty/medium, kotlin, sharedflow, stateflow, testing, viewmodel]

---
# Вопрос (RU)
> Как тестировать `StateFlow` и `SharedFlow` в `ViewModel`? Покрыть стратегии коллекции, библиотеку Turbine, `TestScope`, утверждения и граничные случаи вроде replay cache и семантики "latest value wins".

---

# Question (EN)
> How to test `StateFlow` and `SharedFlow` in `ViewModel`s? Cover collection strategies, Turbine library, `TestScope`, assertions, and edge cases like replay cache and "latest value wins" semantics.

## Ответ (RU)

Тестирование `StateFlow` и `SharedFlow` требует понимания их характеристик:
- `StateFlow` всегда хранит текущее состояние, эмитит последнее значение новым коллекторам и имеет встроенную семантику `distinctUntilChanged` (эмитит только при реальном изменении).
- `SharedFlow` — более общий горячий поток: может сохранять replay cache и буфер, по умолчанию не имеет текущего значения и не делает `distinctUntilChanged`.

Ключевые моменты для тестов во `ViewModel`:
- Использовать `runTest` и правило `MainDispatcherRule`, чтобы переназначить `Dispatchers.Main` и корректно управлять `viewModelScope`.
- Для `StateFlow` часто достаточно проверять `.value` без коллекции.
- Для последовательностей значений и `SharedFlow` удобно использовать Turbine.

### Основы `StateFlow`

`StateFlow` — горячий `Flow`, который всегда имеет значение и при подписке сначала отдаёт текущее значение, затем новые.

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
    fun `начальное состояние равно 0`() {
        assertEquals(0, viewModel.counter.value)
    }

    @Test
    fun `increment увеличивает значение`() {
        viewModel.increment()
        assertEquals(1, viewModel.counter.value)

        viewModel.increment()
        assertEquals(2, viewModel.counter.value)
    }

    @Test
    fun `decrement уменьшает значение`() {
        viewModel.increment()
        viewModel.increment()
        viewModel.decrement()

        assertEquals(1, viewModel.counter.value)
    }

    @Test
    fun `reset сбрасывает значение в 0`() {
        viewModel.increment()
        viewModel.increment()
        viewModel.reset()

        assertEquals(0, viewModel.counter.value)
    }
}
```

### Тестирование `StateFlow` С Асинхронными Операциями

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
    fun `loadUser успех эмитит Idle, Loading, Success`() = runTest {
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
    fun `loadUser ошибка эмитит Idle, Loading, Error`() = runTest {
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
}
```

(Примечание: `User`, `UserRepository`, `FakeUserRepository`, `MainDispatcherRule` предполагаются определёнными в тестовом окружении.)

### Тестирование `StateFlow` — "latest Value wins"

`StateFlow` хранит только последнее значение; после серии быстрых обновлений важно проверить, что итоговое состояние соответствует последнему присвоенному значению.

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

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `StateFlow после быстрых обновлений содержит финальное значение`() = runTest {
    val viewModel = RapidUpdatesViewModel()

    viewModel.updateRapidly()
    advanceUntilIdle()

    assertEquals(99, viewModel.value.value)
}
```

### Тестирование `SharedFlow` — Базовые Случаи

`SharedFlow` — горячий `Flow`, который можно сконфигурировать через replay и буфер. По умолчанию:
- нет начального значения;
- нет свойства `.value`;
- поздние подписчики не получают прошлые эмиссии.

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
    fun `events доставляются активным коллекторам`() = runTest {
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
    fun `SharedFlow без replay не имеет начального значения`() = runTest {
        val collectedEvents = mutableListOf<Event>()
        val job = launch(UnconfinedTestDispatcher(testScheduler)) {
            viewModel.events.take(2).collect { collectedEvents.add(it) }
        }

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

### Тестирование `SharedFlow` С Replay Cache

```kotlin
class NotificationsViewModel : ViewModel() {
    // replay = 3: последние 3 эмиссии будут переотправлены новым коллекторам
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

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `SharedFlow реплейит последние N эмиссий новым коллекторам`() = runTest {
    val viewModel = NotificationsViewModel()

    viewModel.notify(Notification(1, "Message 1"))
    viewModel.notify(Notification(2, "Message 2"))
    viewModel.notify(Notification(3, "Message 3"))
    viewModel.notify(Notification(4, "Message 4"))
    viewModel.notify(Notification(5, "Message 5"))

    advanceUntilIdle()

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
```

### Использование Библиотеки Turbine

```gradle
testImplementation("app.cash.turbine:turbine:1.0.0")
```

```kotlin
import app.cash.turbine.test
```

Пример использования Turbine для `StateFlow` и `SharedFlow` во `ViewModel`-тестах повторяет приведённые выше шаблоны: внутри `test {}` используйте `awaitItem()`, `expectNoEvents()`, `awaitComplete()`, `cancelAndIgnoreRemainingEvents()` для детерминированных проверок.

### Тестирование `StateFlow` distinctUntilChanged

`StateFlow` эмитит только при фактическом изменении значения.

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

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `StateFlow пропускает дубликаты значений`() = runTest {
    val viewModel = ToggleViewModel()

    viewModel.isEnabled.test {
        assertEquals(false, awaitItem())

        viewModel.setEnabled(false)
        expectNoEvents()

        viewModel.setEnabled(true)
        assertEquals(true, awaitItem())

        viewModel.setEnabled(true)
        expectNoEvents()

        viewModel.setEnabled(false)
        assertEquals(false, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Тестирование `SharedFlow` Buffer Overflow

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

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `SharedFlow с DROP_OLDEST без коллектора не реплейит прошлые значения`() = runTest {
    val viewModel = BufferedEventsViewModel()

    viewModel.emitMany(10)

    viewModel.events.test {
        expectNoEvents()
        cancelAndIgnoreRemainingEvents()
    }
}

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `SharedFlow с DROP_OLDEST при активной коллекции отдаёт последние значения`() = runTest {
    val viewModel = BufferedEventsViewModel()

    viewModel.events.test {
        launch { viewModel.emitMany(10) }

        val received = mutableListOf<Int>()
        repeat(3) { received += awaitItem() }

        assertTrue(received.all { it in 7..9 })

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Edge Cases И Подводные Камни

```kotlin
// SharedFlow без replay — поздний коллектор не получает прошлые эмиссии
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `SharedFlow без replay — поздний коллектор пропускает прошлые события`() = runTest {
    val viewModel = EventsViewModel()

    viewModel.sendEvent(Event.UserLoggedIn)
    viewModel.sendEvent(Event.DataLoaded(10))
    advanceUntilIdle()

    val collected = mutableListOf<Event>()
    val job = launch(UnconfinedTestDispatcher(testScheduler)) {
        viewModel.events.collect { collected.add(it) }
    }

    runCurrent()
    assertTrue(collected.isEmpty())

    viewModel.sendEvent(Event.Error("Test"))
    runCurrent()

    assertEquals(1, collected.size)

    job.cancel()
}

// Доступ к текущему значению StateFlow без коллекции
@Test
fun `StateFlow текущее значение доступно без коллекции`() {
    val viewModel = CounterViewModel()

    viewModel.increment()
    viewModel.increment()

    assertEquals(2, viewModel.counter.value)
}

// SharedFlow не имеет свойства value
@Test
fun `SharedFlow не имеет свойства value`() {
    val viewModel = EventsViewModel()
    // viewModel.events.value // ошибка компиляции: нет свойства value
}
```

### Итог (RU)

`StateFlow`:
- Всегда имеет текущее значение (`.value`).
- Немедленно отдаёт его новым коллекторам.
- Эмитит только при реальном изменении.
- Удобен для состояния UI; часто достаточно проверять `.value`.

`SharedFlow`:
- Не имеет `.value` по умолчанию.
- Поведение поздних подписчиков определяется `replay` и буфером.
- Подходит для одноразовых событий (навигация, сообщения).

Turbine:
- Даёт `test {}` DSL для детерминированных проверок.
- Методы `awaitItem()`, `awaitError()`, `awaitComplete()`, `expectNoEvents()`, `cancelAndIgnoreRemainingEvents()` помогают точно описать ожидания.

Стратегии тестирования:
- Используйте `runTest` и `MainDispatcherRule` для контроля корутин и `viewModelScope`.
- Используйте фейковые репозитории вместо тяжёлых моков.
- Для `StateFlow` проверяйте `.value`, когда важен только финальный стейт.
- Для последовательностей и `SharedFlow` используйте Turbine.

---

## Answer (EN)

Testing `StateFlow` and `SharedFlow` requires understanding their characteristics:
- `StateFlow` always holds a current value, emits the latest value to new collectors, and has built-in `distinctUntilChanged` behavior.
- `SharedFlow` is a more general hot flow: it can be configured with replay/buffer, has no current value by default, and does not do `distinctUntilChanged` on its own.

Key points for `ViewModel` tests:
- Use `runTest` and a `MainDispatcherRule` to replace `Dispatchers.Main` so `viewModelScope` is fully controlled.
- For `StateFlow`, often you can assert `.value` directly instead of collecting.
- For emission sequences and `SharedFlow`, Turbine gives clearer, deterministic tests.

### `StateFlow` Basics

`StateFlow` is a hot `Flow` that always has a value and, upon collection, first emits the current value, then subsequent updates.

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

### Testing `StateFlow` with Async Operations

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
    fun `loadUser success emits Idle, Loading, Success`() = runTest {
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
    fun `loadUser failure emits Idle, Loading, Error`() = runTest {
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
}
```

(Helper types `User`, `UserRepository`, `FakeUserRepository`, `MainDispatcherRule` are assumed to be defined in the test environment.)

### Testing `StateFlow` "Latest Value Wins"

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

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `StateFlow exposes final value after rapid updates`() = runTest {
    val viewModel = RapidUpdatesViewModel()

    viewModel.updateRapidly()
    advanceUntilIdle()

    assertEquals(99, viewModel.value.value)
}
```

### Testing `SharedFlow` Basics

`SharedFlow` is a hot `Flow` that can be configured with replay and buffering; by default it has no initial value, no `.value` property, and late collectors do not receive past emissions.

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

### Testing `SharedFlow` with Replay Cache

```kotlin
class NotificationsViewModel : ViewModel() {
    // replay = 3: last 3 emissions are replayed to new collectors
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

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `SharedFlow replays last N emissions to new collectors`() = runTest {
    val viewModel = NotificationsViewModel()

    viewModel.notify(Notification(1, "Message 1"))
    viewModel.notify(Notification(2, "Message 2"))
    viewModel.notify(Notification(3, "Message 3"))
    viewModel.notify(Notification(4, "Message 4"))
    viewModel.notify(Notification(5, "Message 5"))

    advanceUntilIdle()

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
```

### Using Turbine Library

```gradle
testImplementation("app.cash.turbine:turbine:1.0.0")
```

```kotlin
import app.cash.turbine.test
```

Use Turbine's `test {}` DSL for deterministic `Flow` assertions with `awaitItem()`, `awaitError()`, `awaitComplete()`, `expectNoEvents()`, and `cancelAndIgnoreRemainingEvents()` as illustrated in the examples.

### Testing `StateFlow` distinctUntilChanged

`StateFlow` only emits when the value actually changes.

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

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `StateFlow skips duplicate values`() = runTest {
    val viewModel = ToggleViewModel()

    viewModel.isEnabled.test {
        assertEquals(false, awaitItem())

        viewModel.setEnabled(false)
        expectNoEvents() // no new emission for same value

        viewModel.setEnabled(true)
        assertEquals(true, awaitItem())

        viewModel.setEnabled(true)
        expectNoEvents()

        viewModel.setEnabled(false)
        assertEquals(false, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Testing `SharedFlow` Buffer Overflow

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

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `SharedFlow with DROP_OLDEST keeps no history for late collectors`() = runTest {
    val viewModel = BufferedEventsViewModel()

    viewModel.emitMany(10)

    viewModel.events.test {
        expectNoEvents()
        cancelAndIgnoreRemainingEvents()
    }
}

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `SharedFlow with DROP_OLDEST delivers latest values to active collectors`() = runTest {
    val viewModel = BufferedEventsViewModel()

    viewModel.events.test {
        launch { viewModel.emitMany(10) }

        val received = mutableListOf<Int>()
        repeat(3) { received += awaitItem() }

        assertTrue(received.all { it in 7..9 })

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Edge Cases and Gotchas

```kotlin
// SharedFlow without replay - late collector misses previous emissions
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `SharedFlow without replay - late collector misses emissions`() = runTest {
    val viewModel = EventsViewModel()

    viewModel.sendEvent(Event.UserLoggedIn)
    viewModel.sendEvent(Event.DataLoaded(10))
    advanceUntilIdle()

    val collected = mutableListOf<Event>()
    val job = launch(UnconfinedTestDispatcher(testScheduler)) {
        viewModel.events.collect { collected.add(it) }
    }

    runCurrent()
    assertTrue(collected.isEmpty())

    viewModel.sendEvent(Event.Error("Test"))
    runCurrent()

    assertEquals(1, collected.size)

    job.cancel()
}

// StateFlow current value accessible without collection
@Test
fun `StateFlow current value accessible without collection`() {
    val viewModel = CounterViewModel()

    viewModel.increment()
    viewModel.increment()

    assertEquals(2, viewModel.counter.value)
}

// SharedFlow has no current value
@Test
fun `SharedFlow has no current value property`() {
    val viewModel = EventsViewModel()
    // viewModel.events.value // compilation error: no value property
}
```

### Summary

`StateFlow`:
- Always has a current value (`.value`).
- Emits current value immediately to new collectors.
- Only emits on real value changes (`distinctUntilChanged`).
- Great for representing UI state; often testable via direct `.value` assertions.

`SharedFlow`:
- No `.value` by default.
- Replay/buffer configurable; late collectors behavior depends on configuration.
- Suitable for one-off events, navigation, messages.

Turbine:
- `test {}` DSL for deterministic `Flow` assertions.
- `awaitItem()`, `awaitError()`, `awaitComplete()`, `expectNoEvents()`, `cancelAndIgnoreRemainingEvents()` for precise expectations.

Testing strategies:
- Use `runTest` and `MainDispatcherRule` to control coroutines and `viewModelScope`.
- Prefer fake repositories over heavy mocks.
- For `StateFlow`, assert `.value` when you only care about final state.
- Use Turbine for sequences, order-sensitive flows, and `SharedFlow`.

---

## Дополнительные Вопросы (RU)

1. Как поведение `SharingStarted.WhileSubscribed` влияет на запуск и остановку сборщиков при тестировании `StateFlow` и `SharedFlow` во `ViewModel`, и какие проверки нужны, чтобы убедиться, что побочные эффекты не выполняются без активных подписчиков?
2. Как большой replay cache у `SharedFlow` влияет на использование памяти и время выполнения в тестах и продакшене, и как это учитывать при написании проверок?
3. Как тестировать цепочки операторов `Flow` (`map`, `filter`, `debounce` и др.) поверх `StateFlow`/`SharedFlow`, чтобы убедиться в корректном порядке, количестве и задержках эмиссий?
4. В каких сценариях `StateFlow` предпочтительнее `LiveData` во `ViewModel` с точки зрения тестируемости и детерминированности, и как это отразить в тестах?
5. Как организовать и проверить работу нескольких коллекторах `StateFlow`/`SharedFlow` с разными жизненными циклами (например, несколько экранов или компонентов), чтобы избежать утечек и гонок?

---

## Follow-ups

1. How does `SharingStarted.WhileSubscribed` impact when `StateFlow`/`SharedFlow` starts and stops work in a `ViewModel`, and how can you verify that side effects do not run without active collectors?
2. What are the memory and runtime implications of configuring a large `SharedFlow` replay cache in tests and production, and how should tests assert this behavior safely?
3. How can you test `Flow` operator chains (`map`, `filter`, `debounce`, etc.) built on top of `StateFlow`/`SharedFlow` to validate ordering, counts, and timing of emissions?
4. In which scenarios is `StateFlow` preferable to `LiveData` in `ViewModel`s from a testability and determinism perspective, and how should this influence your test design?
5. How do you structure and verify tests for multiple `StateFlow`/`SharedFlow` collectors with different lifecycles (e.g., multiple screens/components) to avoid leaks and race conditions?

---

## Ссылки (RU)

- Документация `StateFlow` и `SharedFlow`: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/
- Библиотека Turbine: https://github.com/cashapp/turbine
- Тестирование `Flow` на Android: https://developer.android.com/kotlin/flow/test
- См. также: [[c-kotlin]], [[c-flow]]

---

## References

- `StateFlow` and `SharedFlow` - Kotlin Docs: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/
- Turbine - Testing Library: https://github.com/cashapp/turbine
- Testing `Flows` - Android Developers: https://developer.android.com/kotlin/flow/test
- See also: [[c-kotlin]], [[c-flow]]

---

## Связанные Вопросы (RU)

- [[q-stateflow-sharedflow-android--kotlin--medium]]
- [[q-stateflow-sharedflow-differences--kotlin--medium]]
- [[q-sharedflow-stateflow--kotlin--medium]]
- [[q-testing-viewmodel-coroutines--kotlin--medium]]
- [[q-testing-flow-operators--kotlin--hard]]
- [[q-flow-testing-advanced--kotlin--hard]]
- [[q-kotlin-flow-basics--kotlin--medium]]

---

## Related Questions

- [[q-stateflow-sharedflow-android--kotlin--medium]]
- [[q-stateflow-sharedflow-differences--kotlin--medium]]
- [[q-sharedflow-stateflow--kotlin--medium]]
- [[q-testing-viewmodel-coroutines--kotlin--medium]]
- [[q-testing-flow-operators--kotlin--hard]]
- [[q-flow-testing-advanced--kotlin--hard]]
- [[q-kotlin-flow-basics--kotlin--medium]]
