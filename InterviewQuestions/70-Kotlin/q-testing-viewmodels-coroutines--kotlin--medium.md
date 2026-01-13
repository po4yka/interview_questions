---
---
---id: kotlin-199
title: "Testing Viewmodels Coroutines / Тестирование Viewmodels Coroutines"
aliases: [Testing Coroutines, Unit Testing, ViewModel Testing, Тестирование ViewModel]
topic: kotlin
subtopics: [coroutines, testing]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, c-stateflow, q-flowon-operator-context-switching--kotlin--hard]
created: 2025-10-15
updated: 2025-11-09
tags: [android, coroutines, difficulty/medium, kotlin, testing, testing-unit, viewmodel]
---
# Вопрос (RU)

> Как правильно тестировать `ViewModel`, использующие корутины? Каковы типичные паттерны и подводные камни?

# Question (EN)

> How do you properly test `ViewModels` that use coroutines? What are the common patterns and pitfalls?

## Ответ (RU)

Тестирование **`ViewModel` с корутинами** требует специальной настройки: управления выполнением корутин, подмены `Dispatchers.Main`, контроля виртуального времени и корректного тестирования `Flow`, `StateFlow` и `SharedFlow`.

### Основная Проблема

```kotlin
// ViewModel
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()

    fun loadUser(id: Int) {
        viewModelScope.launch {
            val user = repository.getUser(id)
            _user.value = user
        }
    }
}

// - НЕПРАВИЛЬНЫЙ тест - не дожидается завершения корутины
@Test
fun `load user updates state`() {
    val viewModel = UserViewModel(fakeRepository)

    viewModel.loadUser(1)

    // ОШИБКА: корутина ещё не завершилась и использует Dispatchers.Main, который не контролируется
    assertEquals(expectedUser, viewModel.user.value)
}
```

**Проблема**: корутина запускается асинхронно во `viewModelScope` (на `Dispatchers.Main`), тест завершает выполнение или читает состояние до окончания работы и без управления диспетчером.

### Решение: runTest И MainDispatcherRule

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class MainDispatcherRule(
    private val testDispatcher: TestDispatcher = StandardTestDispatcher()
) : TestWatcher() {
    override fun starting(description: Description) {
        Dispatchers.setMain(testDispatcher)
    }

    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}

// - ПРАВИЛЬНЫЙ тест
@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `load user updates state`() = runTest {
        // Given
        val fakeRepository = FakeUserRepository().apply {
            setResult(Result.success(expectedUser))
        }
        val viewModel = UserViewModel(fakeRepository)

        // When
        viewModel.loadUser(1)

        // Then - продвигаем виртуальное время, чтобы корутины viewModelScope завершились
        advanceUntilIdle()
        assertEquals(expectedUser, viewModel.user.value)
    }
}
```

**runTest**:
- Автоматически предоставляет `TestScope` и `TestCoroutineScheduler`.
- Может автоматически ожидать дочерние корутины тестового скоупа.
- Перескакивает `delay()` через виртуальное время.
- Корректно работает совместно с `TestDispatcher` при подмене `Dispatchers.Main`.

### MainDispatcherRule Для viewModelScope

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class MainDispatcherRule(
    val dispatcher: TestDispatcher = StandardTestDispatcher()
) : TestWatcher() {
    override fun starting(description: Description) {
        Dispatchers.setMain(dispatcher)
    }

    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}

// Использование в тестах: выбирайте ОДИН подход — либо правило, либо явный setMain/resetMain.
@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `load user updates state`() = runTest {
        val fakeRepository = FakeUserRepository().apply {
            setResult(Result.success(expectedUser))
        }
        val viewModel = UserViewModel(fakeRepository)

        viewModel.loadUser(1)
        // Теперь viewModelScope использует TestDispatcher через Dispatchers.Main

        advanceUntilIdle()
        assertEquals(expectedUser, viewModel.user.value)
    }
}
```

**MainDispatcherRule**:
- Подменяет `Dispatchers.Main` на `TestDispatcher`.
- Обеспечивает выполнение `viewModelScope` на контролируемом диспетчере.
- Использует `TestWatcher` для автоматической установки/сброса в жизненном цикле JUnit.

### StandardTestDispatcher Vs UnconfinedTestDispatcher

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `test with StandardTestDispatcher`() = runTest {
    // Используем планировщик текущего TestScope
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)

    val viewModel = UserViewModel(fakeRepository)
    viewModel.loadUser(1)

    // Нужно явно продвинуть время / выполнить отложенные задачи
    advanceUntilIdle()

    assertEquals(expectedUser, viewModel.user.value)

    Dispatchers.resetMain()
}

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `test with UnconfinedTestDispatcher`() = runTest {
    val dispatcher = UnconfinedTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)

    val viewModel = UserViewModel(fakeRepository)
    viewModel.loadUser(1)

    // Для простых, немедленных операций часто не нужен advanceUntilIdle(),
    // но при структурированной конкуренции и дочерних корутинах он всё равно может понадобиться.
    advanceUntilIdle()
    assertEquals(expectedUser, viewModel.user.value)

    Dispatchers.resetMain()
}
```

**Различия**:
- `StandardTestDispatcher`: задачи ставятся в очередь; используйте `advanceUntilIdle()` / `advanceTimeBy()` / `runCurrent()`.
- `UnconfinedTestDispatcher`: начинает выполнение сразу в текущем стеке, но планирование остаётся; менее детерминирован для сложных случаев, поэтому для тестов `ViewModel` лучше предпочитать `StandardTestDispatcher`.

### Тестирование Flow

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    val users: StateFlow<List<User>> = repository.observeUsers()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )
}

// - Тест Flow
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `users flow emits repository data`() = runTest {
    val fakeRepository = FakeUserRepository()
    val viewModel = UserViewModel(fakeRepository)

    val emissions = mutableListOf<List<User>>()
    val job = launch {
        viewModel.users.take(2).toList(emissions)
    }

    fakeRepository.emit(listOf(user1, user2))

    advanceUntilIdle()
    job.cancel()

    assertEquals(emptyList<List<User>>(), listOf(emissions[0])) // initialValue
    assertEquals(listOf(user1, user2), emissions[1])
}

// Использование библиотеки Turbine
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `users flow emits repository data - with turbine`() = runTest {
    val fakeRepository = FakeUserRepository()
    val viewModel = UserViewModel(fakeRepository)

    viewModel.users.test {
        assertEquals(emptyList<User>(), awaitItem()) // initialValue

        fakeRepository.emit(listOf(user1, user2))
        assertEquals(listOf(user1, user2), awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Тестирование delay() И Виртуального Времени

```kotlin
class TimerViewModel : ViewModel() {
    private val _seconds = MutableStateFlow(0)
    val seconds: StateFlow<Int> = _seconds.asStateFlow()

    fun startTimer() {
        viewModelScope.launch {
            repeat(10) {
                delay(1000)
                _seconds.value += 1
            }
        }
    }
}

// - Тест с виртуальным временем
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `timer increments every second`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)
    val viewModel = TimerViewModel()

    viewModel.startTimer()

    advanceTimeBy(1000)
    assertEquals(1, viewModel.seconds.value)

    advanceTimeBy(1000)
    assertEquals(2, viewModel.seconds.value)

    advanceTimeBy(3000)
    assertEquals(5, viewModel.seconds.value)

    advanceUntilIdle()
    assertEquals(10, viewModel.seconds.value)

    Dispatchers.resetMain()
}
```

**Виртуальное время**:
- `advanceTimeBy(millis)` — продвигает виртуальное время и выполняет задачи, срок которых наступил.
- `advanceUntilIdle()` — выполняет все отложенные задачи, пока очередь не станет пустой.
- `runCurrent()` — выполняет текущие запланированные задачи без изменения времени.

### Тестирование Обработки Ошибок И Последовательностей Состояний

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _state = MutableStateFlow<UiState>(UiState.Idle)
    val state: StateFlow<UiState> = _state.asStateFlow()

    fun loadUser(id: Int) {
        viewModelScope.launch {
            _state.value = UiState.Loading
            try {
                val user = repository.getUser(id)
                _state.value = UiState.Success(user)
            } catch (e: Exception) {
                _state.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

// - Успешная последовательность
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `load user success updates state correctly`() = runTest {
    val fakeRepository = FakeUserRepository().apply {
        setResult(Result.success(expectedUser))
    }
    val viewModel = UserViewModel(fakeRepository)

    val states = mutableListOf<UiState>()
    val job = launch { viewModel.state.take(3).toList(states) }

    viewModel.loadUser(1)
    advanceUntilIdle()
    job.cancel()

    assertEquals(UiState.Idle, states[0])
    assertEquals(UiState.Loading, states[1])
    assertEquals(UiState.Success(expectedUser), states[2])
}

// - Ошибочная последовательность
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `load user failure updates state with error`() = runTest {
    val fakeRepository = FakeUserRepository().apply {
        setResult(Result.failure(IOException("Network error")))
    }
    val viewModel = UserViewModel(fakeRepository)

    viewModel.loadUser(1)
    advanceUntilIdle()

    val state = viewModel.state.value
    assertTrue(state is UiState.Error)
    assertEquals("Network error", (state as UiState.Error).message)
}
```

### Фейковый Репозиторий (Fake Repository)

```kotlin
class FakeUserRepository : UserRepository {
    private var result: Result<User>? = null
    private val usersFlow = MutableStateFlow<List<User>>(emptyList())

    fun setResult(result: Result<User>) {
        this.result = result
    }

    override suspend fun getUser(id: Int): User {
        delay(100) // эмуляция сетевой задержки
        return result?.getOrThrow() ?: throw IllegalStateException("Result not set")
    }

    override fun observeUsers(): Flow<List<User>> = usersFlow.asStateFlow()

    fun emit(users: List<User>) {
        usersFlow.value = users
    }
}
```

### Тестирование Параллельных Операций

```kotlin
class DashboardViewModel(
    private val userRepo: UserRepository,
    private val statsRepo: StatsRepository,
    private val notificationsRepo: NotificationsRepository
) : ViewModel() {

    private val _dashboardState = MutableStateFlow<DashboardData?>(null)
    val dashboardState: StateFlow<DashboardData?> = _dashboardState.asStateFlow()

    fun loadDashboard() = viewModelScope.launch {
        coroutineScope {
            val userDeferred = async { userRepo.getUser() }
            val statsDeferred = async { statsRepo.getStats() }
            val notificationsDeferred = async { notificationsRepo.getNotifications() }

            _dashboardState.value = DashboardData(
                user = userDeferred.await(),
                stats = statsDeferred.await(),
                notifications = notificationsDeferred.await()
            )
        }
    }
}

// - Тест параллельной загрузки с виртуальным временем
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `loadDashboard loads all data in parallel`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)

    val viewModel = DashboardViewModel(
        fakeUserRepo,
        fakeStatsRepo,
        fakeNotificationsRepo
    )

    // Каждый фейковый репозиторий использует задержку 100ms на том же планировщике
    viewModel.loadDashboard()

    // Если бы было последовательно: ~300ms; параллельно: ~100ms виртуального времени.
    advanceTimeBy(150)

    assertNotNull(viewModel.dashboardState.value?.user)
    assertNotNull(viewModel.dashboardState.value?.stats)
    assertNotNull(viewModel.dashboardState.value?.notifications)

    Dispatchers.resetMain()
}
```

### Тестирование Отмены И Debounce

```kotlin
class SearchViewModel(
    private val searchRepo: SearchRepository
) : ViewModel() {
    private val _results = MutableStateFlow<List<ResultItem>>(emptyList())
    val results: StateFlow<List<ResultItem>> = _results.asStateFlow()

    private var searchJob: Job? = null

    fun search(query: String) {
        searchJob?.cancel()
        searchJob = viewModelScope.launch {
            delay(300) // debounce
            val r = searchRepo.search(query)
            _results.value = r
        }
    }
}

// - Тест отмены поиска
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `new search cancels previous search`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)

    val fakeSearchRepo = FakeSearchRepository()
    val viewModel = SearchViewModel(fakeSearchRepo)

    viewModel.search("query1")
    advanceTimeBy(100)

    viewModel.search("query2")
    advanceUntilIdle()

    assertEquals(listOf("query2"), fakeSearchRepo.queries)

    Dispatchers.resetMain()
}

// - Тест debounce
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `search debounces input`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)

    val fakeSearchRepo = FakeSearchRepository()
    val viewModel = SearchViewModel(fakeSearchRepo)

    viewModel.search("q")
    advanceTimeBy(100)

    viewModel.search("qu")
    advanceTimeBy(100)

    viewModel.search("que")
    advanceTimeBy(100)

    viewModel.search("quer")
    advanceTimeBy(100)

    viewModel.search("query")
    advanceTimeBy(300) // окно debounce

    assertEquals(listOf("query"), fakeSearchRepo.queries)

    Dispatchers.resetMain()
}
```

### Тестирование StateFlow/SharedFlow

```kotlin
class EventsViewModel : ViewModel() {
    private val _events = MutableSharedFlow<Event>(extraBufferCapacity = 1)
    val events: SharedFlow<Event> = _events.asSharedFlow()

    fun sendEvent(event: Event) {
        // Для простых единичных событий в тестах можно использовать tryEmit без отдельной корутины
        _events.tryEmit(event)
    }
}

// - Тест SharedFlow
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `events are emitted to flow`() = runTest {
    val viewModel = EventsViewModel()

    val emittedEvents = mutableListOf<Event>()
    val job = launch {
        viewModel.events.take(3).toList(emittedEvents)
    }

    viewModel.sendEvent(Event.UserLogin)
    viewModel.sendEvent(Event.DataLoaded)
    viewModel.sendEvent(Event.Error("Test"))

    advanceUntilIdle()
    job.cancel()

    assertEquals(3, emittedEvents.size)
    assertTrue(emittedEvents[0] is Event.UserLogin)
    assertTrue(emittedEvents[1] is Event.DataLoaded)
    assertTrue(emittedEvents[2] is Event.Error)
}
```

### Тестирование withContext

```kotlin
class ImageViewModel(
    private val imageProcessor: ImageProcessor
) : ViewModel() {
    private val _isProcessing = MutableStateFlow(false)
    val isProcessing: StateFlow<Boolean> = _isProcessing.asStateFlow()

    private val _processedImage = MutableStateFlow<Bitmap?>(null)
    val processedImage: StateFlow<Bitmap?> = _processedImage.asStateFlow()

    fun processImage(bitmap: Bitmap) {
        viewModelScope.launch {
            _isProcessing.value = true

            val processed = withContext(Dispatchers.Default) {
                imageProcessor.process(bitmap)
            }

            _processedImage.value = processed
            _isProcessing.value = false
        }
    }
}

// - Тест поведения withContext через проверку флагов и результата
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `processImage updates state after processing`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)

    val fakeImageProcessor = FakeImageProcessor()
    val viewModel = ImageViewModel(fakeImageProcessor)

    viewModel.processImage(testBitmap)
    advanceUntilIdle()

    assertNotNull(viewModel.processedImage.value)
    assertFalse(viewModel.isProcessing.value)

    Dispatchers.resetMain()
}
```

### Частые Ошибки (Common Pitfalls)

```kotlin
// 1. Плохой тест — без runTest и управления корутинами
@Test
fun `bad test - no runTest`() {
    val viewModel = UserViewModel(fakeRepository)
    viewModel.loadUser(1)
    // ОШИБКА: корутина может не завершиться до проверки, Main не подменён
    assertEquals(expected, viewModel.user.value)
}

// Исправление: использовать runTest + подмену Main (через правило или вручную)
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `good test - with runTest and Main dispatcher`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)

    val viewModel = UserViewModel(fakeRepository)
    viewModel.loadUser(1)

    advanceUntilIdle()
    assertEquals(expected, viewModel.user.value)

    Dispatchers.resetMain()
}

// 2. Не подменён Main dispatcher
@OptIn(ExperimentalCoroutinesApi::class)
@Test(expected = IllegalStateException::class)
fun `bad test - no main dispatcher`() = runTest {
    // Во многих конфигурациях JVM-тестов viewModelScope/Dispatchers.Main без setMain
    // приведёт к падению (например, IllegalStateException об отсутствии Main dispatcher).
    // Конкретный тип ошибки может зависеть от версии библиотек и окружения.
    UserViewModel(fakeRepository)
}

// Исправление: использовать MainDispatcherRule
@OptIn(ExperimentalCoroutinesApi::class)
@get:Rule
val mainDispatcherRule = MainDispatcherRule()

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `good test - with main dispatcher`() = runTest {
    val viewModel = UserViewModel(fakeRepository) // OK
}

// 3. Нет продвижения времени при StandardTestDispatcher
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `bad test - no advance time`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)

    val viewModel = UserViewModel(fakeRepository)
    viewModel.loadUser(1)

    // ОШИБКА: корутина всё ещё в очереди
    assertEquals(expected, viewModel.user.value)

    Dispatchers.resetMain()
}

// Исправление: использовать advanceUntilIdle()
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `good test - advance time`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)

    val viewModel = UserViewModel(fakeRepository)
    viewModel.loadUser(1)

    advanceUntilIdle()
    assertEquals(expected, viewModel.user.value)

    Dispatchers.resetMain()
}
```

### Best Practices (Лучшие практики)

```kotlin
// 1. Всегда используйте runTest для тестов корутин
@Test
fun test() = runTest {
    // ...
}

// 2. Настройте Main dispatcher для тестирования ViewModel
@OptIn(ExperimentalCoroutinesApi::class)
@get:Rule
val mainDispatcherRule = MainDispatcherRule()

// 3. Используйте фейковые репозитории вместо тяжёлых моков
class FakeUserRepository : UserRepository {
    private var users = listOf<User>()

    fun setUsers(users: List<User>) {
        this.users = users
    }

    override suspend fun getUsers(): List<User> = users
}

// 4. Тестируйте состояния, а не детали реализации
@Test
fun `load user updates state`() = runTest {
    // ...
    assertEquals(expectedUser, viewModel.user.value)
}

// 5. Используйте Turbine для тестирования Flow
@Test
fun `test flow emissions`() = runTest {
    viewModel.users.test {
        assertEquals(emptyList<User>(), awaitItem())
        fakeRepo.emit(users)
        assertEquals(users, awaitItem())
    }
}

// 6. Проверяйте последовательности состояний для Loading
@Test
fun `load user goes through loading state`() = runTest {
    val states = mutableListOf<UiState>()
    val job = launch { viewModel.state.take(3).toList(states) }

    viewModel.loadUser(1)
    advanceUntilIdle()
    job.cancel()

    assertEquals(UiState.Idle, states[0])
    assertEquals(UiState.Loading, states[1])
    assertTrue(states[2] is UiState.Success)
}
```

### Dependencies (Зависимости)

```gradle
testImplementation "org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3"
testImplementation "app.cash.turbine:turbine:1.0.0" // Для тестирования Flow
```

**Итог (RU)**: Тестирование **`ViewModel` с корутинами** требует использования `runTest`, подмены `Dispatchers.Main` через `TestDispatcher`/`MainDispatcherRule`, управления виртуальным временем и использования фейковых источников данных, а также корректного тестирования `Flow`/`StateFlow`/`SharedFlow`.

## Answer (EN)

Testing **`ViewModels`** with coroutines requires special setup to control coroutine execution, `Dispatchers.Main`, and virtual time in the test environment, plus correct handling of `Flow`, `StateFlow`, and `SharedFlow`.

### Main Problem

```kotlin
// ViewModel
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()

    fun loadUser(id: Int) {
        viewModelScope.launch {
            val user = repository.getUser(id)
            _user.value = user
        }
    }
}

// - INCORRECT test - doesn't wait for coroutine completion
@Test
fun `load user updates state`() {
    val viewModel = UserViewModel(fakeRepository)

    viewModel.loadUser(1)

    // FAIL: coroutine hasn't completed yet and uses Dispatchers.Main which is not controlled
    assertEquals(expectedUser, viewModel.user.value)
}
```

**Problem**: coroutine starts asynchronously on `viewModelScope` (using `Dispatchers.Main`), test completes or reads state before completion and without controlling the dispatcher.

### Solution: runTest and MainDispatcherRule

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class MainDispatcherRule(
    private val testDispatcher: TestDispatcher = StandardTestDispatcher()
) : TestWatcher() {
    override fun starting(description: Description) {
        Dispatchers.setMain(testDispatcher)
    }

    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}

// - CORRECT test
@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `load user updates state`() = runTest {
        // Given
        val fakeRepository = FakeUserRepository().apply {
            setResult(Result.success(expectedUser))
        }
        val viewModel = UserViewModel(fakeRepository)

        // When
        viewModel.loadUser(1)

        // Then - advance virtual time so viewModelScope coroutines complete
        advanceUntilIdle()
        assertEquals(expectedUser, viewModel.user.value)
    }
}
```

**runTest**:
- Automatically manages a `TestScope` and `TestCoroutineScheduler`.
- Can automatically wait for child coroutines of the test scope.
- Skips `delay()` via virtual time.
- Works together with a `TestDispatcher` when you set `Dispatchers.Main`.

### MainDispatcherRule - for viewModelScope

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class MainDispatcherRule(
    val dispatcher: TestDispatcher = StandardTestDispatcher()
) : TestWatcher() {
    override fun starting(description: Description) {
        Dispatchers.setMain(dispatcher)
    }

    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}

// Usage in tests: choose ONE approach — rule or manual setMain/resetMain.
@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `load user updates state`() = runTest {
        val fakeRepository = FakeUserRepository().apply {
            setResult(Result.success(expectedUser))
        }
        val viewModel = UserViewModel(fakeRepository)

        viewModel.loadUser(1)
        // viewModelScope now uses TestDispatcher via Dispatchers.Main

        advanceUntilIdle()
        assertEquals(expectedUser, viewModel.user.value)
    }
}
```

**MainDispatcherRule**:
- Replaces `Dispatchers.Main` with a `TestDispatcher`.
- Ensures `viewModelScope` (which uses Main) runs on controllable dispatcher.
- Uses `TestWatcher` to automatically set/reset in JUnit lifecycle.

### StandardTestDispatcher Vs UnconfinedTestDispatcher

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `test with StandardTestDispatcher`() = runTest {
    // Use this TestScope's scheduler
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)

    val viewModel = UserViewModel(fakeRepository)
    viewModel.loadUser(1)

    // Need to explicitly advance time / run queued tasks
    advanceUntilIdle()

    assertEquals(expectedUser, viewModel.user.value)

    Dispatchers.resetMain()
}

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `test with UnconfinedTestDispatcher`() = runTest {
    val dispatcher = UnconfinedTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)

    val viewModel = UserViewModel(fakeRepository)
    viewModel.loadUser(1)

    // Usually no need for advanceUntilIdle() for simple, immediate work,
    // but structured concurrency and child coroutines can still require it.
    advanceUntilIdle()
    assertEquals(expectedUser, viewModel.user.value)

    Dispatchers.resetMain()
}
```

**Differences**:
- `StandardTestDispatcher`: tasks are queued; use `advanceUntilIdle()` / `advanceTimeBy()` / `runCurrent()`.
- `UnconfinedTestDispatcher`: starts execution immediately in the current call stack but is still scheduled; behavior is less deterministic for complex cases, so prefer `StandardTestDispatcher` for `ViewModel` tests.

### Testing Flow

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    val users: StateFlow<List<User>> = repository.observeUsers()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )
}

// - Flow test
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `users flow emits repository data`() = runTest {
    val fakeRepository = FakeUserRepository()
    val viewModel = UserViewModel(fakeRepository)

    val emissions = mutableListOf<List<User>>()
    val job = launch {
        viewModel.users.take(2).toList(emissions)
    }

    fakeRepository.emit(listOf(user1, user2))

    advanceUntilIdle()
    job.cancel()

    assertEquals(emptyList<List<User>>(), listOf(emissions[0])) // initial value
    assertEquals(listOf(user1, user2), emissions[1])
}

// Using turbine library
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `users flow emits repository data - with turbine`() = runTest {
    val fakeRepository = FakeUserRepository()
    val viewModel = UserViewModel(fakeRepository)

    viewModel.users.test {
        assertEquals(emptyList<User>(), awaitItem()) // initial value

        fakeRepository.emit(listOf(user1, user2))
        assertEquals(listOf(user1, user2), awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Testing delay()

```kotlin
class TimerViewModel : ViewModel() {
    private val _seconds = MutableStateFlow(0)
    val seconds: StateFlow<Int> = _seconds.asStateFlow()

    fun startTimer() {
        viewModelScope.launch {
            repeat(10) {
                delay(1000)
                _seconds.value += 1
            }
        }
    }
}

// - Test with virtual time
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `timer increments every second`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)
    val viewModel = TimerViewModel()

    viewModel.startTimer()

    advanceTimeBy(1000)
    assertEquals(1, viewModel.seconds.value)

    advanceTimeBy(1000)
    assertEquals(2, viewModel.seconds.value)

    advanceTimeBy(3000)
    assertEquals(5, viewModel.seconds.value)

    advanceUntilIdle()
    assertEquals(10, viewModel.seconds.value)

    Dispatchers.resetMain()
}
```

**Virtual time**:
- `advanceTimeBy(millis)` - advances virtual time by N ms and runs due tasks.
- `advanceUntilIdle()` - runs all pending tasks until idle.
- `runCurrent()` - runs currently scheduled tasks without advancing time.

### Testing Error Handling

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _state = MutableStateFlow<UiState>(UiState.Idle)
    val state: StateFlow<UiState> = _state.asStateFlow()

    fun loadUser(id: Int) {
        viewModelScope.launch {
            _state.value = UiState.Loading
            try {
                val user = repository.getUser(id)
                _state.value = UiState.Success(user)
            } catch (e: Exception) {
                _state.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

// - Test success sequence
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `load user success updates state correctly`() = runTest {
    val fakeRepository = FakeUserRepository().apply {
        setResult(Result.success(expectedUser))
    }
    val viewModel = UserViewModel(fakeRepository)

    val states = mutableListOf<UiState>()
    val job = launch { viewModel.state.take(3).toList(states) }

    viewModel.loadUser(1)
    advanceUntilIdle()
    job.cancel()

    assertEquals(UiState.Idle, states[0])
    assertEquals(UiState.Loading, states[1])
    assertEquals(UiState.Success(expectedUser), states[2])
}

// - Test error state
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `load user failure updates state with error`() = runTest {
    val fakeRepository = FakeUserRepository().apply {
        setResult(Result.failure(IOException("Network error")))
    }
    val viewModel = UserViewModel(fakeRepository)

    viewModel.loadUser(1)
    advanceUntilIdle()

    val state = viewModel.state.value
    assertTrue(state is UiState.Error)
    assertEquals("Network error", (state as UiState.Error).message)
}
```

### Fake Repository

```kotlin
class FakeUserRepository : UserRepository {
    private var result: Result<User>? = null
    private val usersFlow = MutableStateFlow<List<User>>(emptyList())

    fun setResult(result: Result<User>) {
        this.result = result
    }

    override suspend fun getUser(id: Int): User {
        delay(100) // simulate network delay
        return result?.getOrThrow() ?: throw IllegalStateException("Result not set")
    }

    override fun observeUsers(): Flow<List<User>> = usersFlow.asStateFlow()

    fun emit(users: List<User>) {
        usersFlow.value = users
    }
}
```

### Testing Parallel Operations

```kotlin
class DashboardViewModel(
    private val userRepo: UserRepository,
    private val statsRepo: StatsRepository,
    private val notificationsRepo: NotificationsRepository
) : ViewModel() {

    private val _dashboardState = MutableStateFlow<DashboardData?>(null)
    val dashboardState: StateFlow<DashboardData?> = _dashboardState.asStateFlow()

    fun loadDashboard() = viewModelScope.launch {
        coroutineScope {
            val userDeferred = async { userRepo.getUser() }
            val statsDeferred = async { statsRepo.getStats() }
            val notificationsDeferred = async { notificationsRepo.getNotifications() }

            _dashboardState.value = DashboardData(
                user = userDeferred.await(),
                stats = statsDeferred.await(),
                notifications = notificationsDeferred.await()
            )
        }
    }
}

// - Test parallel loading using virtual time
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `loadDashboard loads all data in parallel`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)

    val viewModel = DashboardViewModel(
        fakeUserRepo,
        fakeStatsRepo,
        fakeNotificationsRepo
    )

    // Each fake repo delays for 100ms using the same scheduler
    viewModel.loadDashboard()

    // If executed sequentially: 300ms; in parallel: ~100ms virtual time.
    advanceTimeBy(150)

    assertNotNull(viewModel.dashboardState.value?.user)
    assertNotNull(viewModel.dashboardState.value?.stats)
    assertNotNull(viewModel.dashboardState.value?.notifications)

    Dispatchers.resetMain()
}
```

### Testing Cancellation

```kotlin
class SearchViewModel(
    private val searchRepo: SearchRepository
) : ViewModel() {
    private val _results = MutableStateFlow<List<ResultItem>>(emptyList())
    val results: StateFlow<List<ResultItem>> = _results.asStateFlow()

    private var searchJob: Job? = null

    fun search(query: String) {
        searchJob?.cancel()
        searchJob = viewModelScope.launch {
            delay(300) // Debounce
            val r = searchRepo.search(query)
            _results.value = r
        }
    }
}

// - Test cancellation
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `new search cancels previous search`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)

    val fakeSearchRepo = FakeSearchRepository()
    val viewModel = SearchViewModel(fakeSearchRepo)

    viewModel.search("query1")
    advanceTimeBy(100)

    viewModel.search("query2")
    advanceUntilIdle()

    assertEquals(listOf("query2"), fakeSearchRepo.queries)

    Dispatchers.resetMain()
}

// - Test debounce
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `search debounces input`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)

    val fakeSearchRepo = FakeSearchRepository()
    val viewModel = SearchViewModel(fakeSearchRepo)

    viewModel.search("q")
    advanceTimeBy(100)

    viewModel.search("qu")
    advanceTimeBy(100)

    viewModel.search("que")
    advanceTimeBy(100)

    viewModel.search("quer")
    advanceTimeBy(100)

    viewModel.search("query")
    advanceTimeBy(300) // debounce window

    assertEquals(listOf("query"), fakeSearchRepo.queries)

    Dispatchers.resetMain()
}
```

### Testing StateFlow/SharedFlow

```kotlin
class EventsViewModel : ViewModel() {
    private val _events = MutableSharedFlow<Event>(extraBufferCapacity = 1)
    val events: SharedFlow<Event> = _events.asSharedFlow()

    fun sendEvent(event: Event) {
        // For simple one-off events in tests, use tryEmit without launching a new coroutine
        _events.tryEmit(event)
    }
}

// - SharedFlow test
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `events are emitted to flow`() = runTest {
    val viewModel = EventsViewModel()

    val emittedEvents = mutableListOf<Event>()
    val job = launch {
        viewModel.events.take(3).toList(emittedEvents)
    }

    viewModel.sendEvent(Event.UserLogin)
    viewModel.sendEvent(Event.DataLoaded)
    viewModel.sendEvent(Event.Error("Test"))

    advanceUntilIdle()
    job.cancel()

    assertEquals(3, emittedEvents.size)
    assertTrue(emittedEvents[0] is Event.UserLogin)
    assertTrue(emittedEvents[1] is Event.DataLoaded)
    assertTrue(emittedEvents[2] is Event.Error)
}
```

### Testing withContext

```kotlin
class ImageViewModel(
    private val imageProcessor: ImageProcessor
) : ViewModel() {
    private val _isProcessing = MutableStateFlow(false)
    val isProcessing: StateFlow<Boolean> = _isProcessing.asStateFlow()

    private val _processedImage = MutableStateFlow<Bitmap?>(null)
    val processedImage: StateFlow<Bitmap?> = _processedImage.asStateFlow()

    fun processImage(bitmap: Bitmap) {
        viewModelScope.launch {
            _isProcessing.value = true

            val processed = withContext(Dispatchers.Default) {
                imageProcessor.process(bitmap)
            }

            _processedImage.value = processed
            _isProcessing.value = false
        }
    }
}

// - Test withContext behavior via result and flags
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `processImage updates state after processing`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)

    val fakeImageProcessor = FakeImageProcessor()
    val viewModel = ImageViewModel(fakeImageProcessor)

    viewModel.processImage(testBitmap)
    advanceUntilIdle()

    assertNotNull(viewModel.processedImage.value)
    assertFalse(viewModel.isProcessing.value)

    Dispatchers.resetMain()
}
```

### Common Pitfalls

```kotlin
// 1. Forgot runTest or proper coroutine control
@Test
fun `bad test - no runTest`() {
    val viewModel = UserViewModel(fakeRepository)
    viewModel.loadUser(1)
    // FAIL: coroutine may not complete before assertion, and Main is not controlled
    assertEquals(expected, viewModel.user.value)
}

// Fix: use runTest + Main dispatcher override (via rule or manual)
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `good test - with runTest and Main dispatcher`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)

    val viewModel = UserViewModel(fakeRepository)
    viewModel.loadUser(1)

    advanceUntilIdle()
    assertEquals(expected, viewModel.user.value)

    Dispatchers.resetMain()
}

// 2. Did not set Main dispatcher
@OptIn(ExperimentalCoroutinesApi::class)
@Test(expected = IllegalStateException::class)
fun `bad test - no main dispatcher`() = runTest {
    // In many JVM test setups, viewModelScope/Dispatchers.Main without setMain
    // will crash (e.g., IllegalStateException about missing Main dispatcher).
    // The exact exception type may depend on library versions and environment.
    UserViewModel(fakeRepository)
}

// Fix: use MainDispatcherRule
@OptIn(ExperimentalCoroutinesApi::class)
@get:Rule
val mainDispatcherRule = MainDispatcherRule()

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `good test - with main dispatcher`() = runTest {
    val viewModel = UserViewModel(fakeRepository) // OK
}

// 3. Did not advance time with StandardTestDispatcher
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `bad test - no advance time`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)

    val viewModel = UserViewModel(fakeRepository)
    viewModel.loadUser(1)

    // FAIL: coroutine is still queued
    assertEquals(expected, viewModel.user.value)

    Dispatchers.resetMain()
}

// Fix: advanceUntilIdle()
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `good test - advance time`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)

    val viewModel = UserViewModel(fakeRepository)
    viewModel.loadUser(1)

    advanceUntilIdle()
    assertEquals(expected, viewModel.user.value)

    Dispatchers.resetMain()
}
```

### Best Practices

```kotlin
// 1. Use runTest
@Test
fun test() = runTest {
    // ...
}

// 2. Configure Main dispatcher for ViewModel tests
@OptIn(ExperimentalCoroutinesApi::class)
@get:Rule
val mainDispatcherRule = MainDispatcherRule()

// 3. Use fake repositories instead of heavy mocks
class FakeUserRepository : UserRepository {
    private var users = listOf<User>()

    fun setUsers(users: List<User>) {
        this.users = users
    }

    override suspend fun getUsers(): List<User> = users
}

// 4. Test states, not implementation details
@Test
fun `load user updates state`() = runTest {
    // ...
    assertEquals(expectedUser, viewModel.user.value)
}

// 5. Use turbine for Flow tests
@Test
fun `test flow emissions`() = runTest {
    viewModel.users.test {
        assertEquals(emptyList<User>(), awaitItem())
        fakeRepo.emit(users)
        assertEquals(users, awaitItem())
    }
}

// 6. Verify state sequences for loading states
@Test
fun `load user goes through loading state`() = runTest {
    val states = mutableListOf<UiState>()
    val job = launch { viewModel.state.take(3).toList(states) }

    viewModel.loadUser(1)
    advanceUntilIdle()
    job.cancel()

    assertEquals(UiState.Idle, states[0])
    assertEquals(UiState.Loading, states[1])
    assertTrue(states[2] is UiState.Success)
}
```

### Dependencies

```gradle
testImplementation "org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3"
testImplementation "app.cash.turbine:turbine:1.0.0" // For Flow testing
```

**Summary (EN)**: Testing **`ViewModels` with coroutines** requires configuring `runTest`, controlling `Dispatchers.Main` via a `TestDispatcher`/`MainDispatcherRule`, using virtual time to make execution deterministic, and using fake data sources while properly testing `Flow`/`StateFlow`/`SharedFlow`.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-coroutines]]

## Related Questions

- [[q-flowon-operator-context-switching--kotlin--hard]]
- [[q-kotlin-reflection--kotlin--medium]]
