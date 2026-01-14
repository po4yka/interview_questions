---
id: android-175
title: Android Testing Strategies / Стратегии тестирования Android
aliases:
- Android Testing Strategies
- Стратегии тестирования Android
topic: android
subtopics:
- testing-instrumented
- testing-ui
- testing-unit
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-android-architectural-patterns--android--medium
- q-android-performance-measurement-tools--android--medium
- q-android-security-best-practices--android--medium
- q-integration-testing-strategies--android--medium
- q-koin-testing-strategies--android--medium
- q-tflite-acceleration-strategies--android--hard
created: 2025-10-15
updated: 2025-11-10
sources: []
tags:
- android/testing-instrumented
- android/testing-ui
- android/testing-unit
- difficulty/medium
- testing
anki_cards:
- slug: android-175-0-en
  language: en
  anki_id: 1768363949761
  synced_at: '2026-01-14T09:17:53.136003'
- slug: android-175-0-ru
  language: ru
  anki_id: 1768363949801
  synced_at: '2026-01-14T09:17:53.139144'
---
# Вопрос (RU)
> Какие существуют стратегии тестирования Android приложений и как построить эффективную пирамиду тестов?

---

# Question (EN)
> What are Android testing strategies and how to build an effective testing pyramid?

---

## Ответ (RU)

**Пирамида тестирования Android** распределяет тесты по уровням (проценты примерные, а не жёсткое правило):
- **Unit тесты (~70%)** — быстрые JVM-тесты бизнес-логики без Android Framework
- **Integration тесты (~20%)** — проверка взаимодействия между слоями и с Android компонентами (`Room`, `WorkManager` и т.п.)
- **UI тесты (~10%)** — end-to-end сценарии на эмуляторах/устройствах

### 1. Unit-тесты

Тестируют изолированную логику на JVM (без эмулятора и без Android Framework):

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {
    private val testDispatcher = StandardTestDispatcher()

    private lateinit var viewModel: UserViewModel
    private val repository: UserRepository = mockk()

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        viewModel = UserViewModel(repository)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `loadUsers updates state on success`() = runTest(testDispatcher) {
        // Fast test without Android dependencies
        coEvery { repository.getUsers() } returns listOf(User("Alice"))

        viewModel.loadUsers()

        assertEquals(LoadState.Success, viewModel.state.value)
        assertEquals("Alice", viewModel.users.value.first().name)
    }

    @Test
    fun `loadUsers sets error state on failure`() = runTest(testDispatcher) {
        // Test edge cases
        coEvery { repository.getUsers() } throws NetworkException()

        viewModel.loadUsers()

        assertTrue(viewModel.state.value is LoadState.Error)
    }
}
```

**Инструменты**: JUnit, MockK, Turbine (для `Flow`), Kotest

### 2. Integration-тесты

Проверяют взаимодействие между слоями и с Android компонентами. Пример для `Room` (инструментальный тест):

```kotlin
@RunWith(AndroidJUnit4::class)
class UserDaoTest {

    private lateinit var database: AppDatabase

    @Before
    fun setup() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        // In-memory БД для изоляции
        database = Room.inMemoryDatabaseBuilder(
            context,
            AppDatabase::class.java
        ).build()
    }

    @After
    fun tearDown() {
        database.close()
    }

    @Test
    fun insertAndQuery() = runBlocking {
        val user = User(id = 1, name = "Bob")
        database.userDao().insert(user)

        val result = database.userDao().getById(1)

        assertEquals("Bob", result?.name)
    }
}
```

**Инструменты**: AndroidX Test, Robolectric (для быстрого локального запуска без устройства), реальная или in-memory `Room` БД в интеграционных тестах

### 3. UI-тесты

Проверяют полные пользовательские сценарии:

```kotlin
@Test
fun loginFlow_successfulAuth_navigatesToHome() {
    // Compose UI Testing
    composeTestRule.setContent {
        LoginScreen(navController)
    }

    composeTestRule
        .onNodeWithTag("email")
        .performTextInput("test@mail.com")

    composeTestRule
        .onNodeWithTag("password")
        .performTextInput("password123")

    composeTestRule
        .onNodeWithText("Login")
        .performClick()

    // Verify navigation / outcome
    composeTestRule
        .onNodeWithText("Home Screen")
        .assertIsDisplayed()
}
```

**Espresso пример** (для `View`-based UI, упрощённый):
```kotlin
@Test
fun clickButton_displaysMessage() {
    // Avoid over-testing UI minutiae
    onView(withId(R.id.button)).perform(click())
    onView(withText("Success")).check(matches(isDisplayed()))
}
```

(Для реальных Toast лучше использовать специализированные matchers или проверять побочные эффекты, а не полагаться на простое `isDisplayed()`.)

**Инструменты**: Compose UI Test, Espresso, UI Automator (для межприложенческого взаимодействия)

### Ключевые Практики

1. **Изоляция через DI** — Hilt/Koin позволяют подменять зависимости в тестах (для `Hilt` инструментальные тесты с `HiltAndroidRule`, для JVM-тестов — обычные конструкторы/модули).
2. **Идемпотентность** — тесты не зависят от порядка выполнения и предыдущего состояния.
3. **Детерминизм** — избегать flaky тестов (жесткие таймауты, race conditions, зависимость от сети/часов).
4. **Стратегии Test Doubles**:
   - Mocks для внешних API
   - Fakes для репозиториев (in-memory реализации)
   - Real-компоненты для тех частей, которые и проверяются в интеграционных тестах (например, `Room` БД); для навигации чаще использовать тестовые/подмененные реализации.
5. **CI-оптимизация** — unit/integration на каждый коммит, UI тесты реже (например, на pull request или перед релизом); ограничения по времени рассматривать как целевые бюджеты, а не жесткие нормы.

---

## Answer (EN)

**Android Testing Pyramid** distributes tests by execution speed and isolation (percentages are indicative, not strict rules):
- **Unit tests (~70%)** — fast JVM tests of business logic without Android Framework
- **Integration tests (~20%)** — verify interactions between layers and with Android components (`Room`, `WorkManager`, etc.)
- **UI tests (~10%)** — end-to-end scenarios on emulators/devices

### 1. Unit Tests

Test isolated logic on JVM (no emulator and no Android Framework):

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {
    private val testDispatcher = StandardTestDispatcher()

    private lateinit var viewModel: UserViewModel
    private val repository: UserRepository = mockk()

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        viewModel = UserViewModel(repository)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `loadUsers updates state on success`() = runTest(testDispatcher) {
        // Fast test without Android dependencies
        coEvery { repository.getUsers() } returns listOf(User("Alice"))

        viewModel.loadUsers()

        assertEquals(LoadState.Success, viewModel.state.value)
        assertEquals("Alice", viewModel.users.value.first().name)
    }

    @Test
    fun `loadUsers sets error state on failure`() = runTest(testDispatcher) {
        // Test edge cases
        coEvery { repository.getUsers() } throws NetworkException()

        viewModel.loadUsers()

        assertTrue(viewModel.state.value is LoadState.Error)
    }
}
```

**Tools**: JUnit, MockK, Turbine (for `Flow`), Kotest

### 2. Integration Tests

Verify interaction between layers and with Android components. Example for `Room` (instrumented test):

```kotlin
@RunWith(AndroidJUnit4::class)
class UserDaoTest {

    private lateinit var database: AppDatabase

    @Before
    fun setup() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        // In-memory database for isolation
        database = Room.inMemoryDatabaseBuilder(
            context,
            AppDatabase::class.java
        ).build()
    }

    @After
    fun tearDown() {
        database.close()
    }

    @Test
    fun insertAndQuery() = runBlocking {
        val user = User(id = 1, name = "Bob")
        database.userDao().insert(user)

        val result = database.userDao().getById(1)

        assertEquals("Bob", result?.name)
    }
}
```

**Tools**: AndroidX Test, Robolectric (for fast local execution without a device), real or in-memory `Room` DB in integration tests

### 3. UI Tests

Verify complete user flows:

```kotlin
@Test
fun loginFlow_successfulAuth_navigatesToHome() {
    // Compose UI Testing
    composeTestRule.setContent {
        LoginScreen(navController)
    }

    composeTestRule
        .onNodeWithTag("email")
        .performTextInput("test@mail.com")

    composeTestRule
        .onNodeWithTag("password")
        .performTextInput("password123")

    composeTestRule
        .onNodeWithText("Login")
        .performClick()

    // Verify navigation / outcome
    composeTestRule
        .onNodeWithText("Home Screen")
        .assertIsDisplayed()
}
```

**Espresso example** (for `View`-based UI, simplified):
```kotlin
@Test
fun clickButton_displaysMessage() {
    // Avoid over-testing UI minutiae
    onView(withId(R.id.button)).perform(click())
    onView(withText("Success")).check(matches(isDisplayed()))
}
```

(For real Toasts, prefer dedicated matchers or asserting side effects instead of relying on a naive `isDisplayed()` check.)

**Tools**: Compose UI Test, Espresso, UI Automator (for cross-app interactions)

### Key Practices

1. **Isolation via DI** — Hilt/Koin enable dependency substitution in tests (use `HiltAndroidRule` for instrumented tests; in JVM tests prefer constructor injection/manual wiring).
2. **Idempotence** — tests must not depend on execution order or previous state.
3. **Determinism** — avoid flaky tests (hard-coded timeouts, race conditions, dependency on real network/clock).
4. **Test Doubles strategies**:
   - Mocks for external APIs
   - Fakes for repositories (in-memory implementations)
   - Real components for what you explicitly validate in integration tests (e.g., `Room` DB); for navigation prefer test/dedicated implementations.
5. **CI optimization** — run unit/integration tests on every commit, UI tests less frequently (e.g., per PR or pre-release); treat time limits as target budgets, not rigid correctness rules.

---

## Дополнительные Вопросы (RU)

1. Как тестировать Compose UI с вынесенным состоянием (state hoisting) и учетом рекомпозиции, какие ключевые edge-case-сценарии нужно покрыть?
2. В чем компромисс между использованием Robolectric и инструментальных тестов с точки зрения скорости, реалистичности окружения и поддержки?
3. Как бороться с flaky UI-тестами в CI, какие техники синхронизации и ретраев использовать?
4. В каких случаях использовать screenshot-тесты, а в каких — поведенческие UI-тесты для проверки сценариев пользователя?
5. Как тестировать корутины и эмиссии `Flow`, чтобы избежать зависимостей от реального времени и гонок?

---

## Follow-ups

1. How do you test Compose UI with state hoisting and recomposition, and which edge cases should be covered?
2. What's the trade-off between Robolectric and instrumented tests regarding speed, environment fidelity, and maintenance?
3. How do you handle flaky UI tests in CI, including synchronization strategies and retries?
4. When should you use screenshot testing vs behavioral UI tests for validating user flows?
5. How do you test coroutines and `Flow` emissions while avoiding reliance on real time and race conditions?

---

## Ссылки (RU)

**Официальная документация**:
- https://developer.android.com/training/testing
- https://developer.android.com/jetpack/compose/testing
- https://developer.android.com/studio/test

**Связанные темы**:
- [[q-android-architectural-patterns--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

---

## References

**Official Documentation**:
- https://developer.android.com/training/testing
- https://developer.android.com/jetpack/compose/testing
- https://developer.android.com/studio/test

**Related Topics**:
- [[q-android-architectural-patterns--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

---

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-testing]]
- [[c-unit-testing]]

### Предпосылки (проще)
- [[q-android-project-parts--android--easy]] — Структура приложения
- [[q-android-app-components--android--easy]] — Базовые компоненты Android

### Связанные (тот Же уровень)
- [[q-android-architectural-patterns--android--medium]] — MVVM/MVI и тестируемость
- [[q-android-performance-measurement-tools--android--medium]] — Профилирование и бенчмаркинг
- [[q-android-security-best-practices--android--medium]] — Подходы к безопасности и их тестирование

### Продвинутые (сложнее)
- [[q-android-runtime-internals--android--hard]] — Глубокое понимание для интеграционных тестов

---

## Related Questions

### Prerequisites / Concepts

- [[c-testing]]
- [[c-unit-testing]]

### Prerequisites (Easier)
- [[q-android-project-parts--android--easy]] — Understanding app structure
- [[q-android-app-components--android--easy]] — Core Android components

### Related (Same Level)
- [[q-android-architectural-patterns--android--medium]] — MVVM/MVI enable testability
- [[q-android-performance-measurement-tools--android--medium]] — Profiling and benchmarking
- [[q-android-security-best-practices--android--medium]] — Security testing strategies

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]] — Deep understanding for integration tests
