---
tags:
  - testing
  - mockk
  - mocking
  - kotlin
  - unit-testing
  - coroutines
difficulty: medium
status: draft
---

# MockK Advanced Features

# Question (EN)
> Explain relaxed mocks, spy, mockk annotations, and coroutine mocking in MockK. How does it differ from Mockito?

# Вопрос (RU)
> Объясните relaxed mocks, spy, аннотации mockk и моккирование корутин в MockK. Чем он отличается от Mockito?

---

## Answer (EN)

**MockK** is a Kotlin-first mocking library that provides better support for Kotlin features than Mockito, including coroutines, extension functions, and object mocking.

---

### Basic MockK vs Mockito

**Mockito (Java-style):**

```kotlin
// Mockito - verbose and Kotlin-unfriendly
val repository = mock(UserRepository::class.java)
`when`(repository.getUser(anyInt())).thenReturn(User("John"))

verify(repository).getUser(any())
```

**MockK (Kotlin-native):**

```kotlin
// MockK - Clean Kotlin syntax
val repository = mockk<UserRepository>()
every { repository.getUser(any()) } returns User("John")

verify { repository.getUser(any()) }
```

---

### Relaxed Mocks

**Relaxed mocks** automatically return default values for unmocked calls, eliminating "UnnecessaryStubbingException":

```kotlin
// Regular mock - throws exception for unmocked calls
val mock = mockk<UserRepository>()
mock.getUserCount() //  MockKException: no answer found

// Relaxed mock - returns default values
val relaxedMock = mockk<UserRepository>(relaxed = true)
relaxedMock.getUserCount() //  Returns 0
relaxedMock.getUserName() //  Returns ""
relaxedMock.getUser() //  Returns null

// Can still override specific methods
every { relaxedMock.getUser(1) } returns User("John")
```

**Default values for relaxed mocks:**

```kotlin
val mock = mockk<SomeClass>(relaxed = true)

// Primitives
mock.getInt() // 0
mock.getLong() // 0L
mock.getFloat() // 0f
mock.getDouble() // 0.0
mock.getBoolean() // false

// Objects
mock.getString() // ""
mock.getList() // emptyList()
mock.getUser() // null (nullable)

// Collections
mock.getUsers() // emptyList()
mock.getMap() // emptyMap()
```

**When to use relaxed:**

```kotlin
//  GOOD: Testing one specific method
@Test
fun testUpdateUser() {
    val repository = mockk<UserRepository>(relaxed = true)
    every { repository.updateUser(any()) } returns true

    // Don't care about other methods
    val viewModel = UserViewModel(repository)
    viewModel.updateUser(User("John"))

    verify { repository.updateUser(any()) }
}

//  BAD: Need precise control
@Test
fun testAllMethods() {
    val repository = mockk<UserRepository>(relaxed = true)
    // Better to explicitly mock all methods
}
```

---

### Spy - Partial Mocking

**Spies** use real implementation but allow selective mocking:

```kotlin
class UserRepository {
    fun getUser(id: Int): User {
        return User("Real user $id")
    }

    fun saveUser(user: User): Boolean {
        // Real implementation
        return true
    }
}

@Test
fun testSpy() {
    val repository = spyk(UserRepository())

    // Uses real implementation
    val user1 = repository.getUser(1) // "Real user 1"

    // Override specific method
    every { repository.getUser(2) } returns User("Mocked user")

    val user2 = repository.getUser(2) // "Mocked user"
    val user3 = repository.getUser(3) // "Real user 3"

    // Verify calls
    verify {
        repository.getUser(1)
        repository.getUser(2)
        repository.getUser(3)
    }
}
```

**Spy with recordPrivateCalls:**

```kotlin
class Calculator {
    fun add(a: Int, b: Int): Int {
        return performAdd(a, b)
    }

    private fun performAdd(a: Int, b: Int): Int {
        return a + b
    }
}

@Test
fun testPrivateCalls() {
    val calculator = spyk(Calculator(), recordPrivateCalls = true)

    calculator.add(2, 3)

    // Verify private method called
    verify { calculator["performAdd"](2, 3) }
}
```

---

### MockK Annotations

Annotations simplify test setup:

```kotlin
class UserViewModelTest {
    @MockK
    lateinit var repository: UserRepository

    @MockK
    lateinit var analytics: Analytics

    @RelaxedMockK
    lateinit var logger: Logger

    @SpyK
    var calculator = Calculator()

    @InjectMockKs
    lateinit var viewModel: UserViewModel

    @Before
    fun setUp() {
        MockKAnnotations.init(this)
    }

    @Test
    fun testViewModel() {
        every { repository.getUser(any()) } returns User("John")

        val user = viewModel.loadUser(1)

        assertEquals("John", user.name)
        verify { repository.getUser(1) }
    }
}
```

**Annotation types:**

```kotlin
@MockK // Regular mock
lateinit var mock: SomeClass

@RelaxedMockK // Relaxed mock
lateinit var relaxedMock: SomeClass

@SpyK // Spy with real object
var spy = RealClass()

@InjectMockKs // Inject mocks into this object
lateinit var systemUnderTest: ClassUnderTest
```

**@InjectMockKs example:**

```kotlin
class UserViewModel(
    private val repository: UserRepository,
    private val analytics: Analytics,
    private val logger: Logger
) {
    fun loadUser(id: Int): User {
        logger.log("Loading user $id")
        val user = repository.getUser(id)
        analytics.track("user_loaded")
        return user
    }
}

class UserViewModelTest {
    @MockK
    lateinit var repository: UserRepository

    @RelaxedMockK
    lateinit var analytics: Analytics

    @RelaxedMockK
    lateinit var logger: Logger

    @InjectMockKs
    lateinit var viewModel: UserViewModel // Mocks auto-injected!

    @Before
    fun setUp() {
        MockKAnnotations.init(this)
    }

    @Test
    fun testLoadUser() {
        every { repository.getUser(1) } returns User("John")

        val user = viewModel.loadUser(1)

        assertEquals("John", user.name)
        verify { repository.getUser(1) }
        verify { analytics.track("user_loaded") }
        verify { logger.log("Loading user 1") }
    }
}
```

---

### Coroutine Mocking

MockK has first-class support for suspend functions:

**Basic suspend function:**

```kotlin
interface UserApi {
    suspend fun fetchUser(id: Int): User
}

@Test
fun testSuspendFunction() = runTest {
    val api = mockk<UserApi>()

    // Mock suspend function
    coEvery { api.fetchUser(any()) } returns User("John")

    val user = api.fetchUser(1)

    assertEquals("John", user.name)

    // Verify suspend function
    coVerify { api.fetchUser(1) }
}
```

**Flow mocking:**

```kotlin
interface UserRepository {
    fun observeUser(id: Int): Flow<User>
}

@Test
fun testFlow() = runTest {
    val repository = mockk<UserRepository>()

    // Mock flow
    every { repository.observeUser(any()) } returns flow {
        emit(User("John"))
        delay(100)
        emit(User("Jane"))
    }

    val users = repository.observeUser(1).toList()

    assertEquals(2, users.size)
    assertEquals("John", users[0].name)
    assertEquals("Jane", users[1].name)
}
```

**Delayed responses:**

```kotlin
@Test
fun testDelayedResponse() = runTest {
    val api = mockk<UserApi>()

    coEvery { api.fetchUser(any()) } coAnswers {
        delay(1000) // Simulate network delay
        User("John")
    }

    val start = System.currentTimeMillis()
    val user = api.fetchUser(1)
    val duration = System.currentTimeMillis() - start

    assertTrue(duration >= 1000)
    assertEquals("John", user.name)
}
```

**Exception throwing:**

```kotlin
@Test
fun testSuspendException() = runTest {
    val api = mockk<UserApi>()

    coEvery { api.fetchUser(any()) } throws IOException("Network error")

    assertThrows<IOException> {
        api.fetchUser(1)
    }

    coVerify { api.fetchUser(1) }
}
```

---

### Advanced Features

**1. Answer with lambda:**

```kotlin
@Test
fun testAnswers() {
    val mock = mockk<Calculator>()

    // Answer based on arguments
    every { mock.add(any(), any()) } answers {
        val a = firstArg<Int>()
        val b = secondArg<Int>()
        a + b
    }

    assertEquals(5, mock.add(2, 3))
    assertEquals(10, mock.add(4, 6))
}
```

**2. Slot capturing:**

```kotlin
@Test
fun testSlotCapture() {
    val repository = mockk<UserRepository>(relaxed = true)
    val slot = slot<User>()

    val viewModel = UserViewModel(repository)
    viewModel.saveUser("John", 25)

    verify { repository.saveUser(capture(slot)) }

    // Verify captured argument
    assertEquals("John", slot.captured.name)
    assertEquals(25, slot.captured.age)
}
```

**3. Multiple captures:**

```kotlin
@Test
fun testMultipleCaptures() {
    val repository = mockk<UserRepository>(relaxed = true)
    val slots = mutableListOf<User>()

    viewModel.saveUsers(listOf(
        User("John", 25),
        User("Jane", 30)
    ))

    verify(exactly = 2) {
        repository.saveUser(capture(slots))
    }

    assertEquals(2, slots.size)
    assertEquals("John", slots[0].name)
    assertEquals("Jane", slots[1].name)
}
```

**4. Verification ordering:**

```kotlin
@Test
fun testVerifyOrder() {
    val mock = mockk<UserRepository>(relaxed = true)

    mock.getUser(1)
    mock.saveUser(User("John"))
    mock.getUser(2)

    verifyOrder {
        mock.getUser(1)
        mock.saveUser(any())
        mock.getUser(2)
    }
}

@Test
fun testVerifySequence() {
    val mock = mockk<UserRepository>(relaxed = true)

    mock.getUser(1)
    mock.saveUser(User("John"))

    // Verify exact sequence (no other calls)
    verifySequence {
        mock.getUser(1)
        mock.saveUser(any())
    }
}
```

**5. Verification count:**

```kotlin
@Test
fun testVerifyCount() {
    val mock = mockk<UserRepository>(relaxed = true)

    repeat(3) { mock.getUser(1) }
    mock.getUser(2)

    verify(exactly = 3) { mock.getUser(1) }
    verify(exactly = 1) { mock.getUser(2) }
    verify(atLeast = 1) { mock.getUser(any()) }
    verify(atMost = 5) { mock.getUser(any()) }
}
```

**6. Object mocking:**

```kotlin
object NetworkClient {
    fun isConnected(): Boolean = true
}

@Test
fun testObjectMock() {
    mockkObject(NetworkClient)

    every { NetworkClient.isConnected() } returns false

    assertFalse(NetworkClient.isConnected())

    unmockkObject(NetworkClient)

    assertTrue(NetworkClient.isConnected())
}
```

**7. Static mocking:**

```kotlin
@Test
fun testStaticMock() {
    mockkStatic(Uri::class)

    val mockUri = mockk<Uri>()
    every { Uri.parse(any()) } returns mockUri

    val uri = Uri.parse("https://example.com")

    assertEquals(mockUri, uri)

    unmockkStatic(Uri::class)
}
```

**8. Constructor mocking:**

```kotlin
class ExpensiveClass(val value: String) {
    init {
        // Expensive initialization
        Thread.sleep(1000)
    }
}

@Test
fun testConstructorMock() {
    mockkConstructor(ExpensiveClass::class)

    every { anyConstructed<ExpensiveClass>().value } returns "mocked"

    val instance = ExpensiveClass("real")

    assertEquals("mocked", instance.value)

    unmockkConstructor(ExpensiveClass::class)
}
```

---

### MockK vs Mockito Comparison

| Feature | MockK | Mockito |
|---------|-------|---------|
| **Kotlin syntax** |  Native |  Java-style |
| **Suspend functions** |  Built-in |  Requires kotlin-mockito |
| **Extension functions** |  Supported |  Not supported |
| **Object mocking** |  Built-in |  Requires PowerMock |
| **Top-level functions** |  Supported |  Not supported |
| **Final classes** |  Works by default |  Needs mockito-inline |
| **DSL style** |  every/verify |  when/verify |
| **Relaxed mocks** |  Built-in |  Manual configuration |
| **Coroutine support** |  coEvery/coVerify |  Limited |

---

### Best Practices

**1. Use relaxed mocks judiciously:**

```kotlin
//  DO: Relaxed for dependencies you don't test
@RelaxedMockK
lateinit var logger: Logger

//  DON'T: Relaxed for main dependencies
@MockK // Better: explicit mocking
lateinit var repository: UserRepository
```

**2. Prefer mockk over spy when possible:**

```kotlin
//  DO: Mock when you need full control
val mock = mockk<UserRepository>()

//  USE SPARINGLY: Spy when you need partial mocking
val spy = spyk(UserRepository())
```

**3. Use annotations for cleaner tests:**

```kotlin
//  DO: Use annotations
@MockK lateinit var repository: UserRepository
@InjectMockKs lateinit var viewModel: UserViewModel

//  DON'T: Manual setup when annotations work
val repository = mockk<UserRepository>()
val viewModel = UserViewModel(repository)
```

**4. Clear mocks between tests:**

```kotlin
@After
fun tearDown() {
    clearAllMocks()
    unmockkAll()
}
```

---

## Ответ (RU)

**MockK** — это библиотека моккирования, ориентированная на Kotlin, которая предоставляет лучшую поддержку функций Kotlin, чем Mockito, включая корутины, функции-расширения и моккирование объектов.

### Relaxed Mocks

**Relaxed mocks** автоматически возвращают значения по умолчанию для незамокканных вызовов, устраняя исключения.

### Spy - Частичное моккирование

**Spies** используют реальную реализацию, но позволяют выборочно моккировать методы.

### Аннотации MockK

Аннотации упрощают настройку тестов: `@MockK`, `@RelaxedMockK`, `@SpyK`, `@InjectMockKs`.

### Моккирование корутин

MockK имеет встроенную поддержку suspend функций с `coEvery` и `coVerify`.

### Продвинутые функции

1. Ответы с лямбдами
2. Захват слотов
3. Проверка порядка вызовов
4. Моккирование объектов
5. Моккирование статических методов
6. Моккирование конструкторов

### MockK vs Mockito

MockK лучше для Kotlin благодаря нативному синтаксису, поддержке suspend функций, extension функций и моккирования final классов без дополнительной конфигурации.

### Лучшие практики

1. Используйте relaxed mocks разумно
2. Предпочитайте mockk вместо spy когда возможно
3. Используйте аннотации для чистоты тестов
4. Очищайте моки между тестами

MockK — предпочтительный выбор для Kotlin проектов.

---

## Related Questions

### Related (Medium)
- [[q-testing-viewmodels-turbine--testing--medium]] - Testing
- [[q-testing-compose-ui--android--medium]] - Testing
- [[q-compose-testing--android--medium]] - Testing
- [[q-robolectric-vs-instrumented--testing--medium]] - Testing
- [[q-screenshot-snapshot-testing--testing--medium]] - Testing

### Advanced (Harder)
- [[q-testing-coroutines-flow--testing--hard]] - Testing
