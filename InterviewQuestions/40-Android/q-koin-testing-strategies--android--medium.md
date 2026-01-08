---\
id: android-610
title: Koin Testing Strategies / Стратегии тестирования Koin
aliases: [Koin Testing Strategies, Тестирование модулей Koin]
topic: android
subtopics: [architecture-clean, di-koin, testing-unit]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-dependency-injection, q-android-testing-strategies--android--medium, q-integration-testing-strategies--android--medium, q-koin-fundamentals--android--medium, q-koin-scope-management--android--medium, q-tflite-acceleration-strategies--android--hard]
created: 2025-11-02
updated: 2025-11-10
tags: [android/architecture-clean, android/di-koin, android/testing-unit, dependency-injection, difficulty/medium, koin]
sources:
  - "https://insert-koin.io/docs/reference/koin-android/check-modules"
  - "https://insert-koin.io/docs/reference/koin-test/testing"
---\
# Вопрос (RU)
> Как организовать тестирование модулей `Koin`? Покажите стратегии для юнит-тестов, инструментальных тестов и проверки графа зависимостей.

# Question (EN)
> How do you test `Koin` modules? Demonstrate strategies for unit tests, instrumented tests, and validating the dependency graph.

## Ответ (RU)

Тестирование `Koin` строится вокруг трёх задач: **валидация графа зависимостей**, **подмена зависимостей** и **контроль жизненного цикла**. `Koin` предоставляет утилиты `checkModules`, `KoinTestRule`, `loadKoinModules` / `unloadKoinModules` и возможность переопределения модулей, которые позволяют тестам оставаться изолированными и быстрыми.

### 1. Валидация Графа Модулей (checkModules)

```kotlin
class AppModulesTest {

    @Test
    fun `модули проходят проверку зависимостей`() {
        koinApplication {
            modules(listOf(networkModule, dataModule, domainModule, presentationModule))
        }.checkModules {
            // ✅ Явно объявляем entry-point, иначе не будут проверены зависимости, требующие Android-контекста
            withInstance<Context>(mockk(relaxed = true))
            withInstance<SharedPreferences>(mockk())
        }
    }
}
```

- `koinApplication` создаёт изолированный контейнер для теста.
- `checkModules` разворачивает граф и проверяет, что все зависимости могут быть разрешены.
- `withInstance` добавляет runtime-артефакты (например, `Context`), без которых проверка упадёт.

### 2. Юнит-тесты С KoinTestRule

```kotlin
class UserRepositoryTest : KoinTest {

    @get:Rule
    val koinRule = KoinTestRule.create {
        modules(
            module {
                single<UserApi> { mockk(relaxed = true) }
                single<UserDatabase> { mockk(relaxed = true) }
                // Тестируем реальную реализацию, провайдим зависимости через Koin
                single<UserRepository> { UserRepositoryImpl(get(), get()) }
            }
        )
    }

    // В реальном проекте репозиторий обычно внедряется через конструктор;
    // здесь `by inject()` используется как тестовый helper.
    private val repository: UserRepository by inject()

    private val userApi: UserApi by inject()

    @Test
    fun `возвращает кеш при сетевой ошибке`() = runTest {
        // Мокаем зависимость репозитория
        coEvery { userApi.getUser("42") } returns User("42")

        val result = repository.getUser("42")

        assertTrue(result.isSuccess)
    }
}
```

- `KoinTestRule` гарантирует старт/останов `Koin` перед и после теста.
- `inject()` даёт ленивый доступ к зависимостям.
- Для корутин используйте `runTest` и мокайте зависимости (например, через MockK `coEvery`) вместо мокания тестируемого класса.

### 3. Подмена Зависимостей Во Время Теста (override-модули)

```kotlin
class DashboardViewModelTest : KoinTest {

    private val fakeMetrics = FakeMetricsService()
    private val overrideModule = module(override = true) {
        single<MetricsService> { fakeMetrics }
        single<UserRepository> { FakeUserRepository() }
    }

    @get:Rule
    val koinRule = KoinTestRule.create {
        // Здесь подключаются production-модули приложения
        modules(appModules)
    }

    @Before
    fun setup() {
        // Подключаем тестовый модуль, перекрывающий production-определения
        loadKoinModules(overrideModule)
    }

    @After
    fun tearDown() {
        // Удаляем тестовые определения; контейнер управляется KoinTestRule
        unloadKoinModules(overrideModule)
    }

    @Test
    fun `отправляет событие при загрузке`() = runTest {
        val viewModel: DashboardViewModel by inject()

        viewModel.load()

        assertTrue(fakeMetrics.events.contains("dashboard_opened"))
    }
}
```

- `loadKoinModules` загружает дополнительные тестовые определения.
- Используйте `module(override = true)` или соответствующий механизм переопределения (в зависимости от версии `Koin`) для замены production-зависимостей.
- Не дублируйте управление жизненным циклом: если используете `KoinTestRule` или общий `startKoin` в тестовом раннере, не вызывайте `stopKoin()` точечно в каждом таком тесте без необходимости.

### 4. Инструментальные Тесты С KoinTestRule

```kotlin
@RunWith(AndroidJUnit4::class)
class SettingsFragmentTest : KoinTest {

    @get:Rule
    val koinRule = KoinTestRule.create {
        androidContext(ApplicationProvider.getApplicationContext())
        modules(appModules + testingModule)
    }

    @Test
    fun `отображает email пользователя`() {
        launchFragmentInContainer<SettingsFragment>()

        onView(withId(R.id.emailText))
            .check(matches(withText("test@example.com")))
    }
}
```

- Для инструментальных тестов обязательно передать `androidContext`.
- Отдельный `testingModule` содержит фейковые/фиктивные зависимости.
- `KoinTestRule` автоматически управляет запуском и остановкой `Koin`.

### 5. Практики Для Стабильных Тестов

- **Изоляция**: каждый тест (или suite) должен стартовать `Koin` с минимальным набором модулей.
- **Явный lifecycle**: используйте либо `KoinTestRule`, либо явный `startKoin/stopKoin` для всего набора тестов; избегайте конфликтов.
- **Переопределения**: для подмены зависимостей применяйте override-модули (`module(override = true)`, `loadKoinModules`/`unloadKoinModules`).
- **Параметры**: используйте `parametersOf` для runtime-данных.
- **Валидация**: автоматизируйте `checkModules` в CI.
- **Delegates**: избегайте глобальных `by inject()` в production-коде; предпочтительнее конструктор DI.

## Answer (EN)

Testing `Koin` spans three goals: **validating the graph**, **overriding dependencies**, and **controlling lifecycle**. `Koin` ships helpers such as `checkModules`, `KoinTestRule`, `loadKoinModules` / `unloadKoinModules`, and module overrides to keep tests isolated and deterministic.

### 1. Validate Modules with checkModules

```kotlin
class AppModulesTest {

    @Test
    fun `modules pass dependency verification`() {
        koinApplication {
            modules(listOf(networkModule, dataModule, domainModule, presentationModule))
        }.checkModules {
            // ✅ Explicitly provide entry-points like Context when needed
            withInstance<Context>(mockk(relaxed = true))
            withInstance<SharedPreferences>(mockk())
        }
    }
}
```

- `koinApplication` builds an isolated container for the test.
- `checkModules` resolves the graph and ensures every dependency can be created.
- `withInstance` supplies runtime artifacts (like `Context`) that `Koin` cannot instantiate itself.

### 2. Unit Tests with KoinTestRule

```kotlin
class UserRepositoryTest : KoinTest {

    @get:Rule
    val koinRule = KoinTestRule.create {
        modules(
            module {
                single<UserApi> { mockk(relaxed = true) }
                single<UserDatabase> { mockk(relaxed = true) }
                // Test the real implementation wired via Koin
                single<UserRepository> { UserRepositoryImpl(get(), get()) }
            }
        )
    }

    // In real code, prefer constructor injection; `by inject()` here is a test helper.
    private val repository: UserRepository by inject()

    private val userApi: UserApi by inject()

    @Test
    fun `returns cached data on network failure`() = runTest {
        // Mock the repository's dependency rather than the repository itself
        coEvery { userApi.getUser("42") } returns User("42")

        val result = repository.getUser("42")

        assertTrue(result.isSuccess)
    }
}
```

- `KoinTestRule` handles starting/stopping `Koin` around each test.
- `inject()` gives lazy access to dependencies.
- Use `runTest` and mock lower-level dependencies (e.g., via MockK `coEvery`) instead of mocking the class under test.

### 3. Override Definitions with Test Modules

```kotlin
class DashboardViewModelTest : KoinTest {

    private val fakeMetrics = FakeMetricsService()
    private val overrideModule = module(override = true) {
        single<MetricsService> { fakeMetrics }
        single<UserRepository> { FakeUserRepository() }
    }

    @get:Rule
    val koinRule = KoinTestRule.create {
        // Load production modules here
        modules(appModules)
    }

    @Before
    fun setup() {
        // Load a test module that overrides production bindings
        loadKoinModules(overrideModule)
    }

    @After
    fun tearDown() {
        // Remove test bindings; lifecycle is controlled by KoinTestRule
        unloadKoinModules(overrideModule)
    }

    @Test
    fun `emits analytics event on load`() = runTest {
        val viewModel: DashboardViewModel by inject()

        viewModel.load()

        assertTrue(fakeMetrics.events.contains("dashboard_opened"))
    }
}
```

- `loadKoinModules` loads additional test definitions.
- Use `module(override = true)` (or the appropriate override mechanism for your `Koin` version) to replace production dependencies.
- Avoid conflicting lifecycle control: if `KoinTestRule` or a global `startKoin` manages the container, don't call `stopKoin()` for individual tests unless you own that instance.

### 4. Instrumented Tests with KoinTestRule

```kotlin
@RunWith(AndroidJUnit4::class)
class SettingsFragmentTest : KoinTest {

    @get:Rule
    val koinRule = KoinTestRule.create {
        androidContext(ApplicationProvider.getApplicationContext())
        modules(appModules + testingModule)
    }

    @Test
    fun `displays user email`() {
        launchFragmentInContainer<SettingsFragment>()

        onView(withId(R.id.emailText))
            .check(matches(withText("test@example.com")))
    }
}
```

- Instrumented tests must supply `androidContext`.
- Keep a dedicated `testingModule` with fakes/stubs.
- `KoinTestRule` tears `Koin` down automatically.

### 5. Practices for Stable Tests

- **Isolation**: start `Koin` with the smallest set of modules per test or test suite.
- **Explicit lifecycle**: choose either `KoinTestRule` or manual `startKoin/stopKoin` for the whole test run; avoid mixing patterns that fight each other.
- **Overrides**: use override modules (`module(override = true)`, `loadKoinModules`/`unloadKoinModules`) to swap dependencies.
- **Parameters**: leverage `parametersOf` for runtime inputs.
- **Validation**: run `checkModules` in CI to catch missing bindings early.
- **Delegates**: avoid global `by inject()` in production code; prefer constructor injection.

## Follow-ups
- How does `checkModules` behave with dynamic feature modules?
- What are best practices for testing `Scope` definitions in `Koin`?
- How do you migrate existing `Dagger` unit tests to `Koin`?
- How can you combine `Koin` with MockK or Mockito for integration tests?

## References
- [[c-dependency-injection]]
- https://insert-koin.io/docs/reference/koin-test/testing
- https://insert-koin.io/docs/reference/koin-android/check-modules

## Related Questions
- [[q-koin-fundamentals--android--medium]]
- [[q-koin-scope-management--android--medium]]
- [[q-koin-vs-hilt-comparison--android--medium]]
