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
updated: 2025-10-29
sources: []
tags: [android/testing-unit, android/testing-instrumented, android/testing-ui, testing, junit, espresso, mockk, difficulty/medium]
---
# Вопрос (RU)
> Какие существуют стратегии тестирования Android приложений и как построить эффективную пирамиду тестов?

---

# Question (EN)
> What are Android testing strategies and how to build an effective testing pyramid?

## Ответ (RU)

**Пирамида тестирования Android** распределяет тесты по уровням сложности и скорости выполнения:
- **Unit тесты (70%)** — быстрые JVM-тесты изолированных компонентов
- **Integration тесты (20%)** — проверка взаимодействия модулей
- **UI тесты (10%)** — медленные end-to-end сценарии на устройствах

**1. Unit-тесты** — изолированная логика без Android framework:
```kotlin
class UserViewModelTest {
    @Test
    fun loadUsers_updatesState() = runTest {
        // ✅ Mock зависимостей
        val repo = mockk<UserRepository>()
        coEvery { repo.getUsers() } returns listOf(User("Alice"))

        val vm = UserViewModel(repo)
        vm.loadUsers()

        assertEquals("Alice", vm.users.value?.first()?.name)
    }
}
```

**2. Integration-тесты** — реальные компоненты Android:
```kotlin
@RunWith(AndroidJUnit4::class)
class UserDaoTest {
    @Test
    fun insertAndRetrieve() = runBlocking {
        // ✅ Реальная БД в памяти
        val db = Room.inMemoryDatabaseBuilder(context, DB::class.java).build()

        db.userDao().insert(User("Bob"))
        val users = db.userDao().getAll()

        assertEquals("Bob", users.first().name)
    }
}
```

**3. UI-тесты** — полные пользовательские сценарии:
```kotlin
@Test
fun successfulLogin_navigatesToHome() {
    // ✅ Espresso для UI автоматизации
    onView(withId(R.id.email)).perform(typeText("test@mail.com"))
    onView(withId(R.id.password)).perform(typeText("pass"))
    onView(withId(R.id.loginBtn)).perform(click())

    onView(withId(R.id.homeScreen)).check(matches(isDisplayed()))
}
```

**Ключевые практики:**
- Dependency Injection для замены зависимостей на моки
- Независимые тесты без shared state
- Фокус на критичных путях, не на 100% coverage
- Быстрые unit-тесты для CI, медленные UI — реже

---

# Question (EN)
> What are Android testing strategies and how to build an effective testing pyramid?

## Answer (EN)

**Android Testing Pyramid** distributes tests by complexity and execution speed:
- **Unit tests (70%)** — fast JVM tests of isolated components
- **Integration tests (20%)** — verify module interactions
- **UI tests (10%)** — slow end-to-end scenarios on devices

**1. Unit Tests** — isolated logic without Android framework:
```kotlin
class UserViewModelTest {
    @Test
    fun loadUsers_updatesState() = runTest {
        // ✅ Mock dependencies
        val repo = mockk<UserRepository>()
        coEvery { repo.getUsers() } returns listOf(User("Alice"))

        val vm = UserViewModel(repo)
        vm.loadUsers()

        assertEquals("Alice", vm.users.value?.first()?.name)
    }
}
```

**2. Integration Tests** — real Android components:
```kotlin
@RunWith(AndroidJUnit4::class)
class UserDaoTest {
    @Test
    fun insertAndRetrieve() = runBlocking {
        // ✅ Real in-memory database
        val db = Room.inMemoryDatabaseBuilder(context, DB::class.java).build()

        db.userDao().insert(User("Bob"))
        val users = db.userDao().getAll()

        assertEquals("Bob", users.first().name)
    }
}
```

**3. UI Tests** — complete user scenarios:
```kotlin
@Test
fun successfulLogin_navigatesToHome() {
    // ✅ Espresso for UI automation
    onView(withId(R.id.email)).perform(typeText("test@mail.com"))
    onView(withId(R.id.password)).perform(typeText("pass"))
    onView(withId(R.id.loginBtn)).perform(click())

    onView(withId(R.id.homeScreen)).check(matches(isDisplayed()))
}
```

**Key Practices:**
- Dependency Injection to swap dependencies with mocks
- Independent tests without shared state
- Focus on critical paths, not 100% coverage
- Fast unit tests for CI, slow UI tests less frequently

## Follow-ups

- How do you test Jetpack Compose UI components effectively?
- What are the trade-offs between Robolectric and instrumented tests?
- How do you handle flaky UI tests in CI/CD pipelines?
- When should you use screenshot testing versus UI automation?
- How do you test asynchronous operations with coroutines and Flow?

## References

- [Android Testing Guide](https://developer.android.com/training/testing)
- [Testing on Android Codelab](https://developer.android.com/codelabs/advanced-android-kotlin-training-testing-basics)
- [[q-android-architectural-patterns--android--medium]]

## Related Questions

### Prerequisites (Easier)
- [[q-android-project-parts--android--easy]]
- [[q-android-app-components--android--easy]]

### Related (Same Level)
- [[q-android-performance-measurement-tools--android--medium]]
- [[q-android-architectural-patterns--android--medium]]
- [[q-android-security-best-practices--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]
