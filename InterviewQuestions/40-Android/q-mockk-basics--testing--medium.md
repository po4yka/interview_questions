---
id: android-401
title: "MockK Basics / Основы MockK"
aliases: ["MockK Basics", "Основы MockK"]
topic: android
subtopics: [testing-unit, testing]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-testing, q-mockk-vs-mockito--testing--medium, q-test-doubles-dependency-injection--android--medium, q-coroutines-testing--testing--medium]
created: 2026-01-23
updated: 2026-01-23
tags: [android/testing-unit, difficulty/medium, mockk, mocking, kotlin, test-doubles]

---
# Vopros (RU)

> Что такое MockK и как использовать его базовые функции: mockk, every, verify, coEvery?

# Question (EN)

> What is MockK and how do you use its basic functions: mockk, every, verify, coEvery?

---

## Otvet (RU)

**MockK** - это современная библиотека мокирования, созданная специально для Kotlin. Она предоставляет идиоматичный DSL для создания моков, стабов и верификации вызовов с полной поддержкой корутин.

### Краткий Ответ

- `mockk<T>()` - создает мок объекта типа T
- `every { }` - настраивает поведение мока для синхронных функций
- `coEvery { }` - настраивает поведение для suspend-функций
- `verify { }` - проверяет, что метод был вызван
- `coVerify { }` - проверяет вызов suspend-функции

### Подробный Ответ

### Создание Моков

```kotlin
// Базовое создание мока
val userRepository = mockk<UserRepository>()

// Relaxed мок - возвращает значения по умолчанию (0, "", false, null)
val relaxedRepo = mockk<UserRepository>(relaxed = true)

// Relaxed только для Unit-функций
val unitRelaxed = mockk<UserRepository>(relaxUnitFun = true)
```

### Настройка Поведения с every

```kotlin
interface UserRepository {
    fun getUser(id: String): User
    fun getUserOrNull(id: String): User?
    fun saveUser(user: User): Boolean
}

class UserServiceTest {
    private val repository = mockk<UserRepository>()
    private val service = UserService(repository)

    @Test
    fun `getUser returns user from repository`() {
        // Настройка поведения
        every { repository.getUser("123") } returns User("123", "John")

        // Вызов тестируемого кода
        val user = service.getUser("123")

        // Проверка результата
        assertEquals("John", user.name)
    }

    @Test
    fun `getUser with any argument`() {
        // any() - любой аргумент
        every { repository.getUser(any()) } returns User("default", "Default User")

        val user = service.getUser("any-id")
        assertEquals("Default User", user.name)
    }
}
```

### Работа с Аргументами (Matchers)

```kotlin
@Test
fun `argument matchers examples`() {
    val repo = mockk<UserRepository>()

    // Любой аргумент
    every { repo.getUser(any()) } returns User("1", "Any")

    // Конкретное значение
    every { repo.getUser(eq("specific")) } returns User("2", "Specific")

    // Проверка условия
    every { repo.getUser(match { it.startsWith("admin") }) } returns User("3", "Admin")

    // Захват аргумента
    val slot = slot<String>()
    every { repo.getUser(capture(slot)) } returns User("4", "Captured")

    repo.getUser("test-id")
    assertEquals("test-id", slot.captured)
}
```

### Настройка Разных Ответов

```kotlin
@Test
fun `different return behaviors`() {
    val repo = mockk<UserRepository>()

    // Возврат значения
    every { repo.getUser("1") } returns User("1", "John")

    // Возврат null
    every { repo.getUserOrNull("missing") } returns null

    // Выброс исключения
    every { repo.getUser("error") } throws IllegalArgumentException("User not found")

    // Последовательные ответы
    every { repo.getUser("sequence") } returnsMany listOf(
        User("1", "First"),
        User("2", "Second"),
        User("3", "Third")
    )

    // Или через andThen
    every { repo.saveUser(any()) } returns true andThen false andThen true
}
```

### coEvery для Корутин

```kotlin
interface SuspendRepository {
    suspend fun fetchUser(id: String): User
    suspend fun saveUser(user: User)
    fun observeUsers(): Flow<List<User>>
}

class CoroutineTest {
    private val repo = mockk<SuspendRepository>()

    @Test
    fun `test suspend function`() = runTest {
        // coEvery для suspend-функций
        coEvery { repo.fetchUser("123") } returns User("123", "John")

        val user = repo.fetchUser("123")
        assertEquals("John", user.name)
    }

    @Test
    fun `test suspend function with delay`() = runTest {
        coEvery { repo.fetchUser(any()) } coAnswers {
            delay(1000) // Симуляция сетевой задержки
            User("delayed", "Delayed User")
        }

        val user = repo.fetchUser("any")
        assertEquals("Delayed User", user.name)
    }

    @Test
    fun `test suspend function throws`() = runTest {
        coEvery { repo.fetchUser("error") } throws NetworkException("Connection failed")

        assertThrows<NetworkException> {
            repo.fetchUser("error")
        }
    }
}
```

### Верификация с verify

```kotlin
@Test
fun `verify method calls`() {
    val repo = mockk<UserRepository>(relaxed = true)
    val service = UserService(repo)

    service.processUser("123")

    // Проверка, что метод был вызван
    verify { repo.getUser("123") }

    // Проверка с точным количеством вызовов
    verify(exactly = 1) { repo.getUser("123") }

    // Минимум N вызовов
    verify(atLeast = 1) { repo.getUser(any()) }

    // Максимум N вызовов
    verify(atMost = 3) { repo.saveUser(any()) }

    // Метод не был вызван
    verify(exactly = 0) { repo.getUserOrNull(any()) }

    // Или через wasNot Called
    verify { repo.getUserOrNull(any()) wasNot Called }
}
```

### coVerify для Корутин

```kotlin
@Test
fun `verify suspend function calls`() = runTest {
    val repo = mockk<SuspendRepository>(relaxed = true)

    repo.fetchUser("123")
    repo.saveUser(User("123", "John"))

    // coVerify для suspend-функций
    coVerify { repo.fetchUser("123") }
    coVerify { repo.saveUser(match { it.id == "123" }) }

    // Порядок вызовов
    coVerifySequence {
        repo.fetchUser("123")
        repo.saveUser(any())
    }

    // Любой порядок, но все вызовы
    coVerifyAll {
        repo.saveUser(any())
        repo.fetchUser("123")
    }
}
```

### Полный Пример Теста

```kotlin
class UserViewModelTest {
    private val repository = mockk<UserRepository>()
    private lateinit var viewModel: UserViewModel

    @Before
    fun setup() {
        viewModel = UserViewModel(repository)
    }

    @After
    fun tearDown() {
        // Очистка всех моков
        clearAllMocks()
    }

    @Test
    fun `loadUser updates state on success`() = runTest {
        // Given
        val expectedUser = User("123", "John Doe")
        coEvery { repository.fetchUser("123") } returns expectedUser

        // When
        viewModel.loadUser("123")

        // Then
        assertEquals(UiState.Success(expectedUser), viewModel.uiState.value)
        coVerify(exactly = 1) { repository.fetchUser("123") }
    }

    @Test
    fun `loadUser updates state on error`() = runTest {
        // Given
        coEvery { repository.fetchUser(any()) } throws IOException("Network error")

        // When
        viewModel.loadUser("123")

        // Then
        assertTrue(viewModel.uiState.value is UiState.Error)
        coVerify { repository.fetchUser("123") }
    }
}
```

### Зависимости

```kotlin
// build.gradle.kts
dependencies {
    testImplementation("io.mockk:mockk:1.13.10")
    // Для Android instrumented тестов
    androidTestImplementation("io.mockk:mockk-android:1.13.10")
}
```

### Лучшие Практики

1. Используйте `relaxed = true` осторожно - явная настройка лучше
2. Очищайте моки в `@After` с помощью `clearAllMocks()`
3. Используйте `coEvery`/`coVerify` для всех suspend-функций
4. Предпочитайте `slot<T>()` для захвата и проверки аргументов
5. Используйте `verifySequence` для проверки порядка вызовов

---

## Answer (EN)

**MockK** is a modern mocking library built specifically for Kotlin. It provides an idiomatic DSL for creating mocks, stubs, and verifying calls with full coroutine support.

### Short Version

- `mockk<T>()` - creates a mock of type T
- `every { }` - configures mock behavior for synchronous functions
- `coEvery { }` - configures behavior for suspend functions
- `verify { }` - verifies that a method was called
- `coVerify { }` - verifies suspend function calls

### Detailed Version

### Creating Mocks

```kotlin
// Basic mock creation
val userRepository = mockk<UserRepository>()

// Relaxed mock - returns default values (0, "", false, null)
val relaxedRepo = mockk<UserRepository>(relaxed = true)

// Relaxed only for Unit functions
val unitRelaxed = mockk<UserRepository>(relaxUnitFun = true)
```

### Configuring Behavior with every

```kotlin
interface UserRepository {
    fun getUser(id: String): User
    fun getUserOrNull(id: String): User?
    fun saveUser(user: User): Boolean
}

class UserServiceTest {
    private val repository = mockk<UserRepository>()
    private val service = UserService(repository)

    @Test
    fun `getUser returns user from repository`() {
        // Configure behavior
        every { repository.getUser("123") } returns User("123", "John")

        // Call code under test
        val user = service.getUser("123")

        // Verify result
        assertEquals("John", user.name)
    }

    @Test
    fun `getUser with any argument`() {
        // any() - any argument
        every { repository.getUser(any()) } returns User("default", "Default User")

        val user = service.getUser("any-id")
        assertEquals("Default User", user.name)
    }
}
```

### Argument Matchers

```kotlin
@Test
fun `argument matchers examples`() {
    val repo = mockk<UserRepository>()

    // Any argument
    every { repo.getUser(any()) } returns User("1", "Any")

    // Specific value
    every { repo.getUser(eq("specific")) } returns User("2", "Specific")

    // Condition check
    every { repo.getUser(match { it.startsWith("admin") }) } returns User("3", "Admin")

    // Capture argument
    val slot = slot<String>()
    every { repo.getUser(capture(slot)) } returns User("4", "Captured")

    repo.getUser("test-id")
    assertEquals("test-id", slot.captured)
}
```

### Different Return Behaviors

```kotlin
@Test
fun `different return behaviors`() {
    val repo = mockk<UserRepository>()

    // Return value
    every { repo.getUser("1") } returns User("1", "John")

    // Return null
    every { repo.getUserOrNull("missing") } returns null

    // Throw exception
    every { repo.getUser("error") } throws IllegalArgumentException("User not found")

    // Sequential answers
    every { repo.getUser("sequence") } returnsMany listOf(
        User("1", "First"),
        User("2", "Second"),
        User("3", "Third")
    )

    // Or using andThen
    every { repo.saveUser(any()) } returns true andThen false andThen true
}
```

### coEvery for Coroutines

```kotlin
interface SuspendRepository {
    suspend fun fetchUser(id: String): User
    suspend fun saveUser(user: User)
    fun observeUsers(): Flow<List<User>>
}

class CoroutineTest {
    private val repo = mockk<SuspendRepository>()

    @Test
    fun `test suspend function`() = runTest {
        // coEvery for suspend functions
        coEvery { repo.fetchUser("123") } returns User("123", "John")

        val user = repo.fetchUser("123")
        assertEquals("John", user.name)
    }

    @Test
    fun `test suspend function with delay`() = runTest {
        coEvery { repo.fetchUser(any()) } coAnswers {
            delay(1000) // Simulate network delay
            User("delayed", "Delayed User")
        }

        val user = repo.fetchUser("any")
        assertEquals("Delayed User", user.name)
    }

    @Test
    fun `test suspend function throws`() = runTest {
        coEvery { repo.fetchUser("error") } throws NetworkException("Connection failed")

        assertThrows<NetworkException> {
            repo.fetchUser("error")
        }
    }
}
```

### Verification with verify

```kotlin
@Test
fun `verify method calls`() {
    val repo = mockk<UserRepository>(relaxed = true)
    val service = UserService(repo)

    service.processUser("123")

    // Verify method was called
    verify { repo.getUser("123") }

    // Verify exact number of calls
    verify(exactly = 1) { repo.getUser("123") }

    // At least N calls
    verify(atLeast = 1) { repo.getUser(any()) }

    // At most N calls
    verify(atMost = 3) { repo.saveUser(any()) }

    // Method was not called
    verify(exactly = 0) { repo.getUserOrNull(any()) }

    // Or using wasNot Called
    verify { repo.getUserOrNull(any()) wasNot Called }
}
```

### coVerify for Coroutines

```kotlin
@Test
fun `verify suspend function calls`() = runTest {
    val repo = mockk<SuspendRepository>(relaxed = true)

    repo.fetchUser("123")
    repo.saveUser(User("123", "John"))

    // coVerify for suspend functions
    coVerify { repo.fetchUser("123") }
    coVerify { repo.saveUser(match { it.id == "123" }) }

    // Verify call order
    coVerifySequence {
        repo.fetchUser("123")
        repo.saveUser(any())
    }

    // Any order, but all calls
    coVerifyAll {
        repo.saveUser(any())
        repo.fetchUser("123")
    }
}
```

### Complete Test Example

```kotlin
class UserViewModelTest {
    private val repository = mockk<UserRepository>()
    private lateinit var viewModel: UserViewModel

    @Before
    fun setup() {
        viewModel = UserViewModel(repository)
    }

    @After
    fun tearDown() {
        // Clear all mocks
        clearAllMocks()
    }

    @Test
    fun `loadUser updates state on success`() = runTest {
        // Given
        val expectedUser = User("123", "John Doe")
        coEvery { repository.fetchUser("123") } returns expectedUser

        // When
        viewModel.loadUser("123")

        // Then
        assertEquals(UiState.Success(expectedUser), viewModel.uiState.value)
        coVerify(exactly = 1) { repository.fetchUser("123") }
    }

    @Test
    fun `loadUser updates state on error`() = runTest {
        // Given
        coEvery { repository.fetchUser(any()) } throws IOException("Network error")

        // When
        viewModel.loadUser("123")

        // Then
        assertTrue(viewModel.uiState.value is UiState.Error)
        coVerify { repository.fetchUser("123") }
    }
}
```

### Dependencies

```kotlin
// build.gradle.kts
dependencies {
    testImplementation("io.mockk:mockk:1.13.10")
    // For Android instrumented tests
    androidTestImplementation("io.mockk:mockk-android:1.13.10")
}
```

### Best Practices

1. Use `relaxed = true` sparingly - explicit configuration is better
2. Clear mocks in `@After` using `clearAllMocks()`
3. Use `coEvery`/`coVerify` for all suspend functions
4. Prefer `slot<T>()` for capturing and verifying arguments
5. Use `verifySequence` to verify call order

---

## Follow-ups

- How do you mock static methods or object declarations in MockK?
- What is the difference between `spyk` and `mockk`?
- How do you test private methods with MockK?
- When should you use `relaxed` mocks vs explicit stubbing?

## References

- https://mockk.io/
- https://github.com/mockk/mockk
- https://developer.android.com/training/testing/local-tests

## Related Questions

### Prerequisites (Easier)
- [[q-test-doubles--testing--medium]] - Fake vs Mock vs Stub vs Spy

### Related (Same Level)
- [[q-mockk-vs-mockito--testing--medium]] - MockK vs Mockito comparison
- [[q-coroutines-testing--testing--medium]] - Coroutine testing with runTest
- [[q-test-doubles-dependency-injection--android--medium]] - DI testing with Hilt

### Advanced (Harder)
- [[q-testing-coroutines-flow--android--hard]] - Advanced Flow testing
