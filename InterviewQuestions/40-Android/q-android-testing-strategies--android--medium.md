---
id: 20251012-122775
title: Android Testing Strategies / Стратегии тестирования Android
aliases: ["Android Testing Strategies", "Стратегии тестирования Android"]
topic: android
subtopics: [testing-unit, testing-instrumented, testing-ui]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-architectural-patterns--android--medium, q-android-performance-measurement-tools--android--medium, q-android-security-best-practices--android--medium]
created: 2025-10-15
updated: 2025-10-30
sources: []
tags: [android/testing-unit, android/testing-instrumented, android/testing-ui, testing, junit, espresso, mockk, difficulty/medium]
---
# Вопрос (RU)
> Какие существуют стратегии тестирования Android приложений и как построить эффективную пирамиду тестов?

---

# Question (EN)
> What are Android testing strategies and how to build an effective testing pyramid?

---

## Ответ (RU)

**Пирамида тестирования Android** распределяет тесты по уровням:
- **Unit тесты (70%)** — быстрые JVM-тесты бизнес-логики без Android Framework
- **Integration тесты (20%)** — проверка взаимодействия с Android компонентами (Room, WorkManager)
- **UI тесты (10%)** — end-to-end сценарии на эмуляторах/устройствах

### 1. Unit-тесты

Тестируют изолированную логику на JVM (без эмулятора):

```kotlin
class UserViewModelTest {
    private lateinit var viewModel: UserViewModel
    private val repository: UserRepository = mockk()

    @Test
    fun `loadUsers updates state on success`() = runTest {
        // ✅ Быстрый тест без Android зависимостей
        coEvery { repository.getUsers() } returns listOf(User("Alice"))

        viewModel = UserViewModel(repository)
        viewModel.loadUsers()

        assertEquals(LoadState.Success, viewModel.state.value)
        assertEquals("Alice", viewModel.users.value.first().name)
    }

    @Test
    fun `loadUsers sets error state on failure`() = runTest {
        // ✅ Проверка граничных случаев
        coEvery { repository.getUsers() } throws NetworkException()

        viewModel.loadUsers()

        assertTrue(viewModel.state.value is LoadState.Error)
    }
}
```

**Инструменты**: JUnit, MockK, Turbine (для Flow), Kotest

### 2. Integration-тесты

Проверяют взаимодействие с Android компонентами:

```kotlin
@RunWith(AndroidJUnit4::class)
class UserDaoTest {
    private lateinit var database: AppDatabase

    @Before
    fun setup() {
        // ✅ In-memory БД для изоляции
        database = Room.inMemoryDatabaseBuilder(
            context, AppDatabase::class.java
        ).build()
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

**Инструменты**: AndroidX Test, Robolectric (для быстрого локального запуска)

### 3. UI-тесты

Проверяют полные пользовательские сценарии:

```kotlin
@Test
fun loginFlow_successfulAuth_navigatesToHome() {
    // ✅ Compose UI Testing
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

    // ✅ Проверка навигации
    composeTestRule
        .onNodeWithText("Home Screen")
        .assertIsDisplayed()
}
```

**Espresso пример** (для View-based UI):
```kotlin
@Test
fun clickButton_displaysToast() {
    // ❌ Избегать излишнего UI тестирования мелких деталей
    onView(withId(R.id.button)).perform(click())
    onView(withText("Success")).check(matches(isDisplayed()))
}
```

**Инструменты**: Compose UI Test, Espresso, UI Automator (для межприложенческого взаимодействия)

### Ключевые практики

1. **Изоляция через DI** — Hilt/Koin позволяют подменять зависимости в тестах
2. **Идемпотентность** — тесты не зависят от порядка выполнения
3. **Детерминизм** — избегать flaky тестов (таймауты, race conditions)
4. **Test Doubles стратегии**:
   - Mocks для внешних API
   - Fakes для репозиториев (in-memory реализации)
   - Real для критичных компонентов (navigation, database)
5. **CI оптимизация** — unit/integration на каждый коммит, UI тесты перед релизом

---

## Answer (EN)

**Android Testing Pyramid** distributes tests by execution speed and isolation:
- **Unit tests (70%)** — fast JVM tests of business logic without Android Framework
- **Integration tests (20%)** — verify interaction with Android components (Room, WorkManager)
- **UI tests (10%)** — end-to-end scenarios on emulators/devices

### 1. Unit Tests

Test isolated logic on JVM (no emulator required):

```kotlin
class UserViewModelTest {
    private lateinit var viewModel: UserViewModel
    private val repository: UserRepository = mockk()

    @Test
    fun `loadUsers updates state on success`() = runTest {
        // ✅ Fast test without Android dependencies
        coEvery { repository.getUsers() } returns listOf(User("Alice"))

        viewModel = UserViewModel(repository)
        viewModel.loadUsers()

        assertEquals(LoadState.Success, viewModel.state.value)
        assertEquals("Alice", viewModel.users.value.first().name)
    }

    @Test
    fun `loadUsers sets error state on failure`() = runTest {
        // ✅ Test edge cases
        coEvery { repository.getUsers() } throws NetworkException()

        viewModel.loadUsers()

        assertTrue(viewModel.state.value is LoadState.Error)
    }
}
```

**Tools**: JUnit, MockK, Turbine (for Flow), Kotest

### 2. Integration Tests

Verify interaction with Android components:

```kotlin
@RunWith(AndroidJUnit4::class)
class UserDaoTest {
    private lateinit var database: AppDatabase

    @Before
    fun setup() {
        // ✅ In-memory database for isolation
        database = Room.inMemoryDatabaseBuilder(
            context, AppDatabase::class.java
        ).build()
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

**Tools**: AndroidX Test, Robolectric (for fast local execution)

### 3. UI Tests

Verify complete user flows:

```kotlin
@Test
fun loginFlow_successfulAuth_navigatesToHome() {
    // ✅ Compose UI Testing
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

    // ✅ Verify navigation
    composeTestRule
        .onNodeWithText("Home Screen")
        .assertIsDisplayed()
}
```

**Espresso example** (for View-based UI):
```kotlin
@Test
fun clickButton_displaysToast() {
    // ❌ Avoid over-testing UI minutiae
    onView(withId(R.id.button)).perform(click())
    onView(withText("Success")).check(matches(isDisplayed()))
}
```

**Tools**: Compose UI Test, Espresso, UI Automator (for cross-app interactions)

### Key Practices

1. **Isolation via DI** — Hilt/Koin enable dependency substitution in tests
2. **Idempotence** — tests don't depend on execution order
3. **Determinism** — avoid flaky tests (timeouts, race conditions)
4. **Test Doubles strategies**:
   - Mocks for external APIs
   - Fakes for repositories (in-memory implementations)
   - Real for critical components (navigation, database)
5. **CI optimization** — unit/integration on every commit, UI tests before release

---

## Follow-ups

1. **How do you test Compose UI with state hoisting and recomposition?**
   - Use `composeTestRule.mainClock` to control recomposition timing
   - Test state changes via `advanceTimeBy()` for animations

2. **What's the trade-off between Robolectric and instrumented tests?**
   - Robolectric: fast (JVM), limited fidelity, no real sensors/hardware
   - Instrumented: slower, accurate, tests actual device behavior

3. **How do you handle flaky UI tests in CI?**
   - Use `IdlingResource` for async operations
   - Disable animations (`adb shell settings put global animator_duration_scale 0`)
   - Implement retry logic with test orchestrator

4. **When to use screenshot testing vs behavioral UI tests?**
   - Screenshots: visual regression (layout, colors, fonts)
   - Behavioral: user interactions, navigation, state changes

5. **How do you test coroutines and Flow emissions?**
   - `runTest` with `TestDispatcher` for coroutines
   - `Turbine` library for Flow assertions (`test { awaitItem() }`)

6. **How do you test dependency injection in tests?**
   - Hilt: use `@UninstallModules` + `@TestInstallIn` for test modules
   - Koin: `loadKoinModules()` to override production dependencies

7. **What metrics define a good test suite?**
   - Code coverage (70-80% target), not 100%
   - Execution time (unit: <5s, integration: <30s, UI: <2min)
   - Flakiness rate (<5% failures)

## References

**Concept Notes**:
- Testing Pyramid (concept note pending)
- Dependency Injection in Tests (concept note pending)
- Test Doubles Patterns (concept note pending)

**Official Documentation**:
- [Android Testing Guide](https://developer.android.com/training/testing)
- [Compose Testing](https://developer.android.com/jetpack/compose/testing)
- [Test Your App](https://developer.android.com/studio/test)

**Related Topics**:
- [[q-android-architectural-patterns--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

## Related Questions

### Prerequisites (Easier)
- [[q-android-project-parts--android--easy]] — Understanding app structure
- [[q-android-app-components--android--easy]] — Core Android components

### Related (Same Level)
- [[q-android-architectural-patterns--android--medium]] — MVVM/MVI enable testability
- [[q-android-performance-measurement-tools--android--medium]] — Profiling and benchmarking
- [[q-android-security-best-practices--android--medium]] — Security testing strategies

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]] — Deep understanding for integration tests
- Advanced: Testing custom instrumentation and APK analyzer integration
- Advanced: Writing Gradle test plugins for modular test execution
