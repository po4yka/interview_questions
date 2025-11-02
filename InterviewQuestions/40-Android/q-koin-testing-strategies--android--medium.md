---
id: android-610
title: Koin Testing Strategies / Стратегии тестирования Koin
aliases:
  - Koin Testing Strategies
  - Тестирование модулей Koin
topic: android
subtopics:
  - di-koin
  - testing
  - architecture-clean
question_kind: android
difficulty: medium
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-dependency-injection
  - q-koin-fundamentals--android--medium
  - q-koin-scope-management--android--medium
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/di-koin
  - android/testing
  - dependency-injection
  - koin
  - difficulty/medium
sources:
  - url: https://insert-koin.io/docs/reference/koin-test/testing
    note: Official Koin testing guide
  - url: https://insert-koin.io/docs/reference/koin-android/check-modules
    note: checkModules usage and tips
---

# Вопрос (RU)
> Как организовать тестирование модулей Koin? Покажите стратегии для юнит-тестов, инструментальных тестов и проверки графа зависимостей.

# Question (EN)
> How do you test Koin modules? Demonstrate strategies for unit tests, instrumented tests, and validating the dependency graph.

---

## Ответ (RU)

Тестирование Koin строится вокруг трёх задач: **валидация графа зависимостей**, **подмена зависимостей** и **контроль жизненного цикла**. Koin предоставляет утилиты `checkModules`, `KoinTestRule`, `declare` и `loadKoinModules`, которые позволяют тестам оставаться изолированными и быстрыми.

### 1. Валидация графа модулей (checkModules)

```kotlin
class AppModulesTest {

    @Test
    fun `модули проходят проверку зависимостей`() {
        koinApplication {
            modules(listOf(networkModule, dataModule, domainModule, presentationModule))
        }.checkModules {
            // ✅ Явно объявляем entry-point, иначе модуль не проверит injections в Activity/Fragment
            withInstance<Context>(mockk(relaxed = true))
            withInstance<SharedPreferences>(mockk())
        }
    }
}
```

- `koinApplication` создаёт изолированный контейнер для теста.
- `checkModules` разворачивает граф и проверяет, что все зависимости могут быть разрешены.
- `withInstance` добавляет runtime-артефакты (например, `Context`), без которых проверка упадёт.

### 2. Юнит-тесты с KoinTestRule

```kotlin
class UserRepositoryTest : KoinTest {

    @get:Rule
    val koinRule = KoinTestRule.create {
        modules(
            module {
                single<UserApi> { mockk(relaxed = true) }
                single<UserDatabase> { mockk(relaxed = true) }
                single<UserRepository> { UserRepositoryImpl(get(), get()) }
            }
        )
    }

    private val repository: UserRepository by inject()

    @Test
    fun `возвращает кеш при сетевой ошибке`() = runTest {
        coEvery { repository.getUser("42") } returns Result.success(User("42"))

        val result = repository.getUser("42")

        assertTrue(result.isSuccess)
    }
}
```

- `KoinTestRule` гарантирует старт/останов Koin перед и после теста.
- `inject()` даёт ленивый доступ к зависимостям.
- Для корутин используйте `runTest` и mockk `coEvery`.

### 3. Подмена зависимостей во время теста (`declare`, `loadKoinModules`)

```kotlin
class DashboardViewModelTest : KoinTest {

    private val fakeMetrics = FakeMetricsService()
    private val overrideModule = module {
        single<MetricsService> { fakeMetrics }
    }

    @Before
    fun setup() {
        loadKoinModules(overrideModule)
    }

    @After
    fun tearDown() {
        unloadKoinModules(overrideModule)
        stopKoin() // ✅ очищаем контейнер, иначе возможны утечки между тестами
    }

    @Test
    fun `отправляет событие при загрузке`() = runTest {
        declare {
            single<UserRepository> { FakeUserRepository() }
        }

        val viewModel: DashboardViewModel by inject()

        viewModel.load()

        assertTrue(fakeMetrics.events.contains("dashboard_opened"))
    }
}
```

- `loadKoinModules` загружает дополнительные тестовые определения.
- `declare` позволяет переопределить single/factory «на лету».
- Не забывайте `stopKoin()` или `closeKoin()` в `@After`, если вы модифицируете глобальный контейнер.

### 4. Инструментальные тесты с KoinTestRule

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
- После тестов правило автоматически останавливает Koin.

### 5. Практики для стабильных тестов

- **Изоляция**: каждый тест должен стартовать Koin с минимальным набором модулей.
- **Быстрый teardown**: всегда очищайте контейнеры (`stopKoin`, `unloadKoinModules`).
- **Параметры**: используйте `parametersOf` для runtime данных.
- **Валидация**: автоматизируйте `checkModules` в CI.
- **Delegates**: избегайте глобальных `by inject()` в тестируемых классах; предпочтительнее конструктор DI.

---

## Answer (EN)

Testing Koin spans three goals: **validating the graph**, **overriding dependencies**, and **controlling lifecycle**. Koin ships helpers such as `checkModules`, `KoinTestRule`, `declare`, and `loadKoinModules` to keep tests isolated and deterministic.

### 1. Validate modules with checkModules

```kotlin
class AppModulesTest {

    @Test
    fun `modules pass dependency verification`() {
        koinApplication {
            modules(listOf(networkModule, dataModule, domainModule, presentationModule))
        }.checkModules {
            withInstance<Context>(mockk(relaxed = true))
            withInstance<SharedPreferences>(mockk())
        }
    }
}
```

- `koinApplication` builds an isolated container for the test.
- `checkModules` spins the graph and ensures every dependency resolves.
- `withInstance` injects runtime artifacts (like `Context`) the framework cannot instantiate.

### 2. Unit tests with KoinTestRule

```kotlin
class UserRepositoryTest : KoinTest {

    @get:Rule
    val koinRule = KoinTestRule.create {
        modules(
            module {
                single<UserApi> { mockk(relaxed = true) }
                single<UserDatabase> { mockk(relaxed = true) }
                single<UserRepository> { UserRepositoryImpl(get(), get()) }
            }
        )
    }

    private val repository: UserRepository by inject()

    @Test
    fun `returns cached data on network failure`() = runTest {
        coEvery { repository.getUser("42") } returns Result.success(User("42"))

        val result = repository.getUser("42")

        assertTrue(result.isSuccess)
    }
}
```

- `KoinTestRule` handles starting/stopping Koin around each test.
- `inject()` gives lazy access to the dependency graph.
- Combine with `runTest` and `coEvery` for coroutine-friendly assertions.

### 3. Override definitions (`declare`, `loadKoinModules`)

```kotlin
class DashboardViewModelTest : KoinTest {

    private val fakeMetrics = FakeMetricsService()
    private val overrideModule = module {
        single<MetricsService> { fakeMetrics }
    }

    @Before
    fun setup() {
        loadKoinModules(overrideModule)
    }

    @After
    fun tearDown() {
        unloadKoinModules(overrideModule)
        stopKoin()
    }

    @Test
    fun `emits analytics event on load`() = runTest {
        declare {
            single<UserRepository> { FakeUserRepository() }
        }

        val viewModel: DashboardViewModel by inject()

        viewModel.load()

        assertTrue(fakeMetrics.events.contains("dashboard_opened"))
    }
}
```

- `loadKoinModules` loads additional test modules.
- `declare` lets you override bindings on the fly.
- Clean up with `stopKoin`/`unloadKoinModules` to avoid leakage between tests.

### 4. Instrumented tests with KoinTestRule

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
- The rule tears Koin down automatically.

### 5. Practices for stable tests

- **Isolation**: start Koin with the smallest set of modules per test.
- **Teardown**: always clear the container (`stopKoin`, `unloadKoinModules`).
- **Parameters**: leverage `parametersOf` for runtime inputs.
- **Validation**: run `checkModules` in CI to catch missing bindings.
- **Delegates**: avoid global `by inject()` in production code; prefer constructor injection.

---

## Follow-ups
- How does `checkModules` behave with dynamic feature modules?
- What are best practices for testing `Scope` definitions in Koin?
- How do you migrate existing Dagger unit tests to Koin?
- How can you combine Koin with MockK or Mockito for integration tests?

## References
- [[c-dependency-injection]]
- https://insert-koin.io/docs/reference/koin-test/testing
- https://insert-koin.io/docs/reference/koin-android/check-modules

## Related Questions
- [[q-koin-fundamentals--android--medium]]
- [[q-koin-scope-management--android--medium]]
- [[q-koin-vs-hilt-comparison--android--medium]]
