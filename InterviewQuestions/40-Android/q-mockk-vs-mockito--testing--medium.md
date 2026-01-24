---
id: android-402
title: "MockK vs Mockito / MockK против Mockito"
aliases: ["MockK vs Mockito", "MockK против Mockito"]
topic: android
subtopics: [testing-unit, testing]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-testing, q-mockk-basics--testing--medium, q-test-doubles--testing--medium, q-coroutines-testing--testing--medium]
created: 2026-01-23
updated: 2026-01-23
tags: [android/testing-unit, difficulty/medium, mockk, mockito, kotlin, mocking, comparison]

---
# Vopros (RU)

> В чем разница между MockK и Mockito для тестирования в Kotlin?

# Question (EN)

> What is the difference between MockK and Mockito for Kotlin testing?

---

## Otvet (RU)

**MockK** и **Mockito** - две популярные библиотеки мокирования. MockK создан специально для Kotlin и использует его возможности, тогда как Mockito изначально разрабатывался для Java.

### Краткий Ответ

| Аспект | MockK | Mockito |
|--------|-------|---------|
| Язык | Kotlin-first | Java-first (есть mockito-kotlin) |
| Корутины | Встроенная поддержка | Через mockito-kotlin |
| Final классы | Работает из коробки | Требует настройки |
| DSL | Идиоматичный Kotlin | Java-style API |
| Производительность | Медленнее при запуске | Быстрее |

### Подробный Ответ

### Синтаксис Создания Моков

```kotlin
// MockK
val repository = mockk<UserRepository>()

// Mockito
val repository = mock<UserRepository>()
// или с mockito-kotlin
val repository: UserRepository = mock()
```

### Настройка Поведения

```kotlin
// MockK - DSL-стиль
every { repository.getUser("123") } returns User("123", "John")
every { repository.getUser(any()) } throws NotFoundException()

// Mockito - method-chain стиль
`when`(repository.getUser("123")).thenReturn(User("123", "John"))
whenever(repository.getUser(any())).thenThrow(NotFoundException())

// MockK с блоком answers
every { repository.getUser(any()) } answers {
    val id = firstArg<String>()
    User(id, "User $id")
}

// Mockito с Answer
whenever(repository.getUser(any())).thenAnswer { invocation ->
    val id = invocation.getArgument<String>(0)
    User(id, "User $id")
}
```

### Поддержка Корутин

```kotlin
// MockK - встроенная поддержка
coEvery { repository.fetchUser("123") } returns User("123", "John")
coVerify { repository.fetchUser("123") }

// Mockito-Kotlin - требует специальных функций
whenever(repository.fetchUser("123")).thenReturn(User("123", "John"))
// или через runBlocking
runBlocking {
    whenever(repository.fetchUser("123")).thenReturn(User("123", "John"))
}
```

### Final Классы и Методы

```kotlin
// MockK - работает из коробки
class FinalService {
    fun process(): String = "real"
}

val service = mockk<FinalService>()
every { service.process() } returns "mocked"

// Mockito - требует MockitoExtensions или mock-maker-inline
// Нужно создать файл:
// src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker
// с содержимым: mock-maker-inline
```

### Object и Companion Object

```kotlin
object UserManager {
    fun getCurrentUser(): User = User("real", "Real User")
}

class ServiceWithCompanion {
    companion object {
        fun create(): ServiceWithCompanion = ServiceWithCompanion()
    }
}

// MockK - полная поддержка
mockkObject(UserManager)
every { UserManager.getCurrentUser() } returns User("mock", "Mock User")
unmockkObject(UserManager)

mockkObject(ServiceWithCompanion.Companion)
every { ServiceWithCompanion.create() } returns mockk()
unmockkObject(ServiceWithCompanion.Companion)

// Mockito - не поддерживает напрямую
// Требуется рефакторинг кода или PowerMock
```

### Верификация Вызовов

```kotlin
// MockK
verify { repository.getUser("123") }
verify(exactly = 2) { repository.getUser(any()) }
verify(atLeast = 1, atMost = 3) { repository.saveUser(any()) }
verify { repository.deleteUser(any()) wasNot Called }

verifySequence {
    repository.getUser("123")
    repository.saveUser(any())
}

verifyOrder {
    repository.getUser("123")
    repository.saveUser(any())
    // Может быть что-то между ними
}

// Mockito
verify(repository).getUser("123")
verify(repository, times(2)).getUser(any())
verify(repository, atLeast(1)).saveUser(any())
verify(repository, never()).deleteUser(any())

val inOrder = inOrder(repository)
inOrder.verify(repository).getUser("123")
inOrder.verify(repository).saveUser(any())
```

### Захват Аргументов

```kotlin
// MockK
val slot = slot<User>()
every { repository.saveUser(capture(slot)) } returns true

repository.saveUser(User("123", "John"))
assertEquals("John", slot.captured.name)

// Для множественных вызовов
val slots = mutableListOf<User>()
every { repository.saveUser(capture(slots)) } returns true

// Mockito
val captor = argumentCaptor<User>()
whenever(repository.saveUser(captor.capture())).thenReturn(true)

repository.saveUser(User("123", "John"))
assertEquals("John", captor.firstValue.name)

// Все значения
captor.allValues.forEach { user -> println(user.name) }
```

### Relaxed Mocks

```kotlin
// MockK - встроенная поддержка
val repo = mockk<UserRepository>(relaxed = true)
// Возвращает значения по умолчанию: 0, "", false, null, пустые коллекции

val repoUnitRelaxed = mockk<UserRepository>(relaxUnitFun = true)
// Только Unit-функции не требуют stubbing

// Mockito
val repo = mock<UserRepository> {
    on { getUser(any()) } doReturn User("default", "Default")
}
// Или RETURNS_DEFAULTS, RETURNS_SMART_NULLS
val repo = mock<UserRepository>(defaultAnswer = Answers.RETURNS_SMART_NULLS)
```

### Spy (Частичное Мокирование)

```kotlin
class RealRepository {
    fun getUser(id: String): User = User(id, "Real User")
    fun processUser(id: String): String {
        val user = getUser(id)
        return "Processed: ${user.name}"
    }
}

// MockK
val spy = spyk(RealRepository())
every { spy.getUser(any()) } returns User("mock", "Mock User")
// processUser использует замоканный getUser
val result = spy.processUser("123")
assertEquals("Processed: Mock User", result)

// Mockito
val spy = spy(RealRepository())
whenever(spy.getUser(any())).thenReturn(User("mock", "Mock User"))
val result = spy.processUser("123")
assertEquals("Processed: Mock User", result)
```

### Производительность

```kotlin
// MockK
// + Медленнее при первом запуске (компиляция DSL)
// + Быстрее при большом количестве моков в одном тесте
// - Больше памяти

// Mockito
// + Быстрее при запуске
// + Меньше памяти
// + Лучше для CI с частыми перезапусками
```

### Рекомендации по Выбору

**Используйте MockK когда:**
- Проект полностью на Kotlin
- Активно используются корутины
- Нужно мокировать object/companion
- Нужно мокировать final классы без настройки
- Команда предпочитает Kotlin DSL

**Используйте Mockito когда:**
- Смешанный Java/Kotlin проект
- Команда знакома с Mockito
- Критична производительность тестов
- Простые тесты без корутин

### Миграция с Mockito на MockK

```kotlin
// Mockito
@Mock lateinit var repository: UserRepository
@InjectMocks lateinit var service: UserService

// MockK
@MockK lateinit var repository: UserRepository
@InjectMockKs lateinit var service: UserService

@Before
fun setup() {
    MockKAnnotations.init(this)
}

// Или без аннотаций
val repository = mockk<UserRepository>()
val service = UserService(repository)
```

### Зависимости

```kotlin
// MockK
testImplementation("io.mockk:mockk:1.13.10")
androidTestImplementation("io.mockk:mockk-android:1.13.10")

// Mockito с Kotlin extensions
testImplementation("org.mockito:mockito-core:5.10.0")
testImplementation("org.mockito.kotlin:mockito-kotlin:5.2.1")
androidTestImplementation("org.mockito:mockito-android:5.10.0")
```

---

## Answer (EN)

**MockK** and **Mockito** are two popular mocking libraries. MockK was built specifically for Kotlin and leverages its features, while Mockito was originally designed for Java.

### Short Version

| Aspect | MockK | Mockito |
|--------|-------|---------|
| Language | Kotlin-first | Java-first (mockito-kotlin exists) |
| Coroutines | Built-in support | Via mockito-kotlin |
| Final classes | Works out of the box | Requires configuration |
| DSL | Idiomatic Kotlin | Java-style API |
| Performance | Slower startup | Faster |

### Detailed Version

### Mock Creation Syntax

```kotlin
// MockK
val repository = mockk<UserRepository>()

// Mockito
val repository = mock<UserRepository>()
// or with mockito-kotlin
val repository: UserRepository = mock()
```

### Configuring Behavior

```kotlin
// MockK - DSL style
every { repository.getUser("123") } returns User("123", "John")
every { repository.getUser(any()) } throws NotFoundException()

// Mockito - method-chain style
`when`(repository.getUser("123")).thenReturn(User("123", "John"))
whenever(repository.getUser(any())).thenThrow(NotFoundException())

// MockK with answers block
every { repository.getUser(any()) } answers {
    val id = firstArg<String>()
    User(id, "User $id")
}

// Mockito with Answer
whenever(repository.getUser(any())).thenAnswer { invocation ->
    val id = invocation.getArgument<String>(0)
    User(id, "User $id")
}
```

### Coroutine Support

```kotlin
// MockK - built-in support
coEvery { repository.fetchUser("123") } returns User("123", "John")
coVerify { repository.fetchUser("123") }

// Mockito-Kotlin - requires special functions
whenever(repository.fetchUser("123")).thenReturn(User("123", "John"))
// or via runBlocking
runBlocking {
    whenever(repository.fetchUser("123")).thenReturn(User("123", "John"))
}
```

### Final Classes and Methods

```kotlin
// MockK - works out of the box
class FinalService {
    fun process(): String = "real"
}

val service = mockk<FinalService>()
every { service.process() } returns "mocked"

// Mockito - requires MockitoExtensions or mock-maker-inline
// Need to create file:
// src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker
// with content: mock-maker-inline
```

### Object and Companion Object

```kotlin
object UserManager {
    fun getCurrentUser(): User = User("real", "Real User")
}

class ServiceWithCompanion {
    companion object {
        fun create(): ServiceWithCompanion = ServiceWithCompanion()
    }
}

// MockK - full support
mockkObject(UserManager)
every { UserManager.getCurrentUser() } returns User("mock", "Mock User")
unmockkObject(UserManager)

mockkObject(ServiceWithCompanion.Companion)
every { ServiceWithCompanion.create() } returns mockk()
unmockkObject(ServiceWithCompanion.Companion)

// Mockito - no direct support
// Requires code refactoring or PowerMock
```

### Call Verification

```kotlin
// MockK
verify { repository.getUser("123") }
verify(exactly = 2) { repository.getUser(any()) }
verify(atLeast = 1, atMost = 3) { repository.saveUser(any()) }
verify { repository.deleteUser(any()) wasNot Called }

verifySequence {
    repository.getUser("123")
    repository.saveUser(any())
}

verifyOrder {
    repository.getUser("123")
    repository.saveUser(any())
    // Can have other calls between
}

// Mockito
verify(repository).getUser("123")
verify(repository, times(2)).getUser(any())
verify(repository, atLeast(1)).saveUser(any())
verify(repository, never()).deleteUser(any())

val inOrder = inOrder(repository)
inOrder.verify(repository).getUser("123")
inOrder.verify(repository).saveUser(any())
```

### Argument Capture

```kotlin
// MockK
val slot = slot<User>()
every { repository.saveUser(capture(slot)) } returns true

repository.saveUser(User("123", "John"))
assertEquals("John", slot.captured.name)

// For multiple calls
val slots = mutableListOf<User>()
every { repository.saveUser(capture(slots)) } returns true

// Mockito
val captor = argumentCaptor<User>()
whenever(repository.saveUser(captor.capture())).thenReturn(true)

repository.saveUser(User("123", "John"))
assertEquals("John", captor.firstValue.name)

// All values
captor.allValues.forEach { user -> println(user.name) }
```

### Relaxed Mocks

```kotlin
// MockK - built-in support
val repo = mockk<UserRepository>(relaxed = true)
// Returns default values: 0, "", false, null, empty collections

val repoUnitRelaxed = mockk<UserRepository>(relaxUnitFun = true)
// Only Unit functions don't require stubbing

// Mockito
val repo = mock<UserRepository> {
    on { getUser(any()) } doReturn User("default", "Default")
}
// Or RETURNS_DEFAULTS, RETURNS_SMART_NULLS
val repo = mock<UserRepository>(defaultAnswer = Answers.RETURNS_SMART_NULLS)
```

### Spy (Partial Mocking)

```kotlin
class RealRepository {
    fun getUser(id: String): User = User(id, "Real User")
    fun processUser(id: String): String {
        val user = getUser(id)
        return "Processed: ${user.name}"
    }
}

// MockK
val spy = spyk(RealRepository())
every { spy.getUser(any()) } returns User("mock", "Mock User")
// processUser uses the mocked getUser
val result = spy.processUser("123")
assertEquals("Processed: Mock User", result)

// Mockito
val spy = spy(RealRepository())
whenever(spy.getUser(any())).thenReturn(User("mock", "Mock User"))
val result = spy.processUser("123")
assertEquals("Processed: Mock User", result)
```

### Performance

```kotlin
// MockK
// + Slower on first run (DSL compilation)
// + Faster with many mocks in one test
// - More memory usage

// Mockito
// + Faster startup
// + Less memory
// + Better for CI with frequent restarts
```

### Selection Guidelines

**Use MockK when:**
- Project is fully Kotlin
- Heavy coroutine usage
- Need to mock object/companion
- Need to mock final classes without configuration
- Team prefers Kotlin DSL

**Use Mockito when:**
- Mixed Java/Kotlin project
- Team is familiar with Mockito
- Test performance is critical
- Simple tests without coroutines

### Migration from Mockito to MockK

```kotlin
// Mockito
@Mock lateinit var repository: UserRepository
@InjectMocks lateinit var service: UserService

// MockK
@MockK lateinit var repository: UserRepository
@InjectMockKs lateinit var service: UserService

@Before
fun setup() {
    MockKAnnotations.init(this)
}

// Or without annotations
val repository = mockk<UserRepository>()
val service = UserService(repository)
```

### Dependencies

```kotlin
// MockK
testImplementation("io.mockk:mockk:1.13.10")
androidTestImplementation("io.mockk:mockk-android:1.13.10")

// Mockito with Kotlin extensions
testImplementation("org.mockito:mockito-core:5.10.0")
testImplementation("org.mockito.kotlin:mockito-kotlin:5.2.1")
androidTestImplementation("org.mockito:mockito-android:5.10.0")
```

---

## Follow-ups

- How do you migrate a large test suite from Mockito to MockK?
- What are the memory implications of using MockK in large test suites?
- How do you handle inline functions with MockK?

## References

- https://mockk.io/
- https://github.com/mockito/mockito-kotlin
- https://site.mockito.org/

## Related Questions

### Prerequisites (Easier)
- [[q-test-doubles--testing--medium]] - Fake vs Mock vs Stub vs Spy

### Related (Same Level)
- [[q-mockk-basics--testing--medium]] - MockK basics
- [[q-coroutines-testing--testing--medium]] - Coroutine testing

### Advanced (Harder)
- [[q-testing-coroutines-flow--android--hard]] - Advanced Flow testing
