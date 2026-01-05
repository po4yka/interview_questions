---
id: android-351
title: MockK Advanced Features / Продвинутые возможности MockK
aliases: [MockK Advanced Features, Продвинутые возможности MockK]
topic: android
subtopics: [testing-mocks]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-testing, q-android-testing-strategies--android--medium, q-camerax-advanced-pipeline--android--hard, q-recyclerview-itemdecoration-advanced--android--medium, q-room-type-converters-advanced--android--medium, q-why-use-diffutil--android--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [android/testing-mocks, difficulty/medium]

---
# Вопрос (RU)
> Объясните relaxed mocks, spy, аннотации MockK и моккирование корутин в MockK. Чем MockK отличается от Mockito?

# Question (EN)
> Explain relaxed mocks, spy, MockK annotations, and coroutine mocking in MockK. How does it differ from Mockito?

---

## Ответ (RU)

MockK — это ориентированная на Kotlin библиотека для мокирования, которая предоставляет нативный DSL и удобную поддержку особенностей Kotlin: null-safety, корутины, suspend-функции, final-классы, объекты, top-level и extension-функции.

См. также: [[c-android-testing]].

---

### Базовое Сравнение MockK И Mockito

Этот пример показывает разницу стиля синтаксиса.

```kotlin
// Mockito — больше Java-стиль
val repository = mock(UserRepository::class.java)
`when`(repository.getUser(anyInt())).thenReturn(User("John"))

verify(repository).getUser(any())
```

```kotlin
// MockK — идиоматичный Kotlin DSL
val repository = mockk<UserRepository>()
every { repository.getUser(any()) } returns User("John")

verify { repository.getUser(any()) }
```

---

### Relaxed Mocks

Relaxed mocks автоматически возвращают значения по умолчанию для нестаббленных вызовов и таким образом избегают `MockKException: no answer found for: ...`.

```kotlin
// Обычный мок — выбрасывает исключение для нестаббленных вызовов
val mock = mockk<UserRepository>()
mock.getUserCount() // MockKException: no answer found for: UserRepository(#1).getUserCount()

// Relaxed мок — возвращает значения по умолчанию
val relaxedMock = mockk<UserRepository>(relaxed = true)
relaxedMock.getUserCount() // Возвращает 0
relaxedMock.getUserName() // Возвращает ""

// Для ссылочных типов возвращается null/пустое значение только если сигнатура позволяет
// (для не-nullable типов по-прежнему требуется корректный stub или изменение API)
relaxedMock.getNullableUser() // Возвращает null, если тип возврата User?

// Можно переопределять конкретные методы
every { relaxedMock.getUser(1) } returns User("John")
```

Типичные значения по умолчанию (пример):

```kotlin
val mock = mockk<SomeClass>(relaxed = true)

// Примитивы
mock.getInt() // 0
mock.getLong() // 0L
mock.getFloat() // 0f
mock.getDouble() // 0.0
mock.getBoolean() // false

// Объекты (в зависимости от объявленного типа)
mock.getString() // ""
mock.getList() // emptyList()
mock.getNullableUser() // null для возвращаемого типа User?

// Коллекции
mock.getUsers() // emptyList()
mock.getMap() // emptyMap()
```

Когда использовать relaxed:

```kotlin
// ХОРОШО: когда важны только некоторые взаимодействия
@Test
fun testUpdateUser() {
    val repository = mockk<UserRepository>(relaxed = true)
    every { repository.updateUser(any()) } returns true

    val viewModel = UserViewModel(repository)
    viewModel.updateUser(User("John"))

    verify { repository.updateUser(any()) }
}

// ПЛОХО: когда нужен строгий контроль всех вызовов
@Test
fun testAllMethods() {
    val repository = mockk<UserRepository>(relaxed = true)
    // В таком случае лучше использовать строгий мок без relaxed
}
```

---

### Spy — Частичное Мокирование

Spies делегируют к реальной реализации по умолчанию, но позволяют выборочно переопределять поведение.

```kotlin
class UserRepository {
    fun getUser(id: Int): User = User("Real user $id")
    fun saveUser(user: User): Boolean = true
}

@Test
fun testSpy() {
    val repository = spyk(UserRepository())

    // Используется реальная реализация
    val user1 = repository.getUser(1) // "Real user 1"

    // Переопределяем конкретный вызов
    every { repository.getUser(2) } returns User("Mocked user")

    val user2 = repository.getUser(2) // "Mocked user"
    val user3 = repository.getUser(3) // "Real user 3"

    verify {
        repository.getUser(1)
        repository.getUser(2)
        repository.getUser(3)
    }
}
```

Spy с `recordPrivateCalls`:

```kotlin
class Calculator {
    fun add(a: Int, b: Int): Int = performAdd(a, b)

    private fun performAdd(a: Int, b: Int): Int = a + b
}

@Test
fun testPrivateCalls() {
    val calculator = spyk(Calculator(), recordPrivateCalls = true)

    calculator.add(2, 3)

    // Проверяем вызов приватного метода по имени
    verify { calculator["performAdd"](2, 3) }
}
```

Используйте spies умеренно; по возможности предпочитайте чистые моки и хорошо спроектированных коллабораторов.

---

### Аннотации MockK

Аннотации уменьшают шаблонный код при настройке тестов.

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

Основные типы аннотаций:

```kotlin
@MockK // Обычный мок
lateinit var mock: SomeClass

@RelaxedMockK // Relaxed мок
lateinit var relaxedMock: SomeClass

@SpyK // Spy на реальном объекте
var spy = RealClass()

@InjectMockKs // Внедрение моков/spy в тестируемый объект
lateinit var systemUnderTest: ClassUnderTest
```

Пример `@InjectMockKs`:

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
    lateinit var viewModel: UserViewModel

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

### Моккирование Корутин

MockK имеет полноценную поддержку suspend-функций через `coEvery` / `coVerify`.

Базовый пример с suspend-функцией:

```kotlin
interface UserApi {
    suspend fun fetchUser(id: Int): User
}

@Test
fun testSuspendFunction() = runTest {
    val api = mockk<UserApi>()

    coEvery { api.fetchUser(any()) } returns User("John")

    val user = api.fetchUser(1)

    assertEquals("John", user.name)
    coVerify { api.fetchUser(1) }
}
```

Моккирование `Flow`:

```kotlin
interface UserRepository {
    fun observeUser(id: Int): Flow<User>
}

@Test
fun testFlow() = runTest {
    val repository = mockk<UserRepository>()

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

Исключения в suspend-функциях:

```kotlin
@Test
fun testSuspendException() = runTest {
    val api = mockk<UserApi>()

    coEvery { api.fetchUser(any()) } throws IOException("Network error")

    assertThrows<IOException> {
        // Внутри runTest можно напрямую вызывать suspend-функцию
        api.fetchUser(1)
    }

    coVerify { api.fetchUser(1) }
}
```

---

### Продвинутые Возможности

1. Ответы через лямбда (`answers`):

```kotlin
@Test
fun testAnswers() {
    val mock = mockk<Calculator>()

    every { mock.add(any(), any()) } answers {
        val a = firstArg<Int>()
        val b = secondArg<Int>()
        a + b
    }

    assertEquals(5, mock.add(2, 3))
    assertEquals(10, mock.add(4, 6))
}
```

1. Захват аргументов (`slot`):

```kotlin
@Test
fun testSlotCapture() {
    val repository = mockk<UserRepository>(relaxed = true)
    val slot = slot<User>()
    val viewModel = UserViewModel(repository)

    viewModel.saveUser("John", 25)

    verify { repository.saveUser(capture(slot)) }

    assertEquals("John", slot.captured.name)
    assertEquals(25, slot.captured.age)
}
```

1. Множественный захват:

```kotlin
@Test
fun testMultipleCaptures() {
    val repository = mockk<UserRepository>(relaxed = true)
    val captured = mutableListOf<User>()
    val viewModel = UserViewModel(repository)

    viewModel.saveUsers(
        listOf(
            User("John", 25),
            User("Jane", 30)
        )
    )

    verify(exactly = 2) {
        repository.saveUser(capture(captured))
    }

    assertEquals(2, captured.size)
    assertEquals("John", captured[0].name)
    assertEquals("Jane", captured[1].name)
}
```

1. Проверка порядка вызовов:

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

    // Проверка точной последовательности (без других вызовов)
    verifySequence {
        mock.getUser(1)
        mock.saveUser(any())
    }
}
```

1. Проверка количества вызовов:

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

1. Моккирование `object`:

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

1. Моккирование статических / top-level функций:

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

1. Моккирование конструкторов:

```kotlin
class ExpensiveClass(val value: String) {
    init {
        // Дорогая инициализация
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

### Сравнение MockK И Mockito

Ключевые различия (для Kotlin + Android):

- MockK:
  - Kotlin-first DSL: `every { ... }`, `verify { ... }`, `coEvery`, `coVerify`.
  - Встроенная поддержка suspend-функций, корутин, top-level/extension/object-функций, моккинга конструкторов.
  - Relaxed mocks из коробки.
- Mockito:
  - Изначально Java-ориентирован; поддержка Kotlin улучшена через дополнительные артефакты (`mockito-inline`, `mockito-kotlin`).
  - Современные версии позволяют мокать final-классы и статические методы; конфигурация для Kotlin-кейсов зачастую чуть более многословна по сравнению с MockK.

Главный вывод для собеседования: MockK обычно требует меньше обходных путей для Kotlin-специфичных задач; Mockito способен на сопоставимый функционал, но иногда с дополнительной конфигурацией.

---

### Лучшие Практики

1. Осторожно используйте relaxed mocks:

```kotlin
// МОЖНО: для зависимостей, где взаимодействия не критичны
@RelaxedMockK
lateinit var logger: Logger

// НЕ НУЖНО: для важных коллабораторов, где требуется строгая проверка
@MockK
lateinit var repository: UserRepository
```

1. Предпочитайте чистые моки spy-объектам:

```kotlin
// Предпочтительно
val mock = mockk<UserRepository>()

// Spy используйте только при реальной необходимости частичного мокинга
val spy = spyk(UserRepository())
```

1. Используйте аннотации для более чистых тестов:

```kotlin
@MockK lateinit var repository: UserRepository
@InjectMockKs lateinit var viewModel: UserViewModel
```

1. Очищайте состояние между тестами при использовании глобальных моков:

```kotlin
@After
fun tearDown() {
    clearAllMocks()
    unmockkAll()
}
```

---

## Answer (EN)

MockK is a Kotlin-first mocking library that provides strong support for Kotlin features (null-safety, coroutines, extension functions, objects, top-level functions, final classes) with a DSL that feels natural in Kotlin, and often requires less configuration than Mockito for Kotlin-heavy codebases.

See also: [[c-android-testing]].

---

### Basic MockK Vs Mockito

This example shows the difference in syntax style.

```kotlin
// Mockito - more Java-style in plain usage
val repository = mock(UserRepository::class.java)
`when`(repository.getUser(anyInt())).thenReturn(User("John"))

verify(repository).getUser(any())
```

```kotlin
// MockK - idiomatic Kotlin DSL
val repository = mockk<UserRepository>()
every { repository.getUser(any()) } returns User("John")

verify { repository.getUser(any()) }
```

---

### Relaxed Mocks

Relaxed mocks automatically return default values for unmocked calls to avoid `MockKException: no answer found for: ...` within MockK.

```kotlin
// Regular mock - throws exception for unmocked calls
val mock = mockk<UserRepository>()
mock.getUserCount() // MockKException: no answer found for: UserRepository(#1).getUserCount()

// Relaxed mock - returns default values
val relaxedMock = mockk<UserRepository>(relaxed = true)
relaxedMock.getUserCount() // Returns 0
relaxedMock.getUserName() // Returns ""

// For reference types, null/empty is returned only if the signature allows it
// (non-nullable return types still require proper stubbing or API adjustment)
relaxedMock.getNullableUser() // Returns null if return type is User?

// You can still override specific methods
every { relaxedMock.getUser(1) } returns User("John")
```

Typical default values (conceptual examples):

```kotlin
val mock = mockk<SomeClass>(relaxed = true)

// Primitives
mock.getInt() // 0
mock.getLong() // 0L
mock.getFloat() // 0f
mock.getDouble() // 0.0
mock.getBoolean() // false

// Objects (depending on declared type)
mock.getString() // ""
mock.getList() // emptyList()
mock.getNullableUser() // null for return type User?

// Collections
mock.getUsers() // emptyList()
mock.getMap() // emptyMap()
```

When to use relaxed:

```kotlin
// GOOD: When only some interactions matter
@Test
fun testUpdateUser() {
    val repository = mockk<UserRepository>(relaxed = true)
    every { repository.updateUser(any()) } returns true

    val viewModel = UserViewModel(repository)
    viewModel.updateUser(User("John"))

    verify { repository.updateUser(any()) }
}

// BAD: When you need strict control over all calls
@Test
fun testAllMethods() {
    val repository = mockk<UserRepository>(relaxed = true)
    // Better: use non-relaxed mock and explicitly stub / verify interactions
}
```

---

### Spy - Partial Mocking

Spies delegate to real implementation by default, but allow selective stubbing.

```kotlin
class UserRepository {
    fun getUser(id: Int): User = User("Real user $id")
    fun saveUser(user: User): Boolean = true
}

@Test
fun testSpy() {
    val repository = spyk(UserRepository())

    // Uses real implementation
    val user1 = repository.getUser(1) // "Real user 1"

    // Override specific call
    every { repository.getUser(2) } returns User("Mocked user")

    val user2 = repository.getUser(2) // "Mocked user"
    val user3 = repository.getUser(3) // "Real user 3"

    verify {
        repository.getUser(1)
        repository.getUser(2)
        repository.getUser(3)
    }
}
```

Spy with `recordPrivateCalls`:

```kotlin
class Calculator {
    fun add(a: Int, b: Int): Int = performAdd(a, b)

    private fun performAdd(a: Int, b: Int): Int = a + b
}

@Test
fun testPrivateCalls() {
    val calculator = spyk(Calculator(), recordPrivateCalls = true)

    calculator.add(2, 3)

    // Verify private method call by name
    verify { calculator["performAdd"](2, 3) }
}
```

Use spies sparingly; prefer pure mocks plus well-designed collaborators where possible.

---

### MockK Annotations

Annotations reduce boilerplate in test setup.

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

Main annotation types:

```kotlin
@MockK // Regular mock
lateinit var mock: SomeClass

@RelaxedMockK // Relaxed mock
lateinit var relaxedMock: SomeClass

@SpyK // Spy using real object
var spy = RealClass()

@InjectMockKs // Inject mocks/spy into this object
lateinit var systemUnderTest: ClassUnderTest
```

`@InjectMockKs` example:

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
    lateinit var viewModel: UserViewModel

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

### `Coroutine` Mocking

MockK has first-class support for suspend functions via `coEvery` / `coVerify`.

Basic suspend function:

```kotlin
interface UserApi {
    suspend fun fetchUser(id: Int): User
}

@Test
fun testSuspendFunction() = runTest {
    val api = mockk<UserApi>()

    coEvery { api.fetchUser(any()) } returns User("John")

    val user = api.fetchUser(1)

    assertEquals("John", user.name)
    coVerify { api.fetchUser(1) }
}
```

`Flow` mocking:

```kotlin
interface UserRepository {
    fun observeUser(id: Int): Flow<User>
}

@Test
fun testFlow() = runTest {
    val repository = mockk<UserRepository>()

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

Exception throwing in suspend functions:

```kotlin
@Test
fun testSuspendException() = runTest {
    val api = mockk<UserApi>()

    coEvery { api.fetchUser(any()) } throws IOException("Network error")

    assertThrows<IOException> {
        // Inside runTest we can call the suspend function directly
        api.fetchUser(1)
    }

    coVerify { api.fetchUser(1) }
}
```

---

### Advanced Features

1. Answers with lambda (dynamic behavior):

```kotlin
@Test
fun testAnswers() {
    val mock = mockk<Calculator>()

    every { mock.add(any(), any()) } answers {
        val a = firstArg<Int>()
        val b = secondArg<Int>()
        a + b
    }

    assertEquals(5, mock.add(2, 3))
    assertEquals(10, mock.add(4, 6))
}
```

1. Slot capturing (capture arguments):

```kotlin
@Test
fun testSlotCapture() {
    val repository = mockk<UserRepository>(relaxed = true)
    val slot = slot<User>()
    val viewModel = UserViewModel(repository)

    viewModel.saveUser("John", 25)

    verify { repository.saveUser(capture(slot)) }

    assertEquals("John", slot.captured.name)
    assertEquals(25, slot.captured.age)
}
```

1. Multiple captures:

```kotlin
@Test
fun testMultipleCaptures() {
    val repository = mockk<UserRepository>(relaxed = true)
    val captured = mutableListOf<User>()
    val viewModel = UserViewModel(repository)

    viewModel.saveUsers(
        listOf(
            User("John", 25),
            User("Jane", 30)
        )
    )

    verify(exactly = 2) {
        repository.saveUser(capture(captured))
    }

    assertEquals(2, captured.size)
    assertEquals("John", captured[0].name)
    assertEquals("Jane", captured[1].name)
}
```

1. Verification ordering:

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

1. Verification count:

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

1. Object mocking:

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

1. Static/top-level function mocking:

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

1. Constructor mocking:

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

### MockK Vs Mockito Comparison

High-level differences (as relevant for Kotlin + Android at time of writing):

- MockK:
  - Kotlin-first DSL: `every { ... }`, `verify { ... }`, `coEvery`, `coVerify`.
  - Built-in support for suspend functions, coroutines, top-level/extension/object functions, constructor mocking.
  - Relaxed mocks built-in.
- Mockito:
  - Primarily Java-first; Kotlin support improved via inline mocking and additional artifacts.
  - With newer versions + `mockito-inline` / `mockito-kotlin`, can mock final classes and use more idiomatic Kotlin helpers.
  - Static/object mocking is available in core; configuration may be somewhat more verbose for some Kotlin scenarios compared to MockK.

The key interview takeaway: MockK tends to require fewer workarounds for Kotlin-specific features; Mockito can achieve most of this with additional setup and APIs.

---

### Best Practices

1. Use relaxed mocks judiciously:

```kotlin
// DO: Relaxed for dependencies where interactions are not critical
@RelaxedMockK
lateinit var logger: Logger

// DON'T: Relax important collaborators where you need strict verification
@MockK
lateinit var repository: UserRepository
```

1. Prefer pure mocks over spies when possible:

```kotlin
// Prefer
val mock = mockk<UserRepository>()

// Use spy only when you truly need partial mocking
val spy = spyk(UserRepository())
```

1. Use annotations for cleaner tests:

```kotlin
@MockK lateinit var repository: UserRepository
@InjectMockKs lateinit var viewModel: UserViewModel
```

1. Clear state between tests when using global mocking helpers:

```kotlin
@After
fun tearDown() {
    clearAllMocks()
    unmockkAll()
}
```

---

## Дополнительные Вопросы (RU)

- [[q-android-testing-strategies--android--medium]]
- [[q-why-use-diffutil--android--medium]]
- Как мокировать top-level функции и `object`-singletons в MockK?
- Как протестировать сложную логику ретраев с использованием `answers` и `slot` в MockK?
- Когда стоит предпочитать Mockito вместо MockK в Android-проекте?

## Follow-ups

- [[q-android-testing-strategies--android--medium]]
- [[q-why-use-diffutil--android--medium]]
- How to mock top-level functions and `object` singletons in MockK?
- How to test complex retry logic using `answers` and `slot` in MockK?
- When should you prefer Mockito over MockK in an Android project?

## Ссылки (RU)

- [Local Unit Tests](https://developer.android.com/training/testing/local-tests)
- [Android Documentation](https://developer.android.com/docs)

## References

- [Local Unit Tests](https://developer.android.com/training/testing/local-tests)
- [Android Documentation](https://developer.android.com/docs)

## Связанные Вопросы (RU)

### Предпосылки / Концепции

### Другие

- [[q-android-testing-strategies--android--medium]]
- [[q-why-use-diffutil--android--medium]]

## Related Questions

### Prerequisites / Concepts

### Related (Medium)

- [[q-android-testing-strategies--android--medium]]
- [[q-why-use-diffutil--android--medium]]
