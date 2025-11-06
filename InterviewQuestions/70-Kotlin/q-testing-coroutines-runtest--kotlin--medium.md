---
id: kotlin-106
title: "Testing Coroutines with runTest and TestDispatcher / Тестирование корутин с runTest и TestDispatcher"
aliases: ["Testing Coroutines with runTest and TestDispatcher, Тестирование корутин с runTest и TestDispatcher"]

# Classification
topic: kotlin
subtopics: [coroutines, runtest, test-dispatcher]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Testing Guide

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-testing-coroutine-cancellation--kotlin--medium, q-testing-flow-operators--kotlin--hard, q-testing-stateflow-sharedflow--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [coroutines, difficulty/medium, kotlin, runtest, test-dispatcher, testing]
---
# Вопрос (RU)
> Как тестировать корутины с runTest и TestDispatcher? Объясните виртуальное время, StandardTestDispatcher vs UnconfinedTestDispatcher и практические паттерны тестирования для ViewModels.

---

# Question (EN)
> How to test coroutines with runTest and TestDispatcher? Explain virtual time, StandardTestDispatcher vs UnconfinedTestDispatcher, and practical testing patterns for ViewModels.

## Ответ (RU)

Тестирование корутин требует специальной инфраструктуры для контроля времени выполнения, обработки задержек без реального ожидания и обеспечения детерминированных результатов. Библиотека `kotlinx-coroutines-test` предоставляет мощные инструменты для этого.

### Проблема: Почему Обычные Тесты Не Работают

```kotlin
// Продакшн код
class UserRepository {
    suspend fun fetchUser(id: Int): User {
        delay(1000) // Имитация сетевого запроса
        return User(id, "User $id")
    }
}

class UserViewModel(private val repository: UserRepository) {
    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()

    fun loadUser(id: Int) {
        viewModelScope.launch {
            val result = repository.fetchUser(id)
            _user.value = result
        }
    }
}

//  НЕПРАВИЛЬНО: Тест провалится или зависнет
@Test
fun `load user - неправильный подход`() {
    val repository = UserRepository()
    val viewModel = UserViewModel(repository)

    viewModel.loadUser(1)

    // ПРОВАЛ: Корутина еще не завершилась!
    assertEquals(User(1, "User 1"), viewModel.user.value)
}
```

**Проблемы**:
1. Корутины асинхронные - тест завершается до корутины
2. delay(1000) реально ждет 1 секунду - тесты медленные
3. Нет контроля над порядком выполнения
4. Нестабильные тесты из-за проблем с таймингом

### Решение: runTest И Виртуальное Время

```kotlin
//  ПРАВИЛЬНО: Использование runTest
@Test
fun `load user - правильный подход`() = runTest {
    val repository = FakeUserRepository()
    val viewModel = UserViewModel(repository)

    viewModel.loadUser(1)

    // runTest автоматически:
    // 1. Ждет завершения всех корутин
    // 2. Пропускает задержки (виртуальное время)
    // 3. Обеспечивает детерминированное выполнение

    assertEquals(User(1, "User 1"), viewModel.user.value)
}
```

### Возможности runTest

**runTest** предоставляет:

1. **TestScope**: Специальный scope для тестирования
2. **Виртуальное время**: Задержки не ждут реально
3. **Автоматическое ожидание**: Тест ждет завершения корутин
4. **Контроль времени**: Ручное продвижение через `advanceTimeBy()`
5. **TestDispatcher**: Специальный диспетчер для детерминированного выполнения

### Типы TestDispatcher

#### 1. StandardTestDispatcher

Ставит корутины в очередь, требует явного продвижения времени.

```kotlin
@Test
fun `StandardTestDispatcher - очередь корутин`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)

    var executed = false

    launch(dispatcher) {
        executed = true
    }

    // Корутина в очереди, еще не выполнена
    assertFalse(executed)

    // Нужно явно продвинуть время
    advanceUntilIdle()

    // Теперь выполнилась
    assertTrue(executed)
}
```

**Характеристики StandardTestDispatcher**:
- Корутины в очереди, не выполняются сразу
- Требует явного продвижения времени
- Предсказуемое, детерминированное выполнение
- Лучше для тестирования кода, зависящего от времени
- Больше контроля над порядком выполнения

#### 2. UnconfinedTestDispatcher

Выполняет корутины немедленно до первой точки приостановки.

```kotlin
@Test
fun `UnconfinedTestDispatcher - немедленное выполнение`() = runTest {
    val dispatcher = UnconfinedTestDispatcher(testScheduler)

    var executed = false

    launch(dispatcher) {
        executed = true
    }

    // Уже выполнилась! Не нужен advanceUntilIdle()
    assertTrue(executed)
}
```

**Характеристики UnconfinedTestDispatcher**:
- Выполняется немедленно до точки приостановки
- Меньше явного продвижения времени
- Проще для тестов без зависимостей от времени
- Быстрее выполнение тестов
- Меньше контроля над таймингом

### Функции Контроля Виртуального Времени

#### advanceUntilIdle()

Выполняет все ожидающие корутины до тех пор, пока не останется запланированных задач.

```kotlin
@Test
fun `advanceUntilIdle - выполняет всё`() = runTest {
    val events = mutableListOf<String>()

    launch {
        delay(1000)
        events.add("1 секунда")
        delay(2000)
        events.add("3 секунды всего")
    }

    advanceUntilIdle()

    assertEquals(3, events.size)
    assertEquals(3000, currentTime)
}
```

#### advanceTimeBy(milliseconds)

Продвигает виртуальное время на указанное количество, выполняет корутины, запланированные в этом времени.

```kotlin
@Test
fun `advanceTimeBy - точный контроль`() = runTest {
    val events = mutableListOf<String>()

    launch {
        delay(100)
        events.add("100ms")
    }

    launch {
        delay(200)
        events.add("200ms")
    }

    advanceTimeBy(150)
    assertEquals(listOf("100ms"), events)

    advanceTimeBy(100)
    assertEquals(listOf("100ms", "200ms"), events)
}
```

### Тестирование ViewModel

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

class UserViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `loadUser обновляет состояние`() = runTest {
        val repository = FakeUserRepository()
        val viewModel = UserViewModel(repository)

        viewModel.loadUser(1)

        assertEquals(User(1, "User 1"), viewModel.user.value)
    }
}
```

### Лучшие Практики

1. **Всегда используйте runTest** для тестов с корутинами
2. **Используйте MainDispatcherRule** для тестирования ViewModel
3. **Используйте Fake репозитории**, не моки или реальные
4. **Явно продвигайте время** с StandardTestDispatcher
5. **Отменяйте job'ы коллекции** для предотвращения зависания
6. **Тестируйте последовательности состояний**, не реализацию
7. **Используйте currentTime** для проверки таймингов

---

## Answer (EN)

Testing coroutines requires special infrastructure to control execution timing, handle delays without actually waiting, and ensure deterministic test results. The `kotlinx-coroutines-test` library provides powerful tools for this.

### The Problem: Why Regular Tests Fail

```kotlin
// Production code
class UserRepository {
    suspend fun fetchUser(id: Int): User {
        delay(1000) // Simulate network call
        return User(id, "User $id")
    }
}

class UserViewModel(private val repository: UserRepository) {
    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()

    fun loadUser(id: Int) {
        viewModelScope.launch {
            val result = repository.fetchUser(id)
            _user.value = result
        }
    }
}

//  WRONG: Test will fail or take forever
@Test
fun `load user - wrong approach`() {
    val repository = UserRepository()
    val viewModel = UserViewModel(repository)

    viewModel.loadUser(1)

    // FAILS: Coroutine hasn't completed yet!
    assertEquals(User(1, "User 1"), viewModel.user.value)

    // Even with Thread.sleep(2000), tests become slow
}
```

**Problems**:
1. Coroutines are asynchronous - test completes before coroutine
2. delay(1000) actually waits 1 second - tests are slow
3. No control over execution order
4. Flaky tests due to timing issues

### Solution: runTest and Virtual Time

```kotlin
//  CORRECT: Using runTest
@Test
fun `load user - correct approach`() = runTest {
    val repository = FakeUserRepository()
    val viewModel = UserViewModel(repository)

    viewModel.loadUser(1)

    // runTest automatically:
    // 1. Waits for all coroutines to complete
    // 2. Skips delays (virtual time)
    // 3. Ensures deterministic execution

    assertEquals(User(1, "User 1"), viewModel.user.value)
}

class FakeUserRepository : UserRepository {
    override suspend fun fetchUser(id: Int): User {
        delay(1000) // This completes instantly in tests!
        return User(id, "User $id")
    }
}
```

### runTest Features

**runTest** provides:

1. **TestScope**: Special coroutine scope for testing
2. **Virtual time**: Delays don't actually wait
3. **Automatic waiting**: Test waits for all coroutines to complete
4. **Time control**: Manual time advancement with `advanceTimeBy()`
5. **TestDispatcher**: Special dispatcher for deterministic execution

```kotlin
@Test
fun `runTest features demonstration`() = runTest {
    val startTime = currentTime // Virtual time starts at 0

    launch {
        delay(1000)
        println("After 1 second (virtual)")
    }

    launch {
        delay(2000)
        println("After 2 seconds (virtual)")
    }

    // Test completes instantly, but delays are "honored" virtually
    val endTime = currentTime

    assertTrue(endTime >= 2000) // Virtual time advanced
}
```

### TestDispatcher Types

There are two main TestDispatcher implementations:

#### 1. StandardTestDispatcher (Default)

Schedules coroutines to execute later, requires explicit time advancement.

```kotlin
@Test
fun `StandardTestDispatcher - queues coroutines`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)

    var executed = false

    launch(dispatcher) {
        executed = true
    }

    // Coroutine is queued, not executed yet
    assertFalse(executed)

    // Must explicitly advance time
    advanceUntilIdle()

    // Now it has executed
    assertTrue(executed)
}

@Test
fun `StandardTestDispatcher with delays`() = runTest {
    val results = mutableListOf<String>()

    launch {
        delay(1000)
        results.add("1s")
    }

    launch {
        delay(2000)
        results.add("2s")
    }

    launch {
        delay(500)
        results.add("500ms")
    }

    // Nothing executed yet
    assertTrue(results.isEmpty())

    advanceTimeBy(500)
    assertEquals(listOf("500ms"), results)

    advanceTimeBy(500)
    assertEquals(listOf("500ms", "1s"), results)

    advanceTimeBy(1000)
    assertEquals(listOf("500ms", "1s", "2s"), results)
}
```

**StandardTestDispatcher characteristics**:
- Coroutines are queued, not executed immediately
- Requires explicit time advancement: `advanceUntilIdle()`, `advanceTimeBy()`, `runCurrent()`
- Predictable, deterministic execution
- Best for testing timing-sensitive code
- More control over execution order

#### 2. UnconfinedTestDispatcher

Executes coroutines eagerly until the first suspension point.

```kotlin
@Test
fun `UnconfinedTestDispatcher - immediate execution`() = runTest {
    val dispatcher = UnconfinedTestDispatcher(testScheduler)

    var executed = false

    launch(dispatcher) {
        executed = true
    }

    // Already executed! No need for advanceUntilIdle()
    assertTrue(executed)
}

@Test
fun `UnconfinedTestDispatcher suspends at delay`() = runTest {
    val dispatcher = UnconfinedTestDispatcher(testScheduler)
    val results = mutableListOf<String>()

    launch(dispatcher) {
        results.add("before delay")
        delay(1000)
        results.add("after delay")
    }

    // Executed until delay
    assertEquals(listOf("before delay"), results)

    // Need to advance for code after delay
    advanceUntilIdle()
    assertEquals(listOf("before delay", "after delay"), results)
}

@Test
fun `UnconfinedTestDispatcher comparison`() = runTest {
    val results = mutableListOf<String>()

    // With UnconfinedTestDispatcher
    val unconfined = UnconfinedTestDispatcher(testScheduler)
    launch(unconfined) {
        results.add("A")
        delay(100)
        results.add("B")
    }

    // "A" is already in results
    assertEquals(listOf("A"), results)

    advanceUntilIdle()
    assertEquals(listOf("A", "B"), results)
}
```

**UnconfinedTestDispatcher characteristics**:
- Executes eagerly until first suspension point
- Less explicit time advancement needed
- Simpler for tests without timing dependencies
- Faster test execution
- Less control over timing

### Comparison: Standard Vs Unconfined

```kotlin
@Test
fun `comparing both dispatchers`() = runTest {
    val results = mutableListOf<String>()

    // StandardTestDispatcher
    val standard = StandardTestDispatcher(testScheduler)
    launch(standard) {
        results.add("standard-start")
    }

    // Not executed yet
    assertTrue(results.isEmpty())

    advanceUntilIdle()
    assertEquals(listOf("standard-start"), results)

    // UnconfinedTestDispatcher
    results.clear()
    val unconfined = UnconfinedTestDispatcher(testScheduler)
    launch(unconfined) {
        results.add("unconfined-start")
    }

    // Executed immediately
    assertEquals(listOf("unconfined-start"), results)
}
```

### Virtual Time Control Functions

#### advanceUntilIdle()

Executes all pending coroutines until there are no more scheduled tasks.

```kotlin
@Test
fun `advanceUntilIdle - runs everything`() = runTest {
    val events = mutableListOf<String>()

    launch {
        delay(1000)
        events.add("1 second")
        delay(2000)
        events.add("3 seconds total")
    }

    launch {
        delay(500)
        events.add("500 ms")
    }

    advanceUntilIdle()

    assertEquals(3, events.size)
    assertEquals(3000, currentTime)
}
```

#### advanceTimeBy(milliseconds)

Advances virtual time by specified amount, executes coroutines scheduled within that time.

```kotlin
@Test
fun `advanceTimeBy - precise control`() = runTest {
    val events = mutableListOf<String>()

    launch {
        delay(100)
        events.add("100ms")
    }

    launch {
        delay(200)
        events.add("200ms")
    }

    launch {
        delay(300)
        events.add("300ms")
    }

    advanceTimeBy(150)
    assertEquals(listOf("100ms"), events)
    assertEquals(150, currentTime)

    advanceTimeBy(100)
    assertEquals(listOf("100ms", "200ms"), events)
    assertEquals(250, currentTime)

    advanceTimeBy(50)
    assertEquals(listOf("100ms", "200ms", "300ms"), events)
    assertEquals(300, currentTime)
}
```

#### runCurrent()

Executes only the coroutines scheduled at the current virtual time.

```kotlin
@Test
fun `runCurrent - current tasks only`() = runTest {
    val events = mutableListOf<String>()

    launch {
        events.add("immediate")
    }

    launch {
        delay(100)
        events.add("delayed")
    }

    // Run only immediate tasks
    runCurrent()
    assertEquals(listOf("immediate"), events)

    // Time hasn't advanced
    assertEquals(0, currentTime)

    // Now advance to run delayed task
    advanceTimeBy(100)
    assertEquals(listOf("immediate", "delayed"), events)
}
```

### Testing ViewModels

ViewModels use `viewModelScope` which launches coroutines on `Dispatchers.Main`. In tests, we need to replace the Main dispatcher with a TestDispatcher.

#### MainDispatcherRule

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

// Usage in tests
class UserViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `loadUser updates state`() = runTest {
        val repository = FakeUserRepository()
        val viewModel = UserViewModel(repository)

        viewModel.loadUser(1)

        // viewModelScope now uses TestDispatcher
        assertEquals(User(1, "User 1"), viewModel.user.value)
    }
}
```

#### Complete ViewModel Test Example

```kotlin
data class UiState<out T> {
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val message: String) : UiState<Nothing>()
    object Loading : UiState<Nothing>()
    object Idle : UiState<Nothing>()
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
    fun `initial state is Idle`() {
        assertTrue(viewModel.uiState.value is UiState.Idle)
    }

    @Test
    fun `loadUser success updates state to Success`() = runTest {
        repository.setResult(Result.success(User(1, "John")))

        viewModel.loadUser(1)

        assertTrue(viewModel.uiState.value is UiState.Success)
        assertEquals(User(1, "John"), (viewModel.uiState.value as UiState.Success).data)
    }

    @Test
    fun `loadUser failure updates state to Error`() = runTest {
        repository.setResult(Result.failure(IOException("Network error")))

        viewModel.loadUser(1)

        assertTrue(viewModel.uiState.value is UiState.Error)
        assertEquals("Network error", (viewModel.uiState.value as UiState.Error).message)
    }

    @Test
    fun `loadUser goes through Loading state`() = runTest {
        repository.setDelay(100)
        repository.setResult(Result.success(User(1, "John")))

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

        job.cancel()
    }

    @Test
    fun `multiple rapid loadUser calls - last one wins`() = runTest {
        repository.setDelay(100)

        viewModel.loadUser(1)
        advanceTimeBy(50)

        viewModel.loadUser(2)
        advanceTimeBy(50)

        viewModel.loadUser(3)
        advanceUntilIdle()

        // All three complete, but last one is the final state
        assertTrue(viewModel.uiState.value is UiState.Success)
        assertEquals(User(3, "User 3"), (viewModel.uiState.value as UiState.Success).data)
    }
}

class FakeUserRepository : UserRepository {
    private var result: Result<User> = Result.success(User(0, "Default"))
    private var delayMs: Long = 0

    fun setResult(result: Result<User>) {
        this.result = result
    }

    fun setDelay(ms: Long) {
        this.delayMs = ms
    }

    override suspend fun fetchUser(id: Int): User {
        if (delayMs > 0) delay(delayMs)

        return result.getOrElse { throw it }
            .copy(id = id, name = "User $id")
    }
}
```

### Testing Delays and Timeouts

```kotlin
class TimerViewModel : ViewModel() {
    private val _seconds = MutableStateFlow(0)
    val seconds: StateFlow<Int> = _seconds.asStateFlow()

    fun startTimer(duration: Int) {
        viewModelScope.launch {
            repeat(duration) {
                delay(1000)
                _seconds.value = it + 1
            }
        }
    }
}

class TimerViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `timer increments every second`() = runTest {
        val viewModel = TimerViewModel()

        viewModel.startTimer(5)

        assertEquals(0, viewModel.seconds.value)

        advanceTimeBy(1000)
        assertEquals(1, viewModel.seconds.value)

        advanceTimeBy(2000)
        assertEquals(3, viewModel.seconds.value)

        advanceTimeBy(2000)
        assertEquals(5, viewModel.seconds.value)
    }

    @Test
    fun `timer completes after duration`() = runTest {
        val viewModel = TimerViewModel()

        viewModel.startTimer(3)

        advanceUntilIdle()

        assertEquals(3, viewModel.seconds.value)
        assertEquals(3000, currentTime)
    }
}

// Testing timeout
class DataLoader(private val repository: Repository) {
    suspend fun loadWithTimeout(timeoutMs: Long): Result<Data> {
        return try {
            withTimeout(timeoutMs) {
                Result.success(repository.fetchData())
            }
        } catch (e: TimeoutCancellationException) {
            Result.failure(e)
        }
    }
}

@Test
fun `loadWithTimeout succeeds when data arrives in time`() = runTest {
    val repository = FakeRepository(delayMs = 500)
    val loader = DataLoader(repository)

    val result = loader.loadWithTimeout(1000)

    assertTrue(result.isSuccess)
}

@Test
fun `loadWithTimeout fails when data takes too long`() = runTest {
    val repository = FakeRepository(delayMs = 2000)
    val loader = DataLoader(repository)

    val result = loader.loadWithTimeout(1000)

    assertTrue(result.isFailure)
    assertTrue(result.exceptionOrNull() is TimeoutCancellationException)
}
```

### Testing Parallel Operations

```kotlin
class DashboardViewModel(
    private val userRepo: UserRepository,
    private val statsRepo: StatsRepository,
    private val notificationsRepo: NotificationsRepository
) : ViewModel() {

    data class Dashboard(
        val user: User,
        val stats: Stats,
        val notifications: List<Notification>
    )

    suspend fun loadDashboard(): Dashboard = coroutineScope {
        val userDeferred = async { userRepo.getUser() }
        val statsDeferred = async { statsRepo.getStats() }
        val notificationsDeferred = async { notificationsRepo.getNotifications() }

        Dashboard(
            user = userDeferred.await(),
            stats = statsDeferred.await(),
            notifications = notificationsDeferred.await()
        )
    }
}

@Test
fun `loadDashboard loads all data in parallel`() = runTest {
    val userRepo = FakeUserRepository(delayMs = 100)
    val statsRepo = FakeStatsRepository(delayMs = 100)
    val notificationsRepo = FakeNotificationsRepository(delayMs = 100)

    val viewModel = DashboardViewModel(userRepo, statsRepo, notificationsRepo)

    val startTime = currentTime
    val dashboard = viewModel.loadDashboard()
    val endTime = currentTime

    // All data loaded
    assertNotNull(dashboard.user)
    assertNotNull(dashboard.stats)
    assertNotNull(dashboard.notifications)

    // Parallel execution: took ~100ms not 300ms
    assertTrue(endTime - startTime <= 100)
}

@Test
fun `loadDashboard fails if any repo fails`() = runTest {
    val userRepo = FakeUserRepository()
    val statsRepo = FakeStatsRepository(shouldFail = true)
    val notificationsRepo = FakeNotificationsRepository()

    val viewModel = DashboardViewModel(userRepo, statsRepo, notificationsRepo)

    assertThrows<Exception> {
        viewModel.loadDashboard()
    }
}
```

### Testing Cancellation

```kotlin
class SearchViewModel(private val repository: SearchRepository) : ViewModel() {
    private var searchJob: Job? = null
    private val _results = MutableStateFlow<List<SearchResult>>(emptyList())
    val results: StateFlow<List<SearchResult>> = _results.asStateFlow()

    fun search(query: String) {
        searchJob?.cancel()
        searchJob = viewModelScope.launch {
            delay(300) // Debounce
            val results = repository.search(query)
            _results.value = results
        }
    }
}

@Test
fun `new search cancels previous search`() = runTest {
    val repository = FakeSearchRepository()
    val viewModel = SearchViewModel(repository)

    viewModel.search("query1")
    advanceTimeBy(100)

    viewModel.search("query2")
    advanceUntilIdle()

    // Only query2 was completed
    assertEquals(1, repository.searchCount)
    assertEquals("query2", repository.lastQuery)
}

@Test
fun `search debounces rapid input`() = runTest {
    val repository = FakeSearchRepository()
    val viewModel = SearchViewModel(repository)

    viewModel.search("a")
    advanceTimeBy(100)

    viewModel.search("ab")
    advanceTimeBy(100)

    viewModel.search("abc")
    advanceTimeBy(100)

    viewModel.search("abcd")
    advanceTimeBy(300) // Debounce completes

    // Only last search executed
    assertEquals(1, repository.searchCount)
    assertEquals("abcd", repository.lastQuery)
}
```

### Testing Flow Collection

```kotlin
@Test
fun `collect flow emissions over time`() = runTest {
    val flow = flow {
        emit(1)
        delay(100)
        emit(2)
        delay(100)
        emit(3)
    }

    val emissions = mutableListOf<Int>()
    val job = launch {
        flow.collect { emissions.add(it) }
    }

    runCurrent() // Collect first emission
    assertEquals(listOf(1), emissions)

    advanceTimeBy(100)
    assertEquals(listOf(1, 2), emissions)

    advanceTimeBy(100)
    assertEquals(listOf(1, 2, 3), emissions)

    job.cancel()
}

@Test
fun `collect with take`() = runTest {
    val flow = flow {
        repeat(10) {
            emit(it)
            delay(100)
        }
    }

    val emissions = flow.take(3).toList()

    assertEquals(listOf(0, 1, 2), emissions)
    assertEquals(200, currentTime) // Only waited for 3 emissions
}
```

### Best Practices

```kotlin
//  DO: Use runTest for all coroutine tests
@Test
fun goodTest() = runTest {
    // Test code
}

//  DON'T: Use runBlocking in tests
@Test
fun badTest() = runBlocking { // Slow, doesn't skip delays
    delay(1000) // Actually waits 1 second!
}

//  DO: Use MainDispatcherRule for ViewModels
class ViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()
}

//  DON'T: Forget to set Main dispatcher
@Test
fun badViewModelTest() = runTest {
    val viewModel = MyViewModel() // CRASH: Dispatchers.Main not set!
}

//  DO: Use fake repositories
class FakeRepository : Repository {
    var result: Result<Data>? = null
    override suspend fun getData() = result!!.getOrThrow()
}

//  DON'T: Use real repositories in unit tests
@Test
fun badTest() = runTest {
    val repo = RealRepository(apiService) // Network calls in unit tests!
}

//  DO: Advance time explicitly with StandardTestDispatcher
@Test
fun goodTest() = runTest {
    launch { delay(100) }
    advanceUntilIdle()
    // Assertions
}

//  DON'T: Assume immediate execution with StandardTestDispatcher
@Test
fun badTest() = runTest {
    launch { /* code */ }
    // Assertions here - coroutine not executed yet!
}

//  DO: Test state sequences
@Test
fun goodTest() = runTest {
    val states = mutableListOf<State>()
    val job = launch { viewModel.state.collect { states.add(it) } }

    viewModel.loadData()
    advanceUntilIdle()

    assertEquals(State.Loading, states[0])
    assertEquals(State.Success, states[1])

    job.cancel()
}

//  DO: Use currentTime to verify timing
@Test
fun goodTest() = runTest {
    val start = currentTime
    // Operations with delays
    val end = currentTime
    assertEquals(expectedDelay, end - start)
}
```

### Common Pitfalls

```kotlin
// Pitfall 1: Not waiting for coroutines
@Test
fun pitfall1() = runTest {
    launch(StandardTestDispatcher(testScheduler)) {
        // code
    }
    // Missing advanceUntilIdle()!
}

// Pitfall 2: Using wrong dispatcher
@Test
fun pitfall2() = runTest {
    // Using Dispatchers.IO instead of TestDispatcher
    withContext(Dispatchers.IO) {
        // This won't use virtual time!
    }
}

// Pitfall 3: Not canceling collection jobs
@Test
fun pitfall3() = runTest {
    launch {
        flow.collect { /* ... */ }
    }
    // Job keeps running, test might hang
}

// Pitfall 4: Mixing real time with virtual time
@Test
fun pitfall4() = runTest {
    launch {
        Thread.sleep(1000) // Actual sleep, not delay!
        // Test will actually wait 1 second
    }
}
```

### Dependencies

```gradle
// build.gradle.kts
dependencies {
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
    testImplementation("junit:junit:4.13.2")

    // For ViewModel testing
    testImplementation("androidx.arch.core:core-testing:2.2.0")
}
```

**Summary**:
- **runTest** provides TestScope with virtual time control
- **StandardTestDispatcher**: queues coroutines, requires explicit advancement
- **UnconfinedTestDispatcher**: executes eagerly until suspension
- **advanceUntilIdle()**: runs all pending coroutines
- **advanceTimeBy(ms)**: advances time by specific amount
- **runCurrent()**: executes only current scheduled tasks
- **MainDispatcherRule**: replaces Dispatchers.Main for ViewModel testing
- Use fake repositories, not mocks or real implementations
- Always cancel collection jobs to prevent test hangs

---

## Follow-ups

1. How to test Flow operators like debounce and retry with virtual time?
2. What is turbine library and how does it simplify Flow testing?
3. How to test coroutine exception handling in ViewModels?
4. What are the differences between TestScope, TestCoroutineScope (deprecated), and CoroutineScope?
5. How to test code that uses withContext(Dispatchers.IO)?

---

## References

- [Kotlin Coroutines Testing Guide](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)
- [Testing Kotlin coroutines on Android](https://developer.android.com/kotlin/coroutines/test)
- [runTest API documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/kotlinx.coroutines.test/run-test.html)

---

## Related Questions

- [[q-testing-stateflow-sharedflow--kotlin--medium]] - Testing StateFlow and SharedFlow
- [[q-testing-flow-operators--kotlin--hard]] - Testing Flow operators
- [[q-testing-coroutine-cancellation--kotlin--medium]] - Testing cancellation
- [[q-coroutine-virtual-time--kotlin--medium]] - Virtual time deep dive
- [[q-testing-viewmodels-coroutines--kotlin--medium]] - ViewModel testing patterns
