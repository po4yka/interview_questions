---
id: kotlin-106
title: "Testing Coroutines with runTest and TestDispatcher / Тестирование корутин с runTest и TestDispatcher"
aliases: ["Testing Coroutines with runTest and TestDispatcher", "Тестирование корутин с runTest и TestDispatcher"]
topic: kotlin
subtopics: [coroutines, runtest, test-dispatcher]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Testing Guide
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, q-testing-coroutine-cancellation--kotlin--medium, q-testing-flow-operators--kotlin--hard, q-testing-stateflow-sharedflow--kotlin--medium]
created: 2025-10-12
updated: 2025-11-11
tags: [coroutines, difficulty/medium, kotlin, runtest, test-dispatcher, testing]

date created: Sunday, October 12th 2025, 1:18:39 pm
date modified: Tuesday, November 25th 2025, 8:53:48 pm
---
# Вопрос (RU)
> Как тестировать корутины с `runTest` и `TestDispatcher`? Объясните виртуальное время, `StandardTestDispatcher` vs `UnconfinedTestDispatcher` и практические паттерны тестирования для `ViewModel`.

# Question (EN)
> How to test coroutines with `runTest` and `TestDispatcher`? Explain virtual time, `StandardTestDispatcher` vs `UnconfinedTestDispatcher`, and practical testing patterns for `ViewModel`s.

---

## Ответ (RU)

Тестирование корутин требует специальной инфраструктуры для контроля времени выполнения, обработки задержек без реального ожидания и обеспечения детерминированных результатов. Библиотека `kotlinx-coroutines-test` предоставляет мощные инструменты для этого.

### Проблема: Почему Обычные Тесты Не Работают

```kotlin
// Продакшн код
interface UserRepository {
    suspend fun fetchUser(id: Int): User
}

class RealUserRepository : UserRepository {
    override suspend fun fetchUser(id: Int): User {
        delay(1000) // Имитация сетевого запроса
        return User(id, "User $id")
    }
}

class UserViewModel(private val repository: UserRepository) : ViewModel() {
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
    val repository = RealUserRepository()
    val viewModel = UserViewModel(repository)

    viewModel.loadUser(1)

    // ПРОВАЛ: Корутина еще не завершилась!
    assertEquals(User(1, "User 1"), viewModel.user.value)

    // Даже с Thread.sleep(2000) тест станет медленным и нестабильным
}
```

**Проблемы**:
1. Корутины асинхронные — тест завершается до завершения корутины.
2. `delay(1000)` реально ждет 1 секунду — тесты медленные.
3. Нет контроля над порядком выполнения.
4. Нестабильные тесты из-за проблем с таймингом.

### Решение: runTest И Виртуальное Время

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `load user - правильный подход`() = runTest {
    val repository = FakeUserRepository()
    val viewModel = UserViewModel(repository)

    viewModel.loadUser(1)

    // Важно: код во viewModelScope должен выполняться на TestDispatcher,
    // например через замену Dispatchers.Main (см. MainDispatcherRule ниже).
    advanceUntilIdle()

    // runTest + TestDispatcher позволяют:
    // 1. Управлять временем (виртуальное время)
    // 2. Детерминированно дождаться завершения корутин в тестовом скоупе

    assertEquals(User(1, "User 1"), viewModel.user.value)
}

class FakeUserRepository : UserRepository {
    override suspend fun fetchUser(id: Int): User {
        delay(1000) // В runTest с тестовым диспетчером это завершится виртуально
        return User(id, "User $id")
    }
}
```

### Возможности runTest

`runTest` предоставляет:

1. `TestScope`: специальный scope для тестирования.
2. Виртуальное время: задержки (`delay`) не ждут реально, а управляются `TestScheduler`.
3. Контроль ожидания: можно детерминированно дождаться завершения корутин через `advanceUntilIdle()`, `runCurrent()` и управление временем.
4. Контроль времени: ручное продвижение через `advanceTimeBy()` и другие функции.
5. `TestDispatcher`: специальные диспетчеры, интегрированные с виртуальным временем.

Важно: `runTest` по умолчанию использует тестовый диспетчер только для корутин в своем `TestScope`. Если корутины запускаются в других скоупах или на реальных диспетчерах (`Dispatchers.IO`, не переназначенный `Dispatchers.Main`), они не будут управляться виртуальным временем и не будут автоматически ожидаться.

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `демонстрация возможностей runTest`() = runTest {
    val startTime = currentTime // Виртуальное время стартует с 0

    launch {
        delay(1000)
        println("После 1 секунды (виртуально)")
    }

    launch {
        delay(2000)
        println("После 2 секунд (виртуально)")
    }

    advanceUntilIdle()
    val endTime = currentTime

    assertTrue(endTime >= 2000) // Виртуальное время продвинулось
}
```

### Типы TestDispatcher

Существует два основных варианта `TestDispatcher`.

#### 1. StandardTestDispatcher (диспетчер По Умолчанию Для runTest)

Ставит корутины в очередь, не выполняет их немедленно и использует тестовый планировщик. Для кода после `delay` нужно явно управлять виртуальным временем.

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `StandardTestDispatcher - очередь корутин`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)

    var executed = false

    launch(dispatcher) {
        executed = true
    }

    // Корутина запланирована, но еще не выполнена
    assertFalse(executed)

    // Явно выполняем запланированные задачи на текущем времени
    runCurrent()

    // Теперь выполнилась
    assertTrue(executed)
}

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `StandardTestDispatcher с задержками`() = runTest {
    val results = mutableListOf<String>()

    val dispatcher = StandardTestDispatcher(testScheduler)

    launch(dispatcher) {
        delay(1000)
        results.add("1s")
    }

    launch(dispatcher) {
        delay(2000)
        results.add("2s")
    }

    launch(dispatcher) {
        delay(500)
        results.add("500ms")
    }

    // Пока ничего не выполнено
    assertTrue(results.isEmpty())

    advanceTimeBy(500)
    assertEquals(listOf("500ms"), results)

    advanceTimeBy(500)
    assertEquals(listOf("500ms", "1s"), results)

    advanceTimeBy(1000)
    assertEquals(listOf("500ms", "1s", "2s"), results)
}
```

**Характеристики `StandardTestDispatcher`**:
- Корутины ставятся в очередь и не запускаются немедленно.
- Код после `delay` выполняется только при продвижении виртуального времени (`advanceTimeBy`) или при выполнении всех задач (`advanceUntilIdle`).
- Предсказуемое, детерминированное выполнение.
- Удобен для тестирования кода, зависящего от времени.

#### 2. UnconfinedTestDispatcher

Выполняет корутины немедленно до первой точки приостановки; после `delay` продолжения управляются тем же тестовым планировщиком.

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `UnconfinedTestDispatcher - немедленное выполнение`() = runTest {
    val dispatcher = UnconfinedTestDispatcher(testScheduler)

    var executed = false

    launch(dispatcher) {
        executed = true
    }

    // Уже выполнилась до первой приостановки
    assertTrue(executed)
}

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `UnconfinedTestDispatcher и задержка`() = runTest {
    val dispatcher = UnconfinedTestDispatcher(testScheduler)
    val results = mutableListOf<String>()

    launch(dispatcher) {
        results.add("before delay")
        delay(1000)
        results.add("after delay")
    }

    // Выполнено до delay
    assertEquals(listOf("before delay"), results)

    // Нужно продвинуть время для кода после delay
    advanceUntilIdle()
    assertEquals(listOf("before delay", "after delay"), results)
}
```

**Характеристики `UnconfinedTestDispatcher`**:
- Выполняет код немедленно до первой приостановки.
- Часто требует меньше явных вызовов `advance*` для простых тестов.
- Удобен, когда нет сложных требований к таймингу.

### Сравнение: Standard Vs Unconfined

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `сравнение диспетчеров`() = runTest {
    val results = mutableListOf<String>()

    // StandardTestDispatcher
    val standard = StandardTestDispatcher(testScheduler)
    launch(standard) {
        results.add("standard-start")
    }

    // Пока не выполнено
    assertTrue(results.isEmpty())

    runCurrent()
    assertEquals(listOf("standard-start"), results)

    // UnconfinedTestDispatcher
    results.clear()
    val unconfined = UnconfinedTestDispatcher(testScheduler)
    launch(unconfined) {
        results.add("unconfined-start")
    }

    // Выполнено сразу
    assertEquals(listOf("unconfined-start"), results)
}
```

### Функции Контроля Виртуального Времени

#### advanceUntilIdle()

Выполняет все ожидающие задачи (включая запланированные через `delay`), пока не останется задач; виртуальное время продвигается по мере необходимости.

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `advanceUntilIdle - выполняет всё`() = runTest {
    val events = mutableListOf<String>()

    launch {
        delay(1000)
        events.add("1 секунда")
        delay(2000)
        events.add("3 секунды всего")
    }

    launch {
        delay(500)
        events.add("500 мс")
    }

    advanceUntilIdle()

    assertEquals(3, events.size)
    assertEquals(3000, currentTime)
}
```

#### advanceTimeBy(milliseconds)

Продвигает виртуальное время на указанное значение и выполняет задачи, запланированные в этом интервале.

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
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

Выполняет только задачи, запланированные на текущее виртуальное время, без продвижения времени.

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `runCurrent - только текущие задачи`() = runTest {
    val events = mutableListOf<String>()

    launch {
        events.add("immediate")
    }

    launch {
        delay(100)
        events.add("delayed")
    }

    // Выполняем только задачи на текущем времени
    runCurrent()
    assertEquals(listOf("immediate"), events)

    // Время не изменилось
    assertEquals(0, currentTime)

    // Теперь продвигаем время и запускаем отложенную задачу
    advanceTimeBy(100)
    assertEquals(listOf("immediate", "delayed"), events)
}
```

### Тестирование ViewModel

`ViewModel` обычно использует `viewModelScope` на `Dispatchers.Main`. В тестах нужно заменить `Dispatchers.Main` на `TestDispatcher`, чтобы виртуальное время `runTest` могло им управлять.

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

@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `loadUser обновляет состояние`() = runTest {
        val repository = FakeUserRepository()
        val viewModel = UserViewModel(repository)

        viewModel.loadUser(1)
        advanceUntilIdle()

        // Теперь viewModelScope использует тестовый Main-диспетчер
        assertEquals(User(1, "User 1"), viewModel.user.value)
    }
}
```

#### Полный Пример Тестирования ViewModel

```kotlin
sealed class UiState<out T> {
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
class UserViewModelStateTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var repository: ConfigurableFakeUserRepository
    private lateinit var viewModel: UserViewModel

    @Before
    fun setup() {
        repository = ConfigurableFakeUserRepository()
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
        advanceUntilIdle()

        assertTrue(viewModel.uiState.value is UiState.Success)
        assertEquals(User(1, "John"), (viewModel.uiState.value as UiState.Success).data)
    }

    @Test
    fun `loadUser failure updates state to Error`() = runTest {
        repository.setResult(Result.failure(IOException("Network error")))

        viewModel.loadUser(1)
        advanceUntilIdle()

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

        assertTrue(viewModel.uiState.value is UiState.Success)
        assertEquals(3, (viewModel.uiState.value as UiState.Success).data.id)
    }
}

class ConfigurableFakeUserRepository : UserRepository {
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
        return result.getOrElse { throw it }.copy(id = id)
    }
}
```

### Тестирование Задержек И Таймаутов

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

@OptIn(ExperimentalCoroutinesApi::class)
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

interface Repository {
    suspend fun fetchData(): Data
}

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

class FakeRepository(private val delayMs: Long = 0, private val shouldFail: Boolean = false) : Repository {
    override suspend fun fetchData(): Data {
        if (delayMs > 0) delay(delayMs)
        if (shouldFail) throw IOException("failure")
        return Data()
    }
}

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `loadWithTimeout succeeds when data arrives in time`() = runTest {
    val repository = FakeRepository(delayMs = 500)
    val loader = DataLoader(repository)

    val result = loader.loadWithTimeout(1000)

    assertTrue(result.isSuccess)
}

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `loadWithTimeout fails when data takes too long`() = runTest {
    val repository = FakeRepository(delayMs = 2000)
    val loader = DataLoader(repository)

    val result = loader.loadWithTimeout(1000)

    assertTrue(result.isFailure)
    assertTrue(result.exceptionOrNull() is TimeoutCancellationException)
}
```

### Тестирование Параллельных Операций

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
        val userDeferred = async { userRepo.fetchUser(1) }
        val statsDeferred = async { statsRepo.getStats() }
        val notificationsDeferred = async { notificationsRepo.getNotifications() }

        Dashboard(
            user = userDeferred.await(),
            stats = statsDeferred.await(),
            notifications = notificationsDeferred.await()
        )
    }
}

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `loadDashboard загружает данные параллельно`() = runTest {
    val userRepo = object : UserRepository {
        override suspend fun fetchUser(id: Int): User { delay(100); return User(id, "User $id") }
    }
    val statsRepo = FakeStatsRepository(delayMs = 100)
    val notificationsRepo = FakeNotificationsRepository(delayMs = 100)

    val viewModel = DashboardViewModel(userRepo, statsRepo, notificationsRepo)

    val startTime = currentTime
    val dashboard = viewModel.loadDashboard()
    val endTime = currentTime

    assertNotNull(dashboard.user)
    assertNotNull(dashboard.stats)
    assertNotNull(dashboard.notifications)

    // Параллельное выполнение во времени runTest: ~100ms вместо 300ms
    assertTrue(endTime - startTime <= 100)
}

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `loadDashboard падает при ошибке репозитория`() = runTest {
    val userRepo = object : UserRepository {
        override suspend fun fetchUser(id: Int): User = User(id, "User $id")
    }
    val statsRepo = FakeStatsRepository(shouldFail = true)
    val notificationsRepo = FakeNotificationsRepository()

    val viewModel = DashboardViewModel(userRepo, statsRepo, notificationsRepo)

    var thrown: Throwable? = null
    try {
        viewModel.loadDashboard()
    } catch (e: Throwable) {
        thrown = e
    }

    assertTrue(thrown is Exception)
}
```

### Тестирование Отмены

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

@OptIn(ExperimentalCoroutinesApi::class)
class SearchViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `новый запрос отменяет предыдущий`() = runTest {
        val repository = FakeSearchRepository()
        val viewModel = SearchViewModel(repository)

        viewModel.search("query1")
        advanceTimeBy(100)

        viewModel.search("query2")
        advanceUntilIdle()

        // Выполнен только последний запрос
        assertEquals(1, repository.searchCount)
        assertEquals("query2", repository.lastQuery)
    }

    @Test
    fun `debounce предотвращает лишние запросы`() = runTest {
        val repository = FakeSearchRepository()
        val viewModel = SearchViewModel(repository)

        viewModel.search("a")
        advanceTimeBy(100)

        viewModel.search("ab")
        advanceTimeBy(100)

        viewModel.search("abc")
        advanceTimeBy(100)

        viewModel.search("abcd")
        advanceTimeBy(300) // Debounce завершился

        // Выполнен только последний поиск
        assertEquals(1, repository.searchCount)
        assertEquals("abcd", repository.lastQuery)
    }
}
```

### Тестирование Flow

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `коллекция эмиссий Flow во времени`() = runTest {
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

    runCurrent() // Первая эмиссия
    assertEquals(listOf(1), emissions)

    advanceTimeBy(100)
    assertEquals(listOf(1, 2), emissions)

    advanceTimeBy(100)
    assertEquals(listOf(1, 2, 3), emissions)

    job.cancel()
}

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `коллекция с take`() = runTest {
    val flow = flow {
        repeat(10) {
            emit(it)
            delay(100)
        }
    }

    val emissions = flow.take(3).toList()

    assertEquals(listOf(0, 1, 2), emissions)
    assertEquals(200, currentTime)
}
```

### Лучшие Практики

```kotlin
// DO: используйте runTest для unit-тестов корутин
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun goodTest() = runTest {
    // Test code
}

// DON'T: использовать runBlocking, когда нужно виртуальное время
@Test
fun badTest() = runBlocking { // Медленно, без виртуального времени
    delay(1000)
}

// DO: используйте MainDispatcherRule для ViewModel
class ViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()
}

// DON'T: забывать устанавливать Main для viewModelScope
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun badViewModelTest() = runTest {
    val viewModel = MyViewModel() // Может упасть: Dispatchers.Main не задан!
}

// DO: используйте fake-репозитории
class FakeRepositoryImpl : Repository {
    var result: Result<Data> = Result.success(Data())
    override suspend fun fetchData(): Data = result.getOrThrow()
}

// DON'T: использовать реальные репозитории (сеть/БД) в unit-тестах
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun badRealRepoTest() = runTest {
    val repo = RealRepository(apiService)
}

// DO: явно продвигать время со StandardTestDispatcher
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun goodTimeTest() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    var done = false

    launch(dispatcher) { delay(100); done = true }

    assertFalse(done)
    advanceTimeBy(100)
    assertTrue(done)
}

// DON'T: считать, что StandardTestDispatcher выполняет сразу
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun badAssumptionTest() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    var done = false

    launch(dispatcher) { done = true }

    // Без runCurrent/advanceUntilIdle корутина не выполнится сразу
    assertFalse(done)
}

// DO: тестировать последовательности состояний
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun goodStateSequenceTest() = runTest {
    val states = mutableListOf<State>()
    val job = launch { viewModel.state.collect { states.add(it) } }

    viewModel.loadData()
    advanceUntilIdle()

    assertEquals(State.Loading, states[0])
    assertEquals(State.Success, states[1])

    job.cancel()
}

// DO: использовать currentTime для проверки тайминга
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun goodTimingTest() = runTest {
    val start = currentTime
    delay(500)
    val end = currentTime
    assertEquals(500, end - start)
}
```

### Частые Ошибки

```kotlin
// Ошибка 1: не ждать выполнения корутин с TestDispatcher
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun pitfall1() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    launch(dispatcher) {
        // code
    }
    // Нет runCurrent/advanceUntilIdle: корутина может не выполниться
}

// Ошибка 2: использование реальных диспетчеров
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun pitfall2() = runTest {
    withContext(Dispatchers.IO) {
        // Не использует виртуальное время; лучше внедрять диспетчер через абстракцию
        // и подменять его на TestDispatcher в тестах.
    }
}

// Ошибка 3: не отменять collect jobs
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun pitfall3() = runTest {
    val job = launch {
        flow.collect { /* ... */ }
    }
    // Если не отменить, тест может зависнуть
    job.cancel()
}

// Ошибка 4: смешивание реального и виртуального времени
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun pitfall4() = runTest {
    launch {
        Thread.sleep(1000) // Реальная задержка, а не виртуальная
    }
}
```

### Резюме

- `runTest` предоставляет `TestScope` с управляемым виртуальным временем.
- `StandardTestDispatcher` ставит задачи в очередь и требует явного продвижения времени.
- `UnconfinedTestDispatcher` выполняет до первой приостановки сразу и упрощает простые тесты.
- `advanceUntilIdle()` выполняет все ожидающие задачи.
- `advanceTimeBy(ms)` продвигает виртуальное время на заданное значение.
- `runCurrent()` выполняет задачи на текущем виртуальном времени.
- `MainDispatcherRule` заменяет `Dispatchers.Main`, делая `viewModelScope` тестируемым.
- Используйте фейковые репозитории и внедрение диспетчеров; избегайте реальных I/O в unit-тестах.
- Отменяйте долгоживущие `collect`-job'ы.

---

## Answer (EN)

Testing coroutines requires special infrastructure to control execution timing, handle delays without actually waiting, and ensure deterministic results. The `kotlinx-coroutines-test` library provides the tools for this.

### The Problem: Why Regular Tests Fail

```kotlin
// Production code
interface UserRepository {
    suspend fun fetchUser(id: Int): User
}

class RealUserRepository : UserRepository {
    override suspend fun fetchUser(id: Int): User {
        delay(1000) // Simulate network call
        return User(id, "User $id")
    }
}

class UserViewModel(private val repository: UserRepository) : ViewModel() {
    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()

    fun loadUser(id: Int) {
        viewModelScope.launch {
            val result = repository.fetchUser(id)
            _user.value = result
        }
    }
}

//  WRONG: Test will fail or be slow/flaky
@Test
fun `load user - wrong approach`() {
    val repository = RealUserRepository()
    val viewModel = UserViewModel(repository)

    viewModel.loadUser(1)

    // FAILS: Coroutine hasn't completed yet!
    assertEquals(User(1, "User 1"), viewModel.user.value)

    // Even with Thread.sleep(2000), tests become slow and brittle
}
```

**Problems**:
1. Coroutines are asynchronous — the test may finish before the coroutine.
2. `delay(1000)` really waits 1 second — tests are slow.
3. No control over execution order.
4. Flaky tests due to timing issues.

### Solution: runTest and Virtual Time

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `load user - correct approach`() = runTest {
    val repository = FakeUserRepository()
    val viewModel = UserViewModel(repository)

    viewModel.loadUser(1)

    // Important: viewModelScope must use a TestDispatcher,
    // typically by overriding Dispatchers.Main (see MainDispatcherRule below).
    advanceUntilIdle()

    assertEquals(User(1, "User 1"), viewModel.user.value)
}

class FakeUserRepository : UserRepository {
    override suspend fun fetchUser(id: Int): User {
        delay(1000) // With TestDispatcher this completes via virtual time
        return User(id, "User $id")
    }
}
```

### runTest Features

`runTest` provides:

1. `TestScope`: a dedicated coroutine scope for testing.
2. Virtual time: `delay` is controlled by a `TestScheduler` instead of real time.
3. Deterministic waiting: you can reliably wait for coroutines in the test scope using `advanceUntilIdle()`, `runCurrent()`, and time control APIs.
4. Time control: manual advancement via `advanceTimeBy()` and related functions.
5. Test dispatchers: `StandardTestDispatcher` and `UnconfinedTestDispatcher` integrated with virtual time.

Note: `runTest` only fully controls coroutines launched in its own scope (or on dispatchers that use its `TestScheduler`). Coroutines running on real dispatchers like `Dispatchers.IO` or an unpatched `Dispatchers.Main` are not controlled by virtual time and are not automatically awaited.

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
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

    advanceUntilIdle()
    val endTime = currentTime

    assertTrue(endTime >= 2000) // Virtual time advanced
}
```

### TestDispatcher Types

There are two main `TestDispatcher` implementations used here.

#### 1. StandardTestDispatcher (default for runTest)

Schedules coroutines, does not run them immediately, and relies on the test scheduler. For code after `delay`, you must use virtual time control.

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `StandardTestDispatcher - queues coroutines`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)

    var executed = false

    launch(dispatcher) {
        executed = true
    }

    // Coroutine is queued, not executed yet
    assertFalse(executed)

    // Run tasks scheduled at current time
    runCurrent()

    // Now it has executed
    assertTrue(executed)
}

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `StandardTestDispatcher with delays`() = runTest {
    val results = mutableListOf<String>()

    val dispatcher = StandardTestDispatcher(testScheduler)

    launch(dispatcher) {
        delay(1000)
        results.add("1s")
    }

    launch(dispatcher) {
        delay(2000)
        results.add("2s")
    }

    launch(dispatcher) {
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
- Coroutines are queued, not run immediately.
- Code after `delay` runs only when virtual time is advanced (`advanceTimeBy`) or when all tasks are processed (`advanceUntilIdle`).
- Predictable, deterministic execution.
- Great for timing-sensitive tests.

#### 2. UnconfinedTestDispatcher

Executes coroutines eagerly until the first suspension point; after that, continuations are scheduled with the same test scheduler.

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `UnconfinedTestDispatcher - immediate execution`() = runTest {
    val dispatcher = UnconfinedTestDispatcher(testScheduler)

    var executed = false

    launch(dispatcher) {
        executed = true
    }

    // Already executed up to first suspension
    assertTrue(executed)
}

@OptIn(ExperimentalCoroutinesApi::class)
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
```

**UnconfinedTestDispatcher characteristics**:
- Executes eagerly until the first suspension.
- Often fewer explicit time advancements for simple tests.
- Good for tests not heavily dependent on precise timing.

### Comparison: Standard Vs Unconfined

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
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

    runCurrent()
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

Executes all pending tasks until no more are scheduled; virtual time may advance as needed.

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
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

Advances virtual time by the given amount and executes tasks scheduled within that window.

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
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

Runs only tasks scheduled for the current virtual time (without advancing time).

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
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

`ViewModel` usually uses `viewModelScope` running on `Dispatchers.Main`. In tests, we must replace `Dispatchers.Main` with a `TestDispatcher` so that `runTest` virtual time can control `viewModelScope`.

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

@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `loadUser updates state`() = runTest {
        val repository = FakeUserRepository()
        val viewModel = UserViewModel(repository)

        viewModel.loadUser(1)
        advanceUntilIdle()

        // viewModelScope now uses test dispatcher bound to virtual Main
        assertEquals(User(1, "User 1"), viewModel.user.value)
    }
}
```

#### Complete ViewModel Test Example

```kotlin
sealed class UiState<out T> {
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
class UserViewModelStateTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var repository: ConfigurableFakeUserRepository
    private lateinit var viewModel: UserViewModel

    @Before
    fun setup() {
        repository = ConfigurableFakeUserRepository()
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
        advanceUntilIdle()

        assertTrue(viewModel.uiState.value is UiState.Success)
        assertEquals(User(1, "John"), (viewModel.uiState.value as UiState.Success).data)
    }

    @Test
    fun `loadUser failure updates state to Error`() = runTest {
        repository.setResult(Result.failure(IOException("Network error")))

        viewModel.loadUser(1)
        advanceUntilIdle()

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

        assertTrue(viewModel.uiState.value is UiState.Success)
        assertEquals(3, (viewModel.uiState.value as UiState.Success).data.id)
    }
}

class ConfigurableFakeUserRepository : UserRepository {
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
        return result.getOrElse { throw it }.copy(id = id)
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

@OptIn(ExperimentalCoroutinesApi::class)
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

interface Repository {
    suspend fun fetchData(): Data
}

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

class FakeRepository(private val delayMs: Long = 0, private val shouldFail: Boolean = false) : Repository {
    override suspend fun fetchData(): Data {
        if (delayMs > 0) delay(delayMs)
        if (shouldFail) throw IOException("failure")
        return Data()
    }
}

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `loadWithTimeout succeeds when data arrives in time`() = runTest {
    val repository = FakeRepository(delayMs = 500)
    val loader = DataLoader(repository)

    val result = loader.loadWithTimeout(1000)

    assertTrue(result.isSuccess)
}

@OptIn(ExperimentalCoroutinesApi::class)
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
        val userDeferred = async { userRepo.fetchUser(1) }
        val statsDeferred = async { statsRepo.getStats() }
        val notificationsDeferred = async { notificationsRepo.getNotifications() }

        Dashboard(
            user = userDeferred.await(),
            stats = statsDeferred.await(),
            notifications = notificationsDeferred.await()
        )
    }
}

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `loadDashboard loads all data in parallel`() = runTest {
    val userRepo = object : UserRepository {
        override suspend fun fetchUser(id: Int): User { delay(100); return User(id, "User $id") }
    }
    val statsRepo = FakeStatsRepository(delayMs = 100)
    val notificationsRepo = FakeNotificationsRepository(delayMs = 100)

    val viewModel = DashboardViewModel(userRepo, statsRepo, notificationsRepo)

    val startTime = currentTime
    val dashboard = viewModel.loadDashboard()
    val endTime = currentTime

    assertNotNull(dashboard.user)
    assertNotNull(dashboard.stats)
    assertNotNull(dashboard.notifications)

    // Parallel execution under virtual time: ~100ms instead of 300ms
    assertTrue(endTime - startTime <= 100)
}

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun `loadDashboard fails if any repo fails`() = runTest {
    val userRepo = object : UserRepository {
        override suspend fun fetchUser(id: Int): User = User(id, "User $id")
    }
    val statsRepo = FakeStatsRepository(shouldFail = true)
    val notificationsRepo = FakeNotificationsRepository()

    val viewModel = DashboardViewModel(userRepo, statsRepo, notificationsRepo)

    var thrown: Throwable? = null
    try {
        viewModel.loadDashboard()
    } catch (e: Throwable) {
        thrown = e
    }

    assertTrue(thrown is Exception)
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

@OptIn(ExperimentalCoroutinesApi::class)
class SearchViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

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
}
```

### Testing Flow Collection

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
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

@OptIn(ExperimentalCoroutinesApi::class)
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
    assertEquals(200, currentTime) // Only waited for 3 emissions virtually
}
```

### Best Practices

```kotlin
//  DO: Use runTest for coroutine unit tests
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun goodTest() = runTest {
    // Test code
}

//  DON'T: Use runBlocking in tests when virtual time is needed
@Test
fun badTest() = runBlocking { // Slow, doesn't use virtual time
    delay(1000) // Actually waits 1 second!
}

//  DO: Use MainDispatcherRule for ViewModels
class ViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()
}

//  DON'T: Forget to set Main dispatcher for code using viewModelScope
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun badViewModelTest() = runTest {
    val viewModel = MyViewModel() // May crash: Dispatchers.Main not set!
}

//  DO: Use fake repositories
class FakeRepositoryImpl : Repository {
    var result: Result<Data> = Result.success(Data())
    override suspend fun fetchData(): Data = result.getOrThrow()
}

//  DON'T: Use real repositories (network/DB) in unit tests
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun badRealRepoTest() = runTest {
    val repo = RealRepository(apiService) // Real network calls in unit tests!
}

//  DO: Advance time explicitly with StandardTestDispatcher for delayed code
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun goodTimeTest() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    var done = false

    launch(dispatcher) { delay(100); done = true }

    assertFalse(done)
    advanceTimeBy(100)
    assertTrue(done)
}

//  DON'T: Assume immediate execution with StandardTestDispatcher
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun badAssumptionTest() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    var done = false

    launch(dispatcher) { done = true }

    // Wrong: coroutine not run yet without runCurrent/advanceUntilIdle
    assertFalse(done)
}

//  DO: Test state sequences
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun goodStateSequenceTest() = runTest {
    val states = mutableListOf<State>()
    val job = launch { viewModel.state.collect { states.add(it) } }

    viewModel.loadData()
    advanceUntilIdle()

    assertEquals(State.Loading, states[0])
    assertEquals(State.Success, states[1])

    job.cancel()
}

//  DO: Use currentTime to verify timing
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun goodTimingTest() = runTest {
    val start = currentTime
    delay(500)
    val end = currentTime
    assertEquals(500, end - start)
}
```

### Common Pitfalls

```kotlin
// Pitfall 1: Not waiting for coroutines with TestDispatcher
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun pitfall1() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    launch(dispatcher) {
        // code
    }
    // Missing runCurrent/advanceUntilIdle(): coroutine may not run
}

// Pitfall 2: Using real dispatchers instead of TestDispatcher
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun pitfall2() = runTest {
    withContext(Dispatchers.IO) {
        // This won't use virtual time. Prefer injecting dispatcher (e.g., via constructor)
        // and substituting it with a TestDispatcher in tests.
    }
}

// Pitfall 3: Not canceling collection jobs
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun pitfall3() = runTest {
    val job = launch {
        flow.collect { /* ... */ }
    }
    // If job is not canceled, test may hang
    job.cancel()
}

// Pitfall 4: Mixing real time with virtual time
@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun pitfall4() = runTest {
    launch {
        Thread.sleep(1000) // Actual sleep, NOT virtual; avoid in tests using runTest
    }
}
```

Summary:
- `runTest` provides a `TestScope` with virtual-time control.
- `StandardTestDispatcher`: queues tasks, requires scheduler control for delayed code.
- `UnconfinedTestDispatcher`: runs eagerly until suspension; simpler but less explicit.
- `advanceUntilIdle()`: runs all pending tasks.
- `advanceTimeBy(ms)`: advances virtual time by a given amount.
- `runCurrent()`: runs tasks at the current virtual time.
- `MainDispatcherRule`: replaces `Dispatchers.Main` so `viewModelScope` is testable.
- Prefer fake repositories and injected dispatchers; avoid real I/O.
- Always cancel long-lived collection jobs.

---

## Дополнительные Вопросы (RU)

1. Как тестировать операторы `Flow` вроде `debounce`, `buffer` и `retry` с использованием виртуального времени `runTest` и `TestDispatcher`?
2. Как библиотека Turbine упрощает тестирование холодных `Flow` и горячих `StateFlow`/`SharedFlow`?
3. Как лучше структурировать код `ViewModel`, чтобы обработку исключений в корутинах было проще тестировать с помощью `runTest`?
4. В чем различия между `TestScope`, устаревшим `TestCoroutineScope` и обычным `CoroutineScope` в тестах?
5. Как тестировать код, использующий `withContext(Dispatchers.IO)` или другие реальные диспетчеры, сохраняя контроль виртуального времени?

## Follow-ups

1. How to test `Flow` operators like `debounce`, `buffer`, and `retry` with virtual time using `runTest` and `TestDispatcher`?
2. How does the Turbine library help in testing cold `Flow` and hot `StateFlow`/`SharedFlow` streams?
3. How to structure `ViewModel` code to make coroutine exception handling easily testable with `runTest`?
4. What are the differences between `TestScope`, deprecated `TestCoroutineScope`, and a regular `CoroutineScope` in tests?
5. How to test code that uses `withContext(Dispatchers.IO)` or other real dispatchers while preserving virtual time control?

---

## Ссылки (RU)

- [[c-kotlin]]
- [[c-coroutines]]
- Официальная документация по тестированию корутин: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/
- Статья "Testing Kotlin coroutines on Android": https://developer.android.com/kotlin/coroutines/test

## References

- [[c-kotlin]]
- [[c-coroutines]]
- Kotlin Coroutines Testing Guide: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/
- Testing Kotlin coroutines on Android: https://developer.android.com/kotlin/coroutines/test
- `runTest` API documentation: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/kotlinx.coroutines.test/run-test.html

---

## Связанные Вопросы (RU)

- [[q-testing-stateflow-sharedflow--kotlin--medium]] — Тестирование `StateFlow` и `SharedFlow`
- [[q-testing-flow-operators--kotlin--hard]] — Тестирование операторов `Flow`
- [[q-testing-coroutine-cancellation--kotlin--medium]] — Тестирование отмены корутин
- [[q-coroutine-virtual-time--kotlin--medium]] — Виртуальное время в корутинах
- [[q-testing-viewmodels-coroutines--kotlin--medium]] — Паттерны тестирования `ViewModel` с корутинами

## Related Questions

- [[q-testing-stateflow-sharedflow--kotlin--medium]] - Testing `StateFlow` and `SharedFlow`
- [[q-testing-flow-operators--kotlin--hard]] - Testing `Flow` operators
- [[q-testing-coroutine-cancellation--kotlin--medium]] - Testing cancellation
- [[q-coroutine-virtual-time--kotlin--medium]] - Virtual time deep dive
- [[q-testing-viewmodels-coroutines--kotlin--medium]] - `ViewModel` testing patterns
