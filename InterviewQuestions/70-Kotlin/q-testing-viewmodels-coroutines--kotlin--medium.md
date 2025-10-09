---
tags:
  - kotlin
  - testing
  - coroutines
  - viewmodel
  - unit-testing
difficulty: medium
status: reviewed
---

# Testing ViewModels with Coroutines

**English**: How do you properly test ViewModels that use coroutines? What are the common patterns and pitfalls?

## Answer

Тестирование **ViewModel** с корутинами требует специальной настройки для контроля выполнения корутин и времени в тестовой среде.

### Основная проблема

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

// - НЕПРАВИЛЬНЫЙ тест - не ждет завершения корутины
@Test
fun `load user updates state`() {
    val viewModel = UserViewModel(fakeRepository)

    viewModel.loadUser(1)

    // FAIL: корутина еще не завершилась!
    assertEquals(expectedUser, viewModel.user.value)
}
```

**Проблема**: корутина запускается асинхронно, тест завершается до получения результата.

### Решение: runTest и TestDispatcher

```kotlin
// - ПРАВИЛЬНЫЙ тест
class UserViewModelTest {

    @OptIn(ExperimentalCoroutinesApi::class)
    @Test
    fun `load user updates state`() = runTest {
        // Given
        val fakeRepository = FakeUserRepository()
        val viewModel = UserViewModel(fakeRepository)

        // When
        viewModel.loadUser(1)

        // Then - runTest автоматически ждет завершения корутин
        assertEquals(expectedUser, viewModel.user.value)
    }
}
```

**runTest**:
- - Автоматически ждет завершения всех корутин
- - Предоставляет `TestScope` и `TestDispatcher`
- - Пропускает `delay()` мгновенно
- - Контролирует виртуальное время

### MainDispatcherRule - для viewModelScope

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class MainDispatcherRule(
    private val testDispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : TestWatcher() {
    override fun starting(description: Description) {
        Dispatchers.setMain(testDispatcher)
    }

    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}

// Использование в тестах
class UserViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `load user updates state`() = runTest {
        val viewModel = UserViewModel(fakeRepository)

        viewModel.loadUser(1)
        // viewModelScope теперь использует TestDispatcher

        assertEquals(expectedUser, viewModel.user.value)
    }
}
```

**MainDispatcherRule**:
- - Заменяет `Dispatchers.Main` на `TestDispatcher`
- - Работает с `viewModelScope` (который использует Main)
- - Автоматический cleanup в `@After`

### StandardTestDispatcher vs UnconfinedTestDispatcher

```kotlin
// StandardTestDispatcher - требует явного продвижения времени
@Test
fun `test with StandardTestDispatcher`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)

    val viewModel = UserViewModel(fakeRepository)
    viewModel.loadUser(1)

    // Нужно явно продвинуть время
    advanceUntilIdle() // Или advanceTimeBy()

    assertEquals(expectedUser, viewModel.user.value)

    Dispatchers.resetMain()
}

// UnconfinedTestDispatcher - выполняется немедленно
@Test
fun `test with UnconfinedTestDispatcher`() = runTest {
    val dispatcher = UnconfinedTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)

    val viewModel = UserViewModel(fakeRepository)
    viewModel.loadUser(1)

    // НЕ нужно advanceUntilIdle() - выполнилось сразу
    assertEquals(expectedUser, viewModel.user.value)

    Dispatchers.resetMain()
}
```

**Различия**:
- **StandardTestDispatcher**: корутины в очереди, нужно `advanceUntilIdle()`
- **UnconfinedTestDispatcher**: корутины выполняются немедленно

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
@Test
fun `users flow emits repository data`() = runTest {
    // Given
    val fakeRepository = FakeUserRepository()
    fakeRepository.emit(listOf(user1, user2))

    // When
    val viewModel = UserViewModel(fakeRepository)

    // Collect flow
    val emissions = mutableListOf<List<User>>()
    val job = launch {
        viewModel.users.take(2).toList(emissions)
    }

    advanceUntilIdle()
    job.cancel()

    // Then
    assertEquals(emptyList(), emissions[0]) // initial value
    assertEquals(listOf(user1, user2), emissions[1])
}

// Или используя turbine library
@Test
fun `users flow emits repository data - with turbine`() = runTest {
    val fakeRepository = FakeUserRepository()
    val viewModel = UserViewModel(fakeRepository)

    viewModel.users.test {
        assertEquals(emptyList(), awaitItem()) // initial value

        fakeRepository.emit(listOf(user1, user2))
        assertEquals(listOf(user1, user2), awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Тестирование delay()

```kotlin
class TimerViewModel : ViewModel() {
    private val _seconds = MutableStateFlow(0)
    val seconds: StateFlow<Int> = _seconds.asStateFlow()

    fun startTimer() {
        viewModelScope.launch {
            repeat(10) {
                delay(1000) // 1 секунда
                _seconds.value += 1
            }
        }
    }
}

// - Тест с виртуальным временем
@Test
fun `timer increments every second`() = runTest {
    val viewModel = TimerViewModel()

    viewModel.startTimer()

    // Продвигаем виртуальное время
    advanceTimeBy(1000)
    assertEquals(1, viewModel.seconds.value)

    advanceTimeBy(1000)
    assertEquals(2, viewModel.seconds.value)

    advanceTimeBy(3000)
    assertEquals(5, viewModel.seconds.value)

    // Или до завершения всех корутин
    advanceUntilIdle()
    assertEquals(10, viewModel.seconds.value)
}
```

**Virtual time**:
- `advanceTimeBy(millis)` - продвигает время на N миллисекунд
- `advanceUntilIdle()` - выполняет все pending корутины
- `runCurrent()` - выполняет только текущие scheduled задачи

### Тестирование обработки ошибок

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

// - Тест успешной загрузки
@Test
fun `load user success updates state correctly`() = runTest {
    val fakeRepository = FakeUserRepository()
    fakeRepository.setResult(Result.success(expectedUser))
    val viewModel = UserViewModel(fakeRepository)

    viewModel.loadUser(1)

    // Проверяем последовательность состояний
    val states = mutableListOf<UiState>()
    states.add(viewModel.state.value) // Should be Success

    assertEquals(UiState.Success(expectedUser), states.last())
}

// - Тест ошибки
@Test
fun `load user failure updates state with error`() = runTest {
    val fakeRepository = FakeUserRepository()
    fakeRepository.setResult(Result.failure(IOException("Network error")))
    val viewModel = UserViewModel(fakeRepository)

    viewModel.loadUser(1)

    assertTrue(viewModel.state.value is UiState.Error)
    assertEquals("Network error", (viewModel.state.value as UiState.Error).message)
}
```

### Fake Repository

```kotlin
// - Тестовый repository
class FakeUserRepository : UserRepository {
    private var result: Result<User>? = null
    private val usersFlow = MutableStateFlow<List<User>>(emptyList())

    fun setResult(result: Result<User>) {
        this.result = result
    }

    override suspend fun getUser(id: Int): User {
        delay(100) // Симулируем network delay
        return result?.getOrThrow() ?: throw IllegalStateException("Result not set")
    }

    override fun observeUsers(): Flow<List<User>> {
        return usersFlow.asStateFlow()
    }

    fun emit(users: List<User>) {
        usersFlow.value = users
    }
}
```

### Тестирование параллельных операций

```kotlin
class DashboardViewModel(
    private val userRepo: UserRepository,
    private val statsRepo: StatsRepository,
    private val notificationsRepo: NotificationsRepository
) : ViewModel() {

    suspend fun loadDashboard(): DashboardData = coroutineScope {
        val userDeferred = async { userRepo.getUser() }
        val statsDeferred = async { statsRepo.getStats() }
        val notificationsDeferred = async { notificationsRepo.getNotifications() }

        DashboardData(
            user = userDeferred.await(),
            stats = statsDeferred.await(),
            notifications = notificationsDeferred.await()
        )
    }
}

// - Тест параллельной загрузки
@Test
fun `loadDashboard loads all data in parallel`() = runTest {
    val viewModel = DashboardViewModel(
        fakeUserRepo,
        fakeStatsRepo,
        fakeNotificationsRepo
    )

    val startTime = currentTime
    val result = viewModel.loadDashboard()
    val endTime = currentTime

    // Проверяем что все загрузилось
    assertNotNull(result.user)
    assertNotNull(result.stats)
    assertNotNull(result.notifications)

    // Проверяем что выполнялось параллельно
    // (если бы последовательно - заняло бы 300ms)
    assertTrue(endTime - startTime < 150) // ~100ms (max из трех)
}
```

### Тестирование cancellation

```kotlin
class SearchViewModel(
    private val searchRepo: SearchRepository
) : ViewModel() {
    private var searchJob: Job? = null

    fun search(query: String) {
        searchJob?.cancel() // Отменяем предыдущий поиск
        searchJob = viewModelScope.launch {
            delay(300) // Debounce
            val results = searchRepo.search(query)
            _results.value = results
        }
    }
}

// - Тест отмены
@Test
fun `new search cancels previous search`() = runTest {
    val viewModel = SearchViewModel(fakeSearchRepo)

    // Запускаем первый поиск
    viewModel.search("query1")
    advanceTimeBy(100) // Ждем 100ms

    // Запускаем второй - должен отменить первый
    viewModel.search("query2")
    advanceUntilIdle()

    // Проверяем что выполнился только второй
    assertEquals("query2", fakeSearchRepo.lastQuery)
    verify(fakeSearchRepo, times(1)).search(any()) // Только один вызов
}

// - Тест debounce
@Test
fun `search debounces input`() = runTest {
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
    advanceTimeBy(300) // Debounce прошел

    // Только последний запрос выполнился
    assertEquals("query", fakeSearchRepo.lastQuery)
}
```

### Тестирование StateFlow/SharedFlow

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

// - Тест SharedFlow
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

    job.join()

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
    fun processImage(bitmap: Bitmap) {
        viewModelScope.launch {
            _isProcessing.value = true

            val processed = withContext(Dispatchers.Default) {
                imageProcessor.process(bitmap) // CPU-intensive
            }

            _processedImage.value = processed
            _isProcessing.value = false
        }
    }
}

// - Тест withContext
@Test
fun `processImage uses Default dispatcher`() = runTest {
    val viewModel = ImageViewModel(fakeImageProcessor)

    viewModel.processImage(testBitmap)
    advanceUntilIdle()

    // Проверяем результат
    assertNotNull(viewModel.processedImage.value)
    assertFalse(viewModel.isProcessing.value)
}
```

### Common Pitfalls

```kotlin
// - 1. Забыли runTest
@Test
fun `bad test - no runTest`() {
    val viewModel = UserViewModel(fakeRepository)
    viewModel.loadUser(1)
    // FAIL: корутина не завершилась
    assertEquals(expected, viewModel.user.value)
}

// - Fix: используйте runTest
@Test
fun `good test - with runTest`() = runTest {
    val viewModel = UserViewModel(fakeRepository)
    viewModel.loadUser(1)
    assertEquals(expected, viewModel.user.value)
}

// - 2. Не настроили Main dispatcher
@Test
fun `bad test - no main dispatcher`() = runTest {
    // viewModelScope использует Dispatchers.Main
    val viewModel = UserViewModel(fakeRepository) // CRASH!
}

// - Fix: используйте MainDispatcherRule
@get:Rule
val mainDispatcherRule = MainDispatcherRule()

@Test
fun `good test - with main dispatcher`() = runTest {
    val viewModel = UserViewModel(fakeRepository) // OK
}

// - 3. Не продвинули время
@Test
fun `bad test - no advance time`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)

    val viewModel = UserViewModel(fakeRepository)
    viewModel.loadUser(1)

    // FAIL: корутина в очереди
    assertEquals(expected, viewModel.user.value)
}

// - Fix: advanceUntilIdle()
@Test
fun `good test - advance time`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)

    val viewModel = UserViewModel(fakeRepository)
    viewModel.loadUser(1)

    advanceUntilIdle() // Выполняем pending корутины
    assertEquals(expected, viewModel.user.value)
}
```

### Best Practices

```kotlin
// - 1. Используйте runTest
@Test
fun test() = runTest {
    // ...
}

// - 2. Настройте Main dispatcher
@get:Rule
val mainDispatcherRule = MainDispatcherRule()

// - 3. Используйте Fake repositories
class FakeUserRepository : UserRepository {
    private var users = listOf<User>()

    fun setUsers(users: List<User>) {
        this.users = users
    }

    override suspend fun getUsers() = users
}

// - 4. Тестируйте состояния, не реализацию
@Test
fun `load user updates state`() = runTest {
    viewModel.loadUser(1)

    // Проверяем конечное состояние, не как оно достигнуто
    assertEquals(expectedUser, viewModel.user.value)
}

// - 5. Используйте turbine для Flow
@Test
fun `test flow emissions`() = runTest {
    viewModel.users.test {
        assertEquals(emptyList(), awaitItem())
        fakeRepo.emit(users)
        assertEquals(users, awaitItem())
    }
}

// - 6. Проверяйте sequence состояний
@Test
fun `load user goes through loading state`() = runTest {
    val states = mutableListOf<UiState>()

    val job = launch {
        viewModel.state.take(3).toList(states)
    }

    viewModel.loadUser(1)
    job.join()

    assertEquals(UiState.Idle, states[0])
    assertEquals(UiState.Loading, states[1])
    assertTrue(states[2] is UiState.Success)
}
```

### Dependencies

```gradle
testImplementation "org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3"
testImplementation "app.cash.turbine:turbine:1.0.0" // Для тестирования Flow
```

**English**: Testing **ViewModels with coroutines** requires special setup to control coroutine execution and time in test environment.

**Key tools**: (1) **runTest** - provides TestScope, auto-waits for coroutines, skips delay() instantly. (2) **MainDispatcherRule** - replaces Dispatchers.Main with TestDispatcher for viewModelScope. (3) **TestDispatcher** - StandardTestDispatcher (needs advanceUntilIdle) vs UnconfinedTestDispatcher (executes immediately).

**Virtual time control**: `advanceTimeBy(millis)` advances time by N milliseconds. `advanceUntilIdle()` executes all pending coroutines. `runCurrent()` executes only currently scheduled tasks. `currentTime` gets virtual time.

**Testing patterns**: Use Fake repositories with controllable results. Test Flow with `test {}` (turbine) or `take().toList()`. Test state sequences not implementation. Test error handling with Result.failure(). Test cancellation with multiple rapid calls. Test debouncing with advanceTimeBy().

**Common pitfalls**: Forgetting runTest (test completes before coroutine). Not setting up Main dispatcher (crashes). Not advancing time with StandardTestDispatcher (test fails). Testing implementation instead of state.

**Best practices**: Always use runTest for coroutine tests. Use MainDispatcherRule for ViewModels. Use Fake repositories, not mocks. Test final state, not intermediate steps. Use turbine for Flow testing. Verify state sequences for loading states.

