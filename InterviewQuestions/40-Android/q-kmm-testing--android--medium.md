---\
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
related: [moc-android, q-compose-testing--android--medium, q-testing-coroutines-flow--android--hard, q-testing-viewmodels-turbine--android--medium]
sources: []
created: 2025-10-15
updated: 2025-11-10
tags: [android/coroutines, android/kmp, android/testing-unit, difficulty/medium, kotlin, multiplatform, testing]
anki_cards:
  - slug: android-400-0-en
    front: "How do you test KMM projects across platforms?"
    back: |
      **Test structure:**
      - `commonTest` - shared tests (business logic)
      - `androidUnitTest` - Android-specific (JVM)
      - `iosTest` - iOS-specific

      **Key approaches:**
      - Use `kotlin.test` assertions
      - Turbine for Flow testing
      - expect/actual for platform test drivers
      - Fakes over mocks in commonTest

      ```kotlin
      @Test
      fun test() = runTest {
          repository.observeTasks().test {
              assertEquals(emptyList(), awaitItem())
          }
      }
      ```
    tags:
      - android_testing
      - difficulty::medium
  - slug: android-400-0-ru
    front: "Как тестировать KMM проекты на разных платформах?"
    back: |
      **Структура тестов:**
      - `commonTest` - общие тесты (бизнес-логика)
      - `androidUnitTest` - Android-специфичные (JVM)
      - `iosTest` - iOS-специфичные

      **Ключевые подходы:**
      - Используйте `kotlin.test` assertions
      - Turbine для тестирования Flow
      - expect/actual для платформенных тестовых драйверов
      - Fakes вместо mocks в commonTest

      ```kotlin
      @Test
      fun test() = runTest {
          repository.observeTasks().test {
              assertEquals(emptyList(), awaitItem())
          }
      }
      ```
    tags:
      - android_testing
      - difficulty::medium

---\
# Вопрос (RU)
> Объясните стратегии тестирования KMM проектов. Как писать тесты в commonTest, androidTest и iosTest? Как мокировать платформо-специфичные зависимости?

# Question (EN)
> Explain testing strategies for KMM projects. How do you write tests in commonTest, androidTest, and iosTest? How do you mock platform-specific dependencies?

---

## Ответ (RU)

Тестирование в KMM строится вокруг максимального использования общего кода и общих тестов в `commonTest`, с выделением платформо-специфичных тестов в отдельных source sets. Общие тесты пишутся на базе `kotlin.test`. Для моков используйте мультиплатформенные библиотеки (например, KMP-совместимые артефакты MockK или специализированные KMP-friendly альтернативы), а JVM-специфичные моки (такие как стандартный `io.mockk:mockk`) подключайте только в JVM/Android тестовых source sets.

См. также: [[moc-android]]

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
                // Подключайте только мультиплатформенные зависимости;
                // JVM-only библиотеки (например, io.mockk:mockk) выносите в JVM-специфичные source sets
            }
        }

        val androidUnitTest by getting {
            dependencies {
                implementation(kotlin("test-junit"))
                implementation("androidx.test:core")
                implementation("io.mockk:mockk") // JVM-only, безопасно использовать здесь
            }
        }

        // iosTest обычно настраивается Gradle-плагином KMP и использует commonTest + iOS-специфичные реализации
    }
}
```

**Структура директорий:**

```text
shared/src/
  commonTest/kotlin/         # Общие тесты (все платформы)
  androidUnitTest/kotlin/    # Android-специфичные unit-тесты (JVM)
  iosTest/kotlin/            # iOS-специфичные тесты
```

### Unit-тестирование В commonTest

Общий код (репозитории, use-case, бизнес-логика) тестируется в `commonTest`, чтобы один и тот же тест запускался на разных таргетах.

**Пример теста репозитория:**

```kotlin
// Общий тест - должен работать на всех поддерживаемых платформах
class TaskRepositoryTest {
    private lateinit var repository: TaskRepository
    private lateinit var mockApi: TaskApi

    @BeforeTest
    fun setup() {
        mockApi = mockk()
        repository = TaskRepositoryImpl(
            api = mockApi,
            cache = InMemoryTaskCache() // общий in-memory кеш для тестов
        )
    }

    @Test
    fun `getTasks возвращает кэш при ошибке сети`() = runTest {
        // Given
        val cached = listOf(Task(id = "1", title = "Cached"))
        repository.updateCache(cached)
        coEvery { mockApi.fetchTasks() } throws NetworkException()

        // When
        val result = repository.getTasks()

        // Then
        assertTrue(result.isSuccess)
        assertEquals(cached, result.getOrNull())
    }
}
```

Примечание: чтобы этот пример корректно работал как общий тест, используйте либо KMP-совместимую версию мок-библиотеки, либо замените `mockk()` на фейк/тестовую реализацию `TaskApi`, описанную в общем коде.

**Тестирование `Flow` с Turbine:**

```kotlin
class ObserveTasksTest {
    private lateinit var repository: TaskRepository

    @BeforeTest
    fun setup() {
        repository = TaskRepositoryImpl(
            api = FakeApi(),
            cache = InMemoryTaskCache()
        )
    }

    @Test
    fun `observeTasks эмитит обновления`() = runTest {
        repository.observeTasks().test {
            assertEquals(emptyList<Task>(), awaitItem())

            repository.addTask(Task(id = "1", title = "New"))

            val updated = awaitItem()
            assertEquals(1, updated.size)

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

### Мокирование Платформо-специфичного Кода

Для платформо-специфичных зависимостей в общем коде вместо прямых вызовов используйте `expect/actual` и внедрение зависимостей.

**Expect/Actual для тестовых драйверов БД:**

```kotlin
// Общий тестовый контракт - размещается в общем test source set,
// который компонуется для всех целевых платформ (например, commonTest)
expect class TestDatabaseDriver() {
    fun createInMemoryDriver(): SqlDriver
}

// androidUnitTest - реализация (пример с SQLDelight)
actual class TestDatabaseDriver {
    actual fun createInMemoryDriver(): SqlDriver {
        return JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY).also { driver ->
            TaskDatabase.Schema.create(driver)
        }
    }
}

// iosTest - реализация (пример с SQLDelight)
actual class TestDatabaseDriver {
    actual fun createInMemoryDriver(): SqlDriver {
        return NativeSqliteDriver(TaskDatabase.Schema, name = "test.db")
    }
}
```

**Использование в общих тестах:**

```kotlin
class TaskDatabaseTest {
    private lateinit var driver: SqlDriver
    private lateinit var database: TaskDatabase

    @BeforeTest
    fun setup() {
        driver = TestDatabaseDriver().createInMemoryDriver()
        database = TaskDatabase(driver)
    }

    @Test
    fun `insertTask сохраняет задачу`() {
        val task = Task(id = "1", title = "Test")
        database.taskQueries.insertTask(task.id, task.title)

        val retrieved = database.taskQueries.selectById("1").executeAsOne()
        assertEquals(task.id, retrieved.id)
        assertEquals(task.title, retrieved.title)
    }
}
```

**Фейки для платформенных API:**

```kotlin
// Общий fake для expect/actual PlatformLogger
class FakeLogger : PlatformLogger {
    private val logs = mutableListOf<String>()

    override fun log(message: String) {
        logs.add(message)
    }

    fun assertLogged(substring: String) {
        assertTrue(logs.any { it.contains(substring) })
    }
}
```

### Тестирование Корутин

Общий подход — передавать абстракцию диспетчеров (например, `CoroutineDispatchers`) и подменять их тестовыми в `commonTest`.

```kotlin
object TestDispatchers : CoroutineDispatchers {
    override val main = StandardTestDispatcher()
    override val io = StandardTestDispatcher()
}

@Test
fun `loadTasks обновляет состояние`() = runTest {
    val viewModel = TaskViewModel(
        repository = FakeTaskRepository(),
        dispatchers = TestDispatchers
    )

    viewModel.loadTasks()
    advanceUntilIdle() // Ждем завершения корутин

    assertEquals(LoadingState.Success, viewModel.state.value)
}
```

### Платформо-специфичные Тесты

**Android (инструментальные / JVM):**

Платформенный код (например, работа с `Context`, `SharedPreferences`, файлами) тестируется в `androidUnitTest` (JVM unit-тесты) или `androidTest` (инструментальные тесты на устройстве/эмуляторе).

```kotlin
// Не используйте реальный Context в commonTest
// Используйте его в androidUnitTest / androidTest
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

Для JVM-юнит тестов Android-кода можно использовать Robolectric с `@RunWith(RobolectricTestRunner::class)`.

**iOS:**

iOS-специфичные реализации (например, Keychain, NSUserDefaults) тестируются в `iosTest` с использованием Kotlin/Native тест-раннера или Xcode-проекта, в который интегрирован общий модуль.

```kotlin
class IOSKeychainTest {
    @Test
    fun testIOSSpecificFeature() {
        // Вызов iOS-специфичной реализации expect/actual и проверка поведения
    }
}
```

### Best Practices

**Организация:**
- Максимизируйте долю логики и тестов в `commonTest`.
- Используйте платформо-специфичные тесты только для платформенного кода.
- Группируйте тесты по функциональности/модулю.

**Покрытие:**
- Стремитесь к высокому покрытию (особенно общего кода).
- Тестируйте позитивные и негативные сценарии.
- Для сложных зависимостей используйте фейки и тестовые реализации через DI и `expect/actual`.

**Производительность:**
- Избегайте реальных сетевых вызовов и тяжелых ресурсов.
- Используйте in-memory базы данных.
- Следите, чтобы тесты были быстрыми и детерминированными.

---

## Answer (EN)

KMM testing centers on maximizing shared code and shared tests in `commonTest`, with platform-specific tests in dedicated source sets. Use `kotlin.test` for assertions and multiplatform-friendly mocking libraries. JVM-only mocking libraries (such as the standard `io.mockk:mockk`) should be added only to JVM/Android test source sets.

See also: [[moc-android]]

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
                // Use only multiplatform-compatible dependencies here;
                // JVM-only libraries (e.g., io.mockk:mockk) belong in JVM-specific source sets
            }
        }

        val androidUnitTest by getting {
            dependencies {
                implementation(kotlin("test-junit"))
                implementation("androidx.test:core")
                implementation("io.mockk:mockk") // JVM-only; safe in Android/JVM tests
            }
        }

        // iosTest is configured via the KMP plugin; it reuses commonTest and can add iOS-specific dependencies
    }
}
```

Directory layout:

```text
shared/src/
  commonTest/kotlin/         # Shared tests (all platforms)
  androidUnitTest/kotlin/    # Android-specific unit tests (JVM)
  iosTest/kotlin/            # iOS-specific tests
```

### Unit Testing in commonTest

Put repository, use-case, and business-logic tests in `commonTest` so they run on each target.

**Repository test example:**

```kotlin
// Shared test - should run on all supported targets
class TaskRepositoryTest {
    private lateinit var repository: TaskRepository
    private lateinit var mockApi: TaskApi

    @BeforeTest
    fun setup() {
        mockApi = mockk()
        repository = TaskRepositoryImpl(
            api = mockApi,
            cache = InMemoryTaskCache()
        )
    }

    @Test
    fun `getTasks returns cache on network error`() = runTest {
        // Given
        val cached = listOf(Task(id = "1", title = "Cached"))
        repository.updateCache(cached)
        coEvery { mockApi.fetchTasks() } throws NetworkException()

        // When
        val result = repository.getTasks()

        // Then
        assertTrue(result.isSuccess)
        assertEquals(cached, result.getOrNull())
    }
}
```

Note: for this to be a truly shared test, use a KMP-compatible mocking solution or replace `mockk()` with a fake/test implementation of `TaskApi` defined in shared code.

**`Flow` testing with Turbine:**

```kotlin
class ObserveTasksTest {
    private lateinit var repository: TaskRepository

    @BeforeTest
    fun setup() {
        repository = TaskRepositoryImpl(
            api = FakeApi(),
            cache = InMemoryTaskCache()
        )
    }

    @Test
    fun `observeTasks emits updates`() = runTest {
        repository.observeTasks().test {
            assertEquals(emptyList<Task>(), awaitItem())

            repository.addTask(Task(id = "1", title = "New"))

            val updated = awaitItem()
            assertEquals(1, updated.size)

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

### Mocking Platform-Specific Code

For platform-specific dependencies used from shared code, use `expect/actual` declarations and dependency injection instead of direct platform API calls.

**Expect/Actual for test database driver:**

```kotlin
// Shared test contract - placed in a shared test source set
// that is compiled for all relevant targets (e.g., commonTest)
expect class TestDatabaseDriver() {
    fun createInMemoryDriver(): SqlDriver
}

// androidUnitTest - implementation (SQLDelight example)
actual class TestDatabaseDriver {
    actual fun createInMemoryDriver(): SqlDriver {
        return JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY).also { driver ->
            TaskDatabase.Schema.create(driver)
        }
    }
}

// iosTest - implementation (SQLDelight example)
actual class TestDatabaseDriver {
    actual fun createInMemoryDriver(): SqlDriver {
        return NativeSqliteDriver(TaskDatabase.Schema, name = "test.db")
    }
}
```

**Usage in shared tests:**

```kotlin
class TaskDatabaseTest {
    private lateinit var driver: SqlDriver
    private lateinit var database: TaskDatabase

    @BeforeTest
    fun setup() {
        driver = TestDatabaseDriver().createInMemoryDriver()
        database = TaskDatabase(driver)
    }

    @Test
    fun `insertTask stores task`() {
        val task = Task(id = "1", title = "Test")
        database.taskQueries.insertTask(task.id, task.title)

        val retrieved = database.taskQueries.selectById("1").executeAsOne()
        assertEquals(task.id, retrieved.id)
        assertEquals(task.title, retrieved.title)
    }
}
```

**Fakes for platform APIs:**

```kotlin
// Shared fake for an expect/actual PlatformLogger
class FakeLogger : PlatformLogger {
    private val logs = mutableListOf<String>()

    override fun log(message: String) {
        logs.add(message)
    }

    fun assertLogged(substring: String) {
        assertTrue(logs.any { it.contains(substring) })
    }
}
```

### `Coroutine` Testing

`Inject` a dispatcher provider (e.g., `CoroutineDispatchers`) and use test dispatchers in `commonTest`.

```kotlin
object TestDispatchers : CoroutineDispatchers {
    override val main = StandardTestDispatcher()
    override val io = StandardTestDispatcher()
}

@Test
fun `loadTasks updates state`() = runTest {
    val viewModel = TaskViewModel(
        repository = FakeTaskRepository(),
        dispatchers = TestDispatchers
    )

    viewModel.loadTasks()
    advanceUntilIdle()

    assertEquals(LoadingState.Success, viewModel.state.value)
}
```

### Platform-Specific Tests

**Android:**

Use `androidUnitTest` (JVM unit tests) or `androidTest` (instrumented tests on device/emulator) for Android-specific code (`Context`, `SharedPreferences`, files, etc.).

```kotlin
// Don't use real Context in commonTest
// Use it in androidUnitTest / androidTest
@RunWith(AndroidJUnit4::class)
class AndroidPreferencesTest {
    private lateinit var context: Context

    @Before
    fun setup() {
        context = ApplicationProvider.getApplicationContext()
    }

    @Test
    fun `saveToken persists token`() {
        val prefs = AndroidPreferences(context)
        prefs.saveToken("token")

        assertEquals("token", prefs.getToken())
    }
}
```

For JVM-only tests of Android code, Robolectric can be used with `@RunWith(RobolectricTestRunner::class)`.

**iOS:**

Test iOS-specific implementations (Keychain, NSUserDefaults, etc.) in `iosTest` using the Kotlin/Native test runner or via Xcode integration.

```kotlin
class IOSKeychainTest {
    @Test
    fun testIOSSpecificFeature() {
        // Call iOS-specific expect/actual implementation and assert behavior
    }
}
```

### Best Practices

**Organization:**
- Maximize shared logic and tests in `commonTest`.
- Use platform-specific test source sets only for platform-dependent code.
- Group tests by feature/module.

**Coverage:**
- Aim for high coverage of shared code.
- Test both success and failure paths.
- Prefer fakes and test implementations via DI and `expect/actual` for complex dependencies.

**Performance:**
- Avoid real network calls and heavy resources in tests.
- Use in-memory databases where possible.
- Keep tests fast, deterministic, and reliable.

---

## Follow-ups

- How to test expect/actual implementations separately?
- What are best practices for testing the network layer in KMM?
- How to implement screenshot testing across platforms?
- When to use fakes vs mocks in KMM tests?
- How to optimize test execution time in large KMM projects?

## References

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
