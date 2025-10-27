---
id: 20251012-122775
title: Android Testing Strategies / Стратегии тестирования Android
aliases: [Android Testing Strategies, Стратегии тестирования Android]
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
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android/testing-instrumented, android/testing-ui, android/testing-unit, difficulty/medium]
---
# Вопрос (RU)
> Что такое Стратегии тестирования Android?

---

# Question (EN)
> What are Android Testing Strategies?

## Ответ (RU)

**Пирамида тестирования Android:**
- **Unit тесты (70%)**: Тестируют изолированные компоненты на JVM без Android-зависимостей
- **Integration тесты (20%)**: Проверяют взаимодействие модулей (Robolectric, Room)
- **UI тесты (10%)**: Тестируют пользовательские сценарии на реальных устройствах

**Типы тестов:**

**1. Unit-тесты** (JUnit, MockK):
```kotlin
class UserViewModelTest {
    @Test
    fun `loadUsers updates state`() = runTest {
        // ✅ Изолированный тест ViewModel
        val repository = mockk<UserRepository>()
        val viewModel = UserViewModel(repository)

        coEvery { repository.getUsers() } returns listOf(User(1, "Alice"))
        viewModel.loadUsers()

        assertEquals(1, viewModel.users.value?.size)
    }
}
```

**2. Integration-тесты** (Room, Robolectric):
```kotlin
@RunWith(AndroidJUnit4::class)
class UserDaoTest {
    @Test
    fun insertAndRetrieve() = runBlocking {
        // ✅ Тест реальной БД в памяти
        val db = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java).build()
        val user = User(1, "Alice")

        db.userDao().insert(user)
        val result = db.userDao().getAll()

        assertEquals(user, result[0])
    }
}
```

**3. UI-тесты** (Espresso):
```kotlin
@RunWith(AndroidJUnit4::class)
class LoginTest {
    @Test
    fun successfulLogin() {
        // ✅ End-to-end тест UI
        onView(withId(R.id.email)).perform(typeText("user@test.com"))
        onView(withId(R.id.password)).perform(typeText("pass123"))
        onView(withId(R.id.loginBtn)).perform(click())

        onView(withId(R.id.homeScreen)).check(matches(isDisplayed()))
    }
}
```

**Best Practices:**
- Используйте [[c-dependency-injection]] для тестируемости
- Mock внешние зависимости (сеть, БД)
- Независимые тесты без общего состояния
- Покрытие критичных путей 70-80%

---

# Question (EN)
> What are Android Testing Strategies?

## Answer (EN)

**Android Testing Pyramid:**
- **Unit tests (70%)**: Test isolated components on JVM without Android dependencies
- **Integration tests (20%)**: Verify module interactions (Robolectric, Room)
- **UI tests (10%)**: Test user flows on real devices

**Test Types:**

**1. Unit Tests** (JUnit, MockK):
```kotlin
class UserViewModelTest {
    @Test
    fun `loadUsers updates state`() = runTest {
        // ✅ Isolated ViewModel test
        val repository = mockk<UserRepository>()
        val viewModel = UserViewModel(repository)

        coEvery { repository.getUsers() } returns listOf(User(1, "Alice"))
        viewModel.loadUsers()

        assertEquals(1, viewModel.users.value?.size)
    }
}
```

**2. Integration Tests** (Room, Robolectric):
```kotlin
@RunWith(AndroidJUnit4::class)
class UserDaoTest {
    @Test
    fun insertAndRetrieve() = runBlocking {
        // ✅ Real in-memory database test
        val db = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java).build()
        val user = User(1, "Alice")

        db.userDao().insert(user)
        val result = db.userDao().getAll()

        assertEquals(user, result[0])
    }
}
```

**3. UI Tests** (Espresso):
```kotlin
@RunWith(AndroidJUnit4::class)
class LoginTest {
    @Test
    fun successfulLogin() {
        // ✅ End-to-end UI test
        onView(withId(R.id.email)).perform(typeText("user@test.com"))
        onView(withId(R.id.password)).perform(typeText("pass123"))
        onView(withId(R.id.loginBtn)).perform(click())

        onView(withId(R.id.homeScreen)).check(matches(isDisplayed()))
    }
}
```

**Best Practices:**
- Use [[c-dependency-injection]] for testability
- Mock external dependencies (network, database)
- Keep tests independent without shared state
- Target 70-80% coverage of critical paths

## Follow-ups

- How would you design a test strategy for a feature using Jetpack Compose?
- What are the trade-offs between Robolectric and instrumented tests?
- How do you handle flaky UI tests in CI/CD pipelines?
- What metrics beyond code coverage indicate test suite quality?

## References

- [[c-dependency-injection]]
- [Android Testing Guide](https://developer.android.com/training/testing)

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