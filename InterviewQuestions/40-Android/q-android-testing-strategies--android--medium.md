---
id: 20251012-122775
title: Android Testing Strategies / Стратегии тестирования Android
aliases:
- Android Testing Strategies
- Стратегии тестирования Android
topic: android
subtopics:
- testing-unit
- testing-instrumented
- testing-ui
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-android-performance-measurement-tools--android--medium
- q-android-architectural-patterns--android--medium
- q-android-security-best-practices--android--medium
created: 2025-10-15
updated: 2025-10-15
tags:
- android/testing-unit
- android/testing-instrumented
- android/testing-ui
- testing
- junit
- espresso
- mockito
- quality-assurance
- difficulty/medium
---# Вопрос (RU)
> Какие методы тестирования используются в Android кроме UI тестов?

---

# Question (EN)
> What testing methods are used in Android besides UI tests?

## Ответ (RU)

**Стратегии тестирования Android** обеспечивают комплексную проверку качества через несколько уровней тестирования и автоматизированные инструменты валидации.

**Теория стратегий тестирования:**
Тестирование Android следует тестовой пирамиде: 70% модульных тестов, 20% интеграционных тестов, 10% UI тестов. Каждый уровень проверяет разные аспекты поведения и качества приложения.

**1. Модульные тесты:**
Тестируют отдельные компоненты в изоляции с использованием JVM без Android зависимостей.

```kotlin
// Модульный тест ViewModel
class UserViewModelTest {
    @Test
    fun `loadUsers should update LiveData`() = runTest {
        val repository = mockk<UserRepository>()
        val viewModel = UserViewModel(repository)
        val users = listOf(User(1, "Alice", "alice@example.com"))

        coEvery { repository.getUsers() } returns users
        viewModel.loadUsers()

        assertEquals(users, viewModel.users.value)
    }
}

// Тест бизнес-логики
class CalculatorTest {
    @Test
    fun `add should return sum`() {
        val calculator = Calculator()
        assertEquals(8, calculator.add(5, 3))
    }
}
```

**2. Интеграционные тесты:**
Тестируют взаимодействие модулей с использованием Robolectric или инструментированных тестов.

```kotlin
// Интеграционный тест Robolectric
@RunWith(RobolectricTestRunner::class)
class MainActivityTest {
    @Test
    fun `button click should update text`() {
        val activity = Robolectric.buildActivity(MainActivity::class.java).create().get()
        val button = activity.findViewById<Button>(R.id.button)
        val textView = activity.findViewById<TextView>(R.id.textView)

        button.performClick()

        assertEquals("Button clicked!", textView.text.toString())
    }
}

// Интеграция с Room Database
@RunWith(AndroidJUnit4::class)
class UserDaoTest {
    @Test
    fun insertAndRetrieveUser() = runBlocking {
        val database = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java).build()
        val userDao = database.userDao()
        val user = User(1, "Alice", "alice@example.com")

        userDao.insertUser(user)
        val retrieved = userDao.getAllUsers()

        assertEquals(1, retrieved.size)
        assertEquals(user, retrieved[0])
    }
}
```

**3. UI тесты (Инструментированные):**
Тестируют полные пользовательские сценарии на реальных устройствах или эмуляторах.

```kotlin
@RunWith(AndroidJUnit4::class)
class LoginActivityTest {
    @Test
    fun loginWithValidCredentials_shouldNavigateToHome() {
        onView(withId(R.id.emailEditText))
            .perform(typeText("user@example.com"), closeSoftKeyboard())
        onView(withId(R.id.passwordEditText))
            .perform(typeText("password123"), closeSoftKeyboard())
        onView(withId(R.id.loginButton)).perform(click())

        onView(withId(R.id.homeScreen)).check(matches(isDisplayed()))
    }
}
```

**4. Тесты производительности:**
Измеряют производительность приложения под нагрузкой с использованием Benchmark Library.

```kotlin
@RunWith(AndroidJUnit4::class)
class DatabaseBenchmark {
    @Test
    fun insert1000Users_benchmark() {
        val users = (1..1000).map { User(it, "User$it", "user$it@example.com") }

        val startTime = System.currentTimeMillis()
        runBlocking { users.forEach { userDao.insertUser(it) } }
        val duration = System.currentTimeMillis() - startTime

        assertTrue("Insert took too long: ${duration}ms", duration < 5000)
    }
}
```

**5. Статический анализ:**
Автоматизированные проверки качества кода с использованием Lint, Detekt и SonarQube.

**6. Тесты безопасности:**
Проверяют меры безопасности включая обфускацию ProGuard и закрепление сертификатов.

**7. Snapshot тесты:**
Проверяют консистентность UI с использованием инструментов скриншотного тестирования.

**Тестовая пирамида:**
- **Модульные тесты (70%)**: Быстрые, надежные, тестируют бизнес-логику
- **Интеграционные тесты (20%)**: Тестируют взаимодействие модулей
- **UI тесты (10%)**: Тестируют полные пользовательские сценарии

**Лучшие практики:**
- Используйте паттерн Given-When-Then
- Держите тесты независимыми
- Стремитесь к покрытию модульных тестов 70-80%
- Мокайте внешние зависимости
- Тестируйте граничные случаи и условия ошибок

---

## Answer (EN)

**Android Testing Strategies** provide comprehensive quality assurance through multiple testing layers and automated validation tools.

**Testing Strategies Theory:**
Android testing follows the testing pyramid: 70% unit tests, 20% integration tests, 10% UI tests. Each layer validates different aspects of application behavior and quality.

**1. Unit Tests:**
Test individual components in isolation using JVM without Android dependencies.

```kotlin
// ViewModel Unit Test
class UserViewModelTest {
    @Test
    fun `loadUsers should update LiveData`() = runTest {
        val repository = mockk<UserRepository>()
        val viewModel = UserViewModel(repository)
        val users = listOf(User(1, "Alice", "alice@example.com"))

        coEvery { repository.getUsers() } returns users
        viewModel.loadUsers()

        assertEquals(users, viewModel.users.value)
    }
}

// Business Logic Test
class CalculatorTest {
    @Test
    fun `add should return sum`() {
        val calculator = Calculator()
        assertEquals(8, calculator.add(5, 3))
    }
}
```

**2. Integration Tests:**
Test module interactions using Robolectric or instrumented tests.

```kotlin
// Robolectric Integration Test
@RunWith(RobolectricTestRunner::class)
class MainActivityTest {
    @Test
    fun `button click should update text`() {
        val activity = Robolectric.buildActivity(MainActivity::class.java).create().get()
        val button = activity.findViewById<Button>(R.id.button)
        val textView = activity.findViewById<TextView>(R.id.textView)

        button.performClick()

        assertEquals("Button clicked!", textView.text.toString())
    }
}

// Room Database Integration
@RunWith(AndroidJUnit4::class)
class UserDaoTest {
    @Test
    fun insertAndRetrieveUser() = runBlocking {
        val database = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java).build()
        val userDao = database.userDao()
        val user = User(1, "Alice", "alice@example.com")

        userDao.insertUser(user)
        val retrieved = userDao.getAllUsers()

        assertEquals(1, retrieved.size)
        assertEquals(user, retrieved[0])
    }
}
```

**3. UI Tests (Instrumented):**
Test complete user flows on real devices or emulators.

```kotlin
@RunWith(AndroidJUnit4::class)
class LoginActivityTest {
    @Test
    fun loginWithValidCredentials_shouldNavigateToHome() {
        onView(withId(R.id.emailEditText))
            .perform(typeText("user@example.com"), closeSoftKeyboard())
        onView(withId(R.id.passwordEditText))
            .perform(typeText("password123"), closeSoftKeyboard())
        onView(withId(R.id.loginButton)).perform(click())

        onView(withId(R.id.homeScreen)).check(matches(isDisplayed()))
    }
}
```

**4. Performance Tests:**
Measure application performance under load using Benchmark Library.

```kotlin
@RunWith(AndroidJUnit4::class)
class DatabaseBenchmark {
    @Test
    fun insert1000Users_benchmark() {
        val users = (1..1000).map { User(it, "User$it", "user$it@example.com") }

        val startTime = System.currentTimeMillis()
        runBlocking { users.forEach { userDao.insertUser(it) } }
        val duration = System.currentTimeMillis() - startTime

        assertTrue("Insert took too long: ${duration}ms", duration < 5000)
    }
}
```

**5. Static Analysis:**
Automated code quality checks using Lint, Detekt, and SonarQube.

**6. Security Tests:**
Validate security measures including ProGuard obfuscation and certificate pinning.

**7. Snapshot Tests:**
Verify UI consistency using screenshot testing tools.

**Testing Pyramid:**
- **Unit Tests (70%)**: Fast, reliable, test business logic
- **Integration Tests (20%)**: Test module interactions
- **UI Tests (10%)**: Test complete user flows

**Best Practices:**
- Use Given-When-Then pattern
- Keep tests independent
- Aim for 70-80% unit test coverage
- Mock external dependencies
- Test edge cases and error conditions

## Follow-ups

- How do you test coroutines and Flow in Android?
- What's the difference between Robolectric and instrumented tests?
- How do you measure test coverage in Android projects?
- What are the best practices for mocking in Android tests?

## References

- [[c-testing]]
- [Android Testing Guide](https://developer.android.com/training/testing)
- [Testing Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)

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

