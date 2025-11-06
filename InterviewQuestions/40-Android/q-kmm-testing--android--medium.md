---
id: android-400
title: "KMM Testing / Тестирование в KMM"
aliases: [KMM Testing, Kotlin Multiplatform Testing, Тестирование KMM, Тестирование Kotlin Multiplatform]
topic: android
subtopics: [coroutines, kmp, testing-unit]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-compose-testing--android--medium, q-testing-coroutines-flow--android--hard, q-testing-viewmodels-turbine--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-31
tags: [android/coroutines, android/kmp, android/testing-unit, difficulty/medium, kotlin, multiplatform, testing]
---

# Вопрос (RU)
> Объясните стратегии тестирования KMM проектов. Как писать тесты в commonTest, androidTest и iosTest? Как мокировать платформо-специфичные зависимости?

# Question (EN)
> Explain testing strategies for KMM projects. How do you write tests in commonTest, androidTest, and iosTest? How do you mock platform-specific dependencies?

---

## Ответ (RU)

Тестирование в KMM использует общий код в `commonTest` для всех платформ, с возможностью платформо-специфичных тестов через `expect/actual`. Для утверждений используется `kotlin.test`, для моков - MockK (мультиплатформенный).

### Структура Тестов

**Исходные наборы (Source Sets):**

```kotlin
// shared/build.gradle.kts
kotlin {
    sourceSets {
        val commonTest by getting {
            dependencies {
                implementation(kotlin("test"))
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-test")
                implementation("app.cash.turbine:turbine")
                implementation("io.mockk:mockk")
            }
        }

        val androidUnitTest by getting {
            dependencies {
                implementation(kotlin("test-junit"))
                implementation("androidx.test:core")
            }
        }
    }
}
```

**Структура директорий:**
```
shared/src/
  commonTest/kotlin/         # Общие тесты (все платформы)
  androidUnitTest/kotlin/    # Android-специфичные
  iosTest/kotlin/            # iOS-специфичные
```

### Unit-тестирование В commonTest

**Тест репозитория:**

```kotlin
// ✅ Общий тест - работает на всех платформах
class TaskRepositoryTest {
    private lateinit var repository: TaskRepository
    private lateinit var mockApi: TaskApi

    @BeforeTest
    fun setup() {
        mockApi = mockk()
        repository = TaskRepositoryImpl(mockApi)
    }

    @Test
    fun `getTasks возвращает кэш при ошибке сети`() = runTest {
        // Given
        val cached = listOf(Task(id = "1", title = "Cached"))
        coEvery { mockApi.fetchTasks() } throws NetworkException()

        // When
        val result = repository.getTasks()

        // Then
        assertTrue(result.isSuccess)
        assertEquals(cached, result.getOrNull())
    }
}
```

**Тестирование `Flow` с Turbine:**

```kotlin
@Test
fun `observeTasks эмитит обновления`() = runTest {
    val tasksFlow = MutableStateFlow(emptyList<Task>())
    every { mockDatabase.observeTasks() } returns tasksFlow

    repository.observeTasks().test {
        assertEquals(emptyList(), awaitItem())

        tasksFlow.value = listOf(Task(id = "1", title = "New"))
        assertEquals(1, awaitItem().size)

        cancel()
    }
}
```

### Мокирование Платформо-специфичного Кода

**Expect/Actual для тестовых дублеров:**

```kotlin
// ✅ commonTest - объявление
expect class TestDatabaseDriver {
    fun createInMemoryDriver(): SqlDriver
}

// ✅ androidUnitTest - реализация
actual class TestDatabaseDriver {
    actual fun createInMemoryDriver(): SqlDriver {
        return JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY).apply {
            TaskDatabase.Schema.create(this)
        }
    }
}

// ✅ iosTest - реализация
actual class TestDatabaseDriver {
    actual fun createInMemoryDriver(): SqlDriver {
        return NativeSqliteDriver(TaskDatabase.Schema, name = null)
    }
}
```

**Использование в общих тестах:**

```kotlin
class TaskDatabaseTest {
    private lateinit var driver: SqlDriver

    @BeforeTest
    fun setup() {
        driver = TestDatabaseDriver().createInMemoryDriver()
    }

    @Test
    fun `insertTask сохраняет задачу`() {
        val task = Task(id = "1", title = "Test")
        database.taskQueries.insertTask(task)

        val retrieved = database.taskQueries.selectById("1")
        assertEquals(task, retrieved)
    }
}
```

**Фейки для платформенных API:**

```kotlin
// ✅ commonTest - фейк
class FakeLogger : PlatformLogger() {
    val logs = mutableListOf<String>()

    override fun log(message: String) {
        logs.add(message)
    }

    fun assertLogged(substring: String) {
        assertTrue(logs.any { it.contains(substring) })
    }
}
```

### Тестирование Корутин

**TestDispatchers:**

```kotlin
object TestDispatchers : CoroutineDispatchers {
    override val main = StandardTestDispatcher()
    override val io = StandardTestDispatcher()
}

@Test
fun `loadTasks обновляет состояние`() = runTest {
    val viewModel = TaskViewModel(
        repository = mockRepository,
        dispatchers = TestDispatchers
    )

    viewModel.loadTasks()
    advanceUntilIdle() // Ждем завершения корутин

    assertEquals(LoadingState.Success, viewModel.state.value)
}
```

### Платформо-специфичные Тесты

**Android (с Robolectric):**

```kotlin
// ❌ Не используйте реальный контекст в commonTest
// ✅ Используйте в androidUnitTest
@RunWith(AndroidJUnit4::class)
class AndroidPreferencesTest {
    private lateinit var context: Context

    @Before
    fun setup() {
        context = ApplicationProvider.getApplicationContext()
    }

    @Test
    fun `saveToken сохраняет токен`() {
        val prefs = AndroidPreferences(context)
        prefs.saveToken("token")

        assertEquals("token", prefs.getToken())
    }
}
```

**iOS:**

```kotlin
class IOSKeychainTest {
    @Test
    fun testIOSSpecificFeature() {
        // iOS-специфичная логика
    }
}
```

### Best Practices

**Организация:**
- Максимизируйте код в `commonTest` (80%+)
- Используйте платформо-специфичные тесты только для платформенного кода
- Группируйте тесты по функциональности

**Покрытие:**
- 80%+ для общего кода
- Тестируйте позитивные и негативные сценарии
- Используйте фейки для сложных зависимостей

**Производительность:**
- Тесты <100мс
- In-memory базы данных
- Избегайте реальных сетевых вызовов

---

## Answer (EN)

KMM testing uses shared code in `commonTest` for all platforms, with platform-specific tests via `expect/actual`. Use `kotlin.test` for assertions, MockK for mocks (multiplatform).

### Test Structure

**Source Sets:**

```kotlin
// shared/build.gradle.kts
kotlin {
    sourceSets {
        val commonTest by getting {
            dependencies {
                implementation(kotlin("test"))
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-test")
                implementation("app.cash.turbine:turbine")
                implementation("io.mockk:mockk")
            }
        }

        val androidUnitTest by getting {
            dependencies {
                implementation(kotlin("test-junit"))
                implementation("androidx.test:core")
            }
        }
    }
}
```

### Unit Testing in commonTest

**`Repository` test:**

```kotlin
// ✅ Shared test - runs on all platforms
class TaskRepositoryTest {
    private lateinit var mockApi: TaskApi

    @BeforeTest
    fun setup() {
        mockApi = mockk()
    }

    @Test
    fun `getTasks returns cache on network error`() = runTest {
        // Given
        coEvery { mockApi.fetchTasks() } throws NetworkException()

        // When
        val result = repository.getTasks()

        // Then
        assertTrue(result.isSuccess)
    }
}
```

**`Flow` testing with Turbine:**

```kotlin
@Test
fun `observeTasks emits updates`() = runTest {
    repository.observeTasks().test {
        assertEquals(emptyList(), awaitItem())

        // Trigger update
        repository.addTask(Task(id = "1", title = "New"))

        assertEquals(1, awaitItem().size)
        cancel()
    }
}
```

### Mocking Platform-Specific Code

**Expect/Actual for test doubles:**

```kotlin
// ✅ commonTest - declaration
expect class TestDatabaseDriver {
    fun createInMemoryDriver(): SqlDriver
}

// ✅ androidUnitTest - implementation
actual class TestDatabaseDriver {
    actual fun createInMemoryDriver(): SqlDriver {
        return JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY)
    }
}

// Usage in common tests
class TaskDatabaseTest {
    @BeforeTest
    fun setup() {
        driver = TestDatabaseDriver().createInMemoryDriver()
    }
}
```

**Fakes for platform APIs:**

```kotlin
// ✅ commonTest - fake
class FakeLogger : PlatformLogger() {
    val logs = mutableListOf<String>()

    override fun log(message: String) {
        logs.add(message)
    }
}
```

### `Coroutine` Testing

```kotlin
object TestDispatchers : CoroutineDispatchers {
    override val main = StandardTestDispatcher()
    override val io = StandardTestDispatcher()
}

@Test
fun `loadTasks updates state`() = runTest {
    val viewModel = TaskViewModel(TestDispatchers)
    viewModel.loadTasks()
    advanceUntilIdle()

    assertEquals(LoadingState.Success, viewModel.state.value)
}
```

### Platform-Specific Tests

**Android (with Robolectric):**

```kotlin
// ❌ Don't use real Context in commonTest
// ✅ Use in androidUnitTest
@RunWith(AndroidJUnit4::class)
class AndroidPreferencesTest {
    @Test
    fun `saveToken persists token`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val prefs = AndroidPreferences(context)

        prefs.saveToken("token")
        assertEquals("token", prefs.getToken())
    }
}
```

### Best Practices

**Organization:**
- Maximize code in `commonTest` (80%+)
- Use platform tests only for platform code
- Group tests by functionality

**Coverage:**
- 80%+ for shared code
- Test happy paths and edge cases
- Use fakes for complex dependencies

**Performance:**
- Tests <100ms
- In-memory databases
- Avoid real network calls

---

## Follow-ups

- How to test expect/actual implementations separately?
- What are best practices for testing network layer in KMM?
- How to implement screenshot testing across platforms?
- When to use fakes vs mocks in KMM tests?
- How to optimize test execution time in large KMM projects?

## References

- [[c-kmm]] - Kotlin Multiplatform Mobile concept
- [[c-testing-strategies]] - Testing strategies overview
- [Kotlin Multiplatform Testing](https://kotlinlang.org/docs/multiplatform-run-tests.html)
- [MockK Documentation](https://mockk.io/)
- [Turbine - `Flow` Testing Library](https://github.com/cashapp/turbine)

## Related Questions

### Related (Medium)
- [[q-testing-viewmodels-turbine--android--medium]] - `ViewModel` testing with Turbine
- [[q-compose-testing--android--medium]] - Compose UI testing
- [[q-robolectric-vs-instrumented--android--medium]] - Robolectric vs instrumented tests

### Advanced (Harder)
- [[q-testing-coroutines-flow--android--hard]] - Advanced coroutine testing
