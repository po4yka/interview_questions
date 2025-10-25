---
id: 20251012-122711121
title: "Unit Testing Coroutines Flow"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-service-types-android--android--easy, q-what-do-you-know-about-modifiers--programming-languages--medium, q-how-to-create-animations-in-android--android--medium]
created: 2025-10-15
tags: [testing, coroutines, flow, unit-testing, turbine, mockk, difficulty/medium]
---
# Unit Testing with Coroutines and Flow

# Вопрос (RU)
>

---

## Answer (EN)
# Question (EN)
How do you write unit tests for Kotlin Coroutines and Flow? What are the best practices and common pitfalls?

## Answer (EN)
Testing coroutines and Flow requires special consideration for asynchronous operations, test dispatchers, and timing control. Proper testing ensures code reliability and maintainability.

#### 1. **Setup and Dependencies**

```kotlin
// build.gradle.kts
dependencies {
    // Testing dependencies
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
    testImplementation("app.cash.turbine:turbine:1.0.0")
    testImplementation("io.mockk:mockk:1.13.8")
    testImplementation("com.google.truth:truth:1.1.5")

    // For Android-specific tests
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test:runner:1.5.2")
}
```

#### 2. **Testing Suspend Functions**

```kotlin
// ViewModel with suspend function
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()

    suspend fun loadUser(userId: String) {
        val user = repository.getUser(userId)
        _user.value = user
    }
}

// Test
class UserViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var repository: UserRepository
    private lateinit var viewModel: UserViewModel

    @Before
    fun setup() {
        repository = mockk()
        viewModel = UserViewModel(repository)
    }

    @Test
    fun `loadUser updates user state`() = runTest {
        // Given
        val expectedUser = User("1", "John Doe")
        coEvery { repository.getUser("1") } returns expectedUser

        // When
        viewModel.loadUser("1")

        // Then
        assertEquals(expectedUser, viewModel.user.value)
    }

    @Test
    fun `loadUser handles error`() = runTest {
        // Given
        coEvery { repository.getUser("1") } throws NetworkException()

        // When & Then
        assertThrows<NetworkException> {
            viewModel.loadUser("1")
        }
    }
}

// MainDispatcherRule for testing
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
```

#### 3. **Testing Flow**

**3.1 Basic Flow Testing**

```kotlin
// Repository with Flow
class ArticleRepository(private val apiService: ApiService) {

    fun getArticlesFlow(): Flow<List<Article>> = flow {
        val articles = apiService.getArticles()
        emit(articles)
    }

    fun observeArticles(): Flow<List<Article>> = flow {
        while (currentCoroutineContext().isActive) {
            val articles = apiService.getArticles()
            emit(articles)
            delay(5000)
        }
    }
}

// Test with collect
class ArticleRepositoryTest {

    private lateinit var apiService: ApiService
    private lateinit var repository: ArticleRepository

    @Before
    fun setup() {
        apiService = mockk()
        repository = ArticleRepository(apiService)
    }

    @Test
    fun `getArticlesFlow emits articles`() = runTest {
        // Given
        val expectedArticles = listOf(
            Article("1", "Title 1"),
            Article("2", "Title 2")
        )
        coEvery { apiService.getArticles() } returns expectedArticles

        // When
        val result = repository.getArticlesFlow().first()

        // Then
        assertEquals(expectedArticles, result)
    }

    @Test
    fun `getArticlesFlow emits multiple values`() = runTest {
        // Given
        val articles1 = listOf(Article("1", "First"))
        val articles2 = listOf(Article("2", "Second"))

        coEvery { apiService.getArticles() } returnsMany listOf(articles1, articles2)

        // When
        val results = repository.observeArticles()
            .take(2)
            .toList()

        // Then
        assertEquals(2, results.size)
        assertEquals(articles1, results[0])
        assertEquals(articles2, results[1])
    }
}
```

**3.2 Testing with Turbine**

```kotlin
// Turbine provides cleaner Flow testing API
class ArticleRepositoryTurbineTest {

    @Test
    fun `getArticlesFlow emits articles`() = runTest {
        // Given
        val expectedArticles = listOf(Article("1", "Title"))
        coEvery { apiService.getArticles() } returns expectedArticles

        // When & Then
        repository.getArticlesFlow().test {
            val item = awaitItem()
            assertEquals(expectedArticles, item)
            awaitComplete()
        }
    }

    @Test
    fun `observeArticles emits multiple values with delay`() = runTest {
        // Given
        val articles1 = listOf(Article("1", "First"))
        val articles2 = listOf(Article("2", "Second"))

        coEvery { apiService.getArticles() } returnsMany listOf(articles1, articles2)

        // When & Then
        repository.observeArticles().test {
            assertEquals(articles1, awaitItem())

            // Advance time by 5 seconds
            testScheduler.advanceTimeBy(5000)

            assertEquals(articles2, awaitItem())

            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `flow handles errors`() = runTest {
        // Given
        coEvery { apiService.getArticles() } throws NetworkException()

        // When & Then
        repository.getArticlesFlow().test {
            val error = awaitError()
            assertTrue(error is NetworkException)
        }
    }
}
```

#### 4. **Testing StateFlow and SharedFlow**

```kotlin
// ViewModel with StateFlow
class SearchViewModel(
    private val repository: SearchRepository
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    private val _searchResults = MutableStateFlow<List<Result>>(emptyList())
    val searchResults: StateFlow<List<Result>> = _searchResults.asStateFlow()

    init {
        viewModelScope.launch {
            searchQuery
                .debounce(300)
                .distinctUntilChanged()
                .filter { it.length >= 2 }
                .flatMapLatest { query ->
                    repository.search(query)
                }
                .collect { results ->
                    _searchResults.value = results
                }
        }
    }

    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
    }
}

// Test
class SearchViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var repository: SearchRepository
    private lateinit var viewModel: SearchViewModel

    @Before
    fun setup() {
        repository = mockk()
        viewModel = SearchViewModel(repository)
    }

    @Test
    fun `search query updates trigger repository search`() = runTest {
        // Given
        val expectedResults = listOf(Result("1", "Test"))
        coEvery { repository.search("test") } returns flowOf(expectedResults)

        // When
        viewModel.searchResults.test {
            // Initial empty state
            assertEquals(emptyList<Result>(), awaitItem())

            // Update search query
            viewModel.onSearchQueryChanged("test")

            // Advance time past debounce
            testScheduler.advanceTimeBy(400)

            // Then
            assertEquals(expectedResults, awaitItem())
        }
    }

    @Test
    fun `debounce prevents excessive API calls`() = runTest {
        // Given
        coEvery { repository.search(any()) } returns flowOf(emptyList())

        // When
        viewModel.onSearchQueryChanged("t")
        testScheduler.advanceTimeBy(100)

        viewModel.onSearchQueryChanged("te")
        testScheduler.advanceTimeBy(100)

        viewModel.onSearchQueryChanged("tes")
        testScheduler.advanceTimeBy(100)

        viewModel.onSearchQueryChanged("test")
        testScheduler.advanceTimeBy(400)

        // Then - only one call after debounce
        coVerify(exactly = 1) { repository.search("test") }
    }

    @Test
    fun `short queries are filtered out`() = runTest {
        // When
        viewModel.onSearchQueryChanged("a") // Too short
        testScheduler.advanceTimeBy(400)

        // Then
        coVerify(exactly = 0) { repository.search(any()) }
    }
}
```

#### 5. **Testing with Different Dispatchers**

```kotlin
// Code using specific dispatchers
class DataProcessor(
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO,
    private val defaultDispatcher: CoroutineDispatcher = Dispatchers.Default
) {
    suspend fun processData(data: List<Int>): ProcessedData {
        // IO operation
        val loadedData = withContext(ioDispatcher) {
            loadFromDatabase(data)
        }

        // CPU-intensive operation
        return withContext(defaultDispatcher) {
            compute(loadedData)
        }
    }
}

// Test with TestDispatchers
class DataProcessorTest {

    private val testDispatcher = StandardTestDispatcher()

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `processData uses correct dispatchers`() = runTest(testDispatcher) {
        // Given
        val processor = DataProcessor(
            ioDispatcher = testDispatcher,
            defaultDispatcher = testDispatcher
        )

        // When
        val result = processor.processData(listOf(1, 2, 3))

        // Then
        assertNotNull(result)
        // All operations ran on testDispatcher
    }

    @Test
    fun `UnconfinedTestDispatcher executes immediately`() = runTest(UnconfinedTestDispatcher()) {
        // Executes coroutines eagerly
        // Good for testing without time control
        var executed = false

        launch {
            executed = true
        }

        // Executes immediately, no need to advance time
        assertTrue(executed)
    }

    @Test
    fun `StandardTestDispatcher requires advancing time`() = runTest(StandardTestDispatcher()) {
        // Requires manual time control
        var executed = false

        launch {
            delay(1000)
            executed = false
        }

        // Not executed yet
        assertFalse(executed)

        // Advance time
        testScheduler.advanceTimeBy(1000)
        testScheduler.runCurrent()

        // Now executed
        assertTrue(executed)
    }
}
```

#### 6. **Testing Timeout and Cancellation**

```kotlin
// Function with timeout
class TimeoutExample {
    suspend fun fetchWithTimeout(url: String): String {
        return withTimeout(5000) {
            apiService.fetch(url)
        }
    }

    suspend fun cancellableOperation(): Result {
        return withContext(Dispatchers.IO) {
            repeat(100) { iteration ->
                ensureActive() // Check for cancellation
                processItem(iteration)
            }
            Result.Success
        }
    }
}

// Test
class TimeoutExampleTest {

    @Test
    fun `fetchWithTimeout completes within timeout`() = runTest {
        // Given
        coEvery { apiService.fetch(any()) } coAnswers {
            delay(2000)
            "Success"
        }

        // When
        val result = timeoutExample.fetchWithTimeout("url")

        // Advance time
        testScheduler.advanceTimeBy(2000)

        // Then
        assertEquals("Success", result)
    }

    @Test
    fun `fetchWithTimeout throws on timeout`() = runTest {
        // Given
        coEvery { apiService.fetch(any()) } coAnswers {
            delay(10000) // Longer than timeout
            "Success"
        }

        // When & Then
        assertThrows<TimeoutCancellationException> {
            timeoutExample.fetchWithTimeout("url")
            testScheduler.advanceTimeBy(6000)
        }
    }

    @Test
    fun `cancellableOperation respects cancellation`() = runTest {
        // Given
        val job = launch {
            timeoutExample.cancellableOperation()
        }

        // When
        testScheduler.advanceTimeBy(100)
        job.cancel()

        // Then
        assertTrue(job.isCancelled)
    }
}
```

#### 7. **Testing Cold vs Hot Flows**

```kotlin
// Cold Flow - emits from start for each collector
fun coldFlow(): Flow<Int> = flow {
    println("Cold flow started")
    repeat(3) {
        delay(100)
        emit(it)
    }
}

// Hot Flow - shared between collectors
class HotFlowExample {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    fun emitEvent(event: Event) {
        viewModelScope.launch {
            _events.emit(event)
        }
    }
}

// Tests
class FlowTypeTest {

    @Test
    fun `cold flow starts from beginning for each collector`() = runTest {
        val flow = coldFlow()

        // First collector
        flow.take(2).test {
            assertEquals(0, awaitItem())
            assertEquals(1, awaitItem())
            awaitComplete()
        }

        // Second collector - starts from beginning
        flow.take(2).test {
            assertEquals(0, awaitItem()) // Starts at 0, not 2
            assertEquals(1, awaitItem())
            awaitComplete()
        }
    }

    @Test
    fun `hot flow shares emissions between collectors`() = runTest {
        val hotFlowExample = HotFlowExample()

        // Start collecting
        val job = launch {
            hotFlowExample.events.test {
                assertEquals(Event.Click, awaitItem())
                assertEquals(Event.Scroll, awaitItem())
                cancelAndIgnoreRemainingEvents()
            }
        }

        // Emit events
        hotFlowExample.emitEvent(Event.Click)
        hotFlowExample.emitEvent(Event.Scroll)

        job.join()
    }

    @Test
    fun `hot flow with replay buffer`() = runTest {
        val flow = MutableSharedFlow<Int>(replay = 2)

        // Emit before collecting
        flow.emit(1)
        flow.emit(2)
        flow.emit(3)

        // New collector receives last 2 values
        flow.test {
            assertEquals(2, awaitItem()) // Replay buffer
            assertEquals(3, awaitItem()) // Replay buffer
            expectNoEvents()
        }
    }
}
```

#### 8. **Best Practices**

```kotlin
// - Use TestDispatchers
@get:Rule
val mainDispatcherRule = MainDispatcherRule()

// - Use runTest for coroutine tests
@Test
fun test() = runTest {
    // Test code
}

// - Use Turbine for Flow testing
flow.test {
    assertEquals(expected, awaitItem())
    awaitComplete()
}

// - Inject dispatchers for testability
class MyViewModel(
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO
) {
    fun loadData() = viewModelScope.launch(dispatcher) {
        // ...
    }
}

// - Test error cases
@Test
fun `handles error gracefully`() = runTest {
    coEvery { repository.getData() } throws NetworkException()

    flow.test {
        awaitError()
    }
}

// - Verify timing with virtual time
@Test
fun `debounce timing`() = runTest {
    viewModel.onInput("test")
    testScheduler.advanceTimeBy(100) // Not enough
    coVerify(exactly = 0) { repository.search(any()) }

    testScheduler.advanceTimeBy(300) // Total 400ms
    coVerify(exactly = 1) { repository.search("test") }
}

// - Don't use Thread.sleep in tests
@Test
fun badTest() = runTest {
    Thread.sleep(1000) // - Wrong!
    testScheduler.advanceTimeBy(1000) // - Correct
}

// - Don't forget to advance time
@Test
fun badTest2() = runTest {
    launch {
        delay(1000)
        doSomething()
    }
    // - Test finishes before coroutine executes
    // - Need: testScheduler.advanceUntilIdle()
}
```

### Common Pitfalls

**1. Not using TestDispatchers:**
```kotlin
// - Uses real Dispatchers.Main
@Test
fun test() = runBlocking { ... }

// - Uses TestDispatcher
@Test
fun test() = runTest { ... }
```

**2. Not advancing virtual time:**
```kotlin
@Test
fun test() = runTest {
    launch { delay(1000); doWork() }
    // - Assertion fails, delay not advanced
    verify { doWork() }

    // - Advance time first
    testScheduler.advanceTimeBy(1000)
    verify { doWork() }
}
```

**3. Not cleaning up collectors:**
```kotlin
@Test
fun test() = runTest {
    flow.collect { ... } // - Hangs if flow never completes

    flow.take(1).test { ... } // - Completes after 1 item
}
```

---



## Ответ (RU)

Тестирование Coroutines и Flow требует специального подхода для асинхронных операций, тестовых диспетчеров и управления временем. Правильное тестирование обеспечивает надежность и поддерживаемость кода.

#### Ключевые концепции:

**1. TestDispatchers:**
- `StandardTestDispatcher` - требует ручного управления временем
- `UnconfinedTestDispatcher` - выполняет корутины немедленно
- Используйте `runTest` вместо `runBlocking`

**2. Тестирование suspend функций:**
```kotlin
@Test
fun test() = runTest {
    val result = repository.getData()
    assertEquals(expected, result)
}
```

**3. Тестирование Flow:**
- Используйте Turbine для удобного API
- `awaitItem()` - ожидать следующее значение
- `awaitComplete()` - ожидать завершения
- `awaitError()` - ожидать ошибку

**4. Управление временем:**
```kotlin
testScheduler.advanceTimeBy(1000) // Продвинуть на 1 секунду
testScheduler.advanceUntilIdle()  // До завершения всех задач
```

**5. Тестирование StateFlow/SharedFlow:**
- StateFlow всегда имеет начальное значение
- SharedFlow может иметь replay buffer
- Используйте Turbine для удобства

**Лучшие практики:**
- Используйте TestDispatchers
- Инжектируйте dispatchers для тестируемости
- Управляйте виртуальным временем
- Тестируйте error cases
- Используйте Turbine для Flow
- Очищайте collectors

**Частые ошибки:**
- Не использовать TestDispatchers
- Не продвигать виртуальное время
- Использовать Thread.sleep
- Не закрывать collectors
- Забывать про начальное значение StateFlow

---

## Related Questions

### Related (Medium)
- [[q-testing-viewmodels-turbine--android--medium]] - Testing
- [[q-testing-compose-ui--android--medium]] - Testing
- [[q-compose-testing--android--medium]] - Testing
- [[q-robolectric-vs-instrumented--android--medium]] - Testing
- [[q-screenshot-snapshot-testing--android--medium]] - Testing

### Advanced (Harder)
- [[q-testing-coroutines-flow--android--hard]] - Testing
