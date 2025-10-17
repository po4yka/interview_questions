---
id: "20251015082237524"
title: "Kmm Testing / Kmm Тестирование"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [Kotlin, KMM, Testing, Multiplatform, difficulty/medium]
---
# Testing in Kotlin Multiplatform Mobile

# Question (EN)
> 
Explain testing strategies for KMM projects. How do you write tests in commonTest, androidTest, and iosTest? How do you mock platform-specific dependencies? What are best practices for unit testing, integration testing, and UI testing across platforms?

## Answer (EN)
KMM testing leverages shared test code in commonTest while allowing platform-specific tests, using kotlin.test for unified assertions and expect/actual for platform-specific test implementations.

#### Test Structure and Setup

**1. Test Source Sets Configuration**
```kotlin
// shared/build.gradle.kts
kotlin {
    sourceSets {
        val commonMain by getting {
            dependencies {
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
            }
        }

        val commonTest by getting {
            dependencies {
                // Common test library
                implementation(kotlin("test"))

                // Coroutines test
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")

                // Turbine for Flow testing
                implementation("app.cash.turbine:turbine:1.0.0")

                // MockK (multiplatform)
                implementation("io.mockk:mockk:1.13.8")
            }
        }

        val androidUnitTest by getting {
            dependencies {
                implementation(kotlin("test-junit"))
                implementation("junit:junit:4.13.2")
                implementation("io.mockk:mockk-android:1.13.8")
                implementation("androidx.test:core:1.5.0")
                implementation("org.robolectric:robolectric:4.11.1")
            }
        }

        val iosTest by getting {
            dependencies {
                // iOS-specific test dependencies
            }
        }
    }
}
```

**2. Directory Structure**
```
shared/src/
 commonMain/kotlin/
 commonTest/kotlin/          # Shared tests (run on all platforms)
    repository/
       TaskRepositoryTest.kt
    usecase/
       CreateTaskUseCaseTest.kt
    util/
        TestHelpers.kt
 androidUnitTest/kotlin/     # Android-specific tests
    database/
       TaskDatabaseTest.kt
    util/
        AndroidTestHelpers.kt
 iosTest/kotlin/             # iOS-specific tests
     database/
         TaskDatabaseTest.kt
```

#### Unit Testing in commonTest

**1. Repository Tests**
```kotlin
// commonTest/repository/TaskRepositoryTest.kt
class TaskRepositoryTest {
    private lateinit var repository: TaskRepository
    private lateinit var mockApi: TaskApi
    private lateinit var mockDatabase: TaskDatabase

    @BeforeTest
    fun setup() {
        mockApi = mockk()
        mockDatabase = mockk()

        repository = TaskRepositoryImpl(
            api = mockApi,
            database = mockDatabase,
            logger = TestLogger()
        )
    }

    @AfterTest
    fun tearDown() {
        clearAllMocks()
    }

    @Test
    fun `getTasks returns cached data when network fails`() = runTest {
        // Given
        val cachedTasks = listOf(
            Task(id = "1", title = "Cached Task", userId = "user1")
        )

        coEvery { mockApi.fetchTasks() } throws NetworkException()
        coEvery { mockDatabase.getAllTasks() } returns cachedTasks

        // When
        val result = repository.getTasks()

        // Then
        assertTrue(result.isSuccess)
        assertEquals(cachedTasks, result.getOrNull())

        coVerify { mockApi.fetchTasks() }
        coVerify { mockDatabase.getAllTasks() }
    }

    @Test
    fun `getTasks updates database on successful network call`() = runTest {
        // Given
        val remoteTasks = listOf(
            Task(id = "1", title = "Remote Task", userId = "user1")
        )

        coEvery { mockApi.fetchTasks() } returns remoteTasks
        coEvery { mockDatabase.saveTasks(any()) } just Runs
        coEvery { mockDatabase.getAllTasks() } returns remoteTasks

        // When
        val result = repository.getTasks(forceRefresh = true)

        // Then
        assertTrue(result.isSuccess)
        assertEquals(remoteTasks, result.getOrNull())

        coVerify { mockApi.fetchTasks() }
        coVerify { mockDatabase.saveTasks(remoteTasks) }
    }

    @Test
    fun `createTask returns failure when validation fails`() = runTest {
        // Given
        val invalidTask = Task(
            id = "1",
            title = "", // Invalid: empty title
            userId = "user1"
        )

        // When
        val result = repository.createTask(invalidTask)

        // Then
        assertTrue(result.isFailure)
        assertTrue(result.exceptionOrNull() is ValidationException)
    }
}
```

**2. Use Case Tests**
```kotlin
// commonTest/usecase/CreateTaskUseCaseTest.kt
class CreateTaskUseCaseTest {
    private lateinit var useCase: CreateTaskUseCase
    private lateinit var mockRepository: TaskRepository

    @BeforeTest
    fun setup() {
        mockRepository = mockk()
        useCase = CreateTaskUseCase(mockRepository)
    }

    @Test
    fun `invoke creates task with valid input`() = runTest {
        // Given
        val title = "New Task"
        val description = "Task description"
        val expectedTask = Task(
            id = "generated-id",
            title = title,
            description = description,
            userId = "user1"
        )

        coEvery {
            mockRepository.createTask(any())
        } returns Result.success(expectedTask)

        // When
        val result = useCase(title, description, "user1")

        // Then
        assertTrue(result.isSuccess)
        assertEquals(expectedTask, result.getOrNull())

        coVerify {
            mockRepository.createTask(match { task ->
                task.title == title &&
                task.description == description &&
                task.userId == "user1"
            })
        }
    }

    @Test
    fun `invoke returns failure when title is blank`() = runTest {
        // Given
        val title = "   " // Blank title
        val description = "Description"

        // When
        val result = useCase(title, description, "user1")

        // Then
        assertTrue(result.isFailure)
        assertTrue(result.exceptionOrNull() is ValidationException)

        coVerify(exactly = 0) { mockRepository.createTask(any()) }
    }
}
```

**3. Flow Testing with Turbine**
```kotlin
// commonTest/repository/TaskFlowTest.kt
class TaskFlowTest {
    private lateinit var repository: TaskRepository
    private lateinit var mockDatabase: TaskDatabase

    @BeforeTest
    fun setup() {
        mockDatabase = mockk()
        repository = TaskRepositoryImpl(
            api = mockk(),
            database = mockDatabase,
            logger = TestLogger()
        )
    }

    @Test
    fun `observeTasks emits updates when tasks change`() = runTest {
        // Given
        val initialTasks = listOf(
            Task(id = "1", title = "Task 1", userId = "user1")
        )
        val updatedTasks = listOf(
            Task(id = "1", title = "Task 1", userId = "user1"),
            Task(id = "2", title = "Task 2", userId = "user1")
        )

        val tasksFlow = MutableStateFlow(initialTasks)
        every { mockDatabase.observeTasks() } returns tasksFlow

        // When/Then
        repository.observeTasks().test {
            // First emission
            assertEquals(initialTasks, awaitItem())

            // Update tasks
            tasksFlow.value = updatedTasks

            // Second emission
            assertEquals(updatedTasks, awaitItem())

            cancel()
        }
    }

    @Test
    fun `observeActiveTasks filters completed tasks`() = runTest {
        // Given
        val allTasks = listOf(
            Task(id = "1", title = "Active", completed = false, userId = "user1"),
            Task(id = "2", title = "Completed", completed = true, userId = "user1"),
            Task(id = "3", title = "Active 2", completed = false, userId = "user1")
        )

        every { mockDatabase.observeTasks() } returns flowOf(allTasks)

        // When/Then
        repository.observeActiveTasks("user1").test {
            val activeTasks = awaitItem()

            assertEquals(2, activeTasks.size)
            assertTrue(activeTasks.all { !it.completed })

            awaitComplete()
        }
    }
}
```

#### Mocking Platform-Specific Code

**1. Expect/Actual for Test Doubles**
```kotlin
// commonTest - Test interface
expect class TestDatabaseDriver {
    fun createInMemoryDriver(): SqlDriver
}

// androidUnitTest
actual class TestDatabaseDriver {
    actual fun createInMemoryDriver(): SqlDriver {
        return JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY).apply {
            TaskDatabase.Schema.create(this)
        }
    }
}

// iosTest
actual class TestDatabaseDriver {
    actual fun createInMemoryDriver(): SqlDriver {
        return NativeSqliteDriver(
            schema = TaskDatabase.Schema,
            name = null // in-memory
        )
    }
}

// Usage in commonTest
class TaskDatabaseTest {
    private lateinit var driver: SqlDriver
    private lateinit var database: TaskDatabase

    @BeforeTest
    fun setup() {
        driver = TestDatabaseDriver().createInMemoryDriver()
        database = TaskDatabase(driver)
    }

    @AfterTest
    fun tearDown() {
        driver.close()
    }

    @Test
    fun `insertTask and selectTask returns correct task`() {
        // Test implementation
        val task = Task(id = "1", title = "Test", userId = "user1")

        database.taskQueries.insertTask(task)
        val retrieved = database.taskQueries.selectById("1").executeAsOneOrNull()

        assertEquals(task, retrieved)
    }
}
```

**2. Test Fakes for Platform APIs**
```kotlin
// commonMain - Platform interface
expect class PlatformLogger {
    fun log(tag: String, message: String)
}

// commonTest - Fake implementation
class FakeLogger : PlatformLogger() {
    val logs = mutableListOf<LogEntry>()

    override fun log(tag: String, message: String) {
        logs.add(LogEntry(tag, message))
    }

    fun assertLogged(tag: String, message: String) {
        assertTrue(
            logs.any { it.tag == tag && it.message.contains(message) },
            "Expected log not found: [$tag] $message"
        )
    }

    data class LogEntry(val tag: String, val message: String)
}

// Usage
@Test
fun `repository logs errors`() = runTest {
    val fakeLogger = FakeLogger()
    val repository = TaskRepositoryImpl(
        api = mockk(),
        database = mockk(),
        logger = fakeLogger
    )

    coEvery { mockApi.fetchTasks() } throws NetworkException("Network error")

    repository.getTasks()

    fakeLogger.assertLogged("TaskRepository", "Network error")
}
```

#### Coroutine Testing

**1. TestDispatchers**
```kotlin
// commonTest/util/TestDispatchers.kt
object TestDispatchers : CoroutineDispatchers {
    override val main: CoroutineDispatcher = StandardTestDispatcher()
    override val io: CoroutineDispatcher = StandardTestDispatcher()
    override val default: CoroutineDispatcher = StandardTestDispatcher()
}

// Usage in tests
class TaskViewModelTest {
    private val testScope = TestScope()

    @Test
    fun `loadTasks updates state correctly`() = testScope.runTest {
        val viewModel = TaskViewModel(
            getTasks = mockk(),
            dispatchers = TestDispatchers
        )

        // Test implementation
    }
}
```

**2. Testing Delays and Timeouts**
```kotlin
@Test
fun `retry logic waits between attempts`() = runTest {
    val mockApi = mockk<TaskApi>()
    var attemptCount = 0

    coEvery { mockApi.fetchTasks() } answers {
        attemptCount++
        if (attemptCount < 3) {
            throw NetworkException()
        } else {
            emptyList()
        }
    }

    val repository = TaskRepositoryImpl(
        api = mockApi,
        database = mockk(),
        retryDelay = 1000L
    )

    // Advance virtual time
    val result = repository.getTasks()

    // Verify retry happened
    assertEquals(3, attemptCount)
    assertTrue(result.isSuccess)
}
```

#### Platform-Specific Tests

**1. Android-Specific Tests**
```kotlin
// androidUnitTest/database/TaskDatabaseAndroidTest.kt
@RunWith(AndroidJUnit4::class)
class TaskDatabaseAndroidTest {
    private lateinit var context: Context
    private lateinit var database: TaskDatabase

    @Before
    fun setup() {
        context = ApplicationProvider.getApplicationContext()
        val driver = AndroidSqliteDriver(
            schema = TaskDatabase.Schema,
            context = context,
            name = "test.db"
        )
        database = TaskDatabase(driver)
    }

    @After
    fun tearDown() {
        context.deleteDatabase("test.db")
    }

    @Test
    fun testAndroidSpecificFeature() {
        // Android-specific test using Robolectric
        val task = Task(id = "1", title = "Test", userId = "user1")
        database.taskQueries.insertTask(task)

        val retrieved = database.taskQueries.selectById("1").executeAsOneOrNull()

        assertEquals(task, retrieved)
    }
}

// androidUnitTest/util/AndroidPreferencesTest.kt
@RunWith(RobolectricTestRunner::class)
class AndroidPreferencesTest {
    private lateinit var preferences: AndroidPreferences

    @Before
    fun setup() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        preferences = AndroidPreferences(context)
    }

    @Test
    fun `saveToken and getToken work correctly`() {
        val token = "test-token"

        preferences.saveToken(token)
        val retrieved = preferences.getToken()

        assertEquals(token, retrieved)
    }
}
```

**2. iOS-Specific Tests**
```kotlin
// iosTest/database/TaskDatabaseIOSTest.kt
class TaskDatabaseIOSTest {
    private lateinit var driver: SqlDriver
    private lateinit var database: TaskDatabase

    @BeforeTest
    fun setup() {
        driver = NativeSqliteDriver(
            schema = TaskDatabase.Schema,
            name = "test.db"
        )
        database = TaskDatabase(driver)
    }

    @AfterTest
    fun tearDown() {
        driver.close()
    }

    @Test
    fun testIOSSpecificFeature() {
        val task = Task(id = "1", title = "Test", userId = "user1")
        database.taskQueries.insertTask(task)

        val retrieved = database.taskQueries.selectById("1").executeAsOneOrNull()

        assertEquals(task, retrieved)
    }
}
```

#### Integration Testing

**1. End-to-End Repository Tests**
```kotlin
// commonTest/integration/TaskRepositoryIntegrationTest.kt
class TaskRepositoryIntegrationTest {
    private lateinit var repository: TaskRepository
    private lateinit var database: TaskDatabase
    private lateinit var api: FakeTaskApi

    @BeforeTest
    fun setup() {
        val driver = TestDatabaseDriver().createInMemoryDriver()
        database = TaskDatabase(driver)
        api = FakeTaskApi()

        repository = TaskRepositoryImpl(
            api = api,
            database = TaskDatabaseImpl(database),
            logger = TestLogger()
        )
    }

    @Test
    fun `complete workflow creates, updates, and deletes task`() = runTest {
        // Create task
        val task = Task(
            id = "1",
            title = "Integration Test Task",
            description = "Testing end-to-end",
            userId = "user1"
        )

        api.mockCreateTask(task)
        val created = repository.createTask(task).getOrThrow()

        assertEquals(task.title, created.title)

        // Update task
        val updated = created.copy(completed = true)
        api.mockUpdateTask(updated)
        val result = repository.updateTask(updated).getOrThrow()

        assertTrue(result.completed)

        // Delete task
        api.mockDeleteTask(updated.id)
        repository.deleteTask(updated.id)

        val deleted = repository.getTaskById(updated.id).getOrNull()
        assertNull(deleted)
    }

    @Test
    fun `sync flow updates local database from remote`() = runTest {
        // Given remote tasks
        val remoteTasks = listOf(
            Task(id = "1", title = "Remote 1", userId = "user1"),
            Task(id = "2", title = "Remote 2", userId = "user1")
        )
        api.mockFetchTasks(remoteTasks)

        // When syncing
        repository.sync("user1")

        // Then local database is updated
        val localTasks = repository.getTasks().getOrThrow()

        assertEquals(2, localTasks.size)
        assertEquals(remoteTasks, localTasks)
    }
}

// Fake API for testing
class FakeTaskApi : TaskApi {
    private val tasks = mutableMapOf<String, Task>()

    fun mockFetchTasks(tasks: List<Task>) {
        tasks.forEach { this.tasks[it.id] = it }
    }

    fun mockCreateTask(task: Task) {
        tasks[task.id] = task
    }

    fun mockUpdateTask(task: Task) {
        tasks[task.id] = task
    }

    fun mockDeleteTask(id: String) {
        tasks.remove(id)
    }

    override suspend fun fetchTasks(): List<Task> {
        return tasks.values.toList()
    }

    override suspend fun createTask(task: Task): Task {
        tasks[task.id] = task
        return task
    }

    override suspend fun updateTask(id: String, task: Task): Task {
        tasks[id] = task
        return task
    }

    override suspend fun deleteTask(id: String) {
        tasks.remove(id)
    }
}
```

#### Test Utilities

**1. Test Data Builders**
```kotlin
// commonTest/util/TestDataBuilders.kt
object TaskTestData {
    fun createTask(
        id: String = "test-id",
        title: String = "Test Task",
        description: String = "Test description",
        completed: Boolean = false,
        priority: Int = 0,
        userId: String = "test-user",
        createdAt: Long = Clock.System.now().toEpochMilliseconds()
    ) = Task(
        id = id,
        title = title,
        description = description,
        completed = completed,
        priority = priority,
        dueDate = null,
        createdAt = createdAt,
        updatedAt = createdAt,
        categoryId = null,
        userId = userId
    )

    fun createTasks(count: Int, userId: String = "test-user"): List<Task> {
        return List(count) { index ->
            createTask(
                id = "task-$index",
                title = "Task $index",
                userId = userId
            )
        }
    }
}

// Usage
@Test
fun `repository handles multiple tasks`() = runTest {
    val tasks = TaskTestData.createTasks(10)

    tasks.forEach { repository.createTask(it) }

    val retrieved = repository.getTasks().getOrThrow()

    assertEquals(10, retrieved.size)
}
```

**2. Custom Assertions**
```kotlin
// commonTest/util/Assertions.kt
fun assertTaskEquals(expected: Task, actual: Task, message: String = "") {
    assertEquals(expected.id, actual.id, "$message - id mismatch")
    assertEquals(expected.title, actual.title, "$message - title mismatch")
    assertEquals(expected.completed, actual.completed, "$message - completed mismatch")
}

fun assertResultSuccess(result: Result<*>, message: String = "") {
    assertTrue(result.isSuccess, "$message - expected success but got failure: ${result.exceptionOrNull()}")
}

fun assertResultFailure(result: Result<*>, message: String = "") {
    assertTrue(result.isFailure, "$message - expected failure but got success")
}

inline fun <reified T : Throwable> assertResultFailureWithType(
    result: Result<*>,
    message: String = ""
) {
    assertResultFailure(result, message)
    assertTrue(
        result.exceptionOrNull() is T,
        "$message - expected ${T::class.simpleName} but got ${result.exceptionOrNull()?.javaClass?.simpleName}"
    )
}

// Usage
@Test
fun `createTask validates input`() = runTest {
    val result = repository.createTask(TaskTestData.createTask(title = ""))

    assertResultFailureWithType<ValidationException>(result)
}
```

#### Best Practices

1. **Test Organization**:
   - Keep shared tests in commonTest
   - Platform-specific tests in androidTest/iosTest
   - Use descriptive test names
   - Group related tests in classes

2. **Test Coverage**:
   - Aim for 80%+ coverage in shared code
   - Test happy paths and edge cases
   - Test error scenarios
   - Test concurrent operations

3. **Test Data**:
   - Use builders for test data
   - Keep test data realistic
   - Avoid magic numbers
   - Reuse test data across tests

4. **Mocking**:
   - Mock external dependencies
   - Use fakes for complex dependencies
   - Verify interactions
   - Reset mocks between tests

5. **Performance**:
   - Keep tests fast (<100ms per test)
   - Use in-memory databases
   - Avoid real network calls
   - Parallelize test execution

### Summary

KMM testing provides comprehensive testing capabilities:
- **Shared Tests**: Write once, run on all platforms (commonTest)
- **Platform-Specific**: Test platform implementations separately
- **Mocking**: MockK for dependencies, fakes for complex objects
- **Coroutines**: TestDispatchers and runTest for async code
- **Flows**: Turbine for testing reactive streams
- **Integration**: End-to-end tests with real implementations

Key considerations: maximize shared test code, use proper test doubles, test coroutines correctly, and maintain high coverage in shared logic.

---

# Вопрос (RU)
> 
Объясните стратегии тестирования для KMM проектов. Как писать тесты в commonTest, androidTest и iosTest? Как мокировать platform-specific зависимости? Каковы best practices для unit, integration и UI тестирования на разных платформах?

## Ответ (RU)
Тестирование в KMM использует общий тестовый код в `commonTest`, позволяя при этом писать платформо-специфичные тесты. Для унифицированных утверждений используется `kotlin.test`, а для платформо-специфичных реализаций тестов — `expect/actual`.

#### Структура и настройка тестов

**1. Конфигурация исходных наборов тестов**
```kotlin
// shared/build.gradle.kts
kotlin {
    sourceSets {
        val commonMain by getting {
            dependencies {
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
            }
        }

        val commonTest by getting {
            dependencies {
                // Общая библиотека для тестов
                implementation(kotlin("test"))

                // Тестирование корутин
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")

                // Turbine для тестирования Flow
                implementation("app.cash.turbine:turbine:1.0.0")

                // MockK (мультиплатформенный)
                implementation("io.mockk:mockk:1.13.8")
            }
        }

        val androidUnitTest by getting {
            dependencies {
                implementation(kotlin("test-junit"))
                implementation("junit:junit:4.13.2")
                implementation("io.mockk:mockk-android:1.13.8")
                implementation("androidx.test:core:1.5.0")
                implementation("org.robolectric:robolectric:4.11.1")
            }
        }

        val iosTest by getting {
            dependencies {
                // Зависимости для тестов под iOS
            }
        }
    }
}
```

**2. Структура директорий**
```
shared/src/
 commonMain/kotlin/
 commonTest/kotlin/          # Общие тесты (запускаются на всех платформах)
    repository/
       TaskRepositoryTest.kt
    usecase/
       CreateTaskUseCaseTest.kt
    util/
        TestHelpers.kt
 androidUnitTest/kotlin/     # Специфичные для Android тесты
    database/
       TaskDatabaseTest.kt
    util/
        AndroidTestHelpers.kt
 iosTest/kotlin/             # Специфичные для iOS тесты
     database/
         TaskDatabaseTest.kt
```

#### Модульное тестирование в commonTest

**1. Тесты репозитория**
```kotlin
// commonTest/repository/TaskRepositoryTest.kt
class TaskRepositoryTest {
    private lateinit var repository: TaskRepository
    private lateinit var mockApi: TaskApi
    private lateinit var mockDatabase: TaskDatabase

    @BeforeTest
    fun setup() {
        mockApi = mockk()
        mockDatabase = mockk()

        repository = TaskRepositoryImpl(
            api = mockApi,
            database = mockDatabase,
            logger = TestLogger()
        )
    }

    @AfterTest
    fun tearDown() {
        clearAllMocks()
    }

    @Test
    fun `getTasks returns cached data when network fails`() = runTest {
        // Given
        val cachedTasks = listOf(
            Task(id = "1", title = "Cached Task", userId = "user1")
        )

        coEvery { mockApi.fetchTasks() } throws NetworkException()
        coEvery { mockDatabase.getAllTasks() } returns cachedTasks

        // When
        val result = repository.getTasks()

        // Then
        assertTrue(result.isSuccess)
        assertEquals(cachedTasks, result.getOrNull())

        coVerify { mockApi.fetchTasks() }
        coVerify { mockDatabase.getAllTasks() }
    }
    // ...
}
```

**2. Тесты Use Case**
```kotlin
// commonTest/usecase/CreateTaskUseCaseTest.kt
class CreateTaskUseCaseTest {
    // ...
}
```

**3. Тестирование Flow с помощью Turbine**
```kotlin
// commonTest/repository/TaskFlowTest.kt
class TaskFlowTest {
    // ...
}
```

#### Мокирование платформо-специфичного кода

**1. Expect/Actual для тестовых двойников**
```kotlin
// commonTest - интерфейс для теста
expect class TestDatabaseDriver {
    fun createInMemoryDriver(): SqlDriver
}

// androidUnitTest
actual class TestDatabaseDriver {
    actual fun createInMemoryDriver(): SqlDriver {
        return JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY).apply {
            TaskDatabase.Schema.create(this)
        }
    }
}

// iosTest
actual class TestDatabaseDriver {
    actual fun createInMemoryDriver(): SqlDriver {
        return NativeSqliteDriver(
            schema = TaskDatabase.Schema,
            name = null // в памяти
        )
    }
}

// Использование в commonTest
class TaskDatabaseTest {
    // ...
}
```

**2. Тестовые фейки для платформенных API**
```kotlin
// commonMain - платформенный интерфейс
expect class PlatformLogger {
    fun log(tag: String, message: String)
}

// commonTest - фейковая реализация
class FakeLogger : PlatformLogger() {
    // ...
}
```

#### Тестирование корутин

**1. TestDispatchers**
```kotlin
// commonTest/util/TestDispatchers.kt
object TestDispatchers : CoroutineDispatchers {
    override val main: CoroutineDispatcher = StandardTestDispatcher()
    override val io: CoroutineDispatcher = StandardTestDispatcher()
    override val default: CoroutineDispatcher = StandardTestDispatcher()
}
```

#### Платформо-специфичные тесты

**1. Специфичные для Android тесты**
```kotlin
// androidUnitTest/database/TaskDatabaseAndroidTest.kt
@RunWith(AndroidJUnit4::class)
class TaskDatabaseAndroidTest {
    // ...
}
```

**2. Специфичные для iOS тесты**
```kotlin
// iosTest/database/TaskDatabaseIOSTest.kt
class TaskDatabaseIOSTest {
    // ...
}
```

#### Интеграционное тестирование

**1. Сквозные тесты репозитория**
```kotlin
// commonTest/integration/TaskRepositoryIntegrationTest.kt
class TaskRepositoryIntegrationTest {
    // ...
}
```

#### Утилиты для тестов

**1. Строители тестовых данных**
```kotlin
// commonTest/util/TestDataBuilders.kt
object TaskTestData {
    // ...
}
```

**2. Пользовательские утверждения**
```kotlin
// commonTest/util/Assertions.kt
fun assertTaskEquals(expected: Task, actual: Task, message: String = "") {
    // ...
}
```

#### Лучшие практики

1.  **Организация тестов**:
    *   Общие тесты в `commonTest`.
    *   Платформо-специфичные тесты в `androidTest`/`iosTest`.
2.  **Покрытие тестами**:
    *   Стремитесь к 80%+ покрытию в общем коде.
    *   Тестируйте позитивные и негативные сценарии.
3.  **Тестовые данные**:
    *   Используйте строители для тестовых данных.
4.  **Мокирование**:
    *   Мокируйте внешние зависимости.
    *   Используйте фейки для сложных зависимостей.
5.  **Производительность**:
    *   Тесты должны быть быстрыми (<100мс на тест).
    *   Используйте базы данных в памяти.

### Резюме

Тестирование в KMM обеспечивает комплексные возможности:
- **Общие тесты**: Пишутся один раз, запускаются на всех платформах (`commonTest`).
- **Платформо-специфичные**: Тестирование реализаций для конкретных платформ.
- **Мокирование**: MockK для зависимостей, фейки для сложных объектов.
- **Корутины**: `TestDispatchers` и `runTest` для асинхронного кода.
- **Flows**: Turbine для тестирования реактивных потоков.
- **Интеграция**: Сквозные тесты с реальными реализациями.

Ключевые моменты: максимизация общего тестового кода, использование правильных тестовых двойников, корректное тестирование корутин и поддержание высокого покрытия в общей логике.

---

## Related Questions

### Related (Medium)
- [[q-testing-viewmodels-turbine--testing--medium]] - Testing
- [[q-testing-compose-ui--android--medium]] - Testing
- [[q-compose-testing--android--medium]] - Testing
- [[q-robolectric-vs-instrumented--testing--medium]] - Testing
- [[q-screenshot-snapshot-testing--testing--medium]] - Testing

### Advanced (Harder)
- [[q-testing-coroutines-flow--testing--hard]] - Testing
